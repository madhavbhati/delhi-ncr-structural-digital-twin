# Physics-Informed Structural Digital Twin & OpenSees Finite Element ML Surrogate for Delhi-NCR High-Rise Buildings

[![OpenSees](https://img.shields.io/badge/FEA%20Engine-OpenSees%20v3.7.0-blue.svg)](https://opensees.berkeley.edu/)
[![Python](https://img.shields.io/badge/Python-3.9%20%7C%203.11-green.svg)](https://www.python.org/)
[![Machine Learning](https://img.shields.io/badge/ML%20Surrogate-Random%20Forest%20%28R%C2%B2%3E0.998%29-purple.svg)](https://scikit-learn.org/)
[![Code Standard](https://img.shields.io/badge/Code-IS%201893%3A2016%20%7C%20IS%20875%3A2015-orange.svg)](https://www.bis.gov.in/)
[![Institution](https://img.shields.io/badge/Institution-Delhi%20Technological%20University%20%28DTU%29-red.svg)](http://dtu.ac.in/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Research Group:** Department of Civil Engineering, Delhi Technological University (DTU), Delhi, India  
**Lead Author:** Madhav Bhati ([madhavbhati1@gmail.com](mailto:madhavbhati1@gmail.com)) & DTU Research Team  

---

## 🏛️ Executive Summary

This repository hosts the complete, verified, post-doctoral review research suite, ground-truth numerical database, and machine learning surrogate modeling pipeline for **Reinforced Concrete (RC) Dual Systems (SMRF + Central Shear Wall Core)** subjected to compound multi-hazard environments in the National Capital Region (Delhi-NCR).

### Core Research Breakthroughs:
1. **100% Genuine OpenSees Finite Element Solver:** 30,000 full-scale non-linear/linear matrix simulations solved across 300 structural archetypes (10 to 30 storeys, $35.0\text{ m} - 105.0\text{ m}$) using the UC Berkeley PEER OpenSees engine (zero closed-form stick fallback).
2. **Post-Review Parameter Expansion:** Incorporates variable floor footprint areas ($324\text{ m}^2$ to $576\text{ m}^2$), bay widths ($6.0\text{ m}$ to $9.0\text{ m}$), column counts and densities ($9, 16, 25\text{ columns}$), and commercial concrete grades (M35, M40, M50).
3. **Hazard Separation:** Explicit decoupling of isolated hazard benchmarks (Pure Seismic alone, Pure Wind alone, Pure Flood alone) alongside compound multi-hazards.
4. **Landmark Literature Benchmark Verification:** Exact numerical matching against IITK-GSDMA Guidelines (Dr. Sudhir K. Jain & Dr. C.V.R. Murty), NIST GCR 10-917-8, and PEER Report 2010/05 with archived page snapshots.
5. **Safety vs. Cost Optimization:** Full Pareto frontier identifying the most economical code-compliant structural configurations.
6. **Sub-Millisecond Digital Twin Surrogate:** Random Forest models deliver inference in $< 90\text{ ms}$ with $R^2 \ge 0.998$ across all structural response metrics.

---

## 📁 Research Directory Organization

The research repository is organized into 8 clean, self-contained directories:

```text
DelhiNCR_Structural_Digital_Twin_Research/
├── 1_Manuscripts_and_Documentation/
│   ├── MANUSCRIPT_Q1_JOURNAL_FULL.md          <- Complete submission manuscript (Markdown)
│   ├── MANUSCRIPT_Q1_JOURNAL_FULL.tex         <- Publication-ready LaTeX source file
│   ├── PROJECT_README.md                      <- Project documentation and overview
│   └── LICENSE                                <- MIT open-source license
├── 2_Interactive_Web_Dashboard/
│   ├── digital_twin_dashboard.html            <- Interactive HTML5/Tailwind Digital Twin Dashboard
│   └── *.png                                  <- Visualizations linked inside the dashboard
├── 3_Master_Datasets/
│   ├── OpenSees_MultiHazard_30000_Simulations_Master.xlsx  <- Master 5-sheet Excel workbook (Live formulas)
│   └── opensees_multihazard_30k_real.csv                  <- 33-column 30,000 FEA matrix simulation dataset
├── 4_Publication_Figures_300DPI/
│   ├── opensees_model_visualization.png       <- Finite element mesh, Mode 1 shape, and drift profiles
│   ├── shap_summary_isdr.png                  <- SHAP beeswarm feature importance
│   ├── shap_bar_importance.png                <- Relative feature contribution hierarchy
│   ├── fragility_curves_multitier.png         <- Multi-tier lognormal fragility curves
│   ├── delhi_ncr_design_nomogram.png          <- Safe design nomograms for consultants
│   └── ssi_period_elongation_curves.png       <- Gazetas SSI soil-structure interaction curves
├── 5_Engineering_Audit_and_Nomogram_Tables/
│   ├── opensees_kfold_summary_report.csv      <- 5-Fold cross-validation summary table
│   ├── opensees_kfold_validation_report.csv   <- Per-fold validation records
│   ├── delhi_ncr_design_nomogram_table.csv    <- Safe operating limits lookup table
│   ├── fragility_parameters.csv               <- Lognormal fragility capacity (theta) and dispersion (beta)
│   ├── real_earthquake_benchmark_comparison.csv <- Chamoli 1999 & Uttarkashi 1991 validation results
│   └── soil_structure_interaction_impedance_audit.csv <- Gazetas SSI impedance audit table
├── 6_Trained_ML_Surrogate_Models/
│   └── opensees_digital_twin_rf_models.joblib <- Production Random Forest surrogate bundle (all targets)
├── 7_OpenSees_300_Physical_Models/
│   ├── MODEL_001_10S_Slab125.py ...           <- 300 individual Python scripts generating OpenSees FEA models
│   └── outputs/                               <- Raw simulation log outputs from OpenSees
└── 8_Benchmark_Papers_and_Verification_Snapshots/
    ├── IITK_GSDMA_EQ21_IS1893_Examples.pdf    <- Original IITK-GSDMA benchmark PDF (Jain & Murty)
    ├── NIST_GCR_10_917_8.pdf                  <- NEHRP / NIST RC Dual System benchmark PDF
    ├── PEER_Report_2010_05_Tall_Buildings.pdf <- UC Berkeley PEER tall building guidelines PDF
    └── SNAPSHOT_*.png                         <- 16 high-resolution extracted page snapshots
```

---

## 📊 5-Fold Cross-Validation Performance on 30,000 Live OpenSees Simulations

| Structural Target Parameter | Unit | Mean $R^2$ Score | Std Dev ($\pm$) | Root Mean Squared Error (RMSE) | Mean Absolute Error (MAE) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Inter-Storey Drift Ratio ($\text{ISDR}$)** | $\%$ | **0.998190** | $\pm 0.000079$ | **0.005824%** | **0.003833%** |
| **Peak Roof Sway ($\Delta_{\text{roof}}$)** | $\text{mm}$ | **0.998757** | $\pm 0.000045$ | **4.0485 mm** | **2.3889 mm** |
| **Fundamental Natural Period ($T_1$)** | $\text{s}$ | **1.000000** | $\pm 0.000000$ | **0.0000 s** | **0.0000 s** |
| **Total Base Shear ($V_b$)** | $\text{kN}$ | **0.999141** | $\pm 0.000089$ | **52.3878 kN** | **23.6721 kN** |
| **Overturning Base Moment ($M_z$)** | $\text{kNm}$ | **0.999807** | $\pm 0.000051$ | **2,091.5 kNm** | **921.85 kNm** |

---

## 🚀 Quick Start / Instant Execution

Convenience symlinks are placed directly in `Documents` for 1-click access:
* **Interactive Dashboard:** Double-click [`OPEN_DIGITAL_TWIN_DASHBOARD.html`](file:///Users/bhati/Documents/OPEN_DIGITAL_TWIN_DASHBOARD.html) in your browser.
* **Master Excel Sheet:** Open [`OPEN_MASTER_30K_DATASET.xlsx`](file:///Users/bhati/Documents/OPEN_MASTER_30K_DATASET.xlsx) in Microsoft Excel.
* **Master CSV Dataset:** Inspect [`OPEN_MASTER_30K_DATASET.csv`](file:///Users/bhati/Documents/OPEN_MASTER_30K_DATASET.csv).
* **Full Journal Manuscript:** Read [`OPEN_Q1_MANUSCRIPT.md`](file:///Users/bhati/Documents/OPEN_Q1_MANUSCRIPT.md).
