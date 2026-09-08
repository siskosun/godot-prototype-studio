#!/usr/bin/env python3
"""Validate a served Godot Web export and supplied real-browser observations."""
from __future__ import annotations

import argparse
import json
import math
import ssl
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from _common import deterministic_tree_hash, load_json, sha256_file
from _web import (canvas_resize_policy, cfg_bool, cfg_int, derive_build_id, html_build_id,
                  is_loopback_host, normalize_url, read_build_id, read_web_export_preset, web_files)

PROFILES = {"LOCAL_WEB_TEST", "FIRST_TARGET", "WEB_SHARE", "LAN_SHARE", "NEAR_RELEASE"}
PLAYER_FACING = {"FIRST_TARGET", "WEB_SHARE", "LAN_SHARE", "NEAR_RELEASE"}


def _positive_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        return None
    return number


def _display_fit_errors(canvas: dict[str, Any], min_axis_fill: float, min_area: float) -> list[str]:
    errors: list[str] = []
    css_w = _positive_number(canvas.get("cssWidth"))
    css_h = _positive_number(canvas.get("cssHeight"))
    vp_w = _positive_number(canvas.get("viewportWidth"))
    vp_h = _positive_number(canvas.get("viewportHeight"))
    if css_w is None or css_h is None:
        errors.append("browser canvas cssWidth/cssHeight must be positive numbers")
        return errors
    if vp_w is None or vp_h is None:
        errors.append("browser canvas viewportWidth/viewportHeight must be positive numbers")
        return errors
    cover_w = css_w / vp_w
    cover_h = css_h / vp_h
    area = (css_w * css_h) / (vp_w * vp_h)
    fills_an_axis = cover_w >= min_axis_fill or cover_h >= min_axis_fill
    if not fills_an_axis or area < min_area:
        errors.append(
            f"CSS canvas {int(css_w)}x{int(css_h)} does not adequately fill viewport "
            f"{int(vp_w)}x{int(vp_h)}; pixel-budget PASS is not display-fit"
        )
    if canvas.get("fullyVisible") is not True:
        errors.append("browser canvas is not fully visible in the viewport")
    if canvas.get("clipped") is not False:
        errors.append("browser canvas is clipped or clip state was not ruled out")
    return errors


def _fetch(url: str, allow_self_signed: bool) -> tuple[int, dict[str, str], bytes]:
    context = None
    if url.lower().startswith("https://") and allow_self_signed:
        context = ssl._create_unverified_context()  # Testing a local cert only; browser report proves secure-context behavior.
    request = urllib.request.Request(url, headers={"User-Agent": "GodotPrototypeStudio-WebPreflight/1"})
    handlers: list[Any] = [urllib.request.ProxyHandler({})]
    if url.lower().startswith("https://"):
        handlers.append(urllib.request.HTTPSHandler(context=context))
    opener = urllib.request.build_opener(*handlers)
    with opener.open(request, timeout=8) as response:
        return response.status, {k.lower(): v for k, v in response.headers.items()}, response.read()


def _local_record_path(value: Any, base: Path) -> Path:
    if not isinstance(value, str) or not value.strip() or "://" in value:
        raise ValueError("capture path must be a local file")
    path = Path(value).expanduser()
    path = path if path.is_absolute() else base / path
    if path.is_symlink() or not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"missing/empty capture: {path}")
    return path


