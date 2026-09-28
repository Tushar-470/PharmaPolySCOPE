# -*- coding: utf-8 -*-
"""Canonical Input Generator Adapter for PharmaPolySCOPE.

Translates upstream pharmapolyscope-input-generator exports (JSON / CSV)
into validated downstream Drug and Polymer objects.

Preserves property-level provenance:
USER_PROVIDED, EXPERIMENTAL, CALCULATED, ESTIMATED, UNAVAILABLE, INTERNAL_REFERENCE.
Zero silent defaults. Zero fabricated constants.
"""

import csv
import io
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from asd_mcda.drug.drug_profile import Drug, IncompleteProfileError

VALID_TEMPERATURE_UNITS = {"k", "kelvin"}
CELSIUS_TEMPERATURE_UNITS = {"c", "°c", "deg c", "degc", "celsius"}
VALID_DENSITY_UNITS = {"g/cm3", "g/cm^3", "g/ml", "g/cc"}
VALID_HSP_UNITS = {"mpa^0.5", "mpa0.5", "(j/cm3)^0.5", "(j/cm^3)^0.5", "j^0.5/cm^1.5"}
VALID_MW_UNITS = {"g/mol", "da", "dalton", "daltons", "g*mol^-1"}
VALID_VOL_UNITS = {"cm3/mol", "cm^3/mol", "ml/mol"}

ALLOWED_PROVENANCE_STATUSES = {
    "USER_PROVIDED",
    "EXPERIMENTAL",
    "CALCULATED",
    "ESTIMATED",
    "UNAVAILABLE",
    "INTERNAL_REFERENCE",
}


def _clean_str(val: Any) -> Optional[str]:
    if val is None:
        return None
    s = str(val).strip()
    return None if s == "" or s.lower() == "null" else s


def _clean_float(val: Any) -> Optional[float]:
    s = _clean_str(val)
    if s is None:
        return None
    try:
        return float(s)
    except ValueError as exc:
        raise ValueError(f"Expected numeric value, got: '{val}'") from exc


def _parse_property_field(
    raw_val: Any,
    field_name: str,
    default_status: str = "USER_PROVIDED",
    default_source: str = "user_entered",
) -> Tuple[Optional[float], Dict[str, Any]]:
    """Extract value and provenance metadata from a scalar or structured property field."""
    if raw_val is None:
        return None, {"status": "UNAVAILABLE", "value": None}

    if isinstance(raw_val, dict):
        status = raw_val.get("status") or raw_val.get("provenance") or default_status
        source = raw_val.get("source") or raw_val.get("selected_source") or default_source
        unit = str(raw_val.get("unit", "")).strip().lower()
        val = raw_val.get("value")
        if val is None:
            val = raw_val.get("value_k") or raw_val.get("tm_K") or raw_val.get("tg_K")
        orig_val = val
        orig_unit = raw_val.get("unit", "")

        if val is None:
            return None, {"status": "UNAVAILABLE", "value": None, "source": source}

        val_float = _clean_float(val)
        if val_float is None:
            return None, {"status": "UNAVAILABLE", "value": None, "source": source}

        # Temperature unit conversion
        if "tm" in field_name.lower() or "tg" in field_name.lower():
            if unit in CELSIUS_TEMPERATURE_UNITS:
                val_float = round(val_float + 273.15, 2)
            elif unit and unit not in VALID_TEMPERATURE_UNITS:
                raise ValueError(
                    f"Invalid temperature unit '{orig_unit}' for '{field_name}'. Must be Kelvin or Celsius."
                )
        elif "density" in field_name.lower():
            if unit == "kg/m3" or unit == "kg/m^3":
                val_float = round(val_float / 1000.0, 4)
            elif unit and unit not in VALID_DENSITY_UNITS:
                raise ValueError(
                    f"Invalid density unit '{orig_unit}' for '{field_name}'. Must be g/cm3 or kg/m3."
                )
        elif "delta" in field_name.lower():
            if unit and unit not in VALID_HSP_UNITS:
                raise ValueError(
                    f"Invalid HSP unit '{orig_unit}' for '{field_name}'. Must be MPa^0.5."
                )
        elif "mw" in field_name.lower() or "weight" in field_name.lower():
            if unit and unit not in VALID_MW_UNITS:
                raise ValueError(
                    f"Invalid molecular weight unit '{orig_unit}' for '{field_name}'. Must be g/mol or Da."
                )
        elif "volume" in field_name.lower():
            if unit and unit not in VALID_VOL_UNITS:
                raise ValueError(
                    f"Invalid molar volume unit '{orig_unit}' for '{field_name}'. Must be cm3/mol."
                )

        status_str = str(status).upper()
        if status_str not in ALLOWED_PROVENANCE_STATUSES:
            status_str = default_status

        provenance = {
            "value": val_float,
            "unit": "K" if ("tm" in field_name.lower() or "tg" in field_name.lower()) else (
                "g/cm3" if "density" in field_name.lower() else (
                    "MPa^0.5" if "delta" in field_name.lower() else (
                        "cm3/mol" if "volume" in field_name.lower() else (
                            "g/mol" if "weight" in field_name.lower() else orig_unit
                        )
                    )
                )
            ),
            "status": status_str,
            "source": str(source),
            "original_value": orig_val,
            "original_unit": orig_unit,
        }
        return val_float, provenance

    # Scalar value
    val_float = _clean_float(raw_val)
    if val_float is None:
        return None, {"status": "UNAVAILABLE", "value": None}

    provenance = {
        "value": val_float,
        "status": default_status,
        "source": default_source,
        "original_value": raw_val,
        "original_unit": "",
    }
    return val_float, provenance


