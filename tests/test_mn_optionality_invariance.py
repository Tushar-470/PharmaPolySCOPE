"""
Comprehensive Invariance & Verification Test Suite for Mn Optionality Decoupling.
Module 15 / PharmaPolySCOPE v2 (Variable-K Architecture).

Verifies:
1. Analytical and numerical invariance of core MCDA decision pipeline under Mn omission:
   - S (delta < 1e-15)
   - Z, R, lambda, V_K, w, M_K, t+, t-, D+, D-, C_L (delta < 1e-14)
   - K and ranking permutation sigma (exact discrete identity)
2. Flory-Huggins diagnostic behavior when Mn is supplied vs omitted.
3. Strict prohibition of Mw silent substitution when Mn is omitted.
4. Schema and backend validation rules (PDI >= 1.0, Mn > 0, optional Mn).
5. Null-safety in predictor, engine adapter, and reporting markdown generation.
6. Reference polymer library cryptographic SHA-256 immutability.
"""

import dataclasses
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import pytest
from pydantic import ValidationError

from asd_mcda.compatibility.flory_huggins import (
    FloryHugginsModel,
    evaluate_gate1_diagnostic,
)
from asd_mcda.compatibility.matrix import CompatibilityMatrix
from asd_mcda.drug.drug_profile import Drug
from asd_mcda.polymer.polymer_library import Polymer, PolymerLibrary
from asd_mcda.prediction.predictor import (
    FormulationPredictor,
    PredictionReport,
)
from asd_mcda.v2.ahp import solve_ahp_preference
from asd_mcda.v2.engine import VariableKEngine
from asd_mcda.v2.metrics import (
    compute_distances_and_closeness,
    construct_metric_tensor,
    project_reference_points,
)
from asd_mcda.v2.models import CANONICAL_CRITERIA_ORDER
from asd_mcda.v2.pca import decompose_spectral
from asd_mcda.v2.standardization import standardize_cohort
from backend.models.schemas import PolymerCreate, PolymerResponse, ScreeningResponse
from backend.services.engine_adapter import (
    AUTHORITATIVE_V2_AHP_MATRIX,
    _write_decision_report_md,
)
from backend.services.validation import validate_polymer_input


@pytest.fixture
def test_drug() -> Drug:
    return Drug.from_dict({
        "drug_id": "IND",
        "generic_name": "Indomethacin",
        "canonical_smiles": "CC1=C(C=C(C=C1)OC)C2=C(C3=CC=CC=C3N2CC(=O)O)C(=O)C4=CC=C(C=C4)Cl",
        "molecular_weight_g_mol": 357.79,
        "tm_k": 424.15,
        "tg_k": 315.15,
        "density_crystalline_g_cm3": 1.31,
        "density_amorphous_g_cm3": 1.22,
        "hsp_delta_d": 19.2,
        "hsp_delta_p": 7.9,
        "hsp_delta_h": 8.4,
        "hsp_ro": 8.0,
        "molar_volume_cm3_mol": 273.0,
    })


