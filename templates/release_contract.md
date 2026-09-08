> Optional detailed record. The mission brief remains authoritative; this template does not create another approval stage.

# Release Contract

- DeliveryTarget: GODOT_PROJECT_ZIP+WEB_EXPORT | LOCAL_PROJECT | GODOT_PROJECT_ZIP | DESKTOP_BUILD | WEB_EXPORT | ANDROID_BUILD
- WebShareMode: LOCAL_WEB_TEST | WEB_SHARE | LAN_SHARE | N/A
- TargetPlatformAndArchitecture:
- GodotVersion:
- ExportTemplateVersion:
- SourceBaselineCommitOrHash:
- SourceArtifactPathAndHash:
- WebArtifactPathAndHash:
- ExportPreset:
- RequiredAddonsAndExternalTools:
- EntrypointOrExecutable:
- Exact OpenInstallOrServeInstructions:
- Final SmokeOrPlaythroughMethod:
- EvidencePaths:
- KnownEnvironmentOrPlatformLimitations:

## Web handoff
- WebEntrypoint: index.html
- BuildID:
- WebServeCommand: [serve_web_export.py command; HTTPS LAN URL, not file://]
- WebPreflightCommand:
- BrowserSmokePath: [launch -> normal input -> complete/reset/retry path]
- RequiredTextScriptsOrLocales:
- AudioExpectedAfterGesture: yes | no
- ThreadSupport: false | true [true requires cross-origin isolation]
- MobileVRAMCompression: false | true [true only for an explicit ETC2/ASTC-capable target/import path]
- WebProjectRootAndPreset: [project root + exact Web preset used by WEB_PREFLIGHT]
- CanvasPolicyOrBackingPixelBudget:
- LANReceiverInstructions: [certificate trust/secure-context check, firewall, same network, hard refresh]
