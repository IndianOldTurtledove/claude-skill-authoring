#!/bin/bash
#
# Claude Code Infrastructure Installer
#
# Installation modes:
#   --global    Install to ~/.claude/ (affects all projects)
#   --project   Install to ./.claude/ (current project only, default)
#
# Usage:
#   # Global install (recommended for hooks)
#   curl -fsSL https://raw.githubusercontent.com/IndianOldTurtledove/claude-skill-authoring/main/install.sh | bash -s -- --global
#
#   # Project install
#   curl -fsSL https://raw.githubusercontent.com/IndianOldTurtledove/claude-skill-authoring/main/install.sh | bash
#
# Or after cloning:
#   ./install.sh --global
#   ./install.sh --project
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parse arguments
INSTALL_MODE="project"  # default
for arg in "$@"; do
    case $arg in
        --global|-g)
            INSTALL_MODE="global"
            shift
            ;;
        --project|-p)
            INSTALL_MODE="project"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--global|--project]"
            echo ""
            echo "Options:"
            echo "  --global, -g   Install to ~/.claude/ (all projects)"
            echo "  --project, -p  Install to ./.claude/ (current project, default)"
            echo ""
            echo "Examples:"
            echo "  $0 --global    # Install hooks globally"
            echo "  $0             # Install to current project"
            exit 0
            ;;
    esac
done

# Script directory (where templates are)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATES_DIR="$SCRIPT_DIR/templates"

# Set target directory based on mode
if [ "$INSTALL_MODE" = "global" ]; then
    CLAUDE_DIR="$HOME/.claude"
    SETTINGS_FILE="settings.json"
    MODE_DESC="全局 (Global)"
else
    CLAUDE_DIR="$(pwd)/.claude"
    SETTINGS_FILE="settings.local.json"
    MODE_DESC="项目 (Project)"
fi

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Claude Code Infrastructure Installer  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "安装模式: ${CYAN}$MODE_DESC${NC}"
echo -e "目标目录: ${GREEN}$CLAUDE_DIR${NC}"
echo ""

# Check if templates exist (running from repo vs curl)
if [ ! -d "$TEMPLATES_DIR" ]; then
    echo -e "${YELLOW}模板未找到，正在克隆仓库...${NC}"
    TEMP_DIR=$(mktemp -d)
    git clone --depth 1 https://github.com/IndianOldTurtledove/claude-skill-authoring.git "$TEMP_DIR"
    TEMPLATES_DIR="$TEMP_DIR/templates"
fi

# Show components
echo -e "将安装以下组件:"
echo -e "  ${GREEN}✓${NC} hooks/           (事件钩子: debug-mode-detector, investigation-guard, etc.)"
if [ "$INSTALL_MODE" = "project" ]; then
    echo -e "  ${GREEN}✓${NC} skills/          (skill-rules.json)"
    echo -e "  ${GREEN}✓${NC} agents/          (code-reviewer, error-resolver)"
    echo -e "  ${GREEN}✓${NC} dev/             (dev docs system)"
fi
echo ""

read -p "继续安装? [y/N] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}安装已取消。${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}正在安装...${NC}"

# Create directories
mkdir -p "$CLAUDE_DIR/hooks"

# Copy hooks
echo -e "  ${GREEN}✓${NC} 安装 hooks..."
cp "$TEMPLATES_DIR/hooks/"*.py "$CLAUDE_DIR/hooks/"
cp "$TEMPLATES_DIR/hooks/"*.sh "$CLAUDE_DIR/hooks/"
cp "$TEMPLATES_DIR/hooks/README.md" "$CLAUDE_DIR/hooks/"
chmod +x "$CLAUDE_DIR/hooks/"*.sh

# Project-only components
if [ "$INSTALL_MODE" = "project" ]; then
    mkdir -p "$CLAUDE_DIR/skills"
    mkdir -p "$CLAUDE_DIR/agents"
    DEV_DIR="$(pwd)/dev"
    mkdir -p "$DEV_DIR/active"
    mkdir -p "$DEV_DIR/archive"

    echo -e "  ${GREEN}✓${NC} 安装 skill-rules.json..."
    cp "$TEMPLATES_DIR/skill-rules.json" "$CLAUDE_DIR/skills/"

    echo -e "  ${GREEN}✓${NC} 安装 agent 模板..."
    cp "$TEMPLATES_DIR/agents/"*.md "$CLAUDE_DIR/agents/"

    echo -e "  ${GREEN}✓${NC} 安装 dev docs 模板..."
    cp "$TEMPLATES_DIR/dev-docs/"*.md "$DEV_DIR/"
fi

# Handle settings file
SETTINGS_PATH="$CLAUDE_DIR/$SETTINGS_FILE"

