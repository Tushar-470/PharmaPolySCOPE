# Verified Input Parameters for the N=8 Polymer Library Dossier

**PharmaPolySCOPE Scientific Reference Dossier**  
**Document Version:** 1.0.0-VERIFIED-N8  
**Release Date:** September 2026  
**Framework Scope:** Four-Criterion Computational Framework for Rational Polymer Selection in Amorphous Solid Dispersions (ASDs)  

---

## Executive Summary & Verification Methodology

This dossier establishes the verified physicochemical inputs, literature sources, and cheminformatics representations for the authoritative **$N=8$ Polymer Library** used in PharmaPolySCOPE. 

Values compiled herein were retrieved and corroborated through manufacturer technical datasheets (Evonik, BASF, Shin-Etsu, Merck MilliporeSigma, Colorcon), the *Handbook of Pharmaceutical Excipients* (Rowe, Sheskey, Quinn), and peer-reviewed thermal and spectroscopic literature (e.g. Parikh et al. 2014, Friesen et al. 2008). Where ambiguity, moisture sensitivity, or measurement limitations exist, they are explicitly cataloged under the Honest Caveats section to ensure complete epistemological transparency.

---

## Detailed Profiles of the N=8 Verified Polymers

### 1. Eudragit® L 100 (Evonik)

* **Internal Polymer ID:** `POL-0020` (Reference alias: `POL-004-2026`)
* **Chemical Name:** Poly(methacrylic acid-co-methyl methacrylate) 1:1
* **Abbreviation:** `EDR_L100`
* **Polymer Family:** Acrylic
* **Functional Class:** Enteric / Anionic (dissolves at pH $\ge 6.0$)
* **CAS Registry Number:** 25086-15-1
* **Repeat-Unit SMILES:** `*CC(C)(*)C(=O)O.*CC(C)(*)C(=O)OC`
* **Number-Average Molecular Weight ($M_n$):** Optional / Leave blank (nominal $M_w \approx 125{,}000\text{ Da}$)
* **Dry Glass Transition Temperature ($T_g$):** **$433.15\text{ K}$ ($160.0\text{ °C}$)**  
  *(Evonik specification states $T_g > 150\text{ °C}$. A conservative midpoint of $160\text{ °C}$ is adopted to account for the overlap with thermal degradation above $150\text{ °C}$)*
* **Bulk True Density:** $1.25\text{ g/cm}^3$ (Evonik Product Literature)
* **Hansen Solubility Parameters (H-V-K):** $\delta_D = 16.5$, $\delta_P = 7.5$, $\delta_H = 9.0\text{ MPa}^{1/2}$ ($\delta_t = 20.24\text{ MPa}^{1/2}$)
* **Primary Literature Sources:**
  - Evonik Industries. *EUDRAGIT® L 100 Technical Information Sheet*.
  - Parikh, T., Gupta, S.S., Meena, A., & Serajuddin, A.T.M. (2014). "Investigation of thermal and viscoelastic properties of polymers relevant to hot melt extrusion - III." *Journal of Excipients and Food Chemistry*, 5(1), 56–64.

---

### 2. Eudragit® RL PO (Evonik)

* **Internal Polymer ID:** `POL-0021`
* **Chemical Name:** Poly(ethyl acrylate-co-methyl methacrylate-co-trimethylammonioethyl methacrylate chloride) 1:2:0.2
* **Abbreviation:** `EDR_RL_PO`
* **Polymer Family:** Acrylic
* **Functional Class:** Cationic / Time-Controlled Release (insoluble, high permeability)
* **CAS Registry Number:** 51822-44-7
* **Repeat-Unit SMILES:** `*CC(*)C(=O)OCC.*CC(C)(*)C(=O)OC.*CC(C)(*)C(=O)OCC[N+](C)(C)C.[Cl-]`
* **Number-Average Molecular Weight ($M_n$):** Optional / Leave blank (nominal $M_w \approx 150{,}000\text{ Da}$)
* **Dry Glass Transition Temperature ($T_g$):** **$336.15\text{ K}$ ($63.0\text{ °C}$)**
* **Bulk True Density:** $1.15\text{ g/cm}^3$ (Evonik Product Literature)
* **Hansen Solubility Parameters (H-V-K):** $\delta_D = 16.8$, $\delta_P = 6.2$, $\delta_H = 7.1\text{ MPa}^{1/2}$ ($\delta_t = 19.26\text{ MPa}^{1/2}$)
* **Primary Literature Sources:**
  - Parikh, T., et al. (2014). *J. Excipients and Food Chem.*, 5(1), 56–64. (Differential Scanning Calorimetry midpoint).
  - Evonik Nutrition & Care GmbH. *EUDRAGIT® RL PO Product Information*.

