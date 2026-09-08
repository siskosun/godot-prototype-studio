#!/usr/bin/env python3
"""Check final-artifact release record consistency and hashes; does not run or judge the game."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from _common import deterministic_tree_hash, load_json, sha256_file, should_exclude
from _evidence import local_file
from validate_quality_review import validate_quality

TARGETS = {"LOCAL_PROJECT", "GODOT_PROJECT_ZIP", "DESKTOP_BUILD", "WEB_EXPORT", "ANDROID_BUILD"}
SHARE_MODES = {"LOCAL_WEB_TEST", "LAN_SHARE", "PUBLIC_HOSTED"}
PAIR_KINDS = {"SOURCE_PROJECT", "GODOT_PROJECT_ZIP", "WEB_EXPORT", "DESKTOP_BUILD", "ANDROID_BUILD"}
HEX = re.compile(r"[a-fA-F0-9]{64}\Z")


def _hash_matches(value: Any, actual: str) -> bool:
    return isinstance(value, str) and bool(HEX.fullmatch(value)) and value.lower() == actual.lower()


def _evidence_file(record: Any, base: Path, label: str, errors: list[str]) -> Path | None:
    if not isinstance(record, dict) or not isinstance(record.get("path"), str) or not record["path"].strip():
        errors.append(f"{label}: file path missing")
        return None
    raw = Path(record["path"]).expanduser()
    path = raw if raw.is_absolute() else base / raw
    if path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
        errors.append(f"{label}: symlink evidence is unsupported")
        return None
    if not path.is_file():
        errors.append(f"{label}: missing file {path}")
    elif path.stat().st_size == 0:
        errors.append(f"{label}: empty evidence file {path}")
    elif not _hash_matches(record.get("sha256"), sha256_file(path)):
        errors.append(f"{label}: file hash mismatch")
    else:
        return path
    return None


def _zip_project_members(archive: Path) -> tuple[str, dict[str, zipfile.ZipInfo]]:
    """Return the optional project-root prefix and safe file members for a Godot project ZIP."""
    with zipfile.ZipFile(archive) as bundle:
        members: dict[str, zipfile.ZipInfo] = {}
        for info in bundle.infolist():
            name = info.filename
            path = PurePosixPath(name)
            mode = info.external_attr >> 16
            if (not name or "\\" in name or path.is_absolute() or
                    any(part in {"..", "."} or ":" in part for part in name.rstrip("/").split("/")) or
                    "" in name.rstrip("/").split("/")):
                raise ValueError(f"unsafe ZIP member: {name!r}")
            if stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR):
                raise ValueError(f"unsupported ZIP member type: {name}")
            if info.is_dir():
                continue
            if name in members:
                raise ValueError(f"duplicate ZIP member: {name}")
            members[name] = info
        if "project.godot" in members:
            prefix = ""
        else:
            roots = {name.split("/", 1)[0] for name in members}
            if len(roots) != 1:
                raise ValueError("ZIP must contain one project, optionally inside one folder")
            prefix = next(iter(roots)) + "/"
            if prefix + "project.godot" not in members:
                raise ValueError("ZIP project.godot is missing at the project root")
        return prefix, members


def _has_generated_web(relative_paths: list[str] | set[str]) -> bool:
    return any(path == "export/web" or path.startswith("export/web/") for path in relative_paths)


def _reject_mixed_source(source: Path, kind: str, errors: list[str], label: str) -> None:
    """Keep generated Web payloads out of the source identity used by near-release evidence."""
    if kind == "SOURCE_PROJECT":
        generated = source / "export" / "web"
        if generated.exists():
            errors.append(f"{label}: source identity contains generated export/web; stage/hash source without Web output")
        return
    if kind == "GODOT_PROJECT_ZIP" and source.is_file():
        try:
            prefix, members = _zip_project_members(source)
            relative = {name[len(prefix):] for name in members}
            if _has_generated_web(relative):
                errors.append(f"{label}: source ZIP contains generated export/web; package editable source and Web export separately")
        except (OSError, ValueError, RuntimeError, zipfile.BadZipFile, NotImplementedError) as exc:
            errors.append(f"{label}: invalid source ZIP: {exc}")


def _compare_archive(archive: Path, tree_entries: list[dict[str, Any]], errors: list[str]) -> None:
    """Compare packaged project bytes with the clean tested tree without extracting code."""
    try:
        prefix, members = _zip_project_members(archive)
        relative_members = {name[len(prefix):] for name in members}
        if _has_generated_web(relative_members):
            errors.append("GODOT_PROJECT_ZIP must not contain generated export/web; deliver and hash Web separately")
            return
        with zipfile.ZipFile(archive) as bundle:
            packaged = {}
            for name, info in members.items():
                relative = name[len(prefix):]
                if should_exclude(Path(relative)):
                    continue
                digest = hashlib.sha256()
                with bundle.open(info) as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        digest.update(chunk)
                packaged[relative] = (info.file_size, digest.hexdigest())
            tested = {entry["path"]: (entry["size"], entry["sha256"]) for entry in tree_entries}
            if packaged != tested:
                missing = sorted(set(packaged) - set(tested))
                extra = sorted(set(tested) - set(packaged))
                changed = sorted(k for k in packaged.keys() & tested.keys() if packaged[k] != tested[k])
                errors.append(f"ZIP/testedTree contents differ: missing={missing[:5]}, extra={extra[:5]}, changed={changed[:5]}")
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile, NotImplementedError) as exc:
        errors.append(f"ZIP content verification failed: {exc}")


def _paired_artifacts(value: Any, base: Path, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append("pairedArtifacts must be a list")
        return
    seen: set[str] = set()
    for i, row in enumerate(value):
        label = f"pairedArtifacts[{i}]"
        if not isinstance(row, dict):
            errors.append(f"{label}: object required")
            continue
        kind = row.get("kind")
        if kind not in PAIR_KINDS or kind in seen:
            errors.append(f"{label}: invalid or duplicate kind")
            continue
        seen.add(kind)
        raw = row.get("path")
        if not isinstance(raw, str) or not raw.strip() or "://" in raw:
            errors.append(f"{label}: local path required")
            continue
        path = Path(raw).expanduser()
        path = path if path.is_absolute() else base / path
        _reject_mixed_source(path, kind, errors, label)
        try:
            digest, _ = deterministic_tree_hash(path)
        except (OSError, ValueError) as exc:
            errors.append(f"{label}: {exc}")
            continue
        if not _hash_matches(row.get("sha256"), digest):
            errors.append(f"{label}: hash mismatch")


def _web_preflight(record: Any, base: Path, digest: str, build_id: str, share_mode: str,
                   profile: str | None, errors: list[str]) -> dict[str, Any] | None:
    path = _evidence_file(record, base, "webPreflight", errors)
    if path is None:
        return None
    try:
        data = load_json(path)
    except (OSError, ValueError, TypeError) as exc:
        errors.append(f"webPreflight: {exc}")
        return None
    if not isinstance(data, dict) or data.get("status") != "PASS":
        errors.append("webPreflight: linked preflight must be PASS")
        return data if isinstance(data, dict) else None
    if not _hash_matches(data.get("exportSha256"), digest):
        errors.append("webPreflight: exportSha256 mismatch")
    if data.get("buildId") != build_id:
        errors.append("webPreflight: BUILD_ID mismatch")
    expected_profiles = {
        "LOCAL_WEB_TEST": {"LOCAL_WEB_TEST", "NEAR_RELEASE"},
        "LAN_SHARE": {"LAN_SHARE", "NEAR_RELEASE"},
        "PUBLIC_HOSTED": {"NEAR_RELEASE"},
    }
    if data.get("profile") not in expected_profiles.get(share_mode, set()):
        errors.append("webPreflight: profile does not match shareMode")
    if profile == "NEAR_RELEASE_SLICE" and data.get("profile") != "NEAR_RELEASE":
        errors.append("webPreflight: near-release record requires NEAR_RELEASE preflight")
    return data


def validate_evidence(artifact: Path, evidence: Any, base: Path, excludes: list[str] | None = None,
                      required_profile: str | None = None, required_share_mode: str | None = None) -> dict[str, Any]:
    errors: list[str] = []
    digest, entries = deterministic_tree_hash(artifact, excludes or [])
    if not isinstance(evidence, dict):
        evidence = {}
        errors.append("evidence root must be an object")
    if evidence.get("schemaVersion") != 3:
        errors.append("schemaVersion 3 required; older records are historical, not a current completion certificate")
    if not _hash_matches(evidence.get("artifactSha256"), digest):
        errors.append("artifactSha256 missing, malformed, or mismatched")
    target = evidence.get("target")
    if not isinstance(target, str) or target not in TARGETS:
        errors.append("invalid or missing target")
    recorded = evidence.get("testedArtifact")
    if not isinstance(recorded, str) or not recorded.strip():
        errors.append("testedArtifact must identify the artifact")
    else:
        named = Path(recorded).expanduser()
        named = named if named.is_absolute() else base / named
        if named.resolve() != artifact.resolve():
            errors.append("testedArtifact path does not match the validated artifact")

    _paired_artifacts(evidence.get("pairedArtifacts", []), base, errors)

    required = evidence.get("requiredChecks")
    if not isinstance(required, list) or not required or any(not isinstance(x, str) or not x.strip() for x in required):
        errors.append("requiredChecks must be a nonempty list of check IDs from the brief")
        required = []
    elif len(set(required)) != len(required):
        errors.append("requiredChecks contains duplicates")
    checks = evidence.get("checks")
    if not isinstance(checks, list):
        errors.append("checks must be a list")
        checks = []
    indexed: dict[str, dict[str, Any]] = {}
    for index, check in enumerate(checks):
        label = f"check[{index}]"
        if not isinstance(check, dict):
            errors.append(f"{label}: expected object")
            continue
        name = check.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{label}: missing name")
            continue
        if name in indexed:
            errors.append(f"duplicate check name: {name}")
        indexed[name] = check
        status = check.get("status")
        if not isinstance(status, str) or status not in {"PASS", "FAIL", "PARTIAL", "SKIPPED"}:
            errors.append(f"{name}: invalid status")
        if not isinstance(check.get("executed"), bool):
            errors.append(f"{name}: executed must be boolean")
        if isinstance(status, str) and status in {"PASS", "FAIL", "PARTIAL"} and check.get("executed") is not True:
            errors.append(f"{name}: result requires actual execution")
        if status == "SKIPPED" and (check.get("executed") is not False or not str(check.get("reason", "")).strip()):
            errors.append(f"{name}: SKIPPED requires executed=false and a reason")
        if check.get("executed") is True:
            if not _hash_matches(check.get("artifactSha256"), digest):
                errors.append(f"{name}: tested a different or unidentified artifact")
            records = check.get("evidence")
            if not isinstance(records, list) or not records:
                errors.append(f"{name}: executed check needs evidence files")
            else:
                for n, record in enumerate(records):
                    _evidence_file(record, base, f"{name}.evidence[{n}]", errors)
    for name in required:
        if name not in indexed:
            errors.append(f"required check missing: {name}")
        elif indexed[name].get("status") != "PASS" or indexed[name].get("executed") is not True:
            errors.append(f"required check not executed PASS: {name}")

    if evidence.get("completedLoop") is not True:
        errors.append("completedLoop must be true; for a toy/sandbox this means its defined use/reset loop")
    if not isinstance(evidence.get("errors"), list) or evidence["errors"]:
        errors.append("errors must be an empty list for completion")
    if not isinstance(evidence.get("environment"), dict) or not evidence["environment"]:
        errors.append("environment must identify the tested environment")
    if not isinstance(evidence.get("limitations"), list):
        errors.append("limitations must be a list")
    reviewer = evidence.get("reviewer")
    if not isinstance(reviewer, dict) or reviewer.get("kind") not in ("self", "independent", "human") or not str(reviewer.get("identity", "")).strip():
        errors.append("reviewer must identify self, independent, or human review")
    if isinstance(reviewer, dict) and reviewer.get("kind") == "independent" and not str(reviewer.get("independenceEvidence", "")).strip():
        errors.append("independent reviewer requires independenceEvidence; declaration alone is not proof")
    captures = evidence.get("captures")
    if not isinstance(captures, list):
        errors.append("captures must be a list")
    else:
        for index, capture in enumerate(captures):
            _evidence_file(capture, base, f"captures[{index}]", errors)
        if "presentation" in required and not captures:
            errors.append("required presentation check needs an actual capture")

    if target == "GODOT_PROJECT_ZIP":
        if not artifact.is_file() or artifact.suffix.lower() != ".zip":
            errors.append("GODOT_PROJECT_ZIP requires a ZIP artifact")
        tree = evidence.get("testedTree")
        if not isinstance(tree, dict) or not isinstance(tree.get("path"), str) or not tree["path"].strip():
            errors.append("ZIP requires testedTree path and hash")
        else:
            tree_path = Path(tree["path"]).expanduser()
            tree_path = tree_path if tree_path.is_absolute() else base / tree_path
            if not tree_path.is_dir():
                errors.append("testedTree path is not a directory")
            else:
                try:
                    tree_digest, tree_entries = deterministic_tree_hash(tree_path)
                    if not _hash_matches(tree.get("sha256"), tree_digest):
                        errors.append("testedTree hash mismatch")
                    if artifact.is_file() and artifact.suffix.lower() == ".zip":
                        _compare_archive(artifact, tree_entries, errors)
                except (OSError, ValueError) as exc:
                    errors.append(f"testedTree invalid: {exc}")

    profile = evidence.get("qualityProfile")
    if required_profile is not None and profile != required_profile:
        errors.append("qualityProfile does not match the required brief profile")
    if profile is not None and profile not in ("PROBE", "PRESENTABLE_PROTOTYPE", "NEAR_RELEASE_SLICE"):
        errors.append("unknown qualityProfile")

    preflight_data: dict[str, Any] | None = None
    share_mode = evidence.get("shareMode")
    if required_share_mode is not None and share_mode != required_share_mode:
        errors.append("shareMode does not match the required brief delivery")
    if target == "WEB_EXPORT":
        if not artifact.is_dir():
            errors.append("WEB_EXPORT requires the exported Web directory")
        if share_mode not in SHARE_MODES:
            errors.append("WEB_EXPORT requires shareMode LOCAL_WEB_TEST, LAN_SHARE, or PUBLIC_HOSTED")
        build_id = evidence.get("buildId")
        if not isinstance(build_id, str) or not build_id.startswith("WEB-"):
            errors.append("WEB_EXPORT requires a stamped buildId")
            build_id = ""
        if share_mode in SHARE_MODES:
            preflight_data = _web_preflight(evidence.get("webPreflight"), base, digest, build_id, share_mode, profile, errors)
    elif share_mode is not None or evidence.get("buildId") is not None or evidence.get("webPreflight") is not None:
        errors.append("shareMode/buildId/webPreflight belong only on the WEB_EXPORT record")

    if profile == "NEAR_RELEASE_SLICE":
        if target == "WEB_EXPORT":
            paired = evidence.get("pairedArtifacts")
            if not isinstance(paired, list) or not any(isinstance(row, dict) and row.get("kind") in {"SOURCE_PROJECT", "GODOT_PROJECT_ZIP"} for row in paired):
                errors.append("near-release Web record must pair the separately hashed source project or Godot project ZIP")
            if not isinstance(evidence.get("webAudioExpected"), bool):
                errors.append("near-release Web record must state webAudioExpected from the brief")
            if not isinstance(evidence.get("threadSupport"), bool):
                errors.append("near-release Web record must state threadSupport from the selected Web preset")
            requirements = preflight_data.get("requirements") if isinstance(preflight_data, dict) else None
            if not isinstance(requirements, dict):
                errors.append("near-release Web preflight must record its enforced requirements")
            else:
                if requirements.get("glyphs") is not True:
                    errors.append("near-release Web preflight must enforce text/glyph rendering integrity")
                if requirements.get("projectPresetChecked") is not True:
                    errors.append("near-release Web preflight must inspect the selected Web export preset")
                if requirements.get("canvasBudget") is not True:
                    errors.append("near-release Web preflight must enforce a backing-canvas pixel budget")
                if requirements.get("displayFit") is not True:
                    errors.append("near-release Web preflight must enforce CSS display size, viewport fit, visibility, and primary-control clickability")
                if evidence.get("webAudioExpected") is True and requirements.get("audio") is not True:
                    errors.append("near-release Web audio is expected but preflight did not enforce post-gesture audio")
                if evidence.get("threadSupport") is True and requirements.get("crossOriginIsolation") is not True:
                    errors.append("threaded Web export requires cross-origin-isolation preflight")
            hard = {"web_preflight", "interaction", "presentation", "text_render"}
            if evidence.get("webAudioExpected") is True:
                hard.add("audio")
            missing_hard = sorted(hard - set(required))
            if missing_hard:
                errors.append(f"near-release Web requiredChecks missing hard gates: {missing_hard}")
        elif evidence.get("webAudioExpected") is not None or evidence.get("threadSupport") is not None:
            errors.append("webAudioExpected/threadSupport belong only on a WEB_EXPORT record")
        if excludes:
            errors.append("near-release identity does not allow custom path exclusions")
        review = evidence.get("qualityReview")
        if not isinstance(review, dict):
            errors.append("near-release requires a qualityReview file and hash bound to this player-facing artifact")
        else:
            try:
                review_path = local_file(review.get("path"), base)
                if not _hash_matches(review.get("sha256"), sha256_file(review_path)):
                    errors.append("qualityReview file hash mismatch")
                result = validate_quality(load_json(review_path), review_path.parent, digest)
                errors.extend("qualityReview: " + error for error in result["errors"])
            except (OSError, ValueError, TypeError) as exc:
                errors.append(f"qualityReview: {exc}")
    elif evidence.get("qualityReview") is not None:
        errors.append("qualityReview is only valid with qualityProfile NEAR_RELEASE_SLICE")

    return {
        "artifact": str(artifact),
        "actualSha256": digest,
        "fileCount": len(entries),
        "status": "FAIL" if errors else "PASS",
        "validationScope": "release-record structure, local evidence, artifact/pair hashes, and linked Web preflight consistency only",
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact")
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--required-profile", choices=["PROBE", "PRESENTABLE_PROTOTYPE", "NEAR_RELEASE_SLICE"])
    parser.add_argument("--required-share-mode", choices=sorted(SHARE_MODES))
    args = parser.parse_args()
    artifact = Path(args.artifact).expanduser().absolute()
    path = Path(args.evidence).expanduser().resolve()
    try:
        result = validate_evidence(artifact, load_json(path), path.parent, args.exclude,
                                   args.required_profile, args.required_share_mode)
    except (ValueError, OSError, TypeError) as exc:
        print(json.dumps({"status": "FAIL", "errors": [str(exc)]}, indent=2))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
