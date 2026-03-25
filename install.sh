#!/bin/bash
set -e

SKILL_DIR="$HOME/.openclaw/skills/novel-rpg"
REPO_URL="https://github.com/kiki123124/novel-rpg.git"

echo "正在安装 novel-rpg skill..."

mkdir -p "$HOME/.openclaw/skills"

if [ -d "$SKILL_DIR" ]; then
  echo "已存在，正在更新..."
  cd "$SKILL_DIR" && git pull
else
  git clone "$REPO_URL" "$SKILL_DIR"
fi

python3 "$SKILL_DIR/scripts/book_manager.py" init-builtins

echo ""
echo "✓ novel-rpg skill 安装完成！"
echo ""
echo "使用方式：对 AI 说「小说冒险」「开始冒险」「小说闯关」「novel rpg」"
echo "导入PDF：pip3 install PyMuPDF && python3 $SKILL_DIR/scripts/pdf_import.py import ..."