@pytest.fixture
def five_polymers_with_mn() -> List[Polymer]:
    return [
        Polymer.from_dict({
            "polymer_id": "POL-001",
            "polymer_name": "PVP K30",
            "abbreviation": "PVP_K30",
            "mn_da": 40000.0,
            "mw_da": 50000.0,
            "pdi": 1.25,
            "tg_k": 443.0,
            "density_g_cm3": 1.20,
            "hsp_delta_d": 17.4,
            "hsp_delta_p": 8.2,
            "hsp_delta_h": 11.7,
            "monomer_smiles": "C=CN1CCCC1=O",
        }),
        Polymer.from_dict({
            "polymer_id": "POL-002",
            "polymer_name": "PVP-VA 64",
            "abbreviation": "PVP_VA_64",
            "mn_da": 45000.0,
            "mw_da": 65000.0,
            "pdi": 1.44,
            "tg_k": 380.0,
            "density_g_cm3": 1.20,
            "hsp_delta_d": 17.0,
            "hsp_delta_p": 8.0,
            "hsp_delta_h": 10.0,
            "monomer_smiles": "C=CN1CCCC1=O|CC(=O)OC",
            "copolymer_mole_fractions": "0.6|0.4",
        }),
        Polymer.from_dict({
            "polymer_id": "POL-005",
            "polymer_name": "Soluplus",
            "abbreviation": "SOLUPLUS",
            "mn_da": 90000.0,
            "mw_da": 118000.0,
            "pdi": 1.31,
            "tg_k": 343.0,
            "density_g_cm3": 1.15,
            "hsp_delta_d": 18.0,
            "hsp_delta_p": 8.5,
            "hsp_delta_h": 10.5,
            "monomer_smiles": "C=CN1CCCC1=O",
        }),
        Polymer.from_dict({
            "polymer_id": "POL-006",
            "polymer_name": "Eudragit L100-55",
            "abbreviation": "EDR_L100_55",
            "mn_da": 125000.0,
            "mw_da": 250000.0,
            "pdi": 2.00,
            "tg_k": 438.0,
            "density_g_cm3": 1.25,
            "hsp_delta_d": 16.5,
            "hsp_delta_p": 7.5,
            "hsp_delta_h": 9.0,
            "monomer_smiles": "CC(C)C(=O)OC(C)C",
        }),
        Polymer.from_dict({
            "polymer_id": "POL-007",
            "polymer_name": "HPMC AS-LF",
            "abbreviation": "HPMC_AS_LF",
            "mn_da": 24000.0,
            "mw_da": 36000.0,
            "pdi": 1.50,
            "tg_k": 393.0,
            "density_g_cm3": 1.28,
            "hsp_delta_d": 16.2,
            "hsp_delta_p": 9.1,
            "hsp_delta_h": 12.4,
            "monomer_smiles": "OC1C(O)C(OC2C(O)C(O)C(O)C(CO)O2)C(CO)OC1O",
        }),
    ]


@pytest.fixture
def five_polymers_without_mn(five_polymers_with_mn: List[Polymer]) -> List[Polymer]:
    return [dataclasses.replace(p, mn_da=None) for p in five_polymers_with_mn]


# ==============================================================================
# 1. CORE MCDA MATHEMATICAL INVARIANCE
# ==============================================================================