# Generate hooks config JSON
HOOKS_CONFIG=$(cat <<'HOOKS_JSON'
{
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/skill-activation-prompt.py\" 2>/dev/null || python3 \"$HOME/.claude/hooks/skill-activation-prompt.py\"",
            "timeout": 5
          },
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/debug-mode-detector.py\" 2>/dev/null || python3 \"$HOME/.claude/hooks/debug-mode-detector.py\"",
            "timeout": 3
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Read|Grep|Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/investigation-guard.py\" 2>/dev/null || python3 \"$HOME/.claude/hooks/investigation-guard.py\"",
            "timeout": 3
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-tracker.py\" 2>/dev/null || python3 \"$HOME/.claude/hooks/post-tool-use-tracker.py\"",
            "timeout": 3
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/verification-guard.sh\" 2>/dev/null || bash \"$HOME/.claude/hooks/verification-guard.sh\"",
            "timeout": 15
          }
        ]
      }
    ]
  }
HOOKS_JSON
)

# Merge or create settings
if [ -f "$SETTINGS_PATH" ]; then
    echo -e "  ${YELLOW}!${NC} 检测到已有配置文件: $SETTINGS_FILE"

    # Check if jq is available
    if command -v jq &> /dev/null; then
        # Backup existing
        cp "$SETTINGS_PATH" "$SETTINGS_PATH.backup"
        echo -e "  ${GREEN}✓${NC} 已备份到 $SETTINGS_FILE.backup"

        # Check if hooks already exist
        if jq -e '.hooks' "$SETTINGS_PATH" > /dev/null 2>&1; then
            echo -e "  ${YELLOW}!${NC} 配置中已有 hooks，保存新配置到 hooks-config.json"
            echo "$HOOKS_CONFIG" | jq '.' > "$CLAUDE_DIR/hooks-config.json"
            echo -e "  ${CYAN}→${NC} 请手动合并 hooks-config.json 到 $SETTINGS_FILE"
        else
            # Add hooks to existing config
            jq --argjson hooks "$HOOKS_CONFIG" '. + {hooks: $hooks}' "$SETTINGS_PATH" > "$SETTINGS_PATH.tmp"
            mv "$SETTINGS_PATH.tmp" "$SETTINGS_PATH"
            echo -e "  ${GREEN}✓${NC} 已将 hooks 配置合并到 $SETTINGS_FILE"
        fi
    else
        echo -e "  ${YELLOW}!${NC} 未安装 jq，无法自动合并配置"
        echo "$HOOKS_CONFIG" | python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin), indent=2))" > "$CLAUDE_DIR/hooks-config.json"
        echo -e "  ${CYAN}→${NC} 请手动将 hooks-config.json 合并到 $SETTINGS_FILE"
    fi
else
    # Create new settings file
    echo -e "  ${GREEN}✓${NC} 创建 $SETTINGS_FILE..."
    if [ "$INSTALL_MODE" = "global" ]; then
        # Global: minimal config with just hooks
        echo "{\"hooks\": $HOOKS_CONFIG}" | python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin), indent=2))" > "$SETTINGS_PATH"
    else
        # Project: copy full template
        cp "$TEMPLATES_DIR/settings.local.json" "$SETTINGS_PATH"
    fi
fi

# Cleanup temp directory if used
if [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║       安装完成! Installation Done      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""

# Show installed files
echo -e "已安装的文件:"
echo -e "  ${CYAN}$CLAUDE_DIR/hooks/${NC}"
echo -e "    - skill-activation-prompt.py  (Skill 推荐)"
echo -e "    - debug-mode-detector.py      (Debug 场景检测)"
echo -e "    - investigation-guard.py      (先读后改守卫)"
echo -e "    - post-tool-use-tracker.py    (文件修改追踪)"
echo -e "    - verification-guard.sh       (代码完整性验证)"

if [ "$INSTALL_MODE" = "project" ]; then
    echo -e "  ${CYAN}$CLAUDE_DIR/skills/${NC}"
    echo -e "    - skill-rules.json"
    echo -e "  ${CYAN}$CLAUDE_DIR/agents/${NC}"
    echo -e "    - code-reviewer.md"
    echo -e "    - error-resolver.md"
    echo -e "  ${CYAN}$DEV_DIR/${NC}"
    echo -e "    - TEMPLATE-*.md"
fi

echo ""
echo -e "${YELLOW}下一步:${NC}"
if [ "$INSTALL_MODE" = "global" ]; then
    echo -e "  1. 重启 Claude Code 以激活 hooks"
    echo -e "  2. 如需项目特定配置，在项目中创建 .claude/skills/skill-rules.json"
else
    echo -e "  1. 自定义 ${BLUE}skill-rules.json${NC} 配置项目的 Skills"
    echo -e "  2. 编辑 ${BLUE}post-tool-use-tracker.py${NC} 配置项目的检查命令"
    echo -e "  3. 重启 Claude Code 以激活 hooks"
fi
echo ""
echo -e "文档: ${BLUE}$CLAUDE_DIR/hooks/README.md${NC}"
echo ""
