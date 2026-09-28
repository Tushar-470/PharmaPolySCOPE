"""
End-to-end integration and provenance preservation test.
Proves that:
Input Generator -> Adapter -> Drug object -> Calculation -> Report/Export
preserves property-level provenance exactly without silent modification or status upgrading.
"""

from dataclasses import asdict
import pytest
from fastapi.testclient import TestClient

from asd_mcda.drug.drug_profile import Drug
from asd_mcda.polymer.polymer_library import Polymer, PolymerLibrary
from asd_mcda.compatibility.hsp_model import HSPModel
from asd_mcda.compatibility.flory_huggins import FloryHugginsModel
from asd_mcda.compatibility.matrix import CompatibilityMatrix
from asd_mcda.integration.input_adapter import InputGeneratorAdapter
from backend.main import app


@pytest.fixture
def sample_polymer() -> Polymer:
    return Polymer.from_dict({
        "polymer_id": "POL_TEST_E2E",
        "polymer_name": "PVP-K30",
        "abbreviation": "PVP_K30",
        "mn_da": 40000.0,
        "tg_k": 443.0,
        "density_g_cm3": 1.20,
        "hsp_delta_d": 17.4,
        "hsp_delta_p": 8.2,
        "hsp_delta_h": 11.7,
        "monomer_smiles": "C=CN1CCCC1=O",
    })


def test_end_to_end_provenance_pipeline_preservation(sample_polymer):
    """
    Verify complete pipeline provenance preservation:
    1. Input Generator payload with:
       - tm_K: status = USER_PROVIDED, source = 'DSC_scan_run_04'
       - tg_K: status = ESTIMATED, source = 'boyer_beaman'
    2. Ingestion through InputGeneratorAdapter
    3. Immutable Drug dataclass instance
    4. Thermodynamic & compatibility calculations (HSP, Flory-Huggins, CompatibilityMatrix)
    5. Serialization into export report and API response
    """
    # 1. Upstream Input Generator export payload
    upstream_payload = {
        "entity_id": "DRUG_E2E_001",
        "name": "Naproxen Provenance Reference",
        "canonical_smiles": "CC(C1=CC2=C(C=C1)C=C(C=C2)OC)C(=O)O",
        "tm_K": {
            "value": 156.0,
            "unit": "C",
            "status": "USER_PROVIDED",
            "source": "DSC_scan_run_04",
        },
        "tg_K": {
            "value": 290.5,
            "unit": "K",
            "status": "ESTIMATED",
            "source": "boyer_beaman",
        },
        "true_density_g_cm3": {
            "value": 1280.0,
            "unit": "kg/m3",
            "status": "USER_PROVIDED",
            "source": "helium_pycnometry",
        },
        "hsp": {
            "delta_D": {"value": 18.2, "unit": "MPa^0.5", "status": "USER_PROVIDED", "source": "hansen_handbook_2007"},
            "delta_P": {"value": 6.4, "unit": "MPa^0.5", "status": "USER_PROVIDED", "source": "hansen_handbook_2007"},
            "delta_H": {"value": 8.9, "unit": "MPa^0.5", "status": "USER_PROVIDED", "source": "hansen_handbook_2007"},
            "method": "literature",
            "status": "USER_PROVIDED",
        },
        "molar_volume": 179.8,
        "ro": 7.2,
        "data_integrity_status": "PASS",
    }

    # 2. Ingest through Canonical Adapter
    drug = InputGeneratorAdapter.load_drug_from_dict(upstream_payload)

    # 3. Assert on Drug object metadata
    assert drug.drug_id == "DRUG_E2E_001"
    assert drug.generic_name == "Naproxen Provenance Reference"
    assert drug.tm_k == 429.15
    assert drug.tm_source == "DSC_scan_run_04"
    assert drug.get_property_status("tm_k") == "USER_PROVIDED"
    assert drug.get_property_source("tm_k") == "DSC_scan_run_04"

    assert drug.tg_k == 290.5
    assert drug.tg_source == "boyer_beaman"
    assert drug.get_property_status("tg_k") == "ESTIMATED"
    assert drug.get_property_source("tg_k") == "boyer_beaman"

    # Confirm neither status was upgraded to EXPERIMENTAL
    assert drug.get_property_status("tm_k") != "EXPERIMENTAL"
    assert drug.get_property_status("tg_k") != "EXPERIMENTAL"
    assert drug.tg_source != "experimental"

    # 4. Calculation Stage
    lib = PolymerLibrary([sample_polymer], drug=drug)

    # HSP distance & RED calculation
    hsp_model = HSPModel(drug, lib)
    ra = hsp_model.compute_ra(sample_polymer)
    red = hsp_model.compute_red(sample_polymer)
    assert ra > 0.0
    assert red > 0.0

    # Flory-Huggins chi calculation
    fh_model = FloryHugginsModel(drug, lib)
    chi = fh_model.compute_chi(sample_polymer)
    assert isinstance(chi, float)

    # Compatibility Matrix calculation
    comp_matrix = CompatibilityMatrix(drug, lib)
    df_s = comp_matrix.build_matrix()
    assert len(df_s) == 1
    assert "s_HSP" in df_s.columns
    assert "s_chi" in df_s.columns

    # 5. Report / Export Serialization Stage
    client = TestClient(app)
    api_resp = client.post("/api/drugs/import-generator-export", json=upstream_payload)
    assert api_resp.status_code == 201
    exported_data = api_resp.json()

    # Verify export payload preserves exact provenance
    assert exported_data["drug_id"] == "DRUG_E2E_001"
    assert exported_data["tm_source"] == "DSC_scan_run_04"
    assert exported_data["tg_source"] == "boyer_beaman"

    tm_prov = exported_data["input_provenance"]["tm_k"]
    assert tm_prov["status"] == "USER_PROVIDED"
    assert tm_prov["source"] == "DSC_scan_run_04"
    assert tm_prov["value"] == 429.15
    assert tm_prov["original_value"] == 156.0
    assert tm_prov["original_unit"] == "C"

    tg_prov = exported_data["input_provenance"]["tg_k"]
    assert tg_prov["status"] == "ESTIMATED"
    assert tg_prov["source"] == "boyer_beaman"
    assert tg_prov["value"] == 290.5

    # Clean up test database record
    client.delete("/api/drugs/DRUG_E2E_001")