def test_mn_counterfactual_core_mcda_mathematical_invariance(
    test_drug: Drug,
    five_polymers_with_mn: List[Polymer],
    five_polymers_without_mn: List[Polymer],
):
    """
    Assert that the entire v2 MCDA decision pipeline is strictly and identically
    invariant whether Mn is provided or omitted.
    """
    # ── Run A: Mn provided ──
    lib_a = PolymerLibrary(polymers=five_polymers_with_mn, drug=test_drug)
    comp_a = CompatibilityMatrix(test_drug, lib_a, drug_loading_ww=0.30)
    df_s_a = comp_a.build_matrix()
    S_a = df_s_a[["s_HSP", "s_chi", "s_desc", "s_GT"]].values.astype(float)
    ids_a = df_s_a["polymer_id"].tolist()

    # ── Run B: Mn omitted (None) ──
    lib_b = PolymerLibrary(polymers=five_polymers_without_mn, drug=test_drug)
    comp_b = CompatibilityMatrix(test_drug, lib_b, drug_loading_ww=0.30)
    df_s_b = comp_b.build_matrix()
    S_b = df_s_b[["s_HSP", "s_chi", "s_desc", "s_GT"]].values.astype(float)
    ids_b = df_s_b["polymer_id"].tolist()

    # Candidate IDs must match exactly
    assert ids_a == ids_b
    n = len(ids_a)

    # 1. Decision Matrix S invariance (delta < 1e-15)
    delta_S = np.max(np.abs(S_a - S_b))
    assert delta_S < 1e-15, f"Decision matrix S differed by {delta_S}"

    # 2. Standardization Z invariance (delta < 1e-14)
    Z_a, z_plus_a, z_minus_a, mu_a, sig_a = standardize_cohort(S_a)
    Z_b, z_plus_b, z_minus_b, mu_b, sig_b = standardize_cohort(S_b)
    delta_Z = np.max(np.abs(Z_a - Z_b))
    assert delta_Z < 1e-14, f"Z differed by {delta_Z}"

    # 3. Correlation Matrix R invariance (delta < 1e-14)
    R_a = (Z_a.T @ Z_a) / float(n)
    R_b = (Z_b.T @ Z_b) / float(n)
    delta_R = np.max(np.abs(R_a - R_b))
    assert delta_R < 1e-14, f"R differed by {delta_R}"

    # 4. Retained components K exact equality
    eigvals_a, V_a, K_a, cum_var_a = decompose_spectral(Z_a, variance_threshold=0.95)
    eigvals_b, V_b, K_b, cum_var_b = decompose_spectral(Z_b, variance_threshold=0.95)
    assert K_a == K_b, f"K mismatch: {K_a} vs {K_b}"
    assert K_a == 3  # Indomethacin with 5 polymers retains K=3 (99.96% var)

    # 5. Eigenvectors V_K invariance (delta < 1e-14)
    V_K_a = V_a[:, :K_a]
    V_K_b = V_b[:, :K_b]
    delta_V = np.max(np.abs(V_K_a - V_K_b))
    assert delta_V < 1e-14, f"V_K differed by {delta_V}"

    # 6. AHP weights w invariance (delta < 1e-14)
    w_a, cr_a = solve_ahp_preference(AUTHORITATIVE_V2_AHP_MATRIX)
    w_b, cr_b = solve_ahp_preference(AUTHORITATIVE_V2_AHP_MATRIX)
    delta_w = np.max(np.abs(w_a - w_b))
    assert delta_w < 1e-14, f"w differed by {delta_w}"

    # 7. Metric Tensor M_K invariance (delta < 1e-14)
    M_K_a, W_a = construct_metric_tensor(V_K_a, w_a)
    M_K_b, W_b = construct_metric_tensor(V_K_b, w_b)
    delta_M = np.max(np.abs(M_K_a - M_K_b))
    assert delta_M < 1e-14, f"M_K differed by {delta_M}"

    # 8. Transformed Targets t+, t- invariance (delta < 1e-14)
    t_plus_a, t_minus_a = project_reference_points(z_plus_a, z_minus_a, V_K_a)
    t_plus_b, t_minus_b = project_reference_points(z_plus_b, z_minus_b, V_K_b)
    delta_t_plus = np.max(np.abs(t_plus_a - t_plus_b))
    delta_t_minus = np.max(np.abs(t_minus_a - t_minus_b))
    assert delta_t_plus < 1e-14, f"t+ differed by {delta_t_plus}"
    assert delta_t_minus < 1e-14, f"t- differed by {delta_t_minus}"

    # 9. TOPSIS Distances D+, D- and Closeness C_L invariance (delta < 1e-14)
    D_plus_a, D_minus_a, C_L_a, ranks_a = compute_distances_and_closeness(
        Z_a, z_plus_a, z_minus_a, V_K_a, M_K_a, polymer_ids=ids_a
    )
    D_plus_b, D_minus_b, C_L_b, ranks_b = compute_distances_and_closeness(
        Z_b, z_plus_b, z_minus_b, V_K_b, M_K_b, polymer_ids=ids_b
    )

    delta_d_plus = np.max(np.abs(D_plus_a - D_plus_b))
    delta_d_minus = np.max(np.abs(D_minus_a - D_minus_b))
    delta_cl = np.max(np.abs(C_L_a - C_L_b))
    assert delta_d_plus < 1e-14, f"D+ differed by {delta_d_plus}"
    assert delta_d_minus < 1e-14, f"D- differed by {delta_d_minus}"
    assert delta_cl < 1e-14, f"C_L differed by {delta_cl}"

    # 10. Candidate Rank Permutation sigma exact equality
    assert np.array_equal(ranks_a, ranks_b), f"Rank array mismatch: {ranks_a} vs {ranks_b}"