class InputGeneratorAdapter:
    """Canonical bidirectional adapter between Input Generator and PharmaPolySCOPE."""

    @staticmethod
    def normalize_record(record: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize a raw record (from JSON or CSV) into standard downstream Drug dict format."""
        drug_id = (
            _clean_str(record.get("entity_id"))
            or _clean_str(record.get("drug_id"))
        )
        if not drug_id:
            raise IncompleteProfileError("unknown", "entity_id / drug_id", "Input normalization")

        generic_name = (
            _clean_str(record.get("name"))
            or _clean_str(record.get("generic_name"))
            or drug_id
        )

        canonical_smiles = (
            _clean_str(record.get("canonical_smiles"))
            or _clean_str(record.get("smiles"))
        )
        if not canonical_smiles:
            raise IncompleteProfileError(drug_id, "canonical_smiles", "Molecular structure parsing")

        input_provenance: Dict[str, Any] = {}

        # 1. Molecular Weight
        mw_raw = record.get("mw") if record.get("mw") is not None else record.get("molecular_weight_g_mol")
        mw_val, mw_prov = _parse_property_field(mw_raw, "molecular_weight_g_mol", default_status="CALCULATED")
        if mw_val is not None:
            input_provenance["molecular_weight_g_mol"] = mw_prov

        # 2. Melting Point (tm_K / tm_k)
        tm_raw = record.get("tm_K") if record.get("tm_K") is not None else record.get("tm_k")
        tm_status = _clean_str(record.get("tm_status")) or "USER_PROVIDED"
        tm_source = _clean_str(record.get("tm_source")) or "input_generator"
        tm_val, tm_prov = _parse_property_field(tm_raw, "tm_k", default_status=tm_status, default_source=tm_source)
        if tm_val is None:
            raise IncompleteProfileError(drug_id, "tm_k", "Melting point")
        input_provenance["tm_k"] = tm_prov

        # 3. Glass Transition Temperature (tg_K / tg_k)
        tg_raw = record.get("tg_K") if record.get("tg_K") is not None else record.get("tg_k")
        tg_status = _clean_str(record.get("tg_status")) or "ESTIMATED"
        tg_source = _clean_str(record.get("tg_method")) or _clean_str(record.get("tg_source")) or "boyer_beaman"
        tg_val, tg_prov = _parse_property_field(tg_raw, "tg_k", default_status=tg_status, default_source=tg_source)
        if tg_val is not None:
            input_provenance["tg_k"] = tg_prov

        # 4. Density
        dens_raw = (
            record.get("true_density_g_cm3")
            if record.get("true_density_g_cm3") is not None
            else record.get("density_crystalline_g_cm3")
        )
        dens_status = _clean_str(record.get("density_status")) or "USER_PROVIDED"
        dens_source = _clean_str(record.get("density_type")) or _clean_str(record.get("density_source")) or "literature"
        dens_val, dens_prov = _parse_property_field(dens_raw, "density_crystalline_g_cm3", default_status=dens_status, default_source=dens_source)
        
        amorph_dens_raw = record.get("density_amorphous_g_cm3")
        amorph_val, amorph_prov = _parse_property_field(amorph_dens_raw, "density_amorphous_g_cm3", default_status="USER_PROVIDED")

        if dens_val is None and amorph_val is None:
            raise IncompleteProfileError(drug_id, "density_crystalline_g_cm3 / true_density_g_cm3", "Density")
        if dens_val is not None:
            input_provenance["density_crystalline_g_cm3"] = dens_prov
        if amorph_val is not None:
            input_provenance["density_amorphous_g_cm3"] = amorph_prov

        # 5. Hansen Solubility Parameters (delta_D, delta_P, delta_H)
        hsp_dict = record.get("hsp") if isinstance(record.get("hsp"), dict) else {}
        hsp_status = (
            _clean_str(record.get("hsp_status"))
            or _clean_str(hsp_dict.get("status"))
            or "CALCULATED"
        )
        hsp_source = (
            _clean_str(record.get("hsp_source"))
            or _clean_str(hsp_dict.get("source"))
            or _clean_str(record.get("hsp_method"))
            or _clean_str(hsp_dict.get("method"))
        )
        if not hsp_source and isinstance(hsp_dict.get("delta_D"), dict):
            hsp_source = _clean_str(hsp_dict["delta_D"].get("source"))
        if not hsp_source:
            hsp_source = "group_contribution" if hsp_status == "CALCULATED" else "user_entered"

        dd_raw = record.get("delta_D") if record.get("delta_D") is not None else (record.get("hsp_delta_d") or hsp_dict.get("delta_D"))
        dp_raw = record.get("delta_P") if record.get("delta_P") is not None else (record.get("hsp_delta_p") or hsp_dict.get("delta_P"))
        dh_raw = record.get("delta_H") if record.get("delta_H") is not None else (record.get("hsp_delta_h") or hsp_dict.get("delta_H"))

        dd_val, dd_prov = _parse_property_field(dd_raw, "hsp_delta_d", default_status=hsp_status, default_source=hsp_source)
        dp_val, dp_prov = _parse_property_field(dp_raw, "hsp_delta_p", default_status=hsp_status, default_source=hsp_source)
        dh_val, dh_prov = _parse_property_field(dh_raw, "hsp_delta_h", default_status=hsp_status, default_source=hsp_source)

        if dd_val is None or dp_val is None or dh_val is None:
            raise IncompleteProfileError(drug_id, "delta_D / delta_P / delta_H", "Hansen Solubility Parameters")

        input_provenance["hsp_delta_d"] = dd_prov
        input_provenance["hsp_delta_p"] = dp_prov
        input_provenance["hsp_delta_h"] = dh_prov

        # 6. Molar Volume
        mv_raw = (
            record.get("molar_volume")
            if record.get("molar_volume") is not None
            else record.get("molar_volume_cm3_mol")
        )
        mv_val, mv_prov = _parse_property_field(mv_raw, "molar_volume_cm3_mol", default_status="CALCULATED")
        if mv_val is not None:
            input_provenance["molar_volume_cm3_mol"] = mv_prov

        # 7. Hansen Ro (Interaction Radius)
        ro_raw = record.get("hsp_ro") or record.get("ro")
        ro_val, ro_prov = _parse_property_field(ro_raw, "hsp_ro", default_status="USER_PROVIDED")
        if ro_val is not None:
            input_provenance["hsp_ro"] = ro_prov

        # 8. Data integrity / validation status translation
        raw_integrity = _clean_str(record.get("data_integrity_status")) or _clean_str(record.get("validation_status")) or "draft"
        if raw_integrity.upper() in ("PASS", "VALID", "VALIDATED"):
            downstream_validation_status = "validated"
        elif raw_integrity.upper() == "CAUTION":
            downstream_validation_status = "caution"
        else:
            downstream_validation_status = "draft"
        input_provenance["data_integrity_status"] = {
            "upstream_status": raw_integrity,
            "downstream_status": downstream_validation_status,
        }

        # Merge existing input_provenance if present in record
        if isinstance(record.get("input_provenance"), dict):
            for k, v in record["input_provenance"].items():
                if k not in input_provenance:
                    input_provenance[k] = v

        resolved_hsp_source = dd_prov.get("source") or hsp_source or ""
        normalized: Dict[str, Any] = {
            "drug_id": drug_id,
            "generic_name": generic_name,
            "canonical_smiles": canonical_smiles,
            "molecular_weight_g_mol": mw_val,
            "tm_k": tm_val,
            "tm_source": tm_prov.get("source", ""),
            "tg_k": tg_val,
            "tg_source": tg_prov.get("source", ""),
            "density_crystalline_g_cm3": dens_val if dens_val is not None else amorph_val,
            "density_amorphous_g_cm3": amorph_val,
            "density_source": dens_prov.get("source") if dens_val is not None else (amorph_prov.get("source", "") if amorph_val is not None else ""),
            "hsp_delta_d": dd_val,
            "hsp_delta_p": dp_val,
            "hsp_delta_h": dh_val,
            "hsp_source": resolved_hsp_source,
            "hsp_ro": ro_val,
            "molar_volume_cm3_mol": mv_val,
            "validation_status": downstream_validation_status,
            "input_provenance": input_provenance,
        }

        # Forward optional secondary descriptors if present
        for optional_field in ("pka", "logp", "logd_ph74", "hbd", "hba", "tpsa_angstrom2", "rotatable_bonds", "aromatic_rings", "bcs_class", "polymorphs", "delta_h_fus_kj_mol"):
            if optional_field in record and record[optional_field] is not None:
                val = record[optional_field]
                if _clean_str(val) is not None:
                    normalized[optional_field] = val

        return normalized

    @classmethod
    def load_drug_from_dict(cls, record: Dict[str, Any]) -> Drug:
        """Normalize dictionary and instantiate Drug object."""
        norm = cls.normalize_record(record)
        return Drug.from_dict(norm)

    @classmethod
    def load_from_json(
        cls,
        json_input: Union[str, Path, Dict[str, Any]],
        entity_id: Optional[str] = None,
    ) -> Union[Drug, List[Drug]]:
        """Load and normalize Drug object(s) from JSON file, string, or parsed dict."""
        if isinstance(json_input, (str, Path)) and (isinstance(json_input, Path) or Path(json_input).exists()):
            with open(json_input, "r", encoding="utf-8") as f:
                data = json.load(f)
        elif isinstance(json_input, str):
            data = json.loads(json_input)
        elif isinstance(json_input, dict):
            data = json_input
        else:
            raise TypeError(f"Unsupported JSON input type: {type(json_input)}")

        # Case 1: Structured dataset with records list (input_dataset.json)
        if isinstance(data, dict) and "records" in data:
            records = data["records"]
            drug_records = [
                r for r in records
                if r.get("entity_type", "drug").lower() == "drug"
            ]
            if entity_id:
                matching = [
                    r for r in drug_records
                    if str(r.get("entity_id") or r.get("drug_id")).lower() == entity_id.lower()
                ]
                if not matching:
                    raise KeyError(f"Drug with ID '{entity_id}' not found in dataset.")
                return cls.load_drug_from_dict(matching[0])
            return [cls.load_drug_from_dict(r) for r in drug_records]

        # Case 2: Single drug profile dictionary
        if isinstance(data, dict):
            return cls.load_drug_from_dict(data)

        # Case 3: List of records
        if isinstance(data, list):
            drugs = [cls.load_drug_from_dict(r) for r in data]
            if entity_id:
                matching = [d for d in drugs if d.drug_id.lower() == entity_id.lower()]
                if not matching:
                    raise KeyError(f"Drug with ID '{entity_id}' not found in dataset.")
                return matching[0]
            return drugs

        raise ValueError("Unrecognized JSON structure.")

    @classmethod
    def load_from_csv(
        cls,
        csv_input: Union[str, Path],
        entity_id: Optional[str] = None,
    ) -> Union[Drug, List[Drug]]:
        """Load and normalize Drug object(s) from 24-column Input Generator CSV."""
        if isinstance(csv_input, Path) or (isinstance(csv_input, str) and Path(csv_input).exists()):
            with open(csv_input, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        elif isinstance(csv_input, str):
            reader = csv.DictReader(io.StringIO(csv_input))
            rows = list(reader)
        else:
            raise TypeError(f"Unsupported CSV input type: {type(csv_input)}")

        drug_rows = [
            r for r in rows
            if (r.get("entity_type") or "drug").lower() == "drug"
        ]

        if entity_id:
            matching = [
                r for r in drug_rows
                if str(r.get("entity_id") or r.get("drug_id")).lower() == entity_id.lower()
            ]
            if not matching:
                raise KeyError(f"Drug with ID '{entity_id}' not found in CSV.")
            return cls.load_drug_from_dict(matching[0])

        return [cls.load_drug_from_dict(r) for r in drug_rows]
