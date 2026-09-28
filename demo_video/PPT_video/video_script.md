Yeh raha aapke **SIH 2026 Project: "Causal World Models for Predictive Network Defense" (Team Trace)** ke liye complete **10-Minute Demo Video Script** aur **Director's Guide** (video direct kaise karni hai) Roman Hindi mein:

---

# 🎬 10-Minute Demo Video Script & Direction Plan

### 📋 Video Direct Kaise Karein (Director's Guidelines)

1. **Screen Layout (Picture-in-Picture):**
* Screen ke right-bottom corner par presenter ka webcam hona chahiye aur main screen par slides ya live tool/dashboard dikhna chahiye.


2. **Audio Setup:**
* Awaz confident, clear aur steady pace mein honi chahiye. Background noise bilkul na ho.


3. **Cursor & Highlights:**
* Mouse cursor par yellow circular highlight use karein taki judges ko dikhe ki aap kis metric ya graph par point kar rahe hain.


4. **Flow & Pacing:**
* **0:00 - 3:00:** Problem, core innovation (World Model concept) aur architecture.


* **3:00 - 7:30:** Live hands-on working demo (PCAP upload, K-step simulation, SHAP XAI).


* **7:30 - 10:00:** Baseline benchmark results, feasibility, aur national security impact.





---

## ⏱️ Detailed Timeline & Narration Script

---

### 🔹 Part 1: Problem Statement & Vision (0:00 – 1:30)

* **Screen Display:** Slide 1 (Title Page with Team Trace & Problem Statement 26153) aur fir Slide 2 (Beyond Static IDS vs. World Model).


* **Camera / Action:** Presenter full-screen ya split-screen par namaste/greeting ke sath start karega.

> **Voiceover / Spoken Script:**
> "Namaste respected judges! Hum hain Team Trace. Hum present kar rahe hain hamara solution for Problem Statement ID 26153: **AI based Network Attack Forecasting from Network Traffic Data** under Blockchain & Cybersecurity theme.
> 
> 
> Aaj ke enterprise networks aur Critical Information Infrastructure (CII) mein sabse badi problem hai traditional IDS ki reactive approach. Current machine learning models har network flow ko isolated packet ki tarah evaluate karte hain—yani $X \to Y$ binary classification. Par reality yeh hai ki ek advanced infiltration koi single anomalous packet nahi hota, balki ek slow multi-stage campaign hota hai jo time ke sath evolve hota hai. Jab tak traditional IDS alert deta hai, tab tak breach ho chuka hota hai aur zero lead time milta hai.
> 
> 
> Humne build kiya hai **Causal World Models for Predictive Network Defense**—jo static detection se proactive forecasting par shift karta hai."
> 
> 

---

### 🔹 Part 2: Core Architecture & Dual Ingestion (1:30 – 3:00)

* **Screen Display:** Slide 3 (Technical Approach / 6-Stage Pipeline) aur Slide 4 (CNN-BiLSTM Architecture).


* **Camera / Action:** Diagram ke flow steps (Data $\to$ Temporal Resampling $\to$ Model $\to$ Rollout $\to$ XAI $\to$ UI) ko cursor se trace karein.



> **Voiceover / Spoken Script:**
> "Hamara core model ek classifier nahi, balki ek AI World Model hai jo network environment ki state transition physics seekhta hai: $P(S_{t+1} \mid S_t)$.
> 
> 
> Hamari pipeline 2 levels par telemetry ingest karti hai:
> 
> 
> 1. NetFlow/IPFIX flow statistics (5-tuple, volume, durations).
> 
> 
> 2. Raw PCAP packet metrics via Scapy (port scan entropy, TTL variance, TCP window anomalies, aur duplicate retransmissions).
> 
> 
> 
> 
> Is data ko hum 10-second ya 30-second bins mein aggregate karke temporal sequence tensor $X \in \mathbb{R}^{T \times F}$ banate hain. Deep learning backbone mein humne hybrid **1D CNN + Bidirectional LSTM** use kiya hai. CNN rapid micro-burst attacks jaise sudden SYN sweeps ko pakadta hai, aur BiLSTM long-term macro kill-chain dynamics ko track karta hai. Aur network ke 99:1 imbalance ko tackle karne ke liye humne **Sparse Focal Loss** implement kiya hai."
> 
> 

---

### 🔹 Part 3: Live Demo — Ingestion & Terminal Execution (3:00 – 4:30)

* **Screen Display:** Terminal window dikhayein.
* **Camera / Action:** `python run_pipeline.py --action all` ya synthetic PCAP script execute karke output dikhayein.



> **Voiceover / Spoken Script:**
> "Ab hum chalte hain hamare live prototype ki taraf. Humne poore system ko Dockerize kiya hai aur ek master script `run_pipeline.py` banayi hai.
> 
> 
> *(Terminal par command dikhate hue)*
> Yahan hum `scripts/generate_synthetic_pcap.py` se ek 300-second ka multi-stage attack capture simulate kar rahe hain. Is capture mein 5 realistic stages hain: Reconnaissance, Initial Access, Lateral Movement, C2 beaconing, aur final Exfiltration.
> 
> 
> Ab hum run karte hain hamara offline Streamlit dashboard: `python run_pipeline.py --action demo`. Dhyan rahe, yeh system 100% air-gapped hai—bina kisi external cloud API ya internet dependency ke sovereign servers par safely chalta hai."
> 
> 

---

### 🔹 Part 4: Live UI Demo — K-Step Infiltration Forecasting (4:30 – 6:15)

* **Screen Display:** Streamlit UI Dashboard (`http://localhost:8501`).


* **Camera / Action:**
* Sidebar mein file upload box mein `.pcap` file drag-and-drop karein.


