# evan-llm-wiki

[English](./README.md) | 简体中文

一个通用、以 Markdown 为核心、由 AI Agent 维护的 LLM Wiki 工具集，灵感来自 Karpathy 的 `llm-wiki` 方案。

它不把知识库当成一次性的向量分块缓存，而是在目标项目中初始化一套分层的 Markdown 知识库结构，并驱动一条确定性的“单源逐条维护”流水线：

1. 扫描 `raw/_sources/` 下的原始来源，在 `wiki/_system/manual_queue.json` 生成纯文件任务队列。
2. 每次取出一个 `pending` 任务，使用固定提示词模板（`wiki/_system/manual_runner_prompt.txt`）调用 `codex exec`。
3. 由 Codex 直接阅读主源文件（以及影响理解的本地截图、图表、架构图），手动提炼并更新 `wiki/` 下的页面。
4. 将队列状态、导航索引（`wiki/index.md`）与变更日志（`wiki/log.md`）全部保存在纯文本文件中。

## 目标项目假设与核心规范

本工具基于 Python 3 标准库实现，仅要求目标项目按约定的 `raw/`（只读原始输入）与 `wiki/`（可演进知识产物）目录组织内容。

### 初始化后的目标项目结构

执行 `init` 会在 `--project-root` 下创建以下脚手架：

```text
<project-root>/
├── AGENTS.md                         # 核心 Wiki 维护规范（供 Codex 读取）
├── CLAUDE.md                         # Claude Code 规则入口（指向 AGENTS.md）
├── .codex/skills/llm-wiki/SKILL.md   # `codex exec` 摄入阶段使用的 Skill
├── schema/
│   ├── policy.md                     # Frontmatter 元数据、来源归因与正文结构规范
│   └── workflows.md                  # Ingest / Query / Lint 工作流定义
├── raw/
│   ├── _sources/                     # 只读原始来源（目录或单文件）
│   └── _attachments/                 # 本地附件（图片、PDF、CSV 等）
└── wiki/
    ├── 00_overview/                  # 总览页
    ├── 01_entities/                  # 高频实体页（人物、工具、库、组织等）
    ├── 02_concepts/                  # 跨来源沉淀的稳定概念页
    ├── 03_sources/                   # 每个已处理来源对应的摘要页
    ├── 04_projects/                  # 项目级综合页
    ├── 05_decisions/                 # 结论、权衡与 Lint 修复任务页
    ├── _system/
    │   ├── manual_queue.json         # `--rebuild-queue` 生成的队列状态文件
    │   └── manual_runner_prompt.txt  # 每次调用渲染的提示词模板
    ├── index.md                      # 人工/Agent 维护的导航索引
    └── log.md                        # 按时间追加的维护日志
```

### 来源发现与写作约束

- **支持的来源格式**：`raw/_sources/` 下的子目录（按顺序优先选取 `README.md`、`index.md`、`content.md`、`raw.md`、`raw.txt`、`raw_content.html` 作为主文件，否则取首个 `.md`/`.markdown`/`.txt`/`.html`/`.htm` 文件），或直接放在 `raw/_sources/` 顶层的 `.md`/`.markdown`/`.txt`/`.html`/`.htm` 文件。
- **只读 Raw 层**：严禁在维护 Wiki 时修改 `raw/` 下任何文件。
- **单一主来源归因**：页面 frontmatter 的 `sources` 字段优先只列一个人类可读的主源文件（存在 `README.md` 时仅写 `README.md`）；HTML、JSON 或附件仅作辅助阅读。
- **图片查验**：若来源目录包含影响语义判断的截图、图表或架构图，写入前必须先读取核对，禁止凭空编造。
- **手工综合而非模板套壳**：`wiki/` 页面必须基于精读内容编写，禁止用脚本批量生成内容或机械搬运来源标题。
- **中断恢复**：队列状态在 `pending` → `in_progress` → `done` / `failed` 间流转；若上一次运行中途退出，遗留的 `in_progress` 项会在下次启动时自动重置为 `pending`。

## 环境要求

- **Python 3**（CLI 与队列调度脚本仅依赖标准库）
- **Codex CLI**（`PATH` 中需包含支持 `codex exec` 的 `codex` 命令；使用 `--dry-run` 预览命令时无需实际调用）

## 快速开始

在克隆本仓库后按以下步骤使用：

### 1. 初始化目标项目

```bash
python3 scripts/llm_wiki_cli.py init --project-root /path/to/project
```

默认情况下已存在的文件不会被覆盖；如需重置规则、Schema 或模板文件，可附加 `--force`。

### 2. 放入原始资料

将待整理资料放入 `/path/to/project/raw/_sources/`：
- 每个来源一个子目录，内含 `README.md`、`index.md`、`content.md`、`raw.md`、`raw.txt` 或 `raw_content.html`（可附带图片/附件）；或
- 直接放置 `.md`、`.markdown`、`.txt`、`.html`、`.htm` 文件。

### 3. 重建队列并 Dry-Run 验证

