#!/bin/bash
# Prepare CodeGuard plugin for distribution
# This script copies the rule files from the main rules directory 
# to the skills directory for plugin packaging

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "==================================="
echo "Preparing CodeGuard Plugin"
echo "==================================="
echo ""

# Create skills directory structure if it doesn't exist
echo "1. Creating skills directory structure..."
mkdir -p "$PROJECT_ROOT/skills/software-security"

# Remove old rules directory in skills if it exists
if [ -d "$PROJECT_ROOT/skills/software-security/rules" ]; then
    echo "2. Removing old rules directory..."
    rm -rf "$PROJECT_ROOT/skills/software-security/rules"
fi

# Copy rules to skills directory
echo "3. Copying rules from rules/ to skills/software-security/rules/..."
cp -r "$PROJECT_ROOT/rules" "$PROJECT_ROOT/skills/software-security/rules"

# Count the number of rules
RULE_COUNT=$(find "$PROJECT_ROOT/skills/software-security/rules" -name "*.md" | wc -l | tr -d ' ')

echo "4. Verifying plugin structure..."
# Verify required files exist
if [ ! -f "$PROJECT_ROOT/.claude-plugin/plugin.json" ]; then
    echo "   ERROR: Missing .claude-plugin/plugin.json"
    exit 1
fi

if [ ! -f "$PROJECT_ROOT/.claude-plugin/marketplace.json" ]; then
    echo "   ERROR: Missing .claude-plugin/marketplace.json"
    exit 1
fi

if [ ! -f "$PROJECT_ROOT/skills/software-security/SKILL.md" ]; then
    echo "   ERROR: Missing skills/software-security/SKILL.md"
    exit 1
fi

echo "   ✓ All required plugin files present"
echo ""
echo "==================================="
echo "Plugin Preparation Complete!"
echo "==================================="
echo ""
echo "Summary:"
echo "  - Rules copied: $RULE_COUNT files"
echo "  - Plugin version: $(grep -o '"version": "[^"]*"' "$PROJECT_ROOT/.claude-plugin/plugin.json" | cut -d'"' -f4)"
echo "  - Location: $PROJECT_ROOT"
echo ""
echo "The plugin is ready for distribution."
echo ""
echo "To test locally:"
echo "  1. cd /path/to/parent/directory"
echo "  2. claude"
echo "  3. /plugin marketplace add ./rules"
echo "  4. /plugin install codeguard-security@project-codeguard"
echo ""