def test_variable_k_engine_evaluate_invariance(
    test_drug: Drug,
    five_polymers_with_mn: List[Polymer],
    five_polymers_without_mn: List[Polymer],
):
    """Assert VariableKEngine.evaluate() produces identical snapshots."""
    lib_a = PolymerLibrary(polymers=five_polymers_with_mn, drug=test_drug)
    comp_a = CompatibilityMatrix(test_drug, lib_a, drug_loading_ww=0.30)
    S_a = comp_a.build_matrix()[["s_HSP", "s_chi", "s_desc", "s_GT"]].values.astype(float)
    ids = [p.polymer_id for p in five_polymers_with_mn]

    lib_b = PolymerLibrary(polymers=five_polymers_without_mn, drug=test_drug)
    comp_b = CompatibilityMatrix(test_drug, lib_b, drug_loading_ww=0.30)
    S_b = comp_b.build_matrix()[["s_HSP", "s_chi", "s_desc", "s_GT"]].values.astype(float)

    engine = VariableKEngine()
    snap_a = engine.evaluate(
        scores=S_a,
        pairwise_matrix=AUTHORITATIVE_V2_AHP_MATRIX,
        polymer_ids=ids,
    )
    snap_b = engine.evaluate(
        scores=S_b,
        pairwise_matrix=AUTHORITATIVE_V2_AHP_MATRIX,
        polymer_ids=ids,
    )

    assert snap_a.retained_k == snap_b.retained_k
    assert np.allclose(snap_a.closeness_coefficients, snap_b.closeness_coefficients, atol=1e-14)
    assert snap_a.ranks == snap_b.ranks
    assert snap_a.metrics.ranked_polymer_ids == snap_b.metrics.ranked_polymer_ids


# ==============================================================================
# 2. FLORY-HUGGINS DIAGNOSTIC DECOUPLING
# ==============================================================================

def test_flory_huggins_diagnostic_when_mn_supplied(test_drug: Drug, five_polymers_with_mn: List[Polymer]):
    """When Mn is provided, chi_c and Gate 1 diagnostic evaluate normally."""
    lib = PolymerLibrary(polymers=five_polymers_with_mn, drug=test_drug)
    fhm = FloryHugginsModel(test_drug, lib)

    p = five_polymers_with_mn[0]
    assert p.mn_da is not None
    chi_c = fhm.compute_chi_critical(p)
    assert chi_c is not None
    assert isinstance(chi_c, float)
    assert chi_c > 0.0

    # Diagnostic evaluation
    diag_dict = fhm.evaluate_candidate_gate1(p)
    status = diag_dict["gate1_status"]
    passed = diag_dict["passed"]
    assert status in ("PASS", "FAIL")
    assert isinstance(passed, bool)

    diag_status = evaluate_gate1_diagnostic(0.25, chi_c)
    assert diag_status in ("PASS", "FAIL")


def test_flory_huggins_diagnostic_when_mn_omitted(test_drug: Drug, five_polymers_without_mn: List[Polymer]):
    """When Mn is omitted (None), chi_c is None and Gate 1 is reported as unavailable."""
    lib = PolymerLibrary(polymers=five_polymers_without_mn, drug=test_drug)
    fhm = FloryHugginsModel(test_drug, lib)

    p = five_polymers_without_mn[0]
    assert p.mn_da is None

    # compute_chi_critical returns None
    chi_c = fhm.compute_chi_critical(p)
    assert chi_c is None

    # evaluate_gate1_diagnostic returns explicit unavailable status
    diag_status = evaluate_gate1_diagnostic(0.25, None)
    assert diag_status == "NOT_EVALUATED_MN_UNAVAILABLE"

    # evaluate_candidate_gate1 returns explicit unavailable status with passed=None
    diag_dict = fhm.evaluate_candidate_gate1(p)
    assert diag_dict["gate1_status"] == "NOT_EVALUATED_MN_UNAVAILABLE"
    assert diag_dict["passed"] is None
    assert "critical interaction parameter requires number-average" in diag_dict["message"]


# ==============================================================================
# 3. NEGATIVE TEST: STRICT PROHIBITION OF Mw SILENT SUBSTITUTION
# ==============================================================================

def test_mw_only_no_silent_substitution(test_drug: Drug):
    """
    Assert that when Mw is provided but Mn is None, the system NEVER
    silently substitutes Mw for Mn in Flory-Huggins critical chi computation.
    """
    poly = Polymer.from_dict({
        "polymer_id": "TEST-MW-ONLY",
        "polymer_name": "Test Mw Only",
        "abbreviation": "MW_ONLY",
        "mn_da": None,
        "mw_da": 85000.0,  # High Mw provided!
        "pdi": 1.5,
        "tg_k": 350.0,
        "density_g_cm3": 1.20,
        "hsp_delta_d": 17.0,
        "hsp_delta_p": 8.0,
        "hsp_delta_h": 10.0,
        "monomer_smiles": "C=CN1CCCC1=O",
    })
    lib = PolymerLibrary(polymers=[poly], drug=test_drug)
    fhm = FloryHugginsModel(test_drug, lib)

    # Must return None, never a calculated float using mw_da!
    chi_c = fhm.compute_chi_critical(poly)
    assert chi_c is None, f"Expected None for chi_critical without Mn, got {chi_c}"


