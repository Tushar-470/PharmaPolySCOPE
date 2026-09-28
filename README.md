# Experimental Validation of a Computational Polymer-Ranking Tool for Amorphous Solid Dispersion Development: A Comparative Study of Itraconazole and Fenofibrate

<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/brand/logo-horizontal-dark.svg">
    <img alt="PharmaPolySCOPE" src="docs/brand/logo-horizontal-light.svg" width="360">
  </picture>
  <p><em>PharmaPolySCOPE: Pharmaceutical Polymer Screening and Computational Optimization Platform</em></p>
</div>

An integrated multi-criteria computational decision-support framework for rational polymer selection in amorphous solid dispersion (ASD) formulation development, featuring experimental and prospective validation on **Itraconazole** and **Fenofibrate**.

**Current Software Release**: **PharmaPolySCOPE v2.0.0**<br>
**Frozen Scientific Baseline**: **`v1.5.0-FOUR-CRITERION-FREEZE`**

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Software Release](https://img.shields.io/badge/release-v2.0.0-blue.svg)](https://github.com/Tushar-470/PharmaPolySCOPE/releases/tag/v2.0.0)
[![Scientific Baseline](https://img.shields.io/badge/baseline-v1.5.0--FOUR--CRITERION--FREEZE-green.svg)](docs/v1.5.0_frozen_computational_baseline_record.md)
[![DOI](https://img.shields.io/badge/DOI-to__be__assigned-lightgrey.svg)](#12-citation--academic-license)

> **Release Note**: PharmaPolySCOPE v2.0.0 is the current production software release, providing an extensible Variable-$K$ architecture, dynamic AHP/TOPSIS projection, Morris sensitivity analysis, and authoritative RDKit cheminformatics. The `v1.5.0-FOUR-CRITERION-FREEZE` remains the protected scientific baseline used for historical reproducibility, regression isolation, and benchmark comparisons.

---

## 1. System Identity & Architecture

| Identity Layer | Designation | Description |
| :--- | :--- | :--- |
| **Research Project Title** | **Experimental Validation of a Computational Polymer-Ranking Tool for Amorphous Solid Dispersion Development: A Comparative Study of Itraconazole and Fenofibrate** | Official scientific research and experimental validation project |
| **Product / Framework Name** | **PharmaPolySCOPE** | Public platform identity and computational software suite |
| **Subtitle** | *A Four-Criterion Computational Framework for Rational Polymer Selection in Amorphous Solid Dispersions* | Descriptive scientific methodology designation |
| **Developer** | **Developed by Tushar Mathapati** | Software architecture, computational decision framework & web platform |
| **Current Software Release** | **`v2.0.0`** | Variable-$K$ production architecture, dynamic AHP/TOPSIS, Morris sensitivity, RDKit cheminformatics |
| **Frozen Scientific Baseline** | **`v1.5.0-FOUR-CRITERION-FREEZE`** | Historical four-criterion frozen computational baseline (commit `31eee4d`) |
| **Production Python Engine** | `asd_mcda.v2` | Extensible Variable-$K$ screening, uncertainty, sensitivity, and provenance engine |
| **Historical Engine Core** | `asd_mcda` | Frozen v1.5 computational baseline engine |

---

## 2. Scientific Objective

To replace empirical trial-and-error screening cascades with an integrated, four-criterion multi-criteria decision analysis (MCDA) workflow coupled to stochastic uncertainty quantification and global parameter sensitivity analysis, experimentally validated through a comparative study of **Itraconazole** (`DRG-0001`, weakly basic, glass-forming API) and **Fenofibrate** (`DRG-0002`, neutral, rapid-crystallizing API) against a verified 8-polymer compendial cohort (`POL-0001` through `POL-0008`).

---

## 3. Current Project Lifecycle Status

> **COMPUTATIONAL SCREENING FRAMEWORK; PROSPECTIVE EXPERIMENTAL VALIDATION REQUIRED.**
>
> The computational development phase is closed and frozen. The deterministic ranking and uncertainty quantification provide model-based decision support. Laboratory spray-drying, solid-state characterization (mDSC, PXRD, FTIR), and dissolution testing represent the required prospective experimental validation phase.

---

## 4. Finalized Candidate Libraries (N=2 Drugs & N=8 Polymers)

### 4.1 Comparative Model Drug Cohort

| Drug ID | Generic Name (INN) | Molecular Weight ($M_w$) | Melting Point ($T_m$) | Glass Transition ($T_g$) | Solid Density ($\rho$) | BCS Class | Ionization State |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`DRG-0001`** | **Itraconazole** | $705.65\text{ g/mol}$ | $438.15\text{ K}$ ($165^\circ\text{C}$) | $306.70\text{ K}$ ($33.55^\circ\text{C}$) | $1.270\text{ g/cm}^3$ | Class II | Weak base ($\text{p}K_a \approx 3.7$) |
| **`DRG-0002`** | **Fenofibrate** | $360.83\text{ g/mol}$ | $353.65\text{ K}$ ($80.5^\circ\text{C}$) | $247.55\text{ K}$ ($-25.6^\circ\text{C}$) | $1.162\text{ g/cm}^3$ | Class II | Neutral ester |

### 4.2 Verified Eight-Polymer Carrier Library

| Polymer ID | Canonical Polymer Name | Trade / Common Name | Polymer Family | Polymer Class | Compendial Status | Solid Density ($\rho$) | Glass Transition ($T_g$) |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`POL-0001`** | Eudragit L 100 | Eudragit® L 100 | acrylic | enteric | USP-NF / Ph. Eur. | $1.28\text{ g/cm}^3$ | $423.15\text{ K}$ ($150^\circ\text{C}$) |
| **`POL-0002`** | Eudragit RL PO | Eudragit® RL PO | acrylic | neutral | USP-NF / Ph. Eur. | $1.18\text{ g/cm}^3$ | $338.15\text{ K}$ ($65^\circ\text{C}$) |
| **`POL-0003`** | HPMCAS-MF | AQOAT® AS-MF | cellulosic | enteric | USP-NF / JP | $1.28\text{ g/cm}^3$ | $393.15\text{ K}$ ($120^\circ\text{C}$) |
| **`POL-0004`** | HPMCP-55 | HPMCP HP-55 | cellulosic | enteric | USP-NF / Ph. Eur. | $1.28\text{ g/cm}^3$ | $421.15\text{ K}$ ($148^\circ\text{C}$) |
| **`POL-0005`** | PVA 4-88 | Parteck® MXP | vinylic | neutral | Ph. Eur. / USP | $1.26\text{ g/cm}^3$ | $358.15\text{ K}$ ($85^\circ\text{C}$) |
| **`POL-0006`** | PVAP | Phthalavin® | vinylic | enteric | USP-NF | $1.25\text{ g/cm}^3$ | $383.15\text{ K}$ ($110^\circ\text{C}$) |
| **`POL-0007`** | PVP K30 | Kollidon® 30 | vinylic | neutral | Ph. Eur. / USP / JP | $1.20\text{ g/cm}^3$ | $426.80\text{ K}$ ($153.6^\circ\text{C}$) |
| **`POL-0008`** | PVPVA 64 | Kollidon® VA 64 | vinylic | neutral | Ph. Eur. / USP / JP | $1.20\text{ g/cm}^3$ | $378.15\text{ K}$ ($105^\circ\text{C}$) |

---

## 5. Computational Architecture: v2 Production vs. v1.5 Baseline

PharmaPolySCOPE maintains a strict architectural separation between the **v2 production engine** (`asd_mcda.v2`) and the **frozen v1.5 baseline** (`asd_mcda`):

### 5.1 Production v2 Architecture (`asd_mcda.v2`)

The v2 production architecture is designed for multi-drug extensibility without methodology redesign:

```
[Drug Profile (RDKit Validated) + Polymer Library]
                     │
                     ▼
[1. Compatibility Evaluation across 4 Criteria]
   - Hansen Solubility Parameters (Ra, RED, s_HSP)
   - Flory–Huggins Interaction Parameter (χ via Lindvig, s_chi)
   - Gordon–Taylor Anti-Plasticization (Tg,mix via Simha–Boyer, s_GT)
   - 2D Structural Descriptors (RDKit-derived match, s_desc)
                     │
                     ▼
[2. Population Standardization (Z-score, ddof=0)]
                     │
                     ▼
[3. Dynamic Variable-K PCA (min K for ≥95% Cumulative Variance)]
   - Eigengap Stability Guardrail (Δλ > 0.05)
                     │
                     ▼
[4. Eigenspace AHP Matrix (K × K Pairwise Comparison, CR ≤ 0.10)]
                     │
                     ▼
[5. SP-PRP-TOPSIS Ranking (Projected Metric Tensor M = V_K W_K V_K^T)]
                     │
                     ▼
[6. Joint-Distribution Monte Carlo UQ (N=10,000)]
   - Replicate-Specific Re-computation: S^(b) → Z^(b) → PCA^(b) → K^(b)
   - Outputs: Rank Distribution, Top-k, P(top-1), K Distribution, Stability
                     │
                     ▼
[7. Morris Elementary Effects Global Sensitivity Analysis (r=10, p=4)]
                     │
                     ▼
[8. Cryptographic Provenance Manifest & Immutable Snapshot Output]
```

**Key Features of v2 Architecture**:
- **Dynamic PCA ($K$ is not fixed)**: Automatically selects the minimum number of principal components $K \in \{1, 2, 3, 4\}$ explaining $\ge 95\%$ of cohort variance.
- **Eigengap Guardrails**: Validates that retained components are well-separated ($\lambda_K - \lambda_{K+1} > 0.05$) to prevent subspace instability.
- **Projected Metric TOPSIS**: Computes ideal and anti-ideal Euclidean distances under the metric tensor $\mathbf{M} = \mathbf{V}_K \mathbf{W}_K \mathbf{V}_K^T$.
- **Replicate-Specific Monte Carlo**: Each perturbation sample executes its own standardization, PCA, and $K$-selection, accurately propagating dimensionality uncertainty.
- **Authoritative RDKit Integration**: Validates chemical SMILES, detects valence and stereochemical errors, calculates 2D Lipinski/Crippen descriptors, and protects against silent fallback heuristic corruption.
- **Immutable Snapshots**: Freezes caller memory buffers to guarantee zero side-effects and deterministic provenance.

---

## 6. Production Screening Results: Comparative Study of Itraconazole & Fenofibrate

Evaluated under authoritative **Research Mode** using the Variable-$K$ SP-PRP-TOPSIS engine and joint-distribution Monte Carlo uncertainty quantification ($N=10{,}000$ iterations) against the verified 8-polymer compendial cohort (`POL-0001` through `POL-0008`):

### 6.1 Summary of Top-Ranked Formulation Candidates

| Drug Identifier | Generic Name | Top-Ranked Polymer Candidate | Winner Closeness ($C_L$) | Monte Carlo $P(\text{top-1})$ | Retained Dimensionality ($K$) | Stability Profile |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **`DRG-0001`** | **Itraconazole** | **HPMCAS-MF** (`POL-0003`) | **0.6823** | **91.5%** | $K=3$ ($98.1\%$ variance) | High Stability ($T_g$ margin $\ge 50\,\text{K}$) |
| **`DRG-0002`** | **Fenofibrate** | **PVAP / Phthalavin** (`POL-0006`) | **0.6954** | **72.7%** | $K=3$ ($97.4\%$ variance) | Low Stability ($T_g$ margin $< 30\,\text{K}$) |

### 6.2 Complete Eight-Polymer Ranking Hierarchy

| Rank | Itraconazole (`DRG-0001`) Candidate | Fenofibrate (`DRG-0002`) Candidate |
| :---: | :--- | :--- |
| **1** | **HPMCAS-MF** (`POL-0003`) — *Top Candidate* | **PVAP / Phthalavin** (`POL-0006`) — *Top Candidate* |
| **2** | **Eudragit L 100** (`POL-0001`) | **Eudragit RL PO** (`POL-0002`) |
| **3** | **PVPVA 64** (`POL-0008`) | **Eudragit L 100** (`POL-0001`) |
| **4** | **PVP K30** (`POL-0007`) | **PVPVA 64** (`POL-0008`) |
| **5** | **HPMCP-55** (`POL-0004`) | **HPMCAS-MF** (`POL-0003`) |
| **6** | **PVAP / Phthalavin** (`POL-0006`) | **PVP K30** (`POL-0007`) |
| **7** | **Eudragit RL PO** (`POL-0002`) | **HPMCP-55** (`POL-0004`) |
| **8** | **PVA 4-88** (`POL-0005`) | **PVA 4-88** (`POL-0005`) |

> [!IMPORTANT]
> **Scientific Interpretation of Model Outputs**:
> Computational closeness coefficients ($C_L$) and Monte Carlo selection probabilities ($P(\text{top-1})$) quantify multi-criteria model suitability under assumed parameter distributions. **They do NOT represent probabilities of physical formulation success, experimental solubility enhancement, or clinical efficacy.** Prospective laboratory validation remains mandatory.

---

## 7. Physical Compatibility Diagnostics

### 7.1 Hansen Solubility Parameters (HSP)

$$
R_a = \sqrt{4(\Delta\delta_D)^2 + (\Delta\delta_P)^2 + (\Delta\delta_H)^2}, \quad \mathrm{RED} = \frac{R_a}{R_0}, \quad s_{\mathrm{HSP}} = \max\left(0, 1 - \frac{\mathrm{RED}}{2}\right)
$$

All polymer HSP values in the active library are calculated group-contribution estimates derived via the Hoftyzer–Van Krevelen (H-V-K) method from repeat-unit monomer SMILES.

### 7.2 Flory–Huggins Interaction Parameter ($\chi$)

$$
\chi = \frac{V_m}{RT}\left[0.60(\Delta\delta_D)^2 + 0.25(\Delta\delta_P)^2 + 0.25(\Delta\delta_H)^2\right], \quad s_\chi = \max(0, 1 - \chi)
$$

Calculated via the Lindvig solubility parameter conversion at $T = 298.15\text{ K}$, representing theoretical enthalpy of mixing.

### 7.3 Gordon–Taylor Anti-Plasticization ($T_{g,\mathrm{mix}}$)

$$
T_{g,\mathrm{mix}} = \frac{w_1 T_{g,1} + K_{\mathrm{SB}} w_2 T_{g,2}}{w_1 + K_{\mathrm{SB}} w_2}, \quad K_{\mathrm{SB}} = \frac{\rho_1 T_{g,1}}{\rho_2 T_{g,2}}, \quad s_{\mathrm{GT}} = \mathrm{clip}\left(\frac{T_{g,\mathrm{mix}} - (T_{g,\mathrm{drug}} + 30)}{50}, 0, 1\right)
$$

Predicts glass-transition elevation of the amorphous mixture (at default $w_{\mathrm{drug}} = 0.30$) to assess kinetic crystallization inhibition.

### 7.4 2D Structural Descriptors ($s_{\mathrm{desc}}$)

Evaluates four normalized physicochemical descriptor matches derived from RDKit:

$$
s_{\mathrm{desc}} = 0.25 \cdot \mathrm{match}_{\mathrm{HBD}} + 0.25 \cdot \mathrm{match}_{\mathrm{HBA}} + 0.25 \cdot \mathrm{match}_{\mathrm{TPSA}} + 0.25 \cdot \mathrm{match}_{\mathrm{arom}}
$$

---

## 8. Installation & Quick Start

### Prerequisites
- Python $\ge 3.11$ (compatible with Python 3.11 – 3.14)
- `uv` (recommended) or `pip`

### Installation

```bash
git clone https://github.com/Tushar-470/PharmaPolySCOPE.git
cd PharmaPolySCOPE

# Install package in editable mode with development dependencies
uv pip install -e .
uv pip install -r requirements-dev.txt
```

### Run Verification Test Suites

```bash
# 1. Run the primary v2 production regression suite (116 tests)
pytest tests/v2/ -v

# 2. Run the RDKit cheminformatics integrity suite (29 tests)
pytest tests/v2/test_cheminformatics_integrity.py -v

# 3. Run the web API & presentation test suite (14 tests)
pytest tests/web/ -v
```

### CLI Execution

```bash
# Run comparative screening for Itraconazole (DRG-0001) against verified 8-polymer cohort
python -m asd_mcda.v2.cli --drug data/user_drugs/drg-0001.json --polymers data/verified_n8_polymers.csv

# Run comparative screening for Fenofibrate (DRG-0002) against verified 8-polymer cohort
python -m asd_mcda.v2.cli --drug data/user_drugs/drg-0002.json --polymers data/verified_n8_polymers.csv
```

### Local Research Dashboard

```bash
python start_app.py
```
Access the interactive web UI at `http://localhost:5173` and the OpenAPI docs at `http://localhost:8000/api/docs`.

---

## 9. Repository Map

```text
PharmaPolySCOPE/
├── pyproject.toml              # Package configuration declaring rdkit>=2026.3.6
├── uv.lock                     # Pinned reproducible dependency lockfile
├── README.md                   # Project overview and documentation
├── LICENSE                     # MIT Open Source License
├── CITATION.cff                # Academic citation metadata
│
├── src/asd_mcda/               # Core computational engines
│   ├── v2/                     # Production Variable-K architecture (engine, AHP, TOPSIS, UQ, sensitivity)
│   ├── compatibility/          # Physical models (HSP, Flory-Huggins, Gordon-Taylor)
│   └── ...                     # Supporting modules
│
├── tests/                      # Automated test suites
│   ├── v2/                     # Official v2 regression suite (116 tests)
│   └── web/                    # Web API & presentation test suite (14 tests)
│
├── results/                    # Screening reports and datasets
│   └── v2/                     # Authoritative v2 comparative screening outputs & reports
│       ├── fenofibrate/        # Fenofibrate screening outputs, UQ, and sensitivity data
│       └── itraconazole/       # Itraconazole screening outputs, UQ, and sensitivity data
│
├── data/                       # Curated data profiles
│   ├── verified_n2_drugs.csv   # Finalized N=2 model drug cohort (Itraconazole, Fenofibrate)
│   ├── verified_n8_polymers.csv# Finalized N=8 compendial polymer library
│   └── user_drugs/             # Validated drug JSON profiles (drg-0001.json, drg-0002.json)
│
├── backend/                    # FastAPI REST application
├── frontend/                   # React 18 + Vite interactive dashboard
└── docs/                       # Comprehensive documentation suite
```

---

## 10. Methodological Boundaries & Limitations

1. **Calculated HSP Input**: Polymer HSP values are Hoftyzer–Van Krevelen group-contribution predictions, not direct experimental solubility spheres. A documented polar overestimation bias exists ($\delta_D +2.37$, $\delta_H +3.98\text{ MPa}^{0.5}$).
2. **Enthalpy Approximation**: Flory–Huggins $\chi$ uses Lindvig HSP conversion rather than experimental melting-point depression DSC.
3. **Uncertainty Assumption Scope**: Monte Carlo perturbation distributions reflect assumed literature ranges rather than experimentally determined error covariance matrices.
4. **Pre-Laboratory Nature**: All computational outputs represent thermodynamic and kinetic **pre-laboratory predictions** intended to prioritize candidates, not guaranteed formulation outcomes.
5. **Failure Boundary Mapping Out of Scope**: Failure Boundary Mapping (FBM) is outside the validated v2.0.0 computational screening scope. The platform does not predict manufacturing process failure, define experimentally validated failure boundaries, or generate process design spaces; prospective experimental formulation and process data are required for downstream manufacturing modeling.

*For full technical details, see [`docs/limitations.md`](docs/limitations.md).*

---

## 11. Citation & Academic License

**PharmaPolySCOPE** was developed by **Tushar Mathapati**.

Distributed under the MIT Open Source License. See [`LICENSE`](LICENSE) for terms.

```bibtex
@article{mathapati2026experimental,
  title={Experimental Validation of a Computational Polymer-Ranking Tool for Amorphous Solid Dispersion Development: A Comparative Study of Itraconazole and Fenofibrate},
  author={Mathapati, Tushar},
  year={2026},
  journal={PharmaPolySCOPE Research Investigations},
  url={https://github.com/Tushar-470/PharmaPolySCOPE},
  note={Research Paper / Formulation Study}
}

@software{pharmapolyscope_2026,
  title={PharmaPolySCOPE: Pharmaceutical Polymer Screening and Computational Optimization Platform},
  author={Mathapati, Tushar},
  year={2026},
  version={2.0.0},
  url={https://github.com/Tushar-470/PharmaPolySCOPE},
  note={DOI: to be assigned}
}
```

