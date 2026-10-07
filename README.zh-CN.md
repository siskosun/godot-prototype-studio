# Godot Prototype Studio 1.0.5

[English](README.md) | [中文](README.zh-CN.md)

## 1.0.5：设计与源码的局部修复闭环

新增可选的 `design_map.json`，把设计对象、交互规则、负责源码和测试场景连接起来。检查失败后，工具给出需要调查的局部文件；修改后要求同一测试命令复测。它只提供实现证据，人工 Review、实验选择和不可变发布仍由现有流程负责。

新项目可用 `python scripts/init_workspace.py PROJECT --with-starter --design-map` 生成示例。现有项目需要把示例里的对象、源码路径、唯一锚点和失败标记改成实际内容；小修复不必创建映射。直接使用时：

```bash
python scripts/design_repair.py validate PROJECT --map PROJECT/.prototype/spec/design_map.json
python scripts/run_godot_checks.py PROJECT --mode all --design-map PROJECT/.prototype/spec/design_map.json
python scripts/design_repair.py plan PROJECT --map PROJECT/.prototype/spec/design_map.json --report PROJECT/.prototype/evidence/godot-checks/report.json --write PROJECT/.prototype/evidence/repair-before.json
```

保存计划后，只修改已经确认负责故障、且在授权范围内的源码。重新运行同一 `run_godot_checks.py` 命令，再检查：

```bash
python scripts/design_repair.py verify PROJECT --map PROJECT/.prototype/spec/design_map.json --plan PROJECT/.prototype/evidence/repair-before.json --report PROJECT/.prototype/evidence/godot-checks/report.json --write PROJECT/.prototype/evidence/repair-after.json
```

`LOCAL_REPAIR_VERIFIED` 表示局部文件改动与同命令检查相符。运行时对象绑定、真实玩家输入、浏览器表现和好玩程度仍需要各自的证据。旧报告、未知错误、环境故障、修改测试文件或替换测试命令都不能据此证明修复。

详见[操作与边界](references/design-repair-loop.md)和[Code2Games 逐项映射](audit/code2games-2026-10-07.md)。本次没有引入 Blender、UE5、模型服务或自动裁决。

1.0 是一次收敛版升级，不再继续叠加流程。Godot 已被用户、现有项目或 game-exp 选定时，GPS 直接使用 Godot，不再主动比较 H5；只有技术栈真正开放时才做路线比较。

## 1.0.2–1.0.4

- **1.0.2：**新增 game-exp `iteration_delivery` 返回契约，说明可玩交付状态、玩家可见变化、人工关注点和生产者／构建身份。
- **1.0.3：**兼容的 Godot Web 构建可发布到公开仓库的 GitHub Pages，保留 `play/<result_source_sha>/` 下的不可变版本。部署 URL 仍需通过 WEB_PREFLIGHT 和真实浏览器输入检查，才能声明 `SHAREABLE_URL verified=true`。
- **1.0.4：**改用 game-exp 管理的 GitHub Actions Pages 工作流，绑定所请求版本的准确运行，部署成功后核验实际页面与不可变标记。

完整变化见 [CHANGELOG](CHANGELOG.md)。交付证据仍为实现方自报，不代替人工 Review 或实验生命周期裁定。

## 1.0.1

当技术栈已经确定为 H5 时，GPS 明确把“玩家体验目标、路由决定、复用检索结论”交给 `h5-game-prototype-agent`，不在 GPS 内维护第二套 H5 流程。运行时打包同时改为严格白名单，避免临时测试输出混入 `skill.zip`。

## 1.0.0

- 修复 QA 只能录到 `InputEventAction` 的问题：真人键盘、手柄等 InputMap 映射输入现在会被记录，并保存输入事件来源。
- 普通正式版中关闭 QA 场景控制、输入注入和回放入口；starter 明确最低 Godot 4.3+。
- Godot 相关 Python 子进程统一按 UTF-8 容错解码，补 Windows CI。
- 新增 game-exp 托管模式：game-exp 管 Ledger、Manifest、生命周期、Candidate 与人工门；GPS 只管实现和证据，不重复做晋级系统。
- 移除核心规则里对 GPT-6/Astra 等特定模型索引的绑定，复用来源改为可配置发现源。
- 新增 Godot 4.3+ 实操手册，覆盖 InputMap、Control 焦点、TileMapLayer、Tween、无头测试、Web 导出和常见故障。
- 精简运行时 `SKILL.md`；发布 `skill.zip` 排除 audit、tests、CHANGELOG、研究历史和维护文档。
- 测试文件由版本号改为按功能命名。