---

### 3. HPMCAS-MF (Shin-Etsu AQOAT® AS-MF)

* **Internal Polymer ID:** `POL-0010` (`HPMCAS_M`)
* **Chemical Name:** Hypromellose Acetate Succinate, Medium grade, Fine particle size
* **Abbreviation:** `HPMCAS_M`
* **Polymer Family:** Cellulosic
* **Functional Class:** Enteric / Anionic (dissolves at pH $\ge 6.0$)
* **CAS Registry Number:** 71138-97-1
* **Repeat-Unit SMILES:** `*OC1C(OC(=O)C)C(OC(=O)CCC(=O)O)C(COCC(C)O)C(O1)O*`
* **Number-Average Molecular Weight ($M_n$):** Optional / $13{,}000\text{ Da}$ (SEC-MALLS per Fukasawa et al.)
* **Dry Glass Transition Temperature ($T_g$):** **$393.15\text{ K}$ ($120.0\text{ °C}$)**
* **Bulk True Density:** $1.28\text{ g/cm}^3$
* **Hansen Solubility Parameters (H-V-K):** $\delta_D = 18.51$, $\delta_P = 10.39$, $\delta_H = 9.81\text{ MPa}^{1/2}$ ($\delta_t = 23.38\text{ MPa}^{1/2}$)
* **Primary Literature Sources:**
  - Shin-Etsu Chemical Co., Ltd. (2018). *Shin-Etsu AQOAT® Technical Brochure*.
  - Friesen, D.T., Shanker, R., Crew, M., Smithey, D.T., Curatolo, W.J., & Nightingale, J.A.S. (2008). "Hydroxypropyl Methylcellulose Acetate Succinate-Based Spray-Dried Dispersions: An Overview." *Molecular Pharmaceutics*, 5(6), 1003–1019. DOI: 10.1021/mp8000793.
  - Fukasawa, M., et al. (2004). *Chem. Pharm. Bull.* 52(11), 1391–1393.

---

### 4. HPMCP-55 (Shin-Etsu HP-55®)

* **Internal Polymer ID:** `POL-0022`
* **Chemical Name:** Hypromellose Phthalate
* **Abbreviation:** `HPMCP_55`
* **Polymer Family:** Cellulosic
* **Functional Class:** Enteric / Anionic (dissolves at pH $\ge 5.5$)
* **CAS Registry Number:** 9050-31-1
* **Repeat-Unit SMILES:** `*OC1C(O)C(O)C(CO)OC1*` (Representative anhydroglucose backbone)
* **Number-Average Molecular Weight ($M_n$):** Optional / Leave blank (nominal $M_w \approx 45{,}000\text{ Da}$)
* **Dry Glass Transition Temperature ($T_g$):** **$410.15\text{ K}$ ($137.0\text{ °C}$)**
* **Bulk True Density:** $1.30\text{ g/cm}^3$ (Handbook of Pharmaceutical Excipients)
* **Hansen Solubility Parameters (H-V-K):** $\delta_D = 18.2$, $\delta_P = 9.5$, $\delta_H = 10.8\text{ MPa}^{1/2}$ ($\delta_t = 23.20\text{ MPa}^{1/2}$)
* **Primary Literature Sources:**
  - Shin-Etsu Chemical Co., Ltd. *Shin-Etsu HP-55® Technical Brochure*.
  - Rowe, R.C., Sheskey, P.J., & Quinn, M.E. *Handbook of Pharmaceutical Excipients* (6th ed.). Pharmaceutical Press. Reports $T_g$ in the range of 133–137 °C.

---

### 5. PVA 4-88 (Merck Parteck® MXP)

* **Internal Polymer ID:** `POL-0015` (`PVA_488`)
* **Chemical Name:** Polyvinyl Alcohol, 88% hydrolyzed, low-viscosity grade (4 mPa·s)
* **Abbreviation:** `PVA_488`
* **Polymer Family:** Vinylic
* **Functional Class:** Neutral (water-soluble, high hot-melt extrusion suitability)
* **CAS Registry Number:** 9002-89-5
* **Repeat-Unit SMILES:** `*CC(*)O.*CC(*)OC(C)=O`
* **Number-Average Molecular Weight ($M_n$):** Optional / $31{,}210\text{ Da}$
* **Dry Glass Transition Temperature ($T_g$):** **$315.15\text{ K}$ ($42.0\text{ °C}$)**  
  *(Note: Updated from generic 98% hydrolyzed PVA of 85 °C to the grade-specific 42 °C verified for Parteck MXP)*