# ==============================================================================
# 4. SCHEMA AND BACKEND VALIDATION RULES
# ==============================================================================

def test_pydantic_schema_optional_mn():
    """Verify PolymerCreate and PolymerResponse accept None for mn_da, and ScreeningResponse fields allow None."""
    # PolymerCreate with mn_da = None
    pc = PolymerCreate(
        polymer_id="P-NEW",
        polymer_name="New Polymer",
        abbreviation="NP",
        mn_da=None,
        tg_k=360.0,
        density_g_cm3=1.18,
        hsp_delta_d=17.0,
        hsp_delta_p=8.0,
        hsp_delta_h=10.0,
        monomer_smiles="CC=O",
    )
    assert pc.mn_da is None

    # PolymerResponse with mn_da = None
    pr = PolymerResponse(
        polymer_id="P-NEW",
        polymer_name="New Polymer",
        abbreviation="NP",
        mn_da=None,
        tg_k=360.0,
        density_g_cm3=1.18,
        hsp_delta_d=17.0,
        hsp_delta_p=8.0,
        hsp_delta_h=10.0,
    )
    assert pr.mn_da is None

    # Verify ScreeningResponse model field types allow None
    assert ScreeningResponse.model_fields["chi_critical"].default is None
    assert ScreeningResponse.model_fields["gate1_passed"].default is None


def test_schema_rejection_negative_or_zero_mn():
    """PolymerCreate must reject mn_da <= 0."""
    with pytest.raises(ValidationError):
        PolymerCreate(
            polymer_id="P-BAD",
            polymer_name="Bad Polymer",
            abbreviation="BP",
            mn_da=0.0,  # <= 0 must fail
            tg_k=360.0,
            density_g_cm3=1.18,
            hsp_delta_d=17.0,
            hsp_delta_p=8.0,
            hsp_delta_h=10.0,
            monomer_smiles="CC=O",
        )

    with pytest.raises(ValidationError):
        PolymerCreate(
            polymer_id="P-BAD2",
            polymer_name="Bad Polymer 2",
            abbreviation="BP2",
            mn_da=-500.0,  # < 0 must fail
            tg_k=360.0,
            density_g_cm3=1.18,
            hsp_delta_d=17.0,
            hsp_delta_p=8.0,
            hsp_delta_h=10.0,
            monomer_smiles="CC=O",
        )


def test_backend_validation_service_rules():
    """validate_polymer_input accepts optional Mn, rejects Mn > Mw (PDI < 1.0) and Mn <= 0."""
    # 1. Valid without mn_da
    data_no_mn = {
        "polymer_id": "P-TEST",
        "polymer_name": "Test Poly",
        "abbreviation": "TP",
        "tg_k": 350.0,
        "density_g_cm3": 1.20,
        "hsp_delta_d": 17.0,
        "hsp_delta_p": 8.0,
        "hsp_delta_h": 10.0,
        "monomer_smiles": "C=C",
    }
    status, errors, warnings = validate_polymer_input(data_no_mn)
    assert status == "VALID", f"Expected VALID, got {status} with errors: {errors}"
    assert errors == []

    # 2. Valid with mn_da and mw_da (PDI >= 1.0)
    data_with_mn = dict(data_no_mn, mn_da=40000.0, mw_da=60000.0)
    status, errors, warnings = validate_polymer_input(data_with_mn)
    assert status == "VALID"
    assert errors == []

    # 3. Invalid: mn_da <= 0
    status, errors, warnings = validate_polymer_input(dict(data_no_mn, mn_da=-100.0))
    assert status == "INVALID"
    assert any("Mn must be > 0" in e for e in errors)

    status, errors, warnings = validate_polymer_input(dict(data_no_mn, mn_da=0.0))
    assert status == "INVALID"
    assert any("Mn must be > 0" in e for e in errors)

    # 4. Invalid: mn_da > mw_da (PDI < 1.0 thermodynamic violation)
    status, errors, warnings = validate_polymer_input(dict(data_no_mn, mn_da=50000.0, mw_da=40000.0))
    assert status == "INVALID"
    assert any("cannot exceed Mw" in e for e in errors)


