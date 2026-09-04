from features.pcap_extractor import extract_pcap_features

df = extract_pcap_features("data/raw/synthetic_multi_stage_attack.pcap")
print(df[["Timestamp", "Src IP", "Dst IP", "Dst Port", "Port Scan Entropy", "TotLen Fwd Pkts", "TCP Retransmission Cnt"]].head(10))