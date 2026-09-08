"""Unit/integration fixtures for Web export stamping, serving and preflight.

These tests exercise local fixture files/servers. They do not prove a real Godot game exported,
rendered correctly, sounded correct, or was enjoyable.
"""
from __future__ import annotations

import functools
import json
import shutil
import socket
import ssl
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from _common import deterministic_tree_hash, sha256_file
from _web import derive_build_id, read_web_export_preset, web_files, detect_lan_ip
import serve_web_export as serve
import stamp_web_build as stamp
import web_preflight as preflight


class WebFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.web = self.base / "web"
        self.web.mkdir()
        (self.web / "index.html").write_text(
            '<!doctype html><html><body><canvas id="canvas"></canvas>'
            '<script>const cfg={"canvasResizePolicy":1};</script></body></html>', encoding="utf-8")
        (self.web / "game.wasm").write_bytes(b"\0asmfixture")
        (self.web / "game.pck").write_bytes(b"pck-fixture")
        (self.web / "game.js").write_text('console.log("fixture")', encoding="utf-8")
        stamp.stamp(self.web)
        self.project = self.base / "project"
        self.project.mkdir()
        self.write_preset()
        self.capture = self.base / "browser.png"
        # It need only be a nonempty locally hashed capture for preflight linkage;
        # media signature is checked by the quality validator, not this preflight helper.
        self.capture.write_bytes(b"fixture-browser-capture")

    def write_preset(self, *, policy=1, threads=False, mobile=False, second=False):
        text = f'''[preset.0]\nname="Web"\nplatform="Web"\nrunnable=true\n\n[preset.0.options]\nhtml/canvas_resize_policy={policy}\nvariant/thread_support={'true' if threads else 'false'}\nvram_texture_compression/for_mobile={'true' if mobile else 'false'}\ncustom_template/release=""\n'''
        if second:
            text += '''\n[preset.1]\nname="Other Web"\nplatform="Web"\nrunnable=false\n\n[preset.1.options]\nhtml/canvas_resize_policy=1\nvariant/thread_support=false\nvram_texture_compression/for_mobile=false\n'''
        (self.project / "export_presets.cfg").write_text(text, encoding="utf-8")

    @property
    def build_id(self):
        return (self.web / "BUILD_ID.txt").read_text(encoding="utf-8").strip()

    def browser(self, url, *, secure=False, isolated=False, audio=True, glyphs=True,
                css=(960, 540), viewport=(960, 540), backing=(960, 540),
                visible=True, clipped=False, clickable=True):
        return {
            "schemaVersion": 1,
            "url": url,
            "buildId": self.build_id,
            "engineStarted": True,
            "normalPathPass": True,
            "isSecureContext": secure,
            "crossOriginIsolated": isolated,
            "missingFeatures": [],
            "consoleFatalErrors": [],
            "audioAfterGesture": audio,
            "glyphsOk": glyphs,
            "replacementGlyphsDetected": not glyphs,
            "textOverflowDetected": False,
            "primaryControlClickable": clickable,
            "canvas": {
                "cssWidth": css[0], "cssHeight": css[1],
                "backingWidth": backing[0], "backingHeight": backing[1],
                "devicePixelRatio": 2,
                "viewportWidth": viewport[0], "viewportHeight": viewport[1],
                "fullyVisible": visible,
                "clipped": clipped,
            },
            "capture": {"path": str(self.capture), "sha256": sha256_file(self.capture)},
        }

    def http_server(self, isolation=False):
        serve.GodotHandler.cross_origin_isolation = isolation
        handler = functools.partial(serve.GodotHandler, directory=str(self.web))
        server = serve.http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return server, f"http://127.0.0.1:{server.server_address[1]}/"

    def https_lan_server(self, isolation=False):
        try:
            ip = detect_lan_ip()
        except ValueError as exc:
            self.skipTest(str(exc))
        if not shutil.which("openssl"):
            self.skipTest("openssl unavailable")
        cert = self.base / "cert.pem"
        key = self.base / "key.pem"
        serve.generate_certificate(cert, key, ip, 1)
        serve.GodotHandler.cross_origin_isolation = isolation
        handler = functools.partial(serve.GodotHandler, directory=str(self.web))
        server = serve.http.server.ThreadingHTTPServer(("0.0.0.0", 0), handler)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=str(cert), keyfile=str(key))
        server.socket = context.wrap_socket(server.socket, server_side=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return server, f"https://{ip}:{server.server_address[1]}/"


class StampTests(WebFixture):
    def test_stamp_is_idempotent(self):
        before = self.build_id
        stamp.stamp(self.web)
        self.assertEqual(self.build_id, before)
        self.assertEqual(derive_build_id(self.web), before)
        html = (self.web / "index.html").read_text(encoding="utf-8")
        self.assertEqual(html.count("GODOT_BUILD_ID_START"), 1)

    def test_payload_change_changes_build_id(self):
        before = self.build_id
        (self.web / "game.pck").write_bytes(b"changed-payload")
        stamp.stamp(self.web)
        self.assertNotEqual(self.build_id, before)

    def test_missing_required_web_file_fails(self):
        (self.web / "game.pck").unlink()
        with self.assertRaises(ValueError):
            web_files(self.web)


class PresetTests(WebFixture):
    def test_reads_runnable_web_preset(self):
        preset = read_web_export_preset(self.project)
        self.assertEqual(preset["base"]["name"], "Web")
        self.assertEqual(preset["options"]["variant/thread_support"], "false")

    def test_selects_unique_runnable_when_multiple(self):
        self.write_preset(second=True)
        self.assertEqual(read_web_export_preset(self.project)["base"]["name"], "Web")

    def test_named_preset_resolves(self):
        self.write_preset(second=True)
        self.assertEqual(read_web_export_preset(self.project, "Other Web")["base"]["name"], "Other Web")


class ServeTests(WebFixture):
    def fetch(self, url):
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(url, timeout=5) as response:
            return response.status, {k.lower(): v for k, v in response.headers.items()}, response.read()

    def test_root_is_game_html_not_listing(self):
        _, url = self.http_server(False)
        status, headers, body = self.fetch(url)
        self.assertEqual(status, 200)
        self.assertIn("text/html", headers.get("content-type", ""))
        self.assertIn(b"<canvas", body)
        self.assertIn(self.build_id.encode(), body)
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self.fetch(url + "subdir/")
        self.assertEqual(ctx.exception.code, 404)

    def test_cross_origin_headers_are_conditional(self):
        _, url = self.http_server(False)
        _, headers, _ = self.fetch(url)
        self.assertNotIn("cross-origin-opener-policy", headers)
        # class-level setting changes only future requests; use a fresh server after changing it.
        _, url2 = self.http_server(True)
        _, headers2, _ = self.fetch(url2)
        self.assertEqual(headers2.get("cross-origin-opener-policy"), "same-origin")
        self.assertEqual(headers2.get("cross-origin-embedder-policy"), "require-corp")

    @unittest.skipUnless(shutil.which("openssl"), "openssl unavailable")
    def test_generated_certificate_contains_lan_ip_san(self):
        cert, key = self.base / "cert.pem", self.base / "key.pem"
        serve.generate_certificate(cert, key, "192.168.50.20", 1)
        result = subprocess.run(
            [shutil.which("openssl"), "x509", "-in", str(cert), "-noout", "-ext", "subjectAltName"],
            text=True, capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("IP Address:192.168.50.20", result.stdout)
        self.assertTrue(key.is_file())

    def test_serve_cli_rejects_project_root_even_if_web_payload_is_present(self):
        project = self.base / "accidental-project-root"
        project.mkdir()
        (project / "project.godot").write_text("[application]\n", encoding="utf-8")
        for name in ("index.html", "game.wasm", "game.pck", "game.js", "BUILD_ID.txt"):
            source = self.web / name
            (project / name).write_bytes(source.read_bytes())
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "serve_web_export.py"), str(project), "--ip", "127.0.0.1"],
            text=True, capture_output=True, timeout=5)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("project root", (result.stdout + result.stderr).lower())