# ==============================================================================
# 5. PREDICTOR AND ADAPTER NULL-SAFETY
# ==============================================================================

def test_prediction_report_null_chi_critical(test_drug: Drug, five_polymers_without_mn: List[Polymer]):
    """FormulationPredictor and PredictionReport handle chi_critical=None gracefully without crashing."""
    lib = PolymerLibrary(polymers=five_polymers_without_mn, drug=test_drug)
    predictor = FormulationPredictor(test_drug, lib, drug_loading_ww=0.30)
    report = predictor.predict_for_polymer("POL-005")

    assert report.chi_critical is None
    assert "Phase-boundary diagnostic unavailable" in report.miscibility_class
    assert report.risk_phase_separation == "Unknown (Mn not provided)"


def test_engine_adapter_markdown_report_formatting(
    tmp_path: Path,
    test_drug: Drug,
    five_polymers_without_mn: List[Polymer],
):
    """_write_decision_report_md formats safely when chi_critical is None."""
    lib = PolymerLibrary(polymers=five_polymers_without_mn, drug=test_drug)
    comp = CompatibilityMatrix(test_drug, lib, drug_loading_ww=0.30)
    S = comp.build_matrix()[["s_HSP", "s_chi", "s_desc", "s_GT"]].values.astype(float)
    ids = [p.polymer_id for p in five_polymers_without_mn]

    engine = VariableKEngine()
    snapshot = engine.evaluate(
        scores=S,
        pairwise_matrix=AUTHORITATIVE_V2_AHP_MATRIX,
        polymer_ids=ids,
    )

    class DummyMC:
        p_top1 = {"POL-005": 0.85}
        confidence_tier = "High"
        num_valid = 1000
        num_generated = 1000
        k_distribution = {3: 1.0}

    df_ranking = pd.DataFrame([{
        "topsis_rank": 1,
        "polymer_id": "POL-005",
        "polymer_name": "Soluplus",
        "topsis_cl": 0.65,
        "topsis_ideal_distance": 0.12,
        "topsis_anti_ideal_distance": 0.22,
        "p_top1_percent": 85.0,
    }])

    report_path = tmp_path / "decision_report.md"
    _write_decision_report_md(
        report_path=report_path,
        analysis_id="ANA-TEST-001",
        analysis_fingerprint="sha256-test",
        mode="exploratory",
        execution_tier="EXPLORATORY_SCREENING",
        drug_id="IND",
        drug_name="Indomethacin",
        winner_name="Soluplus",
        winner_id="POL-005",
        df_ranking=df_ranking,
        snapshot=snapshot,
        mc_res=DummyMC(),
        predicted_tg_k=340.0,
        predicted_chi=0.25,
        chi_critical=None,
        miscibility_class="Phase-boundary diagnostic unavailable (Mn not provided)",
        stability_tier="High Stability",
    )
    with open(report_path, "r", encoding="utf-8") as f:
        md_text = f.read()
    assert "N/A - Mn not provided" in md_text


# ==============================================================================
# 6. REFERENCE LIBRARY SHA-256 IMMUTABILITY
# ==============================================================================

def test_reference_polymer_library_sha256_unmodified():
    """Verify that config/polymers/polymer_library_v3_five_polymers.csv has NOT been mutated."""
    lib_path = Path("config/polymers/polymer_library_v3_five_polymers.csv")
    assert lib_path.exists(), f"Reference library not found at {lib_path}"

    with open(lib_path, "rb") as f:
        content = f.read()

    actual_sha = hashlib.sha256(content).hexdigest()
    expected_sha = "5497d606b64e081cac0274e4f5db8343c012fd84191b5ec413990614717c3ac2"
    assert actual_sha == expected_sha, (
        f"CRITICAL: Reference library SHA-256 mutation detected!\n"
        f"Expected: {expected_sha}\nActual:   {actual_sha}"
    )