> **CLI 入口说明**：[`scripts/llm_wiki_cli.py`](./scripts/llm_wiki_cli.py) 目前提供 `init` 与基础 `run --run-once` / `run --run-all`。队列重建与过滤参数（`--rebuild-queue`、`--dry-run`、`--retry-failed`、`--only-source-id`、`--limit`、`--model`、`--codex-arg` 及自定义路径）请直接通过 [`scripts/llm_wiki_runner.py`](./scripts/llm_wiki_runner.py) 调用。

```bash
# 扫描 raw/_sources/ 并重建 wiki/_system/manual_queue.json
python3 scripts/llm_wiki_runner.py --project-root /path/to/project --rebuild-queue

# 预览下一条将执行的 Codex 命令（不修改队列状态，也不实际执行）
python3 scripts/llm_wiki_runner.py --project-root /path/to/project --run-once --dry-run
```

### 4. 执行 Wiki 维护

```bash
# 仅处理一条待办来源
python3 scripts/llm_wiki_cli.py run --project-root /path/to/project --run-once

# 连续处理直到队列清空
python3 scripts/llm_wiki_cli.py run --project-root /path/to/project --run-all

# 重试失败项，或指定单个 source_id
python3 scripts/llm_wiki_runner.py --project-root /path/to/project --run-once --retry-failed
python3 scripts/llm_wiki_runner.py --project-root /path/to/project --run-once --only-source-id example-source
```

[`scripts/llm_wiki_runner.py`](./scripts/llm_wiki_runner.py) 支持的其他常用参数：
- `--model <name>`：向 `codex exec` 透传 `--model <name>`
- `--codex-arg <arg>`：向 `codex exec` 透传额外参数（可重复指定）
- `--limit <n>`：配合 `--rebuild-queue` 限制入队条目数量
- `--source-root`、`--wiki-root`、`--queue-file`、`--prompt-template`：覆盖默认路径

## 仓库结构与文档索引

### 现有实现与模板文件

| 路径 | 用途 |
|---|---|
| [`scripts/llm_wiki_cli.py`](./scripts/llm_wiki_cli.py) | 统一 `llm-wiki` CLI 入口（支持 `init` 与 `run` 子命令） |
| [`scripts/init_llm_wiki.py`](./scripts/init_llm_wiki.py) | 目标项目脚手架初始化脚本（可独立运行） |
| [`scripts/llm_wiki_runner.py`](./scripts/llm_wiki_runner.py) | 来源扫描、原子写队列 JSON、提示词渲染与 `codex exec` 调度器 |
| [`AGENTS.md`](./AGENTS.md) | 随脚手架分发的核心 Wiki 维护规范、归因原则与反模式约束 |
| [`CLAUDE.md`](./CLAUDE.md) | Claude Code 适配说明（指向 `AGENTS.md`） |
| [`.codex/skills/llm-wiki/SKILL.md`](./.codex/skills/llm-wiki/SKILL.md) | 单源摄入阶段供 Codex 调用的 Skill 定义 |
| [`schema/policy.md`](./schema/policy.md) | YAML Frontmatter、正文结构顺序与图片读取规范 |
| [`schema/workflows.md`](./schema/workflows.md) | `Ingest`、`Query`、`Lint` 三大核心工作流定义 |
| [`llm-wiki-design.md`](./llm-wiki-design.md) | 基于 Karpathy 思路的完整方案设计文档（中文） |
| [`docs/usage.md`](./docs/usage.md) | 命令行用法与写作预期说明 |
| [`tests/`](./tests/test_cli_dispatch.py) | 入口回归测试（[`test_cli_dispatch.py`](./tests/test_cli_dispatch.py)、[`test_init_entrypoint.py`](./tests/test_init_entrypoint.py)、[`test_runner_entrypoint.py`](./tests/test_runner_entrypoint.py)），可使用 `pytest` 运行 |

### 路线图与待实现设计文档

[`docs/todo.md`](./docs/todo.md) 维护项目待办事项。`docs/` 下各子目录为对应功能的分步实施计划（除 `llm_wiki_cli.py` 已落地基础调度外，其余尚在规划中）：

- [`docs/cli-entrypoint/README.md`](./docs/cli-entrypoint/README.md) — 统一 CLI 入口改造方案
- [`docs/queue-status-commands/README.md`](./docs/queue-status-commands/README.md) — 规划中的 `status` / `next` / `failed` / `history` 队列查看命令
- [`docs/doctor-command/README.md`](./docs/doctor-command/README.md) — 规划中的 `doctor` 目录与环境诊断命令
- [`docs/incremental-ingest-hashing/README.md`](./docs/incremental-ingest-hashing/README.md) — 规划中的基于内容哈希的增量跳过机制
- [`docs/source-processing-metadata/README.md`](./docs/source-processing-metadata/README.md) — 规划中的单源处理元数据持久化
- [`docs/queue-locking/README.md`](./docs/queue-locking/README.md) — 规划中的 `os.O_EXCL` 单写者文件锁保护
- [`docs/structured-run-logs/README.md`](./docs/structured-run-logs/README.md) — 规划中的 `run_history.jsonl` 结构化运行日志
- [`docs/wiki-lint-command/README.md`](./docs/wiki-lint-command/README.md) — 规划中的 `lint` 健康检查命令