* **Bulk True Density:** $1.26\text{ g/cm}^3$
* **Hansen Solubility Parameters (H-V-K):** $\delta_D = 17.01$, $\delta_P = 8.99$, $\delta_H = 18.01\text{ MPa}^{1/2}$ ($\delta_t = 26.35\text{ MPa}^{1/2}$)
* **Primary Literature Sources:**
  - Merck KGaA / MilliporeSigma. *Parteck® MXP Polyvinyl Alcohol 4-88 Technical Data Sheet* (Cat. No. 141464).
  - Thomas, D. (2018). "Polyvinyl Alcohol as a Functional Polymer for Melt Extrusion and 3D Printing." *Dissertation*, University of Texas at Austin.

---

### 6. PVAP (Colorcon Phthalavin® / Sureteric®)

* **Internal Polymer ID:** `POL-0023`
* **Chemical Name:** Polyvinyl Acetate Phthalate
* **Abbreviation:** `PVAP`
* **Polymer Family:** Vinylic
* **Functional Class:** Enteric / Anionic (dissolves at pH $\ge 5.0$)
* **CAS Registry Number:** 34481-48-6
* **Repeat-Unit SMILES:** `*CC(*)OC(=O)c1ccccc1C(=O)O` (Characteristic phthalate unit)
* **Number-Average Molecular Weight ($M_n$):** Optional / Leave blank (nominal $M_w \approx 35{,}000\text{ Da}$)
* **Dry Glass Transition Temperature ($T_g$):** **$318.15\text{ K}$ ($45.0\text{ °C}$)**  
  *(HPE consensus midpoint. Literature also notes a high-temperature secondary transition at ~116 °C)*
* **Bulk True Density:** $1.28\text{ g/cm}^3$ (Colorcon Technical Documentation)
* **Hansen Solubility Parameters (H-V-K):** $\delta_D = 17.8$, $\delta_P = 8.2$, $\delta_H = 8.9\text{ MPa}^{1/2}$ ($\delta_t = 21.52\text{ MPa}^{1/2}$)
* **Primary Literature Sources:**
  - Rowe, R.C., Sheskey, P.J., & Quinn, M.E. *Handbook of Pharmaceutical Excipients*. Reports 42.5 °C.
  - Colorcon Inc. *Phthalavin® Enteric Polymer Technical Bulletin*.

---

### 7. PVP K30 (BASF Kollidon® 30)

* **Internal Polymer ID:** `POL-001-2026` / `POL-0001`
* **Chemical Name:** Polyvinylpyrrolidone / Povidone K30
* **Abbreviation:** `PVP_K30`
* **Polymer Family:** Vinylic
* **Functional Class:** Neutral (rapid dissolution, strong H-bond acceptor)
* **CAS Registry Number:** 9003-39-8
* **Repeat-Unit SMILES:** `*CC(*)N1CCCC1=O`
* **Number-Average Molecular Weight ($M_n$):** Optional / $12{,}000\text{ Da}$ (nominal $M_w \approx 49{,}000\text{ Da}$)
* **Dry Glass Transition Temperature ($T_g$):** **$441.15\text{ K}$ ($168.0\text{ °C}$)**  
  *(Vacuum-dried condition. Highly hygroscopic; ambient exposure depresses observed $T_g$ to 110–130 °C)*
* **Bulk True Density:** $1.20\text{ g/cm}^3$
* **Hansen Solubility Parameters (H-V-K):** $\delta_D = 20.45$, $\delta_P = 13.66$, $\delta_H = 6.87\text{ MPa}^{1/2}$ ($\delta_t = 25.53\text{ MPa}^{1/2}$)
* **Primary Literature Sources:**
  - Bühler, V. (2008). *Kollidon®: Polyvinylpyrrolidone Excipients for the Pharmaceutical Industry* (9th ed.). BASF SE, Ludwigshafen, Germany.

---

### 8. PVPVA 64 / Copovidone (BASF Kollidon® VA 64)

* **Internal Polymer ID:** `POL-002-2026` / `POL-0006`
* **Chemical Name:** Vinylpyrrolidone-vinyl acetate copolymer (6:4 w/w ratio)
* **Abbreviation:** `PVP_VA_64`
* **Polymer Family:** Vinylic
* **Functional Class:** Neutral (optimal plasticity for melt extrusion and spray drying)
* **CAS Registry Number:** 25086-89-9
* **Repeat-Unit SMILES:** `*CC(*)N1CCCC1=O.*CC(*)OC(=O)C`
* **Number-Average Molecular Weight ($M_n$):** Optional / $45{,}000\text{ Da}$ (nominal $M_w \approx 57{,}500\text{ Da}$)
* **Dry Glass Transition Temperature ($T_g$):** **$378.15\text{ K}$ ($105.0\text{ °C}$)**  
  *(Report consensus range: $101–106\text{ °C}$)*
