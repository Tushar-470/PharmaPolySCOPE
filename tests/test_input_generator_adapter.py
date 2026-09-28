"""
Tests for Canonical Input Generator Adapter in asd_framework.
Verifies exact mapping, USER_PROVIDED provenance preservation, CSV/JSON equivalence,
strict unit validation, and validation status translation.
"""

import pytest
from fastapi.testclient import TestClient

from asd_mcda.drug.drug_profile import Drug
from asd_mcda.integration.input_adapter import InputGeneratorAdapter
from backend.main import app


def test_exact_upstream_mapping_unique_synthetic_values():
    """Test 1: Exact upstream mapping with unique synthetic values, no Indomethacin pollution."""
    record = {
        "entity_id": "SYNTH_API_999",
        "name": "SyntheticumTest",
        "canonical_smiles": "c1ccccc1",
        "tm_K": 401.23,
        "tg_K": 287.61,
        "true_density_g_cm3": 1.47,
        "hsp": {
            "delta_D": 16.21,
            "delta_P": 9.83,
            "delta_H": 12.44,
            "method": "fedors",
            "status": "CALCULATED",
        },
        "molar_volume": 201.77,
        "ro": 6.55,
        "data_integrity_status": "PASS",
    }
    drug = InputGeneratorAdapter.load_drug_from_dict(record)
    assert drug.drug_id == "SYNTH_API_999"
    assert drug.generic_name == "SyntheticumTest"
    assert drug.tm_k == 401.23
    assert drug.tg_k == 287.61
    assert drug.density_crystalline_g_cm3 == 1.47
    assert drug.hsp_delta_d == 16.21
    assert drug.hsp_delta_p == 9.83
    assert drug.hsp_delta_h == 12.44
    assert drug.molar_volume_cm3_mol == 201.77
    assert drug.hsp_ro == 6.55
    assert drug.validation_status == "validated"

    # Verify no Indomethacin numbers are present
    assert drug.density_crystalline_g_cm3 != 1.31
    assert drug.hsp_delta_d != 19.2
    assert drug.hsp_delta_p != 7.9
    assert drug.hsp_delta_h != 8.4
    assert drug.molar_volume_cm3_mol != 273.0
    assert drug.hsp_ro != 8.0


def test_user_provided_status_survives_with_conversion_and_provenance():
    """Test 3: USER_PROVIDED status survives with converted value, unit, and original provenance."""
    record = {
        "entity_id": "USER_PROV_API_01",
        "name": "UserProvidedDrug",
        "canonical_smiles": "CC(=O)Oc1ccccc1C(=O)O",
        "tm_K": {
            "value": 150.0,
            "unit": "C",
            "status": "USER_PROVIDED",
            "source": "lab_notebook_2026_p42",
        },
        "true_density_g_cm3": {
            "value": 1400.0,
            "unit": "kg/m3",
            "status": "USER_PROVIDED",
            "source": "pycnometry_batch_12",
        },
        "hsp": {
            "delta_D": {"value": 17.5, "unit": "MPa^0.5", "status": "USER_PROVIDED", "source": "literature_hansen_2007"},
            "delta_P": {"value": 8.0, "unit": "MPa^0.5", "status": "USER_PROVIDED", "source": "literature_hansen_2007"},
            "delta_H": {"value": 10.5, "unit": "MPa^0.5", "status": "USER_PROVIDED", "source": "literature_hansen_2007"},
        },
        "molar_volume": {
            "value": 130.0,
            "unit": "cm3/mol",
            "status": "USER_PROVIDED",
            "source": "calculated_fedors_user",
        },
    }
    drug = InputGeneratorAdapter.load_drug_from_dict(record)

    # Check converted values
    assert drug.tm_k == 423.15  # 150.0 + 273.15
    assert drug.density_crystalline_g_cm3 == 1.40  # 1400.0 / 1000.0

    # Check provenance
    tm_prov = drug.input_provenance["tm_k"]
    assert tm_prov["status"] == "USER_PROVIDED"
    assert tm_prov["original_value"] == 150.0
    assert tm_prov["original_unit"] == "C"
    assert tm_prov["value"] == 423.15
    assert tm_prov["unit"] == "K"
    assert tm_prov["source"] == "lab_notebook_2026_p42"

    dens_prov = drug.input_provenance["density_crystalline_g_cm3"]
    assert dens_prov["status"] == "USER_PROVIDED"
    assert dens_prov["original_value"] == 1400.0
    assert dens_prov["original_unit"] == "kg/m3"
    assert dens_prov["value"] == 1.40
    assert dens_prov["unit"] == "g/cm3"
    assert dens_prov["source"] == "pycnometry_batch_12"


