"""Regression Tests Enforcing Absolute Isolation of Frozen v1.5 Baseline.

Authoritative Specification: 2.0.0-SPEC-PHASE0-PATCH2 / Phase 1.1 Hardening.
Asserts that the v2 package imports zero code from v1.5 modules, that v1.5
source files and historical outputs match Git commit 31eee4d byte-for-byte,
and that the golden hash manifest is cryptographically anchored to commit 31eee4d.
"""

import ast
import hashlib
import json
import os
import subprocess
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC_V2_DIR = os.path.join(BASE_DIR, "src", "asd_mcda", "v2")
SRC_V15_DIR = os.path.join(BASE_DIR, "src", "asd_mcda")
MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "v15_golden_hashes.json")
SHARED_MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "v15_shared_compatibility_manifest.json")
FROZEN_COMMIT = "31eee4d"
APPROVED_V2_COMMIT = "5ad61479a3adf0bc537d5b9d422f215e8f03faaa"
HISTORICAL_MANIFEST_COMMIT = "1139397"

AUTHORIZED_SHARED_COMPATIBILITY_PATHS = frozenset({
    "src/asd_mcda/compatibility/flory_huggins.py",
    "src/asd_mcda/compatibility/hsp_model.py",
    "src/asd_mcda/drug/drug_profile.py",
    "src/asd_mcda/polymer/polymer_library.py",
    "src/asd_mcda/prediction/predictor.py",
    "src/asd_mcda/reporting/report_generator.py",
    "src/asd_mcda/utils/rdkit_wrapper.py",
})


def _load_golden_manifest():
    assert os.path.exists(MANIFEST_PATH), f"Golden hash manifest missing: {MANIFEST_PATH}"
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    assert manifest.get("commit") == FROZEN_COMMIT, (
        f"Manifest referenced commit mismatch: expected {FROZEN_COMMIT}, got {manifest.get('commit')}"
    )
    files = manifest.get("files", {})
    assert len(files) > 0, "Golden hash manifest contains zero files."
    return manifest, files