尚未宣称完成旧版与 1.0 的“同模型、同预算、7 个代表任务”效果对照。现有回归只能证明工程契约与工具行为，没有证明创作效果提升。

把一个想法做成小而完整的游戏原型或接近发行品质的切片：默认擅长 Godot 2D，但当简单 H5 明显更合适时先让用户选择技术路线。本版保留 0.5.0 的基础：0.5.0 在 0.4.4“完成度、交付形式、证据分离”的基础上增加两条强智能体工作流：所有新原型都进行一次性的视觉参考约定；对新玩法则使用机制实验流程，主动寻找并证伪真正改变决策关系的玩法，而不是只给熟悉循环换皮。

技能保持模型无关。它允许能力较强的智能体自行决定普通实现细节、操作 Godot、读取运行状态和截图、比较变体并修复失败；但模型不能用自己的评价证明玩法好玩、历史原创、像素级一致或玩家偏好。

## 0.8.0 升级内容

本版保留 0.7 的技术路线、复用和多人/LAN 验证能力，重点补上“功能能跑”和“目标游戏体验真的成立”之间的缺口。

- **按需维护体验脊柱**：只有跨系统、反复迭代时，才保留玩家承诺、核心张力/核心动作、实际存在的循环层、设计支柱和明确非目标，用于防止局部优化把整个游戏做偏；不建立第二套 GDD，也不强制成长或 Meta。
- **把体验判断变成可证伪假设**：按“设计意图 -> 可观察玩家行为 -> 正确运行时行为 -> 真人体验证据”推进。模型评价、机器人策略或逻辑测试通过都不能证明好玩。
- **关键玩法规则验证过程而非只看终态**：当中间状态违规也会影响体验时，定义可观察行为契约与相关 tick/状态迁移不变量，用代表场景加有意义的扰动验证；核心要求采用全通过，不用平均通过率掩盖单项失败。
- **关键自动评测先证明自己会失败**：如果评测器会实质决定验收，用独立的故意错误夹具或 mutant 验证它确实能拒绝错误实现；小改动不强制套这套流程。
- **真人试玩以行为观察为主**：提前定义会改变决策的问题，记录冷启动行为、犹豫、预期落差、策略变化和恢复路径，并分开记录观察、玩家陈述、运行事实与解释。不采用固定 5 人、3/5 投票门槛或根据表情直接推断情绪的硬规则。

参见[体验验证闭环](references/experience-validation-loop.md)、[运行时逻辑验证](references/runtime-logic-verification.md)和[0.8.0 升级审计](audit/v0.8.0-experience-validation.md)。0.7 的技术路线、复用和多人验证规则继续有效。

## 0.9.0：可复现评测接口

本版新增一个小型 Evaluation Interface，用于在固定条件下记录和回放操作，但不把“智能体会玩”包装成“真人体验证据”。

- Replay Trace v1 记录场景、种子控制方式、按 physics frame 偏移的命名输入动作。
- 区分场景自己控制随机数的 `SCENE_CONTROLLED` 与只设置 Godot 全局随机种子的 `GLOBAL_RNG_ONLY`。
- 区分项目自己实现的逐帧控制与普通实时 physics frame 等待；后者不得宣称为确定性手动步进。
- 证据来源明确分为可信流程实际观测、智能体/测试者自报、真人报告。
- 筛查保留“通过 / 产品缺陷失败 / 不确定”三类，测试工具或环境失败不得对产品下结论。
- 2—4 个原型内部变体继续复用现有 `compare_prototypes.py` 与 `MACHINE_DOMINATED`；不引入 Elo 或通用“好玩分”。

参见[评测接口与回放证据](references/evaluation-interface.md)和[游戏 QA / 回放](references/game-qa-and-replay.md)。

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
2. 按需选择易理解的参考玩法，说明主要因果变化或不可分割的组合、不变项与证伪条件；不强行归入既有品类。
3. 去主题测试只移除表面包装，不移除构成玩法的信息、感知或反馈。
4. 在生产前推演少量具体回合，检查反事实选择、状态后果、可教学性、恢复路径，以及连点/等待/单一动作是否形成支配策略。
5. 在选定技术栈中先做最短、可重复玩的机制内核，并暴露合法动作、状态变化、结果原因、机会次数、时间边界以及可重复场景或种子。
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

附带脚本使用 Python 3。素材检查工具及对应测试依赖 Pillow，需要由环境提供。工具不会自行安装依赖、发布到公网或调用付费服务。仓库 CI 会在隔离环境单独准备测试依赖。

