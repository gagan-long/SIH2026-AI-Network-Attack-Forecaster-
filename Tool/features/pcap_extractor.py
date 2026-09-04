# features/pcap_extractor.py
import os
import math
import numpy as np
import pandas as pd
from scapy.all import rdpcap, IP, TCP, UDP
from collections import defaultdict

def calculate_entropy(port_list):
    """Calculates Shannon entropy for destination ports to detect port scanning."""
    if not port_list:
        return 0.0
    port_counts = pd.Series(port_list).value_counts()
    probabilities = port_counts / len(port_list)
    entropy = -sum(probabilities * np.log2(probabilities))
    return float(entropy)

def extract_pcap_features(pcap_path):
    """
    Reads a raw .pcap file and extracts flow and packet-level features 
    that align with the canonical 32-feature schema.
    """
    if not os.path.exists(pcap_path):
        raise FileNotFoundError(f"PCAP file not found: {pcap_path}")

    # Read packets into memory
    packets = rdpcap(pcap_path)
    
    # Dictionary to hold session aggregations based on 5-tuple + direction
    flows = defaultdict(lambda: {
        'Timestamp': [], 'Fwd Pkts': 0, 'Bwd Pkts': 0, 
        'Fwd Bytes': 0, 'Bwd Bytes': 0, 'Fwd Pkt Lens': [], 'Bwd Pkt Lens': [],
        'Flags': {'FIN': 0, 'SYN': 0, 'RST': 0, 'PSH': 0, 'ACK': 0, 'URG': 0},
        'TTLs': [], 'Dest Ports': [], 'Duplicate Seqs': set(), 'Retransmissions': 0
    })

    print(f"[INFO] Analyzing {len(packets)} packets from {pcap_path}...")

    # First pass: Aggregate packets into bidirectional flows
    for pkt in packets:
        if not pkt.haslayer(IP):
            continue
            
        ip_layer = pkt[IP]
        src_ip = ip_layer.src
        dst_ip = ip_layer.dst
        proto = ip_layer.proto
        ttl = ip_layer.ttl
        
        sport, dport = 0, 0
        flags = ""
        seq = None
        
        if pkt.haslayer(TCP):
            sport = pkt[TCP].sport
            dport = pkt[TCP].dport
            flags = pkt[TCP].flags
            seq = pkt[TCP].seq
        elif pkt.haslayer(UDP):
            sport = pkt[UDP].sport
            dport = pkt[UDP].dport
            
        # Determine flow direction (smallest IP first to normalize the key)
        if src_ip < dst_ip:
            flow_key = f"{src_ip}-{dst_ip}-{sport}-{dport}-{proto}"
            direction = 'Fwd'
        else:
            flow_key = f"{dst_ip}-{src_ip}-{dport}-{sport}-{proto}"
            direction = 'Bwd'

        # Extract timestamp (handle Scapy float/Edecimal timestamps)
        timestamp = float(pkt.time)
        pkt_len = len(pkt)
        
        # Populate flow metrics
        f = flows[flow_key]
        f['Timestamp'].append(timestamp)
        f['TTLs'].append(ttl)
        f['Dest Ports'].append(dport)
        
        if direction == 'Fwd':
            f['Fwd Pkts'] += 1
            f['Fwd Bytes'] += pkt_len
            f['Fwd Pkt Lens'].append(pkt_len)
        else:
            f['Bwd Pkts'] += 1
            f['Bwd Bytes'] += pkt_len
            f['Bwd Pkt Lens'].append(pkt_len)
            
        # Process TCP Flags
        if 'F' in flags: f['Flags']['FIN'] += 1
        if 'S' in flags: f['Flags']['SYN'] += 1
        if 'R' in flags: f['Flags']['RST'] += 1
        if 'P' in flags: f['Flags']['PSH'] += 1
        if 'A' in flags: f['Flags']['ACK'] += 1
        if 'U' in flags: f['Flags']['URG'] += 1
            
        # Track TCP retransmissions (duplicate sequence numbers from the same source)
        if seq is not None:
            seq_key = f"{src_ip}-{seq}"
            if seq_key in f['Duplicate Seqs']:
                f['Retransmissions'] += 1
            else:
                f['Duplicate Seqs'].add(seq_key)

    # Second pass: Compile aggregated flow statistics into a DataFrame
    extracted_data = []
    
    for key, f in flows.items():
        src_ip, dst_ip, sport, dport, proto = key.split('-')
        
        start_time = min(f['Timestamp'])
        end_time = max(f['Timestamp'])
        duration = end_time - start_time
        
        fwd_lens = f['Fwd Pkt Lens'] if f['Fwd Pkt Lens'] else [0]
        bwd_lens = f['Bwd Pkt Lens'] if f['Bwd Pkt Lens'] else [0]
        
        record = {
            'Timestamp': pd.to_datetime(start_time, unit='s'),
            'Src IP': src_ip,
            'Dst IP': dst_ip,
            'Dst Port': int(dport),
            'Protocol': int(proto),
            'Flow Duration': duration,
            'Tot Fwd Pkts': f['Fwd Pkts'],
            'Tot Bwd Pkts': f['Bwd Pkts'],
            'TotLen Fwd Pkts': f['Fwd Bytes'],
            'TotLen Bwd Pkts': f['Bwd Bytes'],
            'Fwd Pkt Len Max': max(fwd_lens),
            'Fwd Pkt Len Min': min(fwd_lens),
            'Fwd Pkt Len Mean': np.mean(fwd_lens),
            'Fwd Pkt Len Std': np.std(fwd_lens),
            'Bwd Pkt Len Max': max(bwd_lens),
            'Bwd Pkt Len Min': min(bwd_lens),
            'Bwd Pkt Len Mean': np.mean(bwd_lens),
            'Bwd Pkt Len Std': np.std(bwd_lens),
            'Flow Byts/s': (f['Fwd Bytes'] + f['Bwd Bytes']) / duration if duration > 0 else 0,
            'Flow Pkts/s': (f['Fwd Pkts'] + f['Bwd Pkts']) / duration if duration > 0 else 0,
            'FIN Flag Cnt': f['Flags']['FIN'],
            'SYN Flag Cnt': f['Flags']['SYN'],
            'RST Flag Cnt': f['Flags']['RST'],
            'PSH Flag Cnt': f['Flags']['PSH'],
            'ACK Flag Cnt': f['Flags']['ACK'],
            'URG Flag Cnt': f['Flags']['URG'],
            'Down/Up Ratio': f['Bwd Pkts'] / f['Fwd Pkts'] if f['Fwd Pkts'] > 0 else 0,
            'TTL Mean': np.mean(f['TTLs']),
            'TTL Variance': np.var(f['TTLs']),
            'Port Scan Entropy': calculate_entropy(f['Dest Ports']),
            'TCP Retransmission Cnt': f['Retransmissions']
        }
        extracted_data.append(record)

    df = pd.DataFrame(extracted_data)
    print(f"[SUCCESS] Extracted {len(df)} distinct flows from PCAP.")
    return df