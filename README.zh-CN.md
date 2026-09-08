# Godot Prototype Studio 0.5.0

[English](README.md) · [中文](README.zh-CN.md)

把一个想法做成小而完整的 Godot 2D 原型或接近发行品质的切片。0.5.0 在 0.4.4“完成度、交付形式、证据分离”的基础上增加两条强智能体工作流：所有新原型都进行一次性的视觉参考约定；对新玩法则使用机制实验流程，主动寻找并证伪真正改变决策关系的玩法，而不是只给熟悉循环换皮。

技能保持模型无关。它允许能力较强的智能体自行决定普通实现细节、操作 Godot、读取运行状态和截图、比较变体并修复失败；但模型不能用自己的评价证明玩法好玩、历史原创、像素级一致或玩家偏好。

## 首轮视觉参考约定

每个新原型或重大视觉改造，在锁定美术方向前只处理一次视觉参考方式。

如果用户尚未提供可用参考图，主动要求提供 1—3 张，并选择：

- `PARTIAL_REFERENCE`：只参考明确指定的部分，例如构图、镜头、比例、配色、界面层级、材质、光照、动画节奏或特效；未指定部分保持原创。
- `PIXEL_ACCURATE_REFERENCE`：按明确声明的画面和分辨率进行像素级参考。记录目标状态、镜头、裁切、视口、可用素材/字体、允许差异，以及所有权或复制授权。
- `ORIGINAL_DELEGATED`：用户不提供参考图，并授权智能体建立原创视觉基准。
- `NOT_APPLICABLE`：仅用于视觉确实与结果无关的任务，或明确允许保持诊断灰盒的实验。

如果用户已经上传参考图，不再要求重复上传，只询问它们是局部参考还是像素级参考，以及每张图具体控制什么。用户已经说明模式和范围时直接继续，不重复提问。

像素级匹配只对声明的画面和视口成立。叠图或像素差分可以作为证据，但一张截图不能证明动画、交互、战斗中可读性、响应式布局或其他宽高比。第三方受保护表达的复制权不明确时，停止精确复制，但可以继续采用不受保护的局部原则或原创玩法方案。

参见[视觉参考入口](references/visual-reference-intake.md)、[美术方向](references/art-direction.md)和[素材与视觉](references/assets-and-visuals.md)。

## 新玩法工作流

新机制按“玩家看到什么、决定什么、做什么、改变什么，以及下一步能做什么是否发生因果变化”来判断。换题材、增加内容、修改奖励数字或更换特效，本身不算玩法创新。

默认流程保持精简：

1. 用“信息 -> 约束下的行动 -> 状态/关系变化 -> 反馈 -> 下一次决策变化”写出机制命题。
2. 指定一个易理解的参考玩法、一个主要因果变化、保持不变的部分和最小证伪条件。
3. 做“去主题测试”：去掉故事、美术、名称、奖励和内容量后，差异仍应存在。
4. 在生产前推演少量具体回合，检查反事实选择、状态后果、可教学性、恢复路径，以及连点/等待/单一动作是否形成支配策略。
5. 在 Godot 中先做最短、可重复玩的机制内核，并暴露合法动作、状态变化、结果原因、机会次数、时间边界以及可重复场景或种子。
6. 让智能体通过真实输入反复执行“复现 -> 看状态/截图 -> 找到负责规则 -> 修改 -> 重跑”。
7. 只在场景、美术可读性、机会数、平台和输入条件等基本一致时比较因果不同的版本。
8. 条件允许时，用可玩的版本进行小规模真人比较来判断手感和偏好；没有真人证据时，不宣称已验证好玩。

结论强度只使用：`DISTINCT_IN_THIS_PROJECT`、`DISTINCT_AMONG_VERIFIED_REFERENCES`、`HISTORICALLY_NOVEL`。最后一种必须经过专门、广覆盖的检索；模型自信度不是证据。

