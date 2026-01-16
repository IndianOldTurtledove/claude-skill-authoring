# Claude Skill Authoring + Infrastructure

[中文](README.md) | [English](README_EN.md)

一个教 Claude 写 Skill 的 Skill，**外加完整的 Claude Code 基础设施模板**。

## 这是什么？

这个项目包含两部分：

1. **Skill 编写指南** - 教 Claude 如何按照 [Anthropic 官方最佳实践](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) 编写高效 Skill
2. **基础设施模板** - 开箱即用的 Claude Code 增强功能（hooks、agents、dev docs）

基础设施部分灵感来自 [claude-code-infrastructure-showcase](https://github.com/diet103/claude-code-infrastructure-showcase)。

## 快速开始

### 全局安装（推荐，所有项目生效）

```bash
# 一行命令安装到 ~/.claude/
curl -fsSL https://raw.githubusercontent.com/IndianOldTurtledove/claude-skill-authoring/main/install.sh | bash -s -- --global
```

这会把 hooks 安装到 `~/.claude/hooks/`，对所有项目生效。

### 项目级安装

```bash
# 只对当前项目生效
curl -fsSL https://raw.githubusercontent.com/IndianOldTurtledove/claude-skill-authoring/main/install.sh | bash

# 或克隆后安装
git clone https://github.com/IndianOldTurtledove/claude-skill-authoring.git
cd /path/to/your/project
/path/to/claude-skill-authoring/install.sh --project
```

### 只安装 Skill 编写指南

```bash
# 克隆到全局 skills 目录
git clone https://github.com/IndianOldTurtledove/claude-skill-authoring.git ~/.claude/skills/skill-authoring

# 或克隆到特定项目
git clone https://github.com/IndianOldTurtledove/claude-skill-authoring.git .claude/skills/skill-authoring
```

## 功能一览

### 1. Skill 编写指南

当你询问关于创建或改进 Skills 的问题时，Claude 会自动使用这个 skill。

```bash
# 初始化新 skill
python scripts/init_skill.py my-skill-name

# 验证 skill
python scripts/quick_validate.py path/to/skill/

# 打包分发
python scripts/package_skill.py path/to/skill/
```

### 2. Hooks 系统

事件驱动的自动化钩子，覆盖完整开发生命周期：

| Hook | 事件 | 功能 |
|------|------|------|
| skill-activation-prompt | UserPromptSubmit | 自动分析用户输入，推荐相关 Skills |
| debug-mode-detector | UserPromptSubmit | 智能检测 debug 场景，激活系统化调试流程 |
| investigation-guard | PreToolUse | 强制 "先读后改"，防止盲目修改代码 |
| post-tool-use-tracker | PostToolUse | 追踪文件修改，建议 lint/type 检查命令 |
| verification-guard | Stop | 任务结束前验证代码完整性 |

**工作流程**：

```
用户输入 "又报错了，TypeError on line 42"
    |
    v
[UserPromptSubmit Hooks]
    +---> skill-activation-prompt: 推荐相关 skill
    +---> debug-mode-detector: 检测到 debug 场景 (评分机制)
              |
              v
          输出系统化调试提示:
          "Phase 1: 先调查根因..."
    |
    v
Claude 尝试修改文件
    |
    v
[PreToolUse Hook]
    +---> investigation-guard: 检查是否先 Read 过该文件
              |
              +---> 未调查? 警告/阻止，要求先阅读理解
    |
    v
[PostToolUse Hook]
    +---> post-tool-use-tracker: 记录修改，建议检查命令
    |
    v
任务结束
    |
    v
[Stop Hook]
    +---> verification-guard: 验证 Python 语法，确保代码完整
```

**debug-mode-detector 评分机制**：
- 技术信号：`TypeError`、`line 42`、stack trace → 高分
- 问题词：`报错`、`崩溃`、`bug` → 中分
- 挫败感信号：重复尝试、脏话、`???` → 触发更严格模式
- 累积效应：同一会话多次触发，阈值逐渐降低

### 3. skill-rules.json

集中式的 Skill 触发规则配置：

```json
{
  "skills": {
    "backend-dev": {
      "priority": "high",
      "triggers": {
        "promptTriggers": {
          "keywords": ["API", "backend", "database"],
          "intentPatterns": [".*design.*API.*"]
        },
        "fileTriggers": {
          "include": ["src/api/**/*.py"]
        }
      }
    }
  }
}
```

### 4. Dev Docs 系统

跨会话上下文保留，解决 Claude Code 上下文重置后丢失进度的问题：

```
dev/
├── active/
│   └── feature-xxx/
│       ├── feature-xxx-plan.md      # 战略计划
│       ├── feature-xxx-context.md   # 会话进度（频繁更新！）
│       └── feature-xxx-tasks.md     # 任务清单
└── archive/                         # 已完成任务
```

### 5. Agent 模板

专用代理，用于特定任务：

- **code-reviewer** - 代码审查
- **error-resolver** - 错误自动修复

## 项目结构

```
claude-skill-authoring/
├── SKILL.md                    # Skill 编写指南（主指令）
├── install.sh                  # 一键安装脚本
├── scripts/                    # Skill 工具脚本
│   ├── init_skill.py
│   ├── quick_validate.py
│   └── package_skill.py
├── references/                 # Skill 编写参考
│   ├── output-patterns.md
│   └── workflows.md
├── templates/                  # 基础设施模板
│   ├── hooks/                  # Hook 模板
│   │   ├── skill-activation-prompt.py
│   │   ├── debug-mode-detector.py
│   │   ├── investigation-guard.py
│   │   ├── post-tool-use-tracker.py
│   │   ├── verification-guard.sh
│   │   └── README.md
│   ├── skill-rules.json        # 触发规则模板
│   ├── settings.local.json     # 配置模板
│   ├── dev-docs/               # Dev Docs 模板
│   │   ├── TEMPLATE-plan.md
│   │   ├── TEMPLATE-context.md
│   │   └── TEMPLATE-tasks.md
│   └── agents/                 # Agent 模板
│       ├── code-reviewer.md
│       └── error-resolver.md
└── examples/                   # 完整示例
    └── full-project/
```

## Skill 编写核心概念

### 三层加载架构

| 层级 | 加载时机 | Token 成本 | 内容 |
|------|----------|------------|------|
| L1: 元数据 | 启动时 | ~100 tokens | name + description |
| L2: 指令 | 触发时 | <5k tokens | SKILL.md 主体 |
| L3: 资源 | 按需 | 无限制 | scripts/, references/ |

### YAML Frontmatter

```yaml
---
name: my-skill-name      # 小写字母、连字符，最多 64 字符
description: 为 Y 做 X。当处理 Y 或用户提到 X 时使用。
---
```

### 核心原则

1. **简洁** - Claude 很聪明，只添加它不知道的内容
2. **自由度匹配脆弱性** - 灵活任务高自由度，关键操作低自由度
3. **渐进式披露** - SKILL.md 保持 < 500 行，详细内容拆分到 references/
4. **一层深度引用** - 避免嵌套文件引用

## 致谢

- [Anthropic Skills 最佳实践](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [claude-code-infrastructure-showcase](https://github.com/diet103/claude-code-infrastructure-showcase) - 基础设施模式的灵感来源

## 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎贡献！请随时提交 Pull Request。
