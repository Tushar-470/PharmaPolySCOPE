"""
Tests verifying zero silent fallbacks and strict validation in asd_framework.
Ensures that missing physical properties raise explicit IncompleteProfileError
and never substitute Indomethacin or dummy fallback values.
"""

import pytest

from asd_mcda.drug.drug_profile import Drug, IncompleteProfileError
from asd_mcda.polymer.polymer_library import Polymer, PolymerLibrary
from asd_mcda.compatibility.hsp_model import HSPModel
from asd_mcda.compatibility.flory_huggins import FloryHugginsModel
from asd_mcda.utils.rdkit_wrapper import compute_2d_descriptors, hoftyzer_van_krevelen_hsp


@pytest.fixture
def sample_polymer() -> Polymer:
    return Polymer.from_dict({
        "polymer_id": "TEST_POLY_01",
        "polymer_name": "Test Polymer",
        "abbreviation": "TP1",
        "mn_da": 50000.0,
        "tg_k": 350.0,
        "density_g_cm3": 1.18,
        "hsp_delta_d": 17.0,
        "hsp_delta_p": 7.0,
        "hsp_delta_h": 9.0,
        "monomer_smiles": "C=CC(=O)O",
    })


@pytest.fixture
def base_drug_dict() -> dict:
    """Distinct non-Indomethacin drug parameters (Aspirin-like)."""
    return {
        "drug_id": "DRUG_TEST_UNIQUE_001",
        "generic_name": "AcetylsalicylicAcidTest",
        "canonical_smiles": "CC(=O)Oc1ccccc1C(=O)O",
        "tm_k": 408.15,
        "tg_k": 243.15,
        "density_crystalline_g_cm3": 1.40,
        "hsp_delta_d": 17.5,
        "hsp_delta_p": 8.0,
        "hsp_delta_h": 10.5,
        "hsp_ro": 7.5,
        "molar_volume_cm3_mol": 128.7,
    }


def test_omitted_required_fields_raises_incomplete_profile_error(base_drug_dict):
    """Test 2: Omit required fields -> assert no Indomethacin values are substituted, IncompleteProfileError raised."""
    # 1. Density omitted
    no_density = dict(base_drug_dict)
    del no_density["density_crystalline_g_cm3"]
    with pytest.raises(IncompleteProfileError) as exc_info:
        Drug.from_dict(no_density)
    assert "density" in exc_info.value.missing_field.lower()
    assert exc_info.value.drug_id == "DRUG_TEST_UNIQUE_001"

    # 2. HSP delta_d omitted -> must NOT default to 19.2
    no_dd = dict(base_drug_dict)
    del no_dd["hsp_delta_d"]
    with pytest.raises(IncompleteProfileError) as exc_info:
        Drug.from_dict(no_dd)
    assert exc_info.value.missing_field == "hsp_delta_d"

    # 3. HSP delta_p omitted -> must NOT default to 7.9
    no_dp = dict(base_drug_dict)
    del no_dp["hsp_delta_p"]
    with pytest.raises(IncompleteProfileError) as exc_info:
        Drug.from_dict(no_dp)
    assert exc_info.value.missing_field == "hsp_delta_p"

    # 4. HSP delta_h omitted -> must NOT default to 8.4
    no_dh = dict(base_drug_dict)
    del no_dh["hsp_delta_h"]
    with pytest.raises(IncompleteProfileError) as exc_info:
        Drug.from_dict(no_dh)
    assert exc_info.value.missing_field == "hsp_delta_h"

    # 5. Melting point omitted
    no_tm = dict(base_drug_dict)
    del no_tm["tm_k"]
    with pytest.raises(IncompleteProfileError) as exc_info:
        Drug.from_dict(no_tm)
    assert exc_info.value.missing_field == "tm_k"

    # 6. Canonical smiles omitted
    no_smiles = dict(base_drug_dict)
    del no_smiles["canonical_smiles"]
    with pytest.raises(IncompleteProfileError) as exc_info:
        Drug.from_dict(no_smiles)
    assert exc_info.value.missing_field == "canonical_smiles"