def validate(root: Path, url: str | None, profile: str, browser: Any | None,
             allow_self_signed: bool = False, require_audio: bool = False,
             require_glyphs: bool = False, allow_adaptive: bool = False,
             max_backing_width: int | None = None, max_backing_height: int | None = None,
             browser_base: Path | None = None, project_root: Path | None = None,
             preset_name: str | None = None, allow_threads: bool = False,
             allow_mobile_vram: bool = False, require_cross_origin_isolation: bool = False,
             allow_custom_template: bool = False, min_axis_fill: float = 0.9,
             min_css_area: float = 0.5) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, Any] = {}
    if profile not in PROFILES:
        raise ValueError(f"unknown profile: {profile}")
    root = root.resolve()
    files = web_files(root)
    export_hash, _ = deterministic_tree_hash(root)
    expected_build = derive_build_id(root)
    recorded_build = read_build_id(root)
    index = files["index"]
    assert isinstance(index, Path)
    in_html = html_build_id(index)
    if recorded_build != expected_build:
        errors.append("BUILD_ID.txt does not match the current Web payload; restamp after export")
    if in_html != recorded_build:
        errors.append("index.html BUILD_ID does not match BUILD_ID.txt")
    checks["buildId"] = {"expected": expected_build, "recorded": recorded_build, "html": in_html}

    thread_support = False
    if project_root is not None:
        try:
            preset = read_web_export_preset(project_root, preset_name)
            options = preset["options"]
            preset_policy = cfg_int(options.get("html/canvas_resize_policy"))
            preset_threads = cfg_bool(options.get("variant/thread_support"))
            mobile_vram = cfg_bool(options.get("vram_texture_compression/for_mobile"))
            custom_template = str(options.get("custom_template/release", "") or "").strip()
            checks["webPreset"] = {
                "name": preset["base"].get("name"),
                "canvasResizePolicy": preset_policy,
                "threadSupport": preset_threads,
                "mobileVramCompression": mobile_vram,
                "customReleaseTemplate": custom_template,
            }
            if preset_threads is None:
                errors.append("Web preset must explicitly record variant/thread_support")
            else:
                thread_support = preset_threads
                if preset_threads and not allow_threads:
                    errors.append("Web preset enables threads; pass --allow-threads only when the game requires them")
            if mobile_vram is None:
                errors.append("Web preset must explicitly record vram_texture_compression/for_mobile")
            elif mobile_vram and not allow_mobile_vram:
                errors.append("mobile VRAM compression is enabled without an explicit ETC2/ASTC target allowance")
            if preset_policy is None:
                errors.append("Web preset must explicitly record html/canvas_resize_policy")
            if custom_template and not allow_custom_template:
                errors.append("custom Web release template requires explicit version-compatibility verification before --allow-custom-template")
            if custom_template:
                raw = custom_template.replace("res://", str(project_root.expanduser().resolve()) + "/", 1)
                candidate = Path(raw).expanduser()
                if not candidate.is_absolute():
                    candidate = project_root.expanduser().resolve() / candidate
                if not candidate.is_file():
                    errors.append(f"custom Web release template missing: {candidate}")
        except (OSError, ValueError, UnicodeError) as exc:
            errors.append(f"Web preset check failed: {exc}")
    elif profile == "NEAR_RELEASE":
        errors.append("NEAR_RELEASE preflight requires --project-root to verify the Web export preset")

    policy = canvas_resize_policy(index)
    checks["canvasResizePolicy"] = policy
    if policy is None:
        errors.append("canvasResizePolicy not found in exported index.html")
    elif policy != 1:
        if not allow_adaptive:
            errors.append(f"canvasResizePolicy={policy}; default Web gate requires Project policy (1) unless an explicit adaptive/DPR budget is declared")
        elif max_backing_width is None or max_backing_height is None:
            errors.append("adaptive canvas exception requires --max-backing-width and --max-backing-height")

    if project_root is not None and isinstance(checks.get("webPreset"), dict):
        preset_policy = checks["webPreset"].get("canvasResizePolicy")
        if isinstance(preset_policy, int) and policy is not None and preset_policy != policy:
            errors.append("exported canvasResizePolicy does not match the selected Web preset")

    if max_backing_width is not None and max_backing_width <= 0:
        errors.append("--max-backing-width must be positive")
    if max_backing_height is not None and max_backing_height <= 0:
        errors.append("--max-backing-height must be positive")
    if profile == "NEAR_RELEASE" and (max_backing_width is None or max_backing_height is None):
        errors.append("NEAR_RELEASE preflight requires an explicit backing-canvas pixel budget")

    cross_origin_required = bool(require_cross_origin_isolation or thread_support)
    url_norm = normalize_url(url) if url else None
    served_headers: dict[str, str] = {}
    if url_norm:
        parsed = urllib.parse.urlsplit(url_norm)
        non_loopback = not is_loopback_host(parsed.hostname or "")
        if profile == "LAN_SHARE":
            if parsed.scheme.lower() != "https":
                errors.append("LAN share URL must use HTTPS")
            if not non_loopback:
                errors.append("LAN share URL must use the host LAN address, not localhost/loopback")
        elif non_loopback and parsed.scheme.lower() != "https":
            errors.append("non-loopback Web URL must use HTTPS")
        try:
            status, served_headers, body = _fetch(url_norm, allow_self_signed)
            text = body[:2_000_000].decode("utf-8", errors="replace")
            checks["rootHttp"] = {"status": status, "contentType": served_headers.get("content-type", "")}
            if status != 200:
                errors.append(f"GET / returned {status}")
            if "text/html" not in served_headers.get("content-type", "").lower():
                errors.append("GET / is not served as text/html")
            if "<canvas" not in text.lower():
                errors.append("GET / does not appear to be the Godot game HTML")
            if "directory listing" in text.lower() or "directory listing for" in text.lower():
                errors.append("GET / returned a directory listing")
            if recorded_build and recorded_build not in text:
                errors.append("served root does not contain the expected BUILD_ID")
            for key in ("wasm", "pck"):
                path = files[key][0]  # type: ignore[index]
                asset_url = urllib.parse.urljoin(url_norm, urllib.parse.quote(path.name))
                a_status, a_headers, a_body = _fetch(asset_url, allow_self_signed)
                checks[key] = {"status": a_status, "bytes": len(a_body), "contentType": a_headers.get("content-type", "")}
                if a_status != 200 or not a_body:
                    errors.append(f"served {key} file is missing/empty")
                if key == "wasm" and "application/wasm" not in a_headers.get("content-type", "").lower():
                    errors.append(".wasm is not served as application/wasm")
            if cross_origin_required:
                if served_headers.get("cross-origin-opener-policy", "").lower() != "same-origin":
                    errors.append("threaded/cross-origin-isolated Web build is missing Cross-Origin-Opener-Policy: same-origin")
                if served_headers.get("cross-origin-embedder-policy", "").lower() != "require-corp":
                    errors.append("threaded/cross-origin-isolated Web build is missing Cross-Origin-Embedder-Policy: require-corp")
        except (OSError, urllib.error.URLError, urllib.error.HTTPError, ssl.SSLError) as exc:
            errors.append(f"HTTP(S) probe failed: {exc}")
    elif profile != "LOCAL_WEB_TEST":
        errors.append(f"{profile} requires a served --url")

    if min_axis_fill <= 0 or min_axis_fill > 1:
        errors.append("--min-axis-fill must be in (0, 1]")
    if min_css_area <= 0 or min_css_area > 1:
        errors.append("--min-css-area must be in (0, 1]")

    browser_required = profile in PLAYER_FACING
    if browser is None:
        if browser_required:
            errors.append(f"{profile} requires a real-browser report")
    elif not isinstance(browser, dict):
        errors.append("browser report must be a JSON object")
    else:
        checks["browser"] = {k: browser.get(k) for k in (
            "url", "buildId", "engineStarted", "normalPathPass", "isSecureContext", "crossOriginIsolated",
            "primaryControlClickable")}
        if url_norm and normalize_url(str(browser.get("url", ""))) != url_norm:
            errors.append("browser report URL does not match the probed URL")
        if browser.get("buildId") != recorded_build:
            errors.append("browser report BUILD_ID does not match the delivered Web build")
        if browser.get("engineStarted") is not True:
            errors.append("browser report does not prove engine startup")
        if browser.get("normalPathPass") is not True:
            errors.append("browser report does not prove the normal-input smoke path")
        fatal = browser.get("consoleFatalErrors")
        if not isinstance(fatal, list) or fatal:
            errors.append("browser report must contain an empty consoleFatalErrors list")
        missing = browser.get("missingFeatures")
        if missing is not None and (not isinstance(missing, list) or missing):
            errors.append("browser-reported missing features are not empty")
        parsed = urllib.parse.urlsplit(url_norm) if url_norm else None
        secure_required = profile == "LAN_SHARE" or (parsed is not None and not is_loopback_host(parsed.hostname or ""))
        if secure_required and browser.get("isSecureContext") is not True:
            errors.append("browser reports an insecure context")
        if cross_origin_required and browser.get("crossOriginIsolated") is not True:
            errors.append("browser reports crossOriginIsolated=false for a build that requires cross-origin isolation")
        if require_audio and browser.get("audioAfterGesture") is not True:
            errors.append("required Web audio was not heard/observed after a player gesture")
        glyph_required = bool(require_glyphs or profile == "NEAR_RELEASE")
        if glyph_required:
            if browser.get("glyphsOk") is not True:
                errors.append("required-language glyph rendering did not pass")
            if browser.get("replacementGlyphsDetected") is not False:
                errors.append("replacement/tofu glyphs were detected or not explicitly ruled out")
            if browser.get("textOverflowDetected") is not False:
                errors.append("blocking text overflow was detected or not explicitly ruled out")
        canvas = browser.get("canvas")
        if not isinstance(canvas, dict):
            errors.append("browser report requires canvas measurements")
        else:
            checks["canvas"] = {k: canvas.get(k) for k in (
                "cssWidth", "cssHeight", "backingWidth", "backingHeight",
                "devicePixelRatio", "viewportWidth", "viewportHeight", "fullyVisible", "clipped")}
            bw, bh = canvas.get("backingWidth"), canvas.get("backingHeight")
            if not isinstance(bw, int) or bw <= 0 or not isinstance(bh, int) or bh <= 0:
                errors.append("browser canvas backingWidth/backingHeight must be positive integers")
            if max_backing_width is not None and isinstance(bw, int) and bw > max_backing_width:
                errors.append(f"canvas backing width {bw} exceeds budget {max_backing_width}")
            if max_backing_height is not None and isinstance(bh, int) and bh > max_backing_height:
                errors.append(f"canvas backing height {bh} exceeds budget {max_backing_height}")
            if profile in PLAYER_FACING:
                errors.extend(_display_fit_errors(canvas, min_axis_fill, min_css_area))
                if browser.get("primaryControlClickable") is not True:
                    errors.append("primary control was not shown to be visible and clickable")
        capture = browser.get("capture")
        if profile == "NEAR_RELEASE" or require_glyphs:
            if not isinstance(capture, dict):
                errors.append("near-release/text-render browser report requires a capture")
            else:
                base = browser_base or Path.cwd()
                try:
                    path = _local_record_path(capture.get("path"), base)
                    if capture.get("sha256") != sha256_file(path):
                        errors.append("browser capture hash mismatch")
                except (OSError, ValueError) as exc:
                    errors.append(str(exc))

    return {
        "schemaVersion": 1,
        "profile": profile,
        "status": "FAIL" if errors else "PASS",
        "exportDir": str(root),
        "exportSha256": export_hash,
        "buildId": recorded_build,
        "url": url_norm,
        "requirements": {
            "audio": bool(require_audio),
            "glyphs": bool(require_glyphs or profile == "NEAR_RELEASE"),
            "crossOriginIsolation": bool(cross_origin_required),
            "projectPresetChecked": project_root is not None,
            "canvasBudget": max_backing_width is not None and max_backing_height is not None,
            "displayFit": profile in PLAYER_FACING and isinstance(browser, dict),
            "customTemplateExplicitlyAllowed": bool(allow_custom_template),
        },
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
        "validationScope": "Web export files, served HTTP(S), and consistency of supplied browser observations",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export_dir")
    parser.add_argument("--url")
    parser.add_argument("--profile", choices=sorted(PROFILES), default="LOCAL_WEB_TEST")
    parser.add_argument("--browser-report")
    parser.add_argument("--allow-self-signed", action="store_true")
    parser.add_argument("--require-audio", action="store_true")
    parser.add_argument("--require-glyphs", action="store_true")
    parser.add_argument("--allow-adaptive", action="store_true")
    parser.add_argument("--max-backing-width", type=int)
    parser.add_argument("--max-backing-height", type=int)
    parser.add_argument("--project-root")
    parser.add_argument("--preset-name")
    parser.add_argument("--allow-threads", action="store_true")
    parser.add_argument("--allow-mobile-vram", action="store_true")
    parser.add_argument("--require-cross-origin-isolation", action="store_true")
    parser.add_argument("--allow-custom-template", action="store_true")
    parser.add_argument("--min-axis-fill", type=float, default=0.9)
    parser.add_argument("--min-css-area", type=float, default=0.5)
    parser.add_argument("--write")
    args = parser.parse_args()
    try:
        browser = None
        browser_base = None
        if args.browser_report:
            bpath = Path(args.browser_report).expanduser().resolve()
            browser = load_json(bpath)
            browser_base = bpath.parent
        result = validate(Path(args.export_dir), args.url, args.profile, browser,
                          args.allow_self_signed, args.require_audio, args.require_glyphs,
                          args.allow_adaptive, args.max_backing_width, args.max_backing_height,
                          browser_base, Path(args.project_root) if args.project_root else None, args.preset_name,
                          args.allow_threads, args.allow_mobile_vram, args.require_cross_origin_isolation,
                          args.allow_custom_template, args.min_axis_fill, args.min_css_area)
    except (OSError, ValueError, TypeError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}
    if args.write:
        path = Path(args.write).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
