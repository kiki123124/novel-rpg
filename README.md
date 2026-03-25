# Novel RPG - 名著角色扮演闯关

交互式名著角色扮演 Skill，适用于 OpenClaw / Claude Code 等 AI 助手。

选择经典名著中的角色，从其视角体验原著情节，做出选择影响剧情走向。

## 功能

- **内置名著**：西游记（前10回，4个可选角色，27个场景）
- **PDF导入**：导入任意小说，自动分章、提取角色、生成场景
- **多视角体验**：同一故事，不同角色视角，不同选择
- **属性系统**：wisdom / combat / loyalty / reputation，影响可用选项
- **偏离度追踪**：走原著路线或走出自己的平行时空
- **存档系统**：跨会话保存进度

## 安装

```bash
# 克隆到 skills 目录
git clone https://github.com/kiki123124/novel-rpg.git ~/.openclaw/skills/novel-rpg

# 初始化内置书籍数据
python3 ~/.openclaw/skills/novel-rpg/scripts/book_manager.py init-builtins

# （可选）PDF导入需要 PyMuPDF
pip3 install PyMuPDF
```

## 使用

对 AI 说：「名著RPG」「开始冒险」「小说闯关」

### 导入自己的小说

```bash
python3 ~/.openclaw/skills/novel-rpg/scripts/pdf_import.py import "/path/to/book.pdf" --book-id "my-book" --title "书名"
```

## 脚本命令

```bash
# 书籍管理
python3 scripts/book_manager.py list                    # 列出书籍
python3 scripts/book_manager.py characters xiyouji      # 查看角色

# 游戏引擎
python3 scripts/game_engine.py new-game xiyouji sun_wukong  # 新游戏
python3 scripts/game_engine.py list-saves                    # 列出存档
python3 scripts/game_engine.py load <save-id>                # 加载存档

# 场景检索
python3 scripts/scene_retriever.py context xiyouji ch01_s01  # 场景上下文

# PDF导入
python3 scripts/pdf_import.py import "book.pdf" --book-id id --title "名"
python3 scripts/pdf_import.py status <book-id>               # 导入状态
```

## License

MIT