class PreflightTests(WebFixture):
    def test_local_static_preflight_passes(self):
        result = preflight.validate(self.web, None, "LOCAL_WEB_TEST", None, project_root=self.project)
        self.assertEqual(result["status"], "PASS", result["errors"])
        self.assertTrue(result["requirements"]["projectPresetChecked"])

    def test_web_share_http_loopback_with_browser_report_passes(self):
        _, url = self.http_server(False)
        result = preflight.validate(
            self.web, url, "WEB_SHARE", self.browser(url),
            require_audio=True, require_glyphs=True, project_root=self.project,
            browser_base=self.base)
        self.assertEqual(result["status"], "PASS", result["errors"])
        self.assertTrue(result["requirements"]["audio"])
        self.assertTrue(result["requirements"]["glyphs"])

    def test_web_share_rejects_missing_glyphs_when_required(self):
        _, url = self.http_server(False)
        result = preflight.validate(
            self.web, url, "WEB_SHARE", self.browser(url, glyphs=False),
            require_glyphs=True, project_root=self.project, browser_base=self.base)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("glyph" in error.lower() for error in result["errors"]))

    def test_audio_gate_requires_post_gesture_audio(self):
        _, url = self.http_server(False)
        result = preflight.validate(
            self.web, url, "WEB_SHARE", self.browser(url, audio=False),
            require_audio=True, project_root=self.project, browser_base=self.base)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("audio" in error.lower() for error in result["errors"]))

    def test_default_rejects_adaptive_canvas(self):
        self.write_preset(policy=2)
        html = (self.web / "index.html").read_text(encoding="utf-8").replace('"canvasResizePolicy":1', '"canvasResizePolicy":2')
        (self.web / "index.html").write_text(html, encoding="utf-8")
        stamp.stamp(self.web)
        result = preflight.validate(self.web, None, "LOCAL_WEB_TEST", None, project_root=self.project)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("canvasResizePolicy" in error for error in result["errors"]))

    def test_adaptive_canvas_requires_backing_budget(self):
        self.write_preset(policy=2)
        html = (self.web / "index.html").read_text(encoding="utf-8").replace('"canvasResizePolicy":1', '"canvasResizePolicy":2')
        (self.web / "index.html").write_text(html, encoding="utf-8")
        stamp.stamp(self.web)
        fail = preflight.validate(self.web, None, "LOCAL_WEB_TEST", None,
                                  allow_adaptive=True, project_root=self.project)
        self.assertEqual(fail["status"], "FAIL")
        passed = preflight.validate(self.web, None, "LOCAL_WEB_TEST", None,
                                    allow_adaptive=True, max_backing_width=1920, max_backing_height=1080,
                                    project_root=self.project)
        self.assertEqual(passed["status"], "PASS", passed["errors"])

    def test_mobile_vram_requires_explicit_allowance(self):
        self.write_preset(mobile=True)
        result = preflight.validate(self.web, None, "LOCAL_WEB_TEST", None, project_root=self.project)
        self.assertEqual(result["status"], "FAIL")
        result2 = preflight.validate(self.web, None, "LOCAL_WEB_TEST", None,
                                     project_root=self.project, allow_mobile_vram=True)
        self.assertEqual(result2["status"], "PASS", result2["errors"])

    def test_custom_template_requires_explicit_allowance(self):
        template = self.project / "custom.zip"
        template.write_bytes(b"fixture")
        cfg = (self.project / "export_presets.cfg").read_text(encoding="utf-8")
        cfg = cfg.replace('custom_template/release=""', 'custom_template/release="res://custom.zip"')
        (self.project / "export_presets.cfg").write_text(cfg, encoding="utf-8")
        result = preflight.validate(self.web, None, "LOCAL_WEB_TEST", None, project_root=self.project)
        self.assertEqual(result["status"], "FAIL")
        allowed = preflight.validate(self.web, None, "LOCAL_WEB_TEST", None, project_root=self.project, allow_custom_template=True)
        self.assertEqual(allowed["status"], "PASS", allowed["errors"])

    def test_near_release_requires_canvas_budget(self):
        _, url = self.https_lan_server(False)
        result = preflight.validate(
            self.web, url, "NEAR_RELEASE", self.browser(url, secure=True),
            allow_self_signed=True, project_root=self.project, browser_base=self.base)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("pixel budget" in error for error in result["errors"]))

    def test_threaded_build_requires_isolation_in_served_browser(self):
        self.write_preset(threads=True)
        _, url = self.http_server(False)
        result = preflight.validate(
            self.web, url, "WEB_SHARE", self.browser(url, isolated=False),
            project_root=self.project, allow_threads=True, browser_base=self.base)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("Cross-Origin" in error or "crossOriginIsolated" in error for error in result["errors"]))

    def test_near_release_requires_project_preset(self):
        # It also fails on loopback delivery, but project-preset absence must remain explicit.
        _, url = self.http_server(False)
        result = preflight.validate(self.web, url, "NEAR_RELEASE", self.browser(url, secure=True), browser_base=self.base)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("--project-root" in error for error in result["errors"]))

    def test_lan_profile_rejects_loopback_url(self):
        _, url = self.http_server(False)
        result = preflight.validate(
            self.web, url, "LAN_SHARE", self.browser(url, secure=True),
            project_root=self.project, browser_base=self.base)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("LAN address" in error or "HTTPS" in error for error in result["errors"]))


    def test_near_release_allows_localhost_http_final_browser_check(self):
        _, url = self.http_server(False)
        browser = self.browser(url, secure=True, isolated=False, audio=True, glyphs=True)
        result = preflight.validate(
            self.web, url, "NEAR_RELEASE", browser,
            require_audio=True, project_root=self.project,
            max_backing_width=1920, max_backing_height=1080, browser_base=self.base)
        self.assertEqual(result["status"], "PASS", result["errors"])

    def test_postage_stamp_css_fails_even_when_backing_budget_passes(self):
        _, url = self.http_server(False)
        browser = self.browser(url, css=(640, 360), viewport=(1920, 1080), backing=(1280, 720))
        result = preflight.validate(
            self.web, url, "NEAR_RELEASE", browser,
            require_audio=True, project_root=self.project,
            max_backing_width=1920, max_backing_height=1080, browser_base=self.base)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("adequately fill" in error for error in result["errors"]))

    def test_clipped_or_unclickable_control_fails_player_facing_web(self):
        _, url = self.http_server(False)
        clipped = preflight.validate(
            self.web, url, "WEB_SHARE", self.browser(url, clipped=True),
            project_root=self.project, browser_base=self.base)
        self.assertEqual(clipped["status"], "FAIL")
        unclickable = preflight.validate(
            self.web, url, "FIRST_TARGET", self.browser(url, clickable=False),
            require_audio=True, require_glyphs=True, project_root=self.project, browser_base=self.base)
        self.assertEqual(unclickable["status"], "FAIL")
        self.assertTrue(any("clickable" in error for error in unclickable["errors"]))

    def test_first_target_passes_with_display_fit(self):
        _, url = self.http_server(False)
        result = preflight.validate(
            self.web, url, "FIRST_TARGET", self.browser(url),
            require_audio=True, require_glyphs=True, project_root=self.project, browser_base=self.base)
        self.assertEqual(result["status"], "PASS", result["errors"])
        self.assertTrue(result["requirements"]["displayFit"])

    def test_near_release_actual_lan_https_fixture(self):
        _, url = self.https_lan_server(False)
        browser = self.browser(url, secure=True, isolated=False, audio=True, glyphs=True)
        result = preflight.validate(
            self.web, url, "NEAR_RELEASE", browser,
            allow_self_signed=True, require_audio=True, project_root=self.project,
            max_backing_width=1920, max_backing_height=1080, browser_base=self.base)
        self.assertEqual(result["status"], "PASS", result["errors"])
        self.assertTrue(result["requirements"]["glyphs"])
        self.assertFalse(result["requirements"]["crossOriginIsolation"])


if __name__ == "__main__":
    unittest.main()
