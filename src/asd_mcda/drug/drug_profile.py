"""
Immutable Drug dataclass representing the physicochemical identity of the API.
Aligned with SAS V1.0 Section 6.1.
"""

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from asd_mcda.utils.constants import BOYER_BEAMAN_FACTOR
from asd_mcda.utils.helpers import generate_sha256
from asd_mcda.utils.rdkit_wrapper import canonicalize_smiles, get_inchi_key, compute_2d_descriptors


class IncompleteProfileError(ValueError):
    """Raised when a calculation cannot proceed due to missing physical properties."""

    def __init__(self, drug_id: str, missing_field: str, calculation: str):
        super().__init__(
            f"Cannot calculate {calculation} for Drug '{drug_id}': {missing_field} is unavailable."
        )
        self.drug_id = drug_id
        self.missing_field = missing_field
        self.calculation = calculation


@dataclass(frozen=True)
class Drug:
    """Immutable value object representing an Active Pharmaceutical Ingredient (API)."""

    drug_id: str
    generic_name: str
    canonical_smiles: str
    inchi_key: str
    molecular_weight_g_mol: float
    tm_k: float
    tg_k: Optional[float]
    tg_k_estimated: float
    tg_source: str
    density_crystalline_g_cm3: float
    density_amorphous_g_cm3: Optional[float]
    density_source: str
    pka: Optional[float]
    logp: float
    logd_ph74: Optional[float]
    hbd: int
    hba: int
    tpsa_angstrom2: float
    rotatable_bonds: int
    aromatic_rings: int
    hsp_delta_d: float
    hsp_delta_p: float
    hsp_delta_h: float
    hsp_ro: Optional[float] = None
    tm_source: str = ""
    hsp_source: str = ""
    molar_volume_cm3_mol: Optional[float] = None
    delta_h_fus_kj_mol: Optional[float] = None
    bcs_class: str = "II"
    polymorphs: List[str] = field(default_factory=list)
    ionisation_state: str = "neutral"
    data_quality_score: float = 1.0
    validation_status: str = "validated"
    input_provenance: Dict[str, Any] = field(default_factory=dict)
    checksum_sha256: str = ""

    def get_property_status(self, property_name: str) -> str:
        """Return canonical provenance status for property_name."""
        prov = self.input_provenance.get(property_name)
        if isinstance(prov, dict):
            return str(prov.get("status", "UNSPECIFIED"))
        return "UNSPECIFIED"

    def get_property_source(self, property_name: str) -> str:
        """Return canonical provenance source for property_name."""
        prov = self.input_provenance.get(property_name)
        if isinstance(prov, dict):
            return str(prov.get("source", ""))
        if property_name == "tm_k":
            return self.tm_source
        elif property_name == "tg_k":
            return self.tg_source
        elif property_name in ("density_crystalline_g_cm3", "density_amorphous_g_cm3"):
            return self.density_source
        elif property_name in ("hsp_delta_d", "hsp_delta_p", "hsp_delta_h", "hsp"):
            return self.hsp_source
        return ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Drug":
        """Factory method creating a Drug instance from dictionary with validation and automatic descriptor derivation.

        Never silently substitutes another drug's values for missing physical parameters.
        """
        drug_id = str(data.get("drug_id", ""))
        if not drug_id:
            raise IncompleteProfileError("unknown", "drug_id", "Drug profile creation")

        generic_name = str(data.get("generic_name", drug_id))

        if "canonical_smiles" not in data or not data["canonical_smiles"]:
            raise IncompleteProfileError(drug_id, "canonical_smiles", "Molecular structure & descriptors")
        smiles = canonicalize_smiles(data["canonical_smiles"])
        inchi_key = data.get("inchi_key") or get_inchi_key(smiles)

        # Compute 2D descriptors if missing
        descriptors_2d = compute_2d_descriptors(smiles)
        mw = data.get("molecular_weight_g_mol") or descriptors_2d["MolWt"]
        logp = data.get("logp") or descriptors_2d["MolLogP"]
        hbd = data.get("hbd") if data.get("hbd") is not None else descriptors_2d["NumHDonors"]
        hba = data.get("hba") if data.get("hba") is not None else descriptors_2d["NumHAcceptors"]
        tpsa = data.get("tpsa_angstrom2") or descriptors_2d["TPSA"]
        rotb = data.get("rotatable_bonds") if data.get("rotatable_bonds") is not None else descriptors_2d["NumRotatableBonds"]
        arom = data.get("aromatic_rings") if data.get("aromatic_rings") is not None else descriptors_2d["NumAromaticRings"]

        if "tm_k" not in data or data["tm_k"] is None:
            raise IncompleteProfileError(drug_id, "tm_k", "Melting point & thermal properties")
        tm_k = float(data["tm_k"])
        tg_k_estimated = data.get("tg_k_estimated") or (tm_k * BOYER_BEAMAN_FACTOR)
        tg_k = float(data["tg_k"]) if data.get("tg_k") is not None else None

        # Check required HSPs - never default to Indomethacin (19.2, 7.9, 8.4)
        for hsp_field in ("hsp_delta_d", "hsp_delta_p", "hsp_delta_h"):
            if hsp_field not in data or data[hsp_field] is None:
                raise IncompleteProfileError(drug_id, hsp_field, "Hansen Solubility Parameters")
        hsp_delta_d = float(data["hsp_delta_d"])
        hsp_delta_p = float(data["hsp_delta_p"])
        hsp_delta_h = float(data["hsp_delta_h"])

        # Check density: either crystalline or amorphous must be provided - never default to 1.31
        dens_cryst_raw = data.get("density_crystalline_g_cm3")
        dens_amorph_raw = data.get("density_amorphous_g_cm3")
        if dens_cryst_raw is None and dens_amorph_raw is None:
            raise IncompleteProfileError(drug_id, "density_crystalline_g_cm3", "Density & Gordon-Taylor Simha-Boyer K")

        density_amorphous_g_cm3 = float(dens_amorph_raw) if dens_amorph_raw is not None else None
        density_crystalline_g_cm3 = float(dens_cryst_raw) if dens_cryst_raw is not None else float(density_amorphous_g_cm3)

        # Molar volume: None if absent - never default to 273.0
        molar_volume_cm3_mol = float(data["molar_volume_cm3_mol"]) if data.get("molar_volume_cm3_mol") is not None else None

        # HSP Ro: None if absent - never default to 8.0
        hsp_ro = float(data["hsp_ro"]) if data.get("hsp_ro") is not None else None

        # Polymorphs: empty list default - never default to Indomethacin's ["gamma", "alpha"]
        raw_polymorphs = data.get("polymorphs")
        if isinstance(raw_polymorphs, list):
            polymorphs = [str(p) for p in raw_polymorphs]
        elif isinstance(raw_polymorphs, str):
            polymorphs = [raw_polymorphs]
        else:
            polymorphs = []

        input_provenance = dict(data.get("input_provenance", {}))

        # 1. Resolve Tm provenance & source
        tm_prov = input_provenance.get("tm_k")
        if isinstance(tm_prov, dict):
            tm_source = str(tm_prov.get("source") or data.get("tm_source", ""))
            tm_status = str(tm_prov.get("status", "USER_PROVIDED")).upper()
        else:
            raw_tm_source = data.get("tm_source")
            if raw_tm_source is not None and str(raw_tm_source).strip() != "":
                tm_source = str(raw_tm_source).strip()
                tm_status = "EXPERIMENTAL" if tm_source.lower() in ("experimental", "dsc") else "USER_PROVIDED"
            else:
                tm_source = ""
                tm_status = "USER_PROVIDED"
            input_provenance["tm_k"] = {
                "value": tm_k,
                "unit": "K",
                "status": tm_status,
                "source": tm_source or "user_entered",
            }

        # 2. Resolve Tg provenance & source - never claim experimental simply from value presence
        tg_prov = input_provenance.get("tg_k")
        if isinstance(tg_prov, dict):
            tg_status = str(tg_prov.get("status", "ESTIMATED" if tg_k is None else "USER_PROVIDED")).upper()
            tg_source = str(tg_prov.get("source") or data.get("tg_source", ""))
            if not tg_source:
                if tg_status == "ESTIMATED":
                    tg_source = "boyer_beaman"
                elif tg_status == "USER_PROVIDED":
                    tg_source = "user_entered"
                elif tg_status == "EXPERIMENTAL":
                    tg_source = "experimental"
                else:
                    tg_source = "boyer_beaman" if tg_k is None else "user_entered"
        else:
            raw_tg_source = data.get("tg_source")
            if raw_tg_source is not None and str(raw_tg_source).strip() != "":
                tg_source = str(raw_tg_source).strip()
                tg_status = "EXPERIMENTAL" if tg_source.lower() in ("experimental", "experimental_dsc", "dsc") else (
                    "ESTIMATED" if tg_source.lower() in ("boyer_beaman", "estimated") else "USER_PROVIDED"
                )
            elif tg_k is None:
                tg_source = "boyer_beaman"
                tg_status = "ESTIMATED"
            else:
                tg_source = "user_entered"
                tg_status = "USER_PROVIDED"

            input_provenance["tg_k"] = {
                "value": tg_k if tg_k is not None else tg_k_estimated,
                "unit": "K",
                "status": tg_status,
                "source": tg_source,
            }

        # 3. Resolve Density provenance & source
        dens_prov = input_provenance.get("density_crystalline_g_cm3") or input_provenance.get("density_amorphous_g_cm3")
        if isinstance(dens_prov, dict):
            density_source = str(dens_prov.get("source") or data.get("density_source", ""))
            density_status = str(dens_prov.get("status", "USER_PROVIDED")).upper()
        else:
            raw_dens_source = data.get("density_source")
            if raw_dens_source is not None and str(raw_dens_source).strip() != "":
                density_source = str(raw_dens_source).strip()
                density_status = "EXPERIMENTAL" if density_source.lower() in ("experimental", "pycnometry", "helium_pycnometry") else "USER_PROVIDED"
            else:
                density_source = ""
                density_status = "USER_PROVIDED"
            input_provenance["density_crystalline_g_cm3"] = {
                "value": density_crystalline_g_cm3,
                "unit": "g/cm3",
                "status": density_status,
                "source": density_source or "user_entered",
            }

        # 4. Resolve HSP provenance & source
        hsp_prov = input_provenance.get("hsp_delta_d") or input_provenance.get("hsp")
        if isinstance(hsp_prov, dict):
            hsp_source = str(hsp_prov.get("source") or hsp_prov.get("method") or data.get("hsp_source", ""))
            hsp_status = str(hsp_prov.get("status", "CALCULATED")).upper()
        else:
            raw_hsp_source = data.get("hsp_source")
            if raw_hsp_source is not None and str(raw_hsp_source).strip() != "":
                hsp_source = str(raw_hsp_source).strip()
                hsp_status = "CALCULATED" if any(k in hsp_source.lower() for k in ("fedors", "hvk", "group_contribution", "calculated")) else (
                    "EXPERIMENTAL" if hsp_source.lower() == "experimental" else "USER_PROVIDED"
                )
            else:
                hsp_source = ""
                hsp_status = "USER_PROVIDED"
            for f, val in (("hsp_delta_d", hsp_delta_d), ("hsp_delta_p", hsp_delta_p), ("hsp_delta_h", hsp_delta_h)):
                input_provenance[f] = {
                    "value": val,
                    "unit": "MPa^0.5",
                    "status": hsp_status,
                    "source": hsp_source or "user_entered",
                }

        # 5. Molar Volume
        if molar_volume_cm3_mol is not None and "molar_volume_cm3_mol" not in input_provenance:
            mv_source = str(data.get("molar_volume_source", "user_entered"))
            mv_status = "CALCULATED" if any(k in mv_source.lower() for k in ("fedors", "calculated", "group_contribution")) else "USER_PROVIDED"
            input_provenance["molar_volume_cm3_mol"] = {
                "value": molar_volume_cm3_mol,
                "unit": "cm3/mol",
                "status": mv_status,
                "source": mv_source,
            }

        # 6. Ro
        if hsp_ro is not None and "hsp_ro" not in input_provenance:
            ro_source = str(data.get("hsp_ro_source", "user_entered"))
            input_provenance["hsp_ro"] = {
                "value": hsp_ro,
                "unit": "MPa^0.5",
                "status": "USER_PROVIDED",
                "source": ro_source,
            }

        checksum = generate_sha256(data)

        return cls(
            drug_id=drug_id,
            generic_name=generic_name,
            canonical_smiles=smiles,
            inchi_key=inchi_key,
            molecular_weight_g_mol=float(mw),
            tm_k=tm_k,
            tm_source=tm_source,
            tg_k=tg_k,
            tg_k_estimated=float(tg_k_estimated),
            tg_source=tg_source,
            density_crystalline_g_cm3=density_crystalline_g_cm3,
            density_amorphous_g_cm3=density_amorphous_g_cm3,
            density_source=density_source,
            pka=float(data["pka"]) if data.get("pka") is not None else None,
            logp=float(logp),
            logd_ph74=float(data["logd_ph74"]) if data.get("logd_ph74") is not None else None,
            hbd=int(hbd),
            hba=int(hba),
            tpsa_angstrom2=float(tpsa),
            rotatable_bonds=int(rotb),
            aromatic_rings=int(arom),
            hsp_delta_d=hsp_delta_d,
            hsp_delta_p=hsp_delta_p,
            hsp_delta_h=hsp_delta_h,
            hsp_ro=hsp_ro,
            hsp_source=hsp_source,
            molar_volume_cm3_mol=molar_volume_cm3_mol,
            delta_h_fus_kj_mol=float(data["delta_h_fus_kj_mol"]) if data.get("delta_h_fus_kj_mol") is not None else None,
            bcs_class=str(data.get("bcs_class", "II")),
            polymorphs=polymorphs,
            ionisation_state=str(data.get("ionisation_state", "neutral")),
            data_quality_score=float(data.get("data_quality_score", 1.0)),
            validation_status=str(data.get("validation_status", "validated")),
            input_provenance=input_provenance,
            checksum_sha256=checksum,
        )

    @classmethod
    def from_json(cls, path: Union[str, Path]) -> "Drug":
        """Load drug profile from JSON file."""
        path = Path(path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def estimate_tg(self) -> float:
        """Return experimental Tg if available, else Boyer-Beaman estimate."""
        return self.tg_k if self.tg_k is not None else self.tg_k_estimated

    def get_preferred_density(self) -> Tuple[float, str]:
        """Return amorphous density if available, else crystalline density with systematic bias flag."""
        if self.density_amorphous_g_cm3 is not None:
            return self.density_amorphous_g_cm3, "amorphous"
        return self.density_crystalline_g_cm3, "crystalline_systematic_bias_flag"

    def validate_plausibility(self) -> List[str]:
        """Check plausibility rules per SAS V1.0 Section 6.1."""
        warnings = []
        if not (300 < self.tm_k < 800):
            warnings.append(f"Melting point Tm ({self.tm_k} K) outside standard 300-800 K range.")
        dens, source = self.get_preferred_density()
        if not (0.8 < dens < 2.0):
            warnings.append(f"Density ({dens} g/cm3) outside standard 0.8-2.0 g/cm3 range.")
        return warnings