def test_csv_and_json_equivalence():
    """Test 6: Equivalent CSV and JSON records produce identical normalized properties."""
    json_record = {
        "entity_id": "EQUIV_001",
        "name": "EquivalenceDrug",
        "canonical_smiles": "CC(=O)Oc1ccccc1C(=O)O",
        "tm_K": 408.15,
        "tg_K": 243.15,
        "true_density_g_cm3": 1.40,
        "delta_D": 17.5,
        "delta_P": 8.0,
        "delta_H": 10.5,
        "molar_volume": 128.7,
        "ro": 7.5,
        "data_integrity_status": "PASS",
    }

    csv_str = (
        "entity_id,name,entity_type,canonical_smiles,mw,tm_K,tm_status,tm_source,tg_K,tg_status,tg_method,"
        "true_density_g_cm3,density_status,density_type,delta_D,delta_P,delta_H,hsp_method,hsp_status,molar_volume,"
        "hsp_ro,data_integrity_status\n"
        "EQUIV_001,EquivalenceDrug,drug,CC(=O)Oc1ccccc1C(=O)O,180.16,408.15,USER_PROVIDED,lit,243.15,ESTIMATED,boyer_beaman,"
        "1.40,USER_PROVIDED,lit,17.5,8.0,10.5,fedors,CALCULATED,128.7,7.5,PASS\n"
    )

    drug_json = InputGeneratorAdapter.load_drug_from_dict(json_record)
    drug_csv = InputGeneratorAdapter.load_from_csv(csv_str, entity_id="EQUIV_001")

    assert drug_json.drug_id == drug_csv.drug_id
    assert drug_json.generic_name == drug_csv.generic_name
    assert drug_json.canonical_smiles == drug_csv.canonical_smiles
    assert drug_json.tm_k == drug_csv.tm_k
    assert drug_json.tg_k == drug_csv.tg_k
    assert drug_json.density_crystalline_g_cm3 == drug_csv.density_crystalline_g_cm3
    assert drug_json.hsp_delta_d == drug_csv.hsp_delta_d
    assert drug_json.hsp_delta_p == drug_csv.hsp_delta_p
    assert drug_json.hsp_delta_h == drug_csv.hsp_delta_h
    assert drug_json.molar_volume_cm3_mol == drug_csv.molar_volume_cm3_mol
    assert drug_json.hsp_ro == drug_csv.hsp_ro
    assert drug_json.validation_status == drug_csv.validation_status