参见[新玩法发现](references/novel-gameplay.md)、[任务工作流](references/workflow.md)、[变体实验](references/variant-experiments.md)和可选的[机制实验模板](templates/mechanic_lab.md)。

## 完成度、交付与证据

完成度、运行平台/交付形式和证据分开决定。用户要求完成一个可玩或高完成度原型且没有更窄的质量目标时，默认使用 `NEAR_RELEASE_SLICE`：一局范围有限但完整，玩法、美术、界面、运动/音频、失败恢复和真实输入形成一个整体。高完成度**不自动要求**源码 ZIP 或 Web 导出。用户未指定包形式时，默认交付经过测试的原地 Godot 项目；只有请求相应运行平台或接收方式时，才增加 `GODOT_PROJECT_ZIP`、`WEB_EXPORT`、`DESKTOP_BUILD`、`ANDROID_BUILD` 或 `LAN_SHARE`。

如果 Web 被选为交付物，仍必须通过 HTTP 服务并在浏览器中实际检查。只有另一台设备或另一位接收者需要时才做局域网分享。公开托管/发布、付费、上传隐私数据、破坏性变更和第三方视觉表达的精确复制仍保留授权边界。

新项目在出现一个角色、一段必需语言文本、一个按钮和一个声音后，就立即执行第一次目标端冒烟，不等完整关卡。生成大批美术前，先检查一个真实样本的透明通道、锚点、尺寸、遮挡和动作。持续维护短会话状态，使中断后的工作从现状继续，而不是重新开始。

一份任务简报负责验收和授权。可选的机制实验记录只保存发现过程，不成为第二份验收合同。真人试玩不是所有交付的硬门槛，但没有真人证据时不得宣称目标玩家的乐趣或偏好已验证。

## 可选工具

附带脚本使用 Python 3。素材检查工具及对应测试依赖 Pillow，需要由环境提供。工具不会自行安装依赖、发布到公网或调用付费服务。

```bash
python scripts/init_workspace.py PROJECT
python scripts/init_workspace.py PROJECT --novel-gameplay
python scripts/init_workspace.py PROJECT --with-starter --novel-gameplay
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

初始化器默认只生成任务简报和进度记录；`--novel-gameplay` 额外生成 `.prototype/spec/mechanic_lab.md`；`--legacy-full` 保留详细的旧式记录。已有文件不会被覆盖。以上命令是示例，不是固定执行顺序。

`run_godot_checks` 退出码：0 通过，1 失败，2 无法/无效执行，3 部分完成。静态和无头测试不能证明真实交互、画面品质、声音输出、像素一致性、原创性或玩家乐趣。

## 证据与界限

`DONE` 要求所请求的产物及其适用证据都成立。真正无法满足的必要能力或缺陷记为 `BLOCKED`，同时交出当前最强的已验证结果和明确的解锁条件。

如果选择 Web 交付，继续保留 0.4.4 的规则：首个目标端冒烟、显示适配/可点击性检查、BUILD_ID、源码与 Web 分离哈希，以及浏览器中的真实玩家路径验证。接近发行的 Web 验证可以在本机服务上完成；非回环的局域网路线使用 HTTPS。源码暂存不得包含生成的 `export/web`。

校验器只检查结构、记录、哈希和基本媒体签名；不能证明日志真实、场景好看、画面像素级一致、玩法具有历史原创性、评审独立，或玩家觉得好玩。注入状态可以加快诊断，但不能证明玩家正常路径可到达。

## 维护

```bash
python -m unittest discover -s tests -v
```

参见[0.5.0 升级审计](audit/novel-gameplay-upgrade.md)、[强智能体过度约束审计](audit/gpt6-overconstraint-audit.md)、[研究依据](references/research-basis.md)、[行为场景](tests/scenarios.md)和[工具约定](references/tool-contracts.md)。现有测试属于工具夹具和静态指令检查，不是真实的 Godot、GPT-6/Astra、Codex、浏览器或目标玩家试玩。