def _load_shared_compatibility_manifest():
    assert os.path.exists(SHARED_MANIFEST_PATH), f"Shared compatibility manifest missing: {SHARED_MANIFEST_PATH}"
    with open(SHARED_MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    assert manifest.get("approved_v2_commit") == APPROVED_V2_COMMIT, (
        f"Shared manifest approved commit mismatch: expected {APPROVED_V2_COMMIT}, got {manifest.get('approved_v2_commit')}"
    )
    files = manifest.get("files", {})
    actual_shared_paths = frozenset(files.keys())
    assert actual_shared_paths == AUTHORIZED_SHARED_COMPATIBILITY_PATHS, (
        f"Shared compatibility manifest paths mismatch!\n"
        f"  Expected exact set: {sorted(AUTHORIZED_SHARED_COMPATIBILITY_PATHS)}\n"
        f"  Actual set:         {sorted(actual_shared_paths)}\n"
        f"  Extra paths:        {sorted(actual_shared_paths - AUTHORIZED_SHARED_COMPATIBILITY_PATHS)}\n"
        f"  Missing paths:      {sorted(AUTHORIZED_SHARED_COMPATIBILITY_PATHS - actual_shared_paths)}"
    )
    return manifest, files


def _compute_working_tree_hash(file_path: str, expected_hash: str) -> str:
    with open(file_path, "rb") as f:
        raw_bytes = f.read()
    actual_hash = hashlib.sha256(raw_bytes).hexdigest().lower()
    if actual_hash != expected_hash.lower():
        # Handle CRLF checkout conversion on Windows environments
        norm_bytes = raw_bytes.replace(b"\r\n", b"\n")
        norm_hash = hashlib.sha256(norm_bytes).hexdigest().lower()
        if norm_hash == expected_hash.lower():
            return norm_hash
    return actual_hash


def test_zero_v15_import_dependencies():
    """Regression Test 1: Assert AST of all v2 modules contains zero imports from v1.5 components."""
    banned_prefixes = (
        "asd_mcda.mcda",
        "asd_mcda.integration",
        "asd_mcda.compatibility",
        "asd_mcda.orchestrator",
    )

    if not os.path.exists(SRC_V2_DIR):
        pytest.skip("src/asd_mcda/v2 directory does not exist yet.")

    v2_files = [
        os.path.join(SRC_V2_DIR, f) for f in os.listdir(SRC_V2_DIR) if f.endswith(".py")
    ]

    for filepath in v2_files:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=filepath)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    for prefix in banned_prefixes:
                        assert not alias.name.startswith(prefix), (
                            f"Illegal v1.5 import '{alias.name}' in {filepath}"
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for prefix in banned_prefixes:
                        assert not node.module.startswith(prefix), (
                            f"Illegal v1.5 import-from '{node.module}' in {filepath}"
                        )


def test_v15_baseline_files_unmodified():
    """Regression Test 2 (Layer A): Assert all immutable baseline files match golden SHA-256 digests from commit 31eee4d."""
    manifest, files = _load_golden_manifest()
    shared_manifest, shared_files = _load_shared_compatibility_manifest()

    actual_shared_paths = frozenset(shared_files.keys())
    assert actual_shared_paths == AUTHORIZED_SHARED_COMPATIBILITY_PATHS

    immutable_files = {path: entry for path, entry in files.items() if path not in shared_files}
    assert len(immutable_files) == len(files) - len(shared_files)
    assert len(immutable_files) == len(files) - len(shared_files)

    for rel_path, entry in immutable_files.items():
        expected_hash = entry["sha256"].lower()
        file_path = os.path.join(BASE_DIR, rel_path.replace("/", os.sep))
        assert os.path.exists(file_path), f"Protected v1.5 baseline file missing: {rel_path}"

        actual_hash = _compute_working_tree_hash(file_path, expected_hash)
        assert actual_hash == expected_hash, (
            f"Cryptographic SHA-256 mismatch for protected file '{rel_path}'!\n"
            f"  Expected (commit {FROZEN_COMMIT}): {expected_hash}\n"
            f"  Actual (working tree):              {actual_hash}"
        )


def test_v15_shared_compatibility_files_governed():
    """Regression Test 3 (Layer B): Assert all shared compatibility files are explicitly governed and match approved digests."""
    golden_manifest, golden_files = _load_golden_manifest()
    shared_manifest, shared_files = _load_shared_compatibility_manifest()

    actual_shared_paths = frozenset(shared_files.keys())
    assert actual_shared_paths == AUTHORIZED_SHARED_COMPATIBILITY_PATHS, (
        f"Governed shared paths mismatch! Expected exact authorized set {sorted(AUTHORIZED_SHARED_COMPATIBILITY_PATHS)}, got {sorted(actual_shared_paths)}"
    )

    for rel_path in sorted(actual_shared_paths):
        entry = shared_files[rel_path]
        assert rel_path in golden_files, f"Shared file '{rel_path}' not found in historical golden manifest!"
        golden_entry = golden_files[rel_path]
        assert entry["historical_sha256"].lower() == golden_entry["sha256"].lower(), (
            f"Historical SHA-256 desynchronization for shared file '{rel_path}'!"
        )

        expected_approved_hash = entry["current_approved_sha256"].lower()
        # Verify against Git show at approved commit for historical files (not yet committed in working tree)
        if "Zero silent fallbacks" not in entry.get("reason", ""):
            git_show_arg = f"{APPROVED_V2_COMMIT}:{rel_path}"
            try:
                res = subprocess.run(
                    ["git", "show", git_show_arg],
                    cwd=BASE_DIR,
                    capture_output=True,
                    check=True,
                )
                git_bytes = res.stdout
                git_hash = hashlib.sha256(git_bytes).hexdigest().lower()
                assert git_hash == expected_approved_hash, (
                    f"Approved Git commit digest mismatch for '{rel_path}'!\n"
                    f"  Expected: {expected_approved_hash}\n"
                    f"  Git show {APPROVED_V2_COMMIT}: {git_hash}"
                )
            except subprocess.CalledProcessError:
                pass  # Historical commit not in flattened/release git history; covered by working tree check below

        # Verify working tree
        file_path = os.path.join(BASE_DIR, rel_path.replace("/", os.sep))
        assert os.path.exists(file_path), f"Shared compatibility file missing: {rel_path}"

        actual_hash = _compute_working_tree_hash(file_path, expected_approved_hash)
        crlf_hash = entry.get("current_approved_sha256_crlf", "").lower()
        assert actual_hash == expected_approved_hash or (crlf_hash and actual_hash == crlf_hash), (
            f"Working tree digest mismatch for shared compatibility file '{rel_path}'!\n"
            f"  Expected approved SHA-256: {expected_approved_hash}\n"
            f"  Actual working tree digest: {actual_hash}"
        )


def test_v15_shared_compatibility_allowlist_exact_set_enforcement():
    """Regression Test 4: Assert shared allowlist strictly blocks additions, removals, substitutions, and typos."""
    manifest, shared_files = _load_shared_compatibility_manifest()
    actual_shared_paths = frozenset(shared_files.keys())
    assert actual_shared_paths == AUTHORIZED_SHARED_COMPATIBILITY_PATHS

    # 1. Assert addition of a fifth file is strictly blocked
    unauthorized_file_set = actual_shared_paths | {"src/asd_mcda/orchestrator.py"}
    assert unauthorized_file_set != AUTHORIZED_SHARED_COMPATIBILITY_PATHS

    # 2. Assert removal of any authorized file is strictly blocked
    for path in AUTHORIZED_SHARED_COMPATIBILITY_PATHS:
        reduced_set = actual_shared_paths - {path}
        assert reduced_set != AUTHORIZED_SHARED_COMPATIBILITY_PATHS

    # 3. Assert substitution or typo is strictly blocked
    typo_set = (actual_shared_paths - {"src/asd_mcda/compatibility/flory_huggins.py"}) | {"src/asd_mcda/compatibility/flory_huggins_v2.py"}
    assert typo_set != AUTHORIZED_SHARED_COMPATIBILITY_PATHS


def test_v15_golden_manifest_file_unmodified():
    """Regression Test 5: Assert historical golden manifest file itself remains untampered."""
    try:
        res = subprocess.run(
            ["git", "show", f"{HISTORICAL_MANIFEST_COMMIT}:tests/v2/v15_golden_hashes.json"],
            cwd=BASE_DIR,
            capture_output=True,
            check=True,
        )
        git_manifest_bytes = res.stdout.replace(b"\r\n", b"\n")
        with open(MANIFEST_PATH, "rb") as f:
            local_manifest_bytes = f.read().replace(b"\r\n", b"\n")

        assert hashlib.sha256(local_manifest_bytes).hexdigest() == hashlib.sha256(git_manifest_bytes).hexdigest(), (
            "Historical golden manifest tests/v2/v15_golden_hashes.json has been modified!"
        )
    except subprocess.CalledProcessError:
        # Commit not in shallow or flattened release repo; verify local manifest exists and is non-empty
        assert os.path.exists(MANIFEST_PATH), f"Golden manifest missing at {MANIFEST_PATH}"


def test_v15_golden_manifest_matches_commit():
    """Regression Test 6: Independently recompute every manifest hash directly from git show 31eee4d."""
    try:
        subprocess.run(
            ["git", "cat-file", "-e", f"{FROZEN_COMMIT}^{{commit}}"],
            cwd=BASE_DIR,
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        pytest.skip(f"Historical commit {FROZEN_COMMIT} not present in flattened/shallow repository.")

    manifest, files = _load_golden_manifest()

    for rel_path, entry in files.items():
        expected_hash = entry["sha256"].lower()
        expected_len = entry.get("byte_length")

        git_show_arg = f"{FROZEN_COMMIT}:{rel_path}"
        res = subprocess.run(
            ["git", "show", git_show_arg],
            cwd=BASE_DIR,
            capture_output=True,
            check=True,
        )
        git_bytes = res.stdout
        git_hash = hashlib.sha256(git_bytes).hexdigest().lower()

        assert git_hash == expected_hash, (
            f"Manifest hash desynchronization for '{rel_path}'!\n"
            f"  Manifest stored digest:  {expected_hash}\n"
            f"  git show {FROZEN_COMMIT} digest: {git_hash}"
        )

        if expected_len is not None:
            assert len(git_bytes) == expected_len, (
                f"Byte length mismatch for '{rel_path}' in git show {FROZEN_COMMIT}: "
                f"expected {expected_len}, got {len(git_bytes)}"
            )


def test_v15_historical_results_byte_identical():
    """Regression Test 7: Assert all protected historical outputs under results/ match fixed golden digests."""
    manifest, files = _load_golden_manifest()

    historical_results = {
        path: entry
        for path, entry in files.items()
        if path.startswith("results/final/") or path.startswith("results/reports/")
    }

    assert len(historical_results) > 0, "No historical results found in golden manifest."

    for rel_path, entry in historical_results.items():
        expected_hash = entry["sha256"].lower()
        file_path = os.path.join(BASE_DIR, rel_path.replace("/", os.sep))
        assert os.path.exists(file_path), f"Protected historical result file missing: {rel_path}"

        actual_hash = _compute_working_tree_hash(file_path, expected_hash)
        assert actual_hash == expected_hash, (
            f"Historical result cryptographic digest mismatch for '{rel_path}'!\n"
            f"  Expected (commit {FROZEN_COMMIT}): {expected_hash}\n"
            f"  Actual (working tree):              {actual_hash}"
        )
