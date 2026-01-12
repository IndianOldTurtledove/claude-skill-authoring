# Claude Skill 编写指南

[中文](README.md) | [English](README_EN.md)

一个用于创建和验证 Claude Code Skills 的 Skill。是的，这是一个教 Claude 写 Skill 的 Skill。

## 这是什么？

这是一个教 Claude 如何按照 [Anthropic 官方最佳实践](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) 编写高效 Skill 的工具。

## 安装

### Claude Code（推荐）

```bash
# 克隆到全局 skills 目录
git clone https://github.com/IndianOldTurtledove/claude-skill-authoring.git ~/.claude/skills/skill-authoring

# 或克隆到特定项目
git clone https://github.com/IndianOldTurtledove/claude-skill-authoring.git .claude/skills/skill-authoring
```

### 手动安装

将内容复制到项目的 `.claude/skills/skill-authoring/` 或全局的 `~/.claude/skills/skill-authoring/`。

## 使用方法

安装后，当你询问关于创建或改进 Skills 的问题时，Claude 会自动使用这个 skill。

### 快速命令

```bash
# 初始化新 skill
python ~/.claude/skills/skill-authoring/scripts/init_skill.py my-skill-name

# 验证 skill
python ~/.claude/skills/skill-authoring/scripts/quick_validate.py path/to/skill/

# 打包分发
python ~/.claude/skills/skill-authoring/scripts/package_skill.py path/to/skill/
```

### 对话示例

```
你: 帮我创建一个处理 CSV 文件的 skill

Claude: 我来帮你创建一个 CSV 处理 skill。先初始化结构...
[使用 init_skill.py 创建结构]
[编写带有正确 frontmatter 的 SKILL.md]
[使用 quick_validate.py 验证]
```

## 项目结构

```
skill-authoring/
├── SKILL.md                    # 主指令文件（触发时加载）
├── scripts/
│   ├── init_skill.py          # 从模板初始化新 skill
│   ├── quick_validate.py      # 验证 skill 结构和 frontmatter
│   └── package_skill.py       # 打包 skill 用于分发
└── references/
    ├── output-patterns.md     # 模板和示例模式
    └── workflows.md           # 顺序、条件、反馈循环模式
```

## 核心概念

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

## 验证规则

`quick_validate.py` 脚本检查：

- SKILL.md 存在且有有效的 YAML frontmatter
- `name`: 小写字母、连字符，最多 64 字符，不含 "anthropic"/"claude"
- `description`: 最多 1024 字符，不含尖括号
- SKILL.md 主体 < 500 行
- 无 Windows 风格路径

## 相关资源

- [Anthropic Skills 仓库](https://github.com/anthropics/skills) - Anthropic 官方 skills
- [Skills 最佳实践](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) - 官方文档
- [Skills 概述](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) - 架构说明
- [awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) - 社区 skills 集合

## 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎贡献！请随时提交 Pull Request。
