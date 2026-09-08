#!/usr/bin/env python3
"""Serve one Godot Web export over LAN HTTPS; this is not public hosting."""
from __future__ import annotations

import argparse
import functools
import http.server
import json
import os
import shutil
import ssl
import subprocess
import tempfile
import threading
from pathlib import Path
from urllib.parse import urlsplit

from _web import detect_lan_ip, read_build_id, web_files


class GodotHandler(http.server.SimpleHTTPRequestHandler):
    cross_origin_isolation = False
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".wasm": "application/wasm",
        ".pck": "application/octet-stream",
    }

    def do_GET(self) -> None:
        parsed = urlsplit(self.path)
        if parsed.path == "/":
            self.path = "/index.html" + (("?" + parsed.query) if parsed.query else "")
        super().do_GET()

    def do_HEAD(self) -> None:
        parsed = urlsplit(self.path)
        if parsed.path == "/":
            self.path = "/index.html" + (("?" + parsed.query) if parsed.query else "")
        super().do_HEAD()

    def list_directory(self, path):  # noqa: ANN001
        self.send_error(404, "Directory listing disabled")
        return None

    def end_headers(self) -> None:
        if self.cross_origin_isolation:
            self.send_header("Cross-Origin-Opener-Policy", "same-origin")
            self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
            self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


class RedirectHandler(http.server.BaseHTTPRequestHandler):
    https_port = 8443
    lan_ip = "127.0.0.1"

    def _redirect(self) -> None:
        target = f"https://{self.lan_ip}:{self.https_port}/"
        self.send_response(302)
        self.send_header("Location", target)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    do_GET = _redirect
    do_HEAD = _redirect

    def log_message(self, fmt, *args):  # noqa: ANN001
        return


def generate_certificate(cert: Path, key: Path, ip: str, days: int) -> None:
    openssl = shutil.which("openssl")
    if not openssl:
        raise ValueError("openssl is required to generate the LAN certificate; provide --cert and --key instead")
    cert.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        openssl, "req", "-x509", "-newkey", "rsa:2048", "-sha256", "-nodes",
        "-keyout", str(key), "-out", str(cert), "-days", str(days),
        "-subj", f"/CN={ip}",
        "-addext", f"subjectAltName=IP:{ip},IP:127.0.0.1,DNS:localhost",
        "-addext", "keyUsage=digitalSignature,keyEncipherment",
        "-addext", "extendedKeyUsage=serverAuth",
    ]
    run = subprocess.run(cmd, text=True, capture_output=True)
    if run.returncode != 0:
        raise ValueError("openssl certificate generation failed: " + (run.stderr.strip() or run.stdout.strip()))
    try:
        os.chmod(key, 0o600)
    except OSError:
        pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export_dir")
    parser.add_argument("--port", type=int, default=8443)
    parser.add_argument("--ip", help="LAN IPv4 address advertised in the URL")
    parser.add_argument("--cert")
    parser.add_argument("--key")
    parser.add_argument("--cert-dir")
    parser.add_argument("--cert-days", type=int, default=7)
    parser.add_argument("--http-redirect-port", type=int, default=0)
    parser.add_argument("--cross-origin-isolation", action="store_true", help="Send COOP/COEP for a threaded Web export")
    args = parser.parse_args()

    temp_cert_dir = None
    try:
        root = Path(args.export_dir).expanduser().resolve()
        web_files(root)
        if (root / "project.godot").exists():
            raise ValueError("refusing to serve a Godot project root; serve the dedicated Web export directory")
        build_id = read_build_id(root)
        if not build_id:
            raise ValueError("BUILD_ID.txt missing; run stamp_web_build.py after the final export")
        ip = detect_lan_ip(args.ip)
        if not (1 <= args.port <= 65535):
            raise ValueError("--port must be 1..65535")
        if bool(args.cert) != bool(args.key):
            raise ValueError("--cert and --key must be supplied together")
        if args.cert:
            cert, key = Path(args.cert).expanduser().resolve(), Path(args.key).expanduser().resolve()
            if not cert.is_file() or not key.is_file():
                raise ValueError("provided certificate/key file missing")
        else:
            if args.cert_dir:
                cert_dir = Path(args.cert_dir).expanduser().resolve()
                cert_dir.mkdir(parents=True, exist_ok=True)
            else:
                temp_cert_dir = tempfile.TemporaryDirectory(prefix="godot-lan-cert-")
                cert_dir = Path(temp_cert_dir.name)
            cert, key = cert_dir / "lan-cert.pem", cert_dir / "lan-key.pem"
            generate_certificate(cert, key, ip, args.cert_days)

        GodotHandler.cross_origin_isolation = bool(args.cross_origin_isolation)
        handler = functools.partial(GodotHandler, directory=str(root))
        server = http.server.ThreadingHTTPServer(("0.0.0.0", args.port), handler)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=str(cert), keyfile=str(key))
        server.socket = context.wrap_socket(server.socket, server_side=True)

        redirect_server = None
        redirect_thread = None
        if args.http_redirect_port:
            if not (1 <= args.http_redirect_port <= 65535) or args.http_redirect_port == args.port:
                raise ValueError("--http-redirect-port must be a different valid port")
            RedirectHandler.https_port = args.port
            RedirectHandler.lan_ip = ip
            redirect_server = http.server.ThreadingHTTPServer(("0.0.0.0", args.http_redirect_port), RedirectHandler)
            redirect_thread = threading.Thread(target=redirect_server.serve_forever, daemon=True)
            redirect_thread.start()

        print(json.dumps({
            "status": "SERVING",
            "scope": "LAN development share; not public hosting",
            "root": str(root),
            "buildId": build_id,
            "lanUrl": f"https://{ip}:{args.port}/",
            "localUrl": f"https://localhost:{args.port}/",
            "certificate": str(cert),
            "crossOriginIsolation": bool(args.cross_origin_isolation),
            "certificateTrust": "Receiver must trust/accept the local certificate and then confirm window.isSecureContext=true.",
            "firewall": f"Allow inbound TCP {args.port} on the trusted LAN if the receiver cannot connect.",
            "httpRedirect": f"http://{ip}:{args.http_redirect_port}/" if args.http_redirect_port else None,
        }, indent=2), flush=True)
        server.serve_forever()
        return 0
    except KeyboardInterrupt:
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "FAIL", "errors": [str(exc)]}, indent=2))
        return 1
    finally:
        try:
            if "redirect_server" in locals() and redirect_server:
                redirect_server.shutdown()
                redirect_server.server_close()
        except Exception:
            pass
        try:
            if "server" in locals():
                server.server_close()
        except Exception:
            pass
        if temp_cert_dir is not None:
            temp_cert_dir.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