def test_incompatible_units_fail_explicitly():
    """Test 7: Incompatible units fail explicitly with ValueError."""
    # Incompatible unit for temperature
    rec_bad_tm = {
        "entity_id": "BAD_UNIT_01",
        "canonical_smiles": "CC(=O)Oc1ccccc1C(=O)O",
        "tm_K": {"value": 400.0, "unit": "kg/m3"},
        "true_density_g_cm3": 1.40,
        "delta_D": 17.5,
        "delta_P": 8.0,
        "delta_H": 10.5,
    }
    with pytest.raises(ValueError) as exc:
        InputGeneratorAdapter.normalize_record(rec_bad_tm)
    assert "Invalid temperature unit" in str(exc.value)

    # Incompatible unit for density
    rec_bad_dens = {
        "entity_id": "BAD_UNIT_02",
        "canonical_smiles": "CC(=O)Oc1ccccc1C(=O)O",
        "tm_K": 400.0,
        "true_density_g_cm3": {"value": 1.4, "unit": "Kelvin"},
        "delta_D": 17.5,
        "delta_P": 8.0,
        "delta_H": 10.5,
    }
    with pytest.raises(ValueError) as exc:
        InputGeneratorAdapter.normalize_record(rec_bad_dens)
    assert "Invalid density unit" in str(exc.value)

    # Incompatible unit for HSP
    rec_bad_hsp = {
        "entity_id": "BAD_UNIT_03",
        "canonical_smiles": "CC(=O)Oc1ccccc1C(=O)O",
        "tm_K": 400.0,
        "true_density_g_cm3": 1.4,
        "delta_D": {"value": 17.5, "unit": "g/mol"},
        "delta_P": 8.0,
        "delta_H": 10.5,
    }
    with pytest.raises(ValueError) as exc:
        InputGeneratorAdapter.normalize_record(rec_bad_hsp)
    assert "Invalid HSP unit" in str(exc.value)


def test_data_integrity_status_translation():
    """Test 9: Upstream data_integrity_status translates cleanly to downstream validation_status."""
    base = {
        "canonical_smiles": "CC(=O)Oc1ccccc1C(=O)O",
        "tm_K": 400.0,
        "true_density_g_cm3": 1.4,
        "delta_D": 17.5,
        "delta_P": 8.0,
        "delta_H": 10.5,
    }

    # PASS -> validated
    rec_pass = dict(base, entity_id="INTEG_PASS", data_integrity_status="PASS")
    d_pass = InputGeneratorAdapter.load_drug_from_dict(rec_pass)
    assert d_pass.validation_status == "validated"
    assert d_pass.input_provenance["data_integrity_status"]["upstream_status"] == "PASS"

    # CAUTION -> caution
    rec_caut = dict(base, entity_id="INTEG_CAUTION", data_integrity_status="CAUTION")
    d_caut = InputGeneratorAdapter.load_drug_from_dict(rec_caut)
    assert d_caut.validation_status == "caution"
    assert d_caut.input_provenance["data_integrity_status"]["upstream_status"] == "CAUTION"

    # FAIL -> draft
    rec_fail = dict(base, entity_id="INTEG_FAIL", data_integrity_status="FAIL")
    d_fail = InputGeneratorAdapter.load_drug_from_dict(rec_fail)
    assert d_fail.validation_status == "draft"
    assert d_fail.input_provenance["data_integrity_status"]["upstream_status"] == "FAIL"


def test_api_import_generator_export_endpoint():
    """Verify POST /api/drugs/import-generator-export endpoint."""
    client = TestClient(app)
    export_payload = {
        "entity_id": "EXPORT_TEST_001",
        "name": "ExportTestAPI",
        "canonical_smiles": "CC(=O)Oc1ccccc1C(=O)O",
        "tm_K": 408.15,
        "tg_K": 243.15,
        "true_density_g_cm3": 1.40,
        "delta_D": 17.5,
        "delta_P": 8.0,
        "delta_H": 10.5,
        "molar_volume": 128.7,
        "ro": 7.5,
        "data_integrity_status": "PASS",
    }
    resp = client.post("/api/drugs/import-generator-export", json=export_payload)
    assert resp.status_code == 201
    saved_drug = resp.json()
    assert saved_drug["drug_id"] == "EXPORT_TEST_001"
    assert saved_drug["generic_name"] == "ExportTestAPI"
    assert saved_drug["tm_k"] == 408.15
    assert saved_drug["density_crystalline_g_cm3"] == 1.40
    assert saved_drug["molar_volume_cm3_mol"] == 128.7
    assert saved_drug["hsp_ro"] == 7.5
