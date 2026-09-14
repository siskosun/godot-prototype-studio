"""0.7 route/reuse and runtime-identity utility tests; not live gameplay or multi-device validation."""
from __future__ import annotations

import functools
import json
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from _common import sha256_file
import serve_web_export as serve
import stamp_web_build as stamp
import validate_mission_brief as brief
import web_preflight as preflight


class RouteIntentTests(unittest.TestCase):
    def base(self) -> str:
        content = {name: "A concrete declared requirement." for name in brief.REQUIRED}
        content["Completion"] = "DONE when verified. BLOCKED only by a genuine unmet requirement."
        return "\n".join(f"## {name}\n{text}\n" for name, text in content.items())

    def routed(self, *, stack="OPEN", route="GODOT", h5="NOT_SIMPLER", reuse="BUILD_NEW",
               seed="none", rationale="Godot is the cheaper adequate route for this fixture.") -> str:
        section = f'''## Pre-development Route
- Stack constraint: {stack}
- Selected route: {route}
- H5 decision: {h5}
- Route rationale: {rationale}
- Reuse scan: .prototype/research/reuse_scan.md checked current public sources
- Reuse decision: {reuse}
- Seed source: {seed}
'''
        return self.base() + "\n" + section

    def test_valid_godot_and_h5_routes(self):
        self.assertEqual(brief.validate_text(self.routed()), [])
        self.assertEqual(brief.validate_text(self.routed(route="H5", h5="USER_SELECTED_H5",
                                                         rationale="H5 meets the same browser-only acceptance with less infrastructure.")), [])

    def test_user_locked_stack_cannot_silently_change(self):
        errors = brief.validate_text(self.routed(stack="USER_LOCKED_GODOT", route="H5", h5="USER_SELECTED_H5"))
        self.assertTrue(any("USER_LOCKED_GODOT" in item for item in errors))

    def test_unresolved_h5_offer_is_not_formal_route(self):
        text = self.routed().replace("H5 decision: NOT_SIMPLER", "H5 decision: H5_CANDIDATE")
        self.assertTrue(any("H5 decision" in item for item in brief.validate_text(text)))

    def test_copy_and_adapt_requires_pinned_seed(self):
        errors = brief.validate_text(self.routed(reuse="COPY_AND_ADAPT", seed="none"))
        self.assertTrue(any("Seed source" in item for item in errors))
        valid = self.routed(reuse="COPY_AND_ADAPT", seed="https://example.test/repo @ abc123, MIT")
        self.assertEqual(brief.validate_text(valid), [])

    def test_cross_stack_decline_keeps_selected_route(self):
        self.assertEqual(brief.validate_text(self.routed(reuse="CROSS_STACK_DECLINED")), [])


class WorkspaceOptionTests(unittest.TestCase):
    def run_init(self, root: Path, *args: str):
        return subprocess.run([sys.executable, str(ROOT / "scripts" / "init_workspace.py"), str(root), *args],
                              text=True, capture_output=True, timeout=15)

    def test_reuse_and_multiplayer_records_are_opt_in_and_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            result = self.run_init(root, "--reuse-scan", "--multiplayer")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            reuse = root / ".prototype/research/reuse_scan.md"
            matrix = root / ".prototype/spec/multiplayer_session_matrix.md"
            self.assertTrue(reuse.is_file())
            self.assertTrue(matrix.is_file())
            reuse.write_text("user-owned reuse scan", encoding="utf-8")
            matrix.write_text("user-owned multiplayer matrix", encoding="utf-8")
            result = self.run_init(root, "--reuse-scan", "--multiplayer")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(reuse.read_text(encoding="utf-8"), "user-owned reuse scan")
            self.assertEqual(matrix.read_text(encoding="utf-8"), "user-owned multiplayer matrix")


class RuntimeIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.web = self.root / "web"
        self.web.mkdir()
        (self.web / "index.html").write_text(
            '<!doctype html><html><body><canvas id="canvas"></canvas>'
            '<script>const cfg={"canvasResizePolicy":1};</script></body></html>', encoding="utf-8")
        (self.web / "game.wasm").write_bytes(b"\0asmfixture")
        (self.web / "game.pck").write_bytes(b"pck-fixture")
        (self.web / "game.js").write_text('console.log("fixture")', encoding="utf-8")
        stamp.stamp(self.web)
        self.project = self.root / "project"
        self.project.mkdir()
        (self.project / "export_presets.cfg").write_text(
            '[preset.0]\nname="Web"\nplatform="Web"\nrunnable=true\n\n'
            '[preset.0.options]\nhtml/canvas_resize_policy=1\nvariant/thread_support=false\n'
            'vram_texture_compression/for_mobile=false\ncustom_template/release=""\n', encoding="utf-8")
        self.capture = self.root / "capture.png"
        self.capture.write_bytes(b"fixture-capture")
        self.server = None
        self.addCleanup(self.cleanup_handler)

    def cleanup_handler(self):
        serve.GodotHandler.runtime_instance_id = ""
        serve.GodotHandler.cross_origin_isolation = False
        if self.server is not None:
            self.server.shutdown()
            self.server.server_close()

    def start(self, instance_id: str):
        serve.GodotHandler.runtime_instance_id = instance_id
        serve.GodotHandler.cross_origin_isolation = False
        handler = functools.partial(serve.GodotHandler, directory=str(self.web))
        self.server = serve.http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return f"http://127.0.0.1:{self.server.server_address[1]}/"

    def browser(self, url: str):
        return {
            "schemaVersion": 1,
            "url": url,
            "buildId": (self.web / "BUILD_ID.txt").read_text().strip(),
            "engineStarted": True,
            "normalPathPass": True,
            "isSecureContext": False,
            "crossOriginIsolated": False,
            "missingFeatures": [],
            "consoleFatalErrors": [],
            "audioAfterGesture": True,
            "glyphsOk": True,
            "replacementGlyphsDetected": False,
            "textOverflowDetected": False,
            "primaryControlClickable": True,
            "canvas": {"cssWidth": 960, "cssHeight": 540, "backingWidth": 960, "backingHeight": 540,
                       "devicePixelRatio": 1, "viewportWidth": 960, "viewportHeight": 540,
                       "fullyVisible": True, "clipped": False},
            "capture": {"path": str(self.capture), "sha256": sha256_file(self.capture)},
        }

    def record(self, url: str, instance_id: str):
        return {
            "schemaVersion": 1,
            "status": "SERVING",
            "processId": 123,
            "instanceId": instance_id,
            "buildId": (self.web / "BUILD_ID.txt").read_text().strip(),
            "lanUrl": "https://192.168.1.20:8443/",
            "localUrl": url,
            "serverScriptSha256": sha256_file(ROOT / "scripts" / "serve_web_export.py"),
            "webHelperSha256": sha256_file(ROOT / "scripts" / "_web.py"),
        }

    def test_preflight_binds_observed_server_instance(self):
        url = self.start("instance-good")
        result = preflight.validate(self.web, url, "WEB_SHARE", self.browser(url),
                                    project_root=self.project, runtime_record=self.record(url, "instance-good"))
        self.assertEqual(result["status"], "PASS", result["errors"])
        self.assertTrue(result["requirements"]["runtimeInstanceBound"])

    def test_old_process_or_edited_server_cannot_reuse_runtime_record(self):
        url = self.start("instance-live")
        old = self.record(url, "instance-old")
        result = preflight.validate(self.web, url, "WEB_SHARE", self.browser(url),
                                    project_root=self.project, runtime_record=old)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("X-GPS-Instance-ID" in item for item in result["errors"]))
        current = self.record(url, "instance-live")
        current["serverScriptSha256"] = "0" * 64
        result = preflight.validate(self.web, url, "WEB_SHARE", self.browser(url),
                                    project_root=self.project, runtime_record=current)
        self.assertTrue(any("serverScriptSha256" in item for item in result["errors"]))


if __name__ == "__main__":
    unittest.main()