def test_polymorphs_defaults_to_empty_list_not_indomethacin(base_drug_dict):
    """Verify polymorphs list defaults to empty list and never to ['gamma', 'alpha']."""
    d = Drug.from_dict(base_drug_dict)
    assert d.polymorphs == []
    assert d.polymorphs != ["gamma", "alpha"]


def test_missing_molar_volume_blocks_flory_huggins(base_drug_dict, sample_polymer):
    """Test 4: Omit molar_volume_cm3_mol -> assert FloryHugginsModel.compute_chi() raises IncompleteProfileError."""
    data_no_vm = dict(base_drug_dict)
    del data_no_vm["molar_volume_cm3_mol"]
    drug = Drug.from_dict(data_no_vm)

    # Must be None, never defaulted to 273.0
    assert drug.molar_volume_cm3_mol is None

    lib = PolymerLibrary([sample_polymer], drug=drug)
    fh_model = FloryHugginsModel(drug=drug, polymer_library=lib)

    with pytest.raises(IncompleteProfileError) as exc_info:
        fh_model.compute_chi(sample_polymer)
    assert exc_info.value.missing_field == "molar_volume_cm3_mol"
    assert "Flory-Huggins" in exc_info.value.calculation

    with pytest.raises(IncompleteProfileError) as exc_info:
        fh_model.compute_chi_critical(sample_polymer)
    assert exc_info.value.missing_field == "molar_volume_cm3_mol"


def test_missing_hsp_ro_blocks_red_and_s_hsp_and_gate1(base_drug_dict, sample_polymer):
    """Test 5: Omit hsp_ro -> assert compute_red raises IncompleteProfileError and check_gate1 reports blocked."""
    data_no_ro = dict(base_drug_dict)
    del data_no_ro["hsp_ro"]
    drug = Drug.from_dict(data_no_ro)

    # Must be None, never defaulted to 8.0
    assert drug.hsp_ro is None

    lib = PolymerLibrary([sample_polymer], drug=drug)
    hsp_model = HSPModel(drug=drug, polymer_library=lib)

    # Ra should still work (pure distance, no Ro needed)
    ra = hsp_model.compute_ra(sample_polymer)
    assert ra > 0.0

    # compute_red must raise IncompleteProfileError
    with pytest.raises(IncompleteProfileError) as exc_info:
        hsp_model.compute_red(sample_polymer)
    assert exc_info.value.missing_field == "hsp_ro"
    assert "RED" in exc_info.value.calculation

    # compute_s_hsp must raise IncompleteProfileError
    with pytest.raises(IncompleteProfileError) as exc_info:
        hsp_model.compute_s_hsp(sample_polymer)
    assert exc_info.value.missing_field == "hsp_ro"

    # check_gate1 must NOT pass or default to 8.0; must explicitly return GateResult(passed=False)
    gate1_res = hsp_model.check_gate1()
    assert gate1_res.passed is False
    assert gate1_res.n_passing == 0
    assert "Gate 1 BLOCKED: hsp_ro is unavailable" in gate1_res.message


def test_rdkit_invalid_smiles_raises_error():
    """Test 8: Invalid SMILES or RDKit failure -> assert compute_2d_descriptors raises error instead of dummy descriptors."""
    with pytest.raises(ValueError) as exc_info:
        compute_2d_descriptors("INVALID_SMILES_STRING_NOT_CHEMICAL")
    assert "failed to parse chemical structure" in str(exc_info.value)


def test_hvk_string_matching_fallback_prohibited():
    """Verify legacy hardcoded HVK fallback (17.5, 8.0, 10.0) is prohibited."""
    with pytest.raises(ValueError) as exc_info:
        hoftyzer_van_krevelen_hsp("CC(=O)Oc1ccccc1C(=O)O")
    assert "Hardcoded fallback HSPs are prohibited" in str(exc_info.value)
