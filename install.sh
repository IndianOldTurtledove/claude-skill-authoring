#!/bin/bash
#
# Claude Code Infrastructure Installer
#
# One-click installation of Claude Code infrastructure components:
# - Hooks (skill-activation, file-tracker)
# - Skill rules template
# - Dev docs system
# - Agent templates
#
# Inspired by: https://github.com/diet103/claude-code-infrastructure-showcase
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/IndianOldTurtledove/claude-skill-authoring/main/install.sh | bash
#
# Or after cloning:
#   ./install.sh
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory (where templates are)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATES_DIR="$SCRIPT_DIR/templates"

# Target directory (current working directory)
TARGET_DIR="$(pwd)"
CLAUDE_DIR="$TARGET_DIR/.claude"
DEV_DIR="$TARGET_DIR/dev"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  Claude Code Infrastructure   ${NC}"
echo -e "${BLUE}  Installer                    ${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if templates exist (running from repo vs curl)
if [ ! -d "$TEMPLATES_DIR" ]; then
    echo -e "${YELLOW}Templates not found locally. Cloning repository...${NC}"
    TEMP_DIR=$(mktemp -d)
    git clone --depth 1 https://github.com/IndianOldTurtledove/claude-skill-authoring.git "$TEMP_DIR"
    TEMPLATES_DIR="$TEMP_DIR/templates"
fi

# Confirmation
echo -e "This will install Claude Code infrastructure to:"
echo -e "  ${GREEN}$TARGET_DIR${NC}"
echo ""
echo -e "Components:"
echo -e "  - .claude/hooks/       (event hooks)"
echo -e "  - .claude/skills/      (skill-rules.json)"
echo -e "  - .claude/agents/      (agent templates)"
echo -e "  - dev/                 (dev docs system)"
echo ""
read -p "Continue? [y/N] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Installation cancelled.${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}Installing...${NC}"

# Create directories
echo -e "  Creating directories..."
mkdir -p "$CLAUDE_DIR/hooks"
mkdir -p "$CLAUDE_DIR/skills"
mkdir -p "$CLAUDE_DIR/agents"
mkdir -p "$DEV_DIR/active"
mkdir -p "$DEV_DIR/archive"

# Copy hooks
echo -e "  Installing hooks..."
cp "$TEMPLATES_DIR/hooks/"*.py "$CLAUDE_DIR/hooks/"
cp "$TEMPLATES_DIR/hooks/"*.sh "$CLAUDE_DIR/hooks/"
cp "$TEMPLATES_DIR/hooks/README.md" "$CLAUDE_DIR/hooks/"
chmod +x "$CLAUDE_DIR/hooks/"*.sh

# Copy skill-rules.json
echo -e "  Installing skill-rules.json..."
cp "$TEMPLATES_DIR/skill-rules.json" "$CLAUDE_DIR/skills/"

# Copy agents
echo -e "  Installing agent templates..."
cp "$TEMPLATES_DIR/agents/"*.md "$CLAUDE_DIR/agents/"

# Copy dev docs
echo -e "  Installing dev docs templates..."
cp "$TEMPLATES_DIR/dev-docs/"*.md "$DEV_DIR/"

# Copy settings template (don't overwrite existing)
if [ ! -f "$CLAUDE_DIR/settings.local.json" ]; then
    echo -e "  Installing settings.local.json..."
    cp "$TEMPLATES_DIR/settings.local.json" "$CLAUDE_DIR/"
else
    echo -e "  ${YELLOW}settings.local.json exists, skipping (merge manually)${NC}"
    echo -e "  Template saved to: $CLAUDE_DIR/settings.local.json.template"
    cp "$TEMPLATES_DIR/settings.local.json" "$CLAUDE_DIR/settings.local.json.template"
fi

# Cleanup temp directory if used
if [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}  Installation Complete!       ${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "Installed files:"
echo -e "  $CLAUDE_DIR/hooks/"
echo -e "    - skill-activation-prompt.py/.sh"
echo -e "    - post-tool-use-tracker.py/.sh"
echo -e "  $CLAUDE_DIR/skills/"
echo -e "    - skill-rules.json"
echo -e "  $CLAUDE_DIR/agents/"
echo -e "    - code-reviewer.md"
echo -e "    - error-resolver.md"
echo -e "  $DEV_DIR/"
echo -e "    - TEMPLATE-plan.md"
echo -e "    - TEMPLATE-context.md"
echo -e "    - TEMPLATE-tasks.md"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Customize ${BLUE}skill-rules.json${NC} for your project's skills"
echo -e "  2. Edit ${BLUE}post-tool-use-tracker.py${NC} CHECK_COMMANDS for your toolchain"
echo -e "  3. If settings.local.json existed, merge hooks config manually"
echo -e "  4. Restart Claude Code to activate hooks"
echo ""
echo -e "Documentation:"
echo -e "  - Hooks: $CLAUDE_DIR/hooks/README.md"
echo -e "  - Dev Docs: $DEV_DIR/README.md"
echo -e "  - Agents: $CLAUDE_DIR/agents/README.md"
echo ""
echo -e "Inspired by: ${BLUE}https://github.com/diet103/claude-code-infrastructure-showcase${NC}"
