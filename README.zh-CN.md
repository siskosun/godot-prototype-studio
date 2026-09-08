# Godot Prototype Studio 0.4.4

[English](README.md) · [中文](README.zh-CN.md)

当用户要求交付可玩、完成度较高的结果时，把一个想法做成小而完整、接近发行品质的 Godot 2D 切片。机制探针、灰盒、技术验证和局部修复保持各自原有范围。完成度、运行平台/交付形式和证据要分开判断：高完成度并不自动等于源码 ZIP 加 Web 导出。接近发行的路径覆盖完整设计、尽早的目标端冒烟、一体化品质样例、完整一局、美术/体验/手感、真实输入、修复，以及对所要求产物的实测交付。它不承诺完整商业游戏，也不承诺已验证的受众喜好。

## 使用

加载 `SKILL.md`，不要整目录预读参考文档。通过宿主支持的导入流程替换旧技能包；仅打包并不会把它安装进账号。保留项目文件和历史。更新后的归档只包含这一份技能。

示例请求：

> 把这个想法做成接近发行品质的 Godot 切片：[想法]。范围要小但完整。核对最接近的已发行游戏，改进设计，并在该想法内自行选择可逆细节。继续完成美术、用户体验、玩法调校、真实操作、修复、最终 Web 导出/浏览器检查和打包。只在完成或真正受阻时停止。

明确要求先批准简报、用户保留的美术决定、粗糙实验、定向修 bug，以及指定平台，均优先于默认策略。完成度较高的委托，默认按所要求的运行平台做到接近发行的完成度。只有用户要求交接源码包或网页时，才增加源码 ZIP 或 Web 导出；选定的 Web 产物必须经 HTTP 服务并在浏览器里检查显示适配和像素预算。只有接收方需要时，才做局域网分享。付费、公开托管/发布、上传隐私数据和破坏性变更，仍需既有授权。默认不需要付费后端或外部框架。

## 要品质，不要加流程

一份简报负责验收和授权；一份进度记录用于中断恢复。最终的接近发行审查按该简报覆盖九个维度：玩法、体验、美术、运动/音频、可靠性、性能、平台/访问、文本渲染、交付/权利。适用维度必须 `PASS`；确实不存在的要求可以记为 `NOT_APPLICABLE` 并写明简报依据；拿不到的证据记为 `UNVERIFIED`，不能用来宣称接近发行已完成。品质样例必须是可运行场景，不是一张概念图。

只在相关时读取对应参考。引擎情报、风险测试、回放、自动策略和变体是按需工具，不是强制审批关卡。真人试玩默认不阻断交付；没有真人证据时，必须明确写明玩家体验尚未验证。

## 可选工具

附带脚本使用 Python 3。素材检查工具和对应测试模块依赖 Pillow，需由环境自行提供。局域网服务器可以使用已有证书/密钥，或用 `openssl` 生成短期自签名开发证书。这些工具不会安装依赖、不会发布到公网、也不会调用付费服务。缺少 Pillow 时，完整回归套件不算全部通过。

```bash
python scripts/init_workspace.py PROJECT
python scripts/detect_capabilities.py PROJECT --write
python scripts/run_godot_checks.py PROJECT --mode import
python scripts/inspect_engine_context.py PROJECT --write
python scripts/inspect_asset_set.py MANIFEST --root PROJECT --contact-sheet REVIEW.png
python scripts/stamp_web_build.py export/web
python scripts/serve_web_export.py export/web
python scripts/web_preflight.py export/web --url http://127.0.0.1:8000/ --profile FIRST_TARGET --browser-report BROWSER.json --project-root PROJECT --require-glyphs --require-audio
python scripts/web_preflight.py export/web --url http://127.0.0.1:8000/ --profile NEAR_RELEASE --browser-report BROWSER.json --project-root PROJECT --max-backing-width 1920 --max-backing-height 1080
python scripts/package_and_report.py PROJECT --out release
python scripts/change_impact.py --before-tree OLD --after-tree NEW
python scripts/validate_quality_review.py REVIEW.json --artifact ARTIFACT
python scripts/validate_release_evidence.py ARTIFACT --evidence RELEASE.json
```

这些是示例，不是固定顺序。`run_godot_checks` 退出码：0 通过，1 失败，2 无法/无效执行，3 部分完成。它不会覆盖全部真实输入、渲染/音频路径或目标导出。可选 starter 只是检测夹具，不是成品游戏或美术模板。

## 证据与界限

`DONE` 要求所请求的产物及其必要品质/证据都成立。真正无法满足的必要能力或缺陷记为 `BLOCKED`，同时交出可用的部分结果和明确的解锁条件。保留最初失败痕迹和最终复测身份。项目 ZIP 必须与干净的实测目录一致。选定的 Web 构建必须从冻结的最终源码导出、盖上 BUILD_ID，并在浏览器里走完要求的玩家路径，包括 CSS 显示适配和可点击性。接近发行的 Web 验证可以在本机 HTTP 服务上进行；非回环/局域网地址使用 HTTPS。只有该路线真正属于交付时，局域网分享才额外检查安全上下文、证书、防火墙和网络。源码和 Web 哈希分开记录。最终源码 ZIP/暂存不得包含生成的 `export/web`；校验器会拒绝源码与 Web 混在一起的身份。接近发行的品质审查绑定到所选的玩家向产物。

校验器只检查记录、文件、哈希一致性和基本媒体签名；不能证明日志真实、画面好看、评审独立，或玩家觉得好玩。不要把自我审查写成真人证据，也不要把注入状态写成玩家正常可到达。

## 维护

```bash
python -m unittest discover -s tests -v
```

参见[升级审计](audit/upgrade-audit.md)、[强智能体过度约束审计](audit/gpt6-overconstraint-audit.md)、[研究依据](references/research-basis.md)、[行为场景](tests/scenarios.md)和[工具约定](references/tool-contracts.md)。现有测试是工具夹具和静态指令审查，不是真实的 Godot/Codex 或目标玩家试玩。在实际部署环境里再跑对应的引擎验收。
