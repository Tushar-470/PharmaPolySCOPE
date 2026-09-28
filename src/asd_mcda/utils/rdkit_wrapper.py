"""
RDKit wrapper providing canonicalization, 2D descriptor calculations, and group contribution estimates.
Handles graceful fallback if RDKit is missing or parsing fails.
"""

import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Attempt to import RDKit
try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, inchi, rdMolDescriptors
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    logger.warning("RDKit is not installed. Using fallback descriptor calculations.")


def is_rdkit_available() -> bool:
    """Return True if RDKit is installed and available."""
    return RDKIT_AVAILABLE


def canonicalize_smiles(smiles: str) -> str:
    """Canonicalize a SMILES string using RDKit if available, else return cleaned string."""
    if not smiles or not smiles.strip():
        raise ValueError("SMILES string cannot be empty.")
    
    clean_smiles = smiles.strip()
    if RDKIT_AVAILABLE:
        mol = Chem.MolFromSmiles(clean_smiles)
        if mol is None:
            logger.warning(f"RDKit failed to parse SMILES: {clean_smiles}")
            return clean_smiles
        return Chem.MolToSmiles(mol, canonical=True)
    return clean_smiles


def get_inchi_key(smiles: str) -> str:
    """Derive InChIKey from SMILES string."""
    if RDKIT_AVAILABLE:
        mol = Chem.MolFromSmiles(smiles)
        if mol is not None:
            return inchi.MolToInchiKey(mol)
    return "UNKNOWN_INCHI_KEY"


def _fallback_2d_descriptors(smiles: str) -> Dict[str, float]:
    """Historical fallback descriptor dictionary for regression comparison only.
    Prohibited in production execution.
    """
    return {
        "MolWt": 350.0,
        "MolLogP": 3.0,
        "TPSA": 60.0,
        "NumHDonors": 2,
        "NumHAcceptors": 4,
        "NumRotatableBonds": 4,
        "NumAromaticRings": 2,
        "FractionalTPSA": 60.0 / 350.0,
    }


def compute_2d_descriptors(smiles: str) -> Dict[str, float]:
    """
    Compute 2D molecular descriptors via RDKit.
    Returns dictionary with: MolWt, MolLogP, TPSA, NumHDonors, NumHAcceptors,
    NumRotatableBonds, NumAromaticRings, FractionalTPSA.
    """
    clean_smiles = canonicalize_smiles(smiles)
    
    if not RDKIT_AVAILABLE:
        raise RuntimeError(
            "RDKit is required for molecular descriptor calculations. "
            "Silent fallback dummy descriptors are prohibited in production."
        )

    mol = Chem.MolFromSmiles(clean_smiles)
    if mol is None:
        raise ValueError(f"RDKit failed to parse chemical structure from SMILES: '{clean_smiles}'.")

    mw = Descriptors.MolWt(mol)
    tpsa = Descriptors.TPSA(mol)
    logp = Descriptors.MolLogP(mol)
    hbd = Descriptors.NumHDonors(mol)
    hba = Descriptors.NumHAcceptors(mol)
    rotb = Descriptors.NumRotatableBonds(mol)
    arom = rdMolDescriptors.CalcNumAromaticRings(mol)
    frac_tpsa = tpsa / mw if mw > 0 else 0.0

    return {
        "MolWt": float(mw),
        "MolLogP": float(logp),
        "TPSA": float(tpsa),
        "NumHDonors": int(hbd),
        "NumHAcceptors": int(hba),
        "NumRotatableBonds": int(rotb),
        "NumAromaticRings": int(arom),
        "FractionalTPSA": float(frac_tpsa),
    }


def hoftyzer_van_krevelen_hsp(smiles: str, molar_volume: Optional[float] = None) -> Tuple[float, float, float]:
    """
    Estimate Hansen Solubility Parameters (delta_D, delta_P, delta_H) via Hoftyzer-Van Krevelen group contribution.
    Hardcoded string-matching and arbitrary dummy values are strictly prohibited in production.
    """
    raise ValueError(
        "Hoftyzer-Van Krevelen calculation requires group contribution decomposition or "
        "upstream Input Generator values. Hardcoded fallback HSPs are prohibited."
    )
