# 通用 LLM-Wiki 方案（基于 Karpathy 的 llm-wiki 思想）

你要的是可长期积累、可复用、可扩展的知识体系统一方案，而不是“每次问答即时检索后重算答案”。下方方案把知识库设计为**持久化编译产物**，让 LLM 做知识维护，用户做方向与判断。

## 一、核心设计目标

- 让知识随时间增量成长，而非仅靠聊天历史。
- 避免重复人工维护实体关系、引用、矛盾跟踪和版本沉淀。
- 支持个人/团队/项目共用同一结构：只换 Schema 就能迁移到不同领域。
- 保留可审计性：每一次来源接入、模型改写、冲突修正都可追踪。
- 用 Git 作为“事实版本系统”，可回滚、可评审。

## 二、系统三层（从底到顶）

- Raw 层（不可改动）
  - 存放原始输入：文章、论文、会议纪要、代码、邮件、表格、访谈文本、截图文字稿等。
  - 只追加，不直接编辑。
- Wiki 层（可进化）
  - Markdown 文件集，分为主题页、实体页、对比页、方法页、行动清单、总览页。
  - 负责抽象、整合、跨页链接、结论更新、版本化。
- Schema 层（可配置）
  - 定义写作规范、目录规则、元数据格式、工作流（ingest / query / lint / publish）的触发条件与输出模板。
  - 推荐文件：`AGENTS.md`（给 Codex）或 `CLAUDE.md`（给 Claude）。  

## 三、目录建议（通用且可扩展）

```text
llm-wiki/
  raw/
    _sources/           # 原始输入（按来源分类，可加日期前缀）
    _attachments/       # 本地附件：图片、PDF、CSV 等
  wiki/
    00_overview/
    01_entities/
    02_concepts/
    03_sources/
    04_projects/
    05_decisions/
    index.md
    log.md
  schema/
    policy.md           # 写作规范与页内结构
    workflows.md        # 具体操作流程
    prompts.md          # 关键提示词模板
  tools/
    scripts/
      ingest-template.md
      query-template.md
      lint-template.md
  README.md
```

## 四、工作流

- Ingest（摄入）
  1. 将新源文件放入 `raw/_sources/`，补充最小元数据（来源、时间、来源链接、领域标签）。
  2. LLM 读取源文件并输出：
     - `wiki/03_sources/` 下新增该来源摘要页（含信度/假设/局限）。
     - 更新相关实体页与概念页（`01_entities/`, `02_concepts/`）。
     - 更新 `wiki/index.md` 与 `wiki/log.md`。
  3. 若发现冲突：在受影响页建立 `## Conflicts` 区块并标注证据与待确认项。
- Query（查询）
  1. 检索 `wiki/index.md` 与相关分类页，定位候选页面。
  2. 以“可复用工件”返回结果（例如：回答、比较表、决策框架、行动清单）。
  3. 重要问题产出新页面（如 `05_decisions/`）并入库，防止知识只留在聊天记录。
- Lint（健康检查）
  1. 周期性跑 `lint`，让 LLM 检查：
     - 事实冲突/过期信息
     - 孤立页面（无入链）
     - 术语重复定义不一致
     - 源失效与引用缺失
  2. 自动生成 `wiki/05_decisions/2026-xx-xx_lint-report.md`，列出待修复清单与优先级。

## 五、页面结构规范（建议固定）

每个 wiki 页统一前置元数据，便于检索和自动化：

```yaml
---
id: concept/xxx
type: concept|entity|source|decision|comparison
scope: personal|team|project|product
status: draft|stable|deprecated
updated: 2026-04-14
sources: [raw/source-id-1, raw/source-id-2]
confidence: high|medium|low
---
```

正文要求（建议顺序）：

- 定义
- 关键观点
- 证据（按来源）
- 关联（链接到其他 wiki 页）
- 最近修订与争议
- 下一步验证问题

## 六、最小可交付（MVP）

- 第一天可用：手动执行 ingest + 周期性 query + 每周 lint。
- 第一周完善：
  - `index.md` 结构化目录（类别 + one-line summary + linked sources）。
  - `log.md` 可机读日志（固定前缀，如 `## [2026-04-14] ingest | xxx`）。
  - 统一命名规则与最小 prompt（schema）固定下来。
- 第二周：接入检索脚本（`ripgrep` + 文件元数据过滤），再决定是否加向量检索。

## 七、团队化与并发扩展

- 写入冲突规避：一轮 ingest 使用“加锁文件”（`wiki/.lock`）或时间窗口批次提交。
- 变更提交规范：每次 ingest / lint / query 都形成 git commit（可选签名）。
- 权责分离：人负责源头评估与争议裁决，模型负责归档、链接、摘要与清单化。
- 隐私域控制：`raw/` 与 `wiki/` 可按项目设置加密仓库或私有子模块。

## 八、推荐实施顺序（7 天）

1. Day 1：建立目录+Schema+命名规则+3~5个源文件入库验证。
2. Day 2~3：定义实体/概念页模板，完成两类来源的自动 ingest。
3. Day 4：形成查询模版（报告、对比、行动清单）。
4. Day 5：引入 lint 报告并修复第一轮矛盾/孤岛页。
5. Day 6~7：加入日志驱动告警（过期来源、冲突、低置信度）和回溯。

## 九、你可以直接复制给 LLM 的摘要

“你是本知识库的维护者。每次有新来源进入时，必须更新 `wiki/` 中的实体页与概念页、索引和日志；查询要优先检索 index，再给出可追溯答案；每次回答要产出可复用页面；每周执行 lint，修复冲突与失效链接。你只写 wiki，不改 raw，所有变化附来源和时间戳，可回退。”