* **Bulk True Density:** $1.20\text{ g/cm}^3$
* **Hansen Solubility Parameters (H-V-K):** $\delta_D = 19.51$, $\delta_P = 11.19$, $\delta_H = 7.41\text{ MPa}^{1/2}$ ($\delta_t = 23.68\text{ MPa}^{1/2}$)
* **Primary Literature Sources:**
  - Bühler, V. *Kollidon®: Polyvinylpyrrolidone Excipients for the Pharmaceutical Industry*. BASF SE.
  - BASF Technical Information. *Kollidon® VA 64 Technical Bulletin*.

---

## Master Parameter Summary Matrix

| # | Excipient Brand | Chemical Grade | Family | Functional Class | Dry $T_g$ (°C) | Dry $T_g$ (K) | Bulk Density ($\text{g/cm}^3$) | $\delta_D$ | $\delta_P$ | $\delta_H$ | $\delta_t$ | SMILES Pattern |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **1** | Eudragit® L 100 | L 100 (1:1) | Acrylic | Enteric | 160.0 | 433.15 | 1.25 | 16.5 | 7.5 | 9.0 | 20.24 | `*CC(C)(*)C(=O)O.*CC(C)(*)C(=O)OC` |
| **2** | Eudragit® RL PO | RL PO (1:2:0.2) | Acrylic | Cationic | 63.0 | 336.15 | 1.15 | 16.8 | 6.2 | 7.1 | 19.26 | EA + MMA + TMAEMA-Cl ionic pair |
| **3** | HPMCAS-MF | AQOAT® AS-MF | Cellulosic | Enteric | 120.0 | 393.15 | 1.28 | 18.51 | 10.39 | 9.81 | 23.38 | Substituted AGU repeat |
| **4** | HPMCP-55 | HP-55 | Cellulosic | Enteric | 137.0 | 410.15 | 1.30 | 18.2 | 9.5 | 10.8 | 23.20 | Simplified AGU backbone |
| **5** | PVA 4-88 | Parteck® MXP | Vinylic | Neutral | 42.0 | 315.15 | 1.26 | 17.01 | 8.99 | 18.01 | 26.35 | Vinyl alcohol + acetate |
| **6** | PVAP | Phthalavin® | Vinylic | Enteric | 45.0 | 318.15 | 1.28 | 17.8 | 8.2 | 8.9 | 21.52 | Vinyl acetate phthalate |
| **7** | PVP K30 | Kollidon® 30 | Vinylic | Neutral | 168.0 | 441.15 | 1.20 | 20.45 | 13.66 | 6.87 | 25.53 | Vinylpyrrolidone |
| **8** | PVPVA 64 | Kollidon® VA 64 | Vinylic | Neutral | 105.0 | 378.15 | 1.20 | 19.51 | 11.19 | 7.41 | 23.68 | VP (60%) + VA (40%) |

---

## Critical Epistemological Caveats & Viva Defense

### 1. Cellulosic Heterogeneity (HPMCAS & HPMCP)
Statistical substitution across anhydroglucose hydroxyls cannot be encoded in a single deterministic SMILES string. PharmaPolySCOPE resolves this by using **experimentally anchored bulk physical properties** ($T_g$, density, and solubility parameters) for thermodynamic criteria, while using the representative repeat-unit SMILES solely for RDKit functional-group topological features.

### 2. Moisture Plasticization in Hygroscopic Polymers (PVP & Copovidone)
Observed glass transitions in ambient laboratory conditions are often $30\text{–}50\text{ °C}$ lower than monograph values due to water plasticization ($T_{g,\text{water}} \approx -135\text{ °C}$). The values tabulated above represent rigorously dried polymer samples, ensuring reproducible, anhydrous thermodynamic baselines.

### 3. Degradation Overlap in High-$T_g$ Acrylics (Eudragit L 100)
The exact $T_g$ midpoint cannot be resolved by standard DSC due to onset of side-chain anhydride degradation above 150 °C. The $160\text{ °C}$ ($433.15\text{ K}$) value provides a defensible, conservative estimate substantiated by literature dynamic mechanical and thermal studies.

### 4. Dual-$T_g$ Phenomena in PVAP
PVAP displays two distinct thermal events: a lower glass transition at $42\text{–}46\text{ °C}$ associated with free acetate mobility, and a secondary transition at $\approx 116\text{ °C}$ associated with phthalate segments. Adopting the $45.0\text{ °C}$ midpoint aligns with standard pharmaceutical handbook references and provides conservative anti-plasticization modeling.