* Forecast Horizon slider ($K=10$) aur Window Size ($10S$) adjust karein.


* Plotly ka line chart aur top KPI cards zoom karke dikhayein.





> **Voiceover / Spoken Script:**
> "Yeh hai hamara Defender Dashboard. Hum sidebar se synthetic multi-stage PCAP file upload kar rahe hain. Ingestion engine ne automatically canonical 32 packet aur flow features extract kar liye.
> 
> 
> Top metrics par dhyan dein:
> 
> 
> * Current Window Risk sirf **22.4%** hai.
> 
> 
> * Lekin hamara model autoregressive **K-Step rollout** perform kar raha hai. Yeh future state predict karta hai, sequence buffer mein append karta hai, aur agle $K=10$ time windows tak simulate karta hai.
> 
> 
> * Peak Forecasted Risk dekhiye—yeh **88.6%** tak escalate ho rahi hai!
> 
> 
> * Aur sabse critical metric: **Defensive Lead Time: +4 Windows Ahead (approx 3.5 se 7 minutes)**!
> 
> 
> 
> 
> Is interactive Plotly graph mein aap red curve dekh sakte hain jo critical threshold line (0.75) ko cross kar rahi hai. Yani attacker ke actual lateral movement ya data steal karne se pehle hi SOC team ke paas actionable lead time hai."
> 
> 

---

### 🔹 Part 5: Live UI Demo — SHAP Explainability & MITRE ATT&CK (6:15 – 7:30)

* **Screen Display:** Dashboard ke bottom section (SHAP bar chart aur MITRE ATT&CK stage progression ribbon).


* **Camera / Action:** Horizontal bar chart par cursor le jayein aur MITRE progression arrows ko highlight karein.



> **Voiceover / Spoken Script:**
> "Critical infrastructure mein koi bhi black-box alerts accept nahi karta. Isliye humne integrate kiya hai **SHAP Explainability Engine**.
> 
> 
> Left side bar chart mein aap top driving features dekh sakte hain:
> 
> 
> * Port Scan Entropy (+35% impact)
> 
> 
> * TCP Retransmission count (+28% impact)
> 
> 
> * SYN flag spikes aur IAT variance.
> 
> 
> 
> 
> Right side par MITRE ATT&CK kill-chain progression ribbon hai:
> 
> 
> `Reconnaissance ➔ Initial Access ➔ Lateral Movement ➔ C2 ➔ Exfiltration`
> 
> Yani security team ko na sirf yeh pata chalta hai ki attack escalate hone wala hai, balki yeh bhi pata chalta hai ki attacker kaun si MITRE stage par badh raha hai aur kaun se network parameters isko drive kar rahe hain."
> 
> 

---

### 🔹 Part 6: Empirical Benchmark vs. Static Baseline (7:30 – 8:45)

* **Screen Display:** Slide 5 (Impact and Benefits - Benchmark Table).


* **Camera / Action:** Table mein F1-Score, False Positive Rate, aur Lead Time comparison par focus karein.



> **Voiceover / Spoken Script:**
> "Humne apne World Model ko evaluate karne ke liye same features par ek static Logistic Regression baseline se head-to-head compare kiya hai. Results clear proof hain:
> 
> 
> 1. **Macro F1-Score:** Baseline ka 71.0% tha, jabki hamare World Model ne achieve kiya **90.3%**—jo ki **+27.1% relative improvement** hai.
> 
> 
> 2. **False Positive Rate:** 8.4% se gir kar sirf **1.6%** reh gaya hai—yani alert fatigue mein **81% ki direct reduction**!
> 
> 
> 3. **Defensive Lead Time:** Static baseline breach ke baad alert karta hai (0 minute lead time), jabki hamara system **3.5 to 7.0 minutes of actionable advance warning** provide karta hai. Is lead time mein automated SOAR playbooks malicious IP ko quarantine kar sakti hain."
> 
> 
> 
> 

---

### 🔹 Part 7: Feasibility, CII Impact & Conclusion (8:45 – 10:00)

* **Screen Display:** Slide 4 (Feasibility) aur Slide 5 (National Security Alignment).


* **Camera / Action:** Presenter camera par aakar confident closing remarks deliver karega.



> **Voiceover / Spoken Script:**
> "Feasibility aur real-world deployment ke context mein:
> 
> 
> * Model inference time under **50 milliseconds** hai, jo bina heavy GPU clusters ke standard CPU/edge hardware par flawlessly chalta hai.
> 
> 
> * Concept drift aur zero-day attacks ko handle karne ke liye humne dynamic Threat Intel mapper implement kiya hai jo raw signatures ke bajaye underlying tactics (CVE $\to$ CWE $\to$ CAPEC $\to$ ATT&CK) par generalize karta hai.
> 
> 
> 
> 
> Yeh solution hamare desh ke defense, banking, power grid aur telecom jaise Critical Information Infrastructure ko multi-crore breaches se protect karta hai. Poori tarah open-source, air-gapped aur sovereign hone ki wajah se yeh **Atmanirbhar Bharat** ke cyber-resilience vision ko direct strengthen karta hai.
> 
> 
> Thank you very much, judges! Team Trace ab aapke questions ke liye ready hai."
> 
> 

---

### 💡 Video Recording Pro-Tips:

1. **Screen Resolution:** Screen recording ko 1080p (1920x1080) par record karein.
2. **Smooth Transitions:** Slides se Streamlit browser tab par switch karte waqt 1 second ka pause lein taki video clean lage.
3. **Timer Check:** Har section ke estimated timing ko follow karein taki video 9:45 se 10:00 minutes ke beech mein naturally complete ho sake.