```bash
python scripts/init_workspace.py PROJECT
python scripts/init_workspace.py PROJECT --novel-gameplay --reuse-scan
python scripts/init_workspace.py PROJECT --multiplayer
python scripts/init_workspace.py PROJECT --with-starter --novel-gameplay
python scripts/detect_capabilities.py PROJECT --write
python scripts/run_godot_checks.py PROJECT --mode import
python scripts/inspect_engine_context.py PROJECT --write
python scripts/inspect_asset_set.py MANIFEST --root PROJECT --contact-sheet REVIEW.png
python scripts/stamp_web_build.py export/web
python scripts/serve_web_export.py export/web --runtime-record .prototype/evidence/web-server.json
python scripts/web_preflight.py export/web --url http://127.0.0.1:8000/ --profile FIRST_TARGET --browser-report BROWSER.json --project-root PROJECT --require-glyphs --require-audio
# 多人/LAN 需要绑定正在运行的服务实例时，再加 --runtime-record .prototype/evidence/web-server.json
python scripts/web_preflight.py export/web --url http://127.0.0.1:8000/ --profile NEAR_RELEASE --browser-report BROWSER.json --project-root PROJECT --max-backing-width 1920 --max-backing-height 1080
python scripts/package_and_report.py PROJECT --out release
python scripts/change_impact.py --before-tree OLD --after-tree NEW
python scripts/validate_quality_review.py REVIEW.json --artifact ARTIFACT
python scripts/validate_release_evidence.py ARTIFACT --evidence RELEASE.json
```

初始化器默认只生成任务简报和进度记录；`--novel-gameplay` 额外生成 `.prototype/spec/mechanic_lab.md`；`--reuse-scan` 生成开发前复用检索记录；`--multiplayer` 生成多客户端联合验收矩阵；`--legacy-full` 保留详细的旧式记录。已有文件不会被覆盖。以上命令是示例，不是固定执行顺序。

`run_godot_checks` 退出码：0 通过，1 失败，2 无法/无效执行，3 部分完成。静态和无头测试不能证明真实交互、画面品质、声音输出、像素一致性、原创性或玩家乐趣。

## 证据与界限

`DONE` 要求所请求的产物及其适用证据都成立。真正无法满足的必要能力或缺陷记为 `BLOCKED`，同时交出当前最强的已验证结果和明确的解锁条件。

如果选择 Web 交付，继续保留 0.4.4 的规则：首个目标端冒烟、显示适配/可点击性检查、BUILD_ID、源码与 Web 分离哈希，以及浏览器中的真实玩家路径验证。接近发行的 Web 验证可以在本机服务上完成；非回环的局域网路线使用 HTTPS。源码暂存不得包含生成的 `export/web`。

校验器只检查结构、记录、哈希和基本媒体签名；不能证明日志真实、场景好看、画面像素级一致、玩法具有历史原创性、评审独立，或玩家觉得好玩。注入状态可以加快诊断，但不能证明玩家正常路径可到达。

## 维护

```bash
python -m unittest discover -s tests -v
```

单元测试会检查两份 README 的主标题与当前版本段，以及 CHANGELOG 最新版本是否与 `VERSION` 一致。

参见[0.5.0 升级审计](audit/novel-gameplay-upgrade.md)、[强智能体过度约束审计](audit/gpt6-overconstraint-audit.md)、[研究依据](references/research-basis.md)、[行为场景](tests/scenarios.md)和[工具约定](references/tool-contracts.md)。现有测试属于工具夹具和静态指令检查，不是真实的 Godot、GPT-6/Astra、Codex、浏览器或目标玩家试玩。

## 0.6.0 可选连续性检查

在技能目录执行，文件路径相对于 PROJECT。先填写已有简报和计划，再建立检查点。

```bash
python scripts/init_workspace.py PROJECT --with-memory
python scripts/check_project_memory.py PROJECT
python scripts/verification_checkpoint.py freeze PROJECT --plan .prototype/spec/mechanic_lab.md --out .prototype/evidence/review-01.json
python scripts/verification_checkpoint.py check PROJECT --record .prototype/evidence/review-01.json
```

`CURRENT_RECORD` 和 `MATCH` 只表示声明的文件一致，不表示已测试或设计成立。记录过期时重新核对，不自动否决游戏。

仓库 CI 执行工具回归并保存精确源码和日志。0.5.0 基线存在棋盘格测试夹具被初始化覆盖的问题；本版修正准备顺序，不修改检测器或放松断言。CI 不代表真实代理对照测试或真人试玩。

使用宿主支持的技能导入流程安装完整 `skill.zip`。更新 GitHub 或下载文件不等于已安装到账号。
