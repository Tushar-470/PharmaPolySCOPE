"""
Drug management API routes.
Provides CRUD operations for drug profiles.
Reference drugs are read-only; user-created drugs can be modified/deleted.
"""

from dataclasses import asdict
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Union

from backend.models.schemas import DrugProfileCreate, DrugProfileResponse, ValidationResult
from backend.services import engine_adapter
from backend.services.validation import validate_drug_input
from asd_mcda.integration.input_adapter import InputGeneratorAdapter

router = APIRouter(prefix="/api/drugs", tags=["Drugs"])


@router.get("", response_model=List[DrugProfileResponse])
async def list_drugs(core_only: bool = False):
    """List all available drug profiles (reference + user-created). If core_only=True, return only active core cohort."""
    return engine_adapter.list_drugs(core_only=core_only)


@router.get("/{drug_id}", response_model=DrugProfileResponse)
async def get_drug(drug_id: str):
    """Get a single drug profile by ID."""
    drug = engine_adapter.get_drug(drug_id)
    if drug is None:
        raise HTTPException(status_code=404, detail=f"Drug profile '{drug_id}' not found.")
    return drug


@router.post("", response_model=DrugProfileResponse, status_code=201)
async def create_drug(drug: DrugProfileCreate):
    """Create a new user drug profile."""
    existing = engine_adapter.get_drug(drug.drug_id)
    if existing is not None:
        raise HTTPException(status_code=409, detail=f"Drug ID '{drug.drug_id}' already exists.")

    data = drug.model_dump()
    saved = engine_adapter.save_drug(data)
    return saved


@router.post("/import-generator-export", response_model=Union[DrugProfileResponse, List[DrugProfileResponse]], status_code=201)
async def import_generator_export(payload: Dict[str, Any]):
    """Import and normalize a drug export (or multi-record dataset) from PharmaPolySCOPE Input Generator."""
    try:
        if "records" in payload:
            drugs = InputGeneratorAdapter.load_from_json(payload)
            if not isinstance(drugs, list):
                drugs = [drugs]
            saved_list = []
            for d in drugs:
                d_dict = asdict(d)
                saved = engine_adapter.save_drug(d_dict)
                saved_list.append(saved)
            return saved_list
        else:
            drug = InputGeneratorAdapter.load_drug_from_dict(payload)
            d_dict = asdict(drug)
            saved = engine_adapter.save_drug(d_dict)
            return saved
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/validate", response_model=ValidationResult)
async def validate_drug(drug: DrugProfileCreate):
    """Validate drug profile data without saving."""
    data = drug.model_dump()
    status, errors, warnings = validate_drug_input(data)
    return ValidationResult(status=status, errors=errors, warnings=warnings)


@router.delete("/{drug_id}")
async def delete_drug(drug_id: str):
    """Delete a user-created drug profile. Reference drugs cannot be deleted."""
    drug = engine_adapter.get_drug(drug_id)
    if drug is None:
        raise HTTPException(status_code=404, detail=f"Drug '{drug_id}' not found.")
    if drug.get("is_reference", True):
        raise HTTPException(status_code=403, detail="Cannot delete reference drug profiles.")

    deleted = engine_adapter.delete_drug(drug_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete drug profile.")
    return {"message": f"Drug '{drug_id}' deleted successfully."}
