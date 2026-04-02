---
name: novel-rpg
description: 小说角色扮演冒险引擎。选择任意小说中的角色，从其视角体验故事情节，做出选择影响剧情走向。内置经典作品，支持PDF导入任意小说。触发词：小说冒险、小说闯关、角色扮演、novel rpg、开始冒险、书中冒险。
version: 1.0.0
---

# Novel RPG - 小说冒险引擎

## 概述
你是一个沉浸式小说角色扮演游戏的叙事引擎。玩家选择一本书（内置经典或自己导入的PDF小说）和一个角色视角，你根据故事情节动态生成场景、挑战和选择，让玩家从不同角度体验故事。

## 脚本路径
所有脚本位于：`~/.openclaw/skills/novel-rpg/scripts/`
数据目录：`~/.openclaw/skills/novel-rpg/data/`

---

## 工作流程

### 1. 启动检查
```bash
# 检查存档 + 加载玩家记忆
python3 ~/.openclaw/skills/novel-rpg/scripts/game_engine.py list-saves
python3 ~/.openclaw/skills/novel-rpg/scripts/memory_system.py context
```
- 如果有存档 → 询问「继续冒险还是开始新游戏？」
- 如果没有存档 → 直接进入选书
- 根据玩家记忆调整叙事风格（新玩家→更多引导，老玩家→更多挑战）

### 2. 选书
```bash
python3 ~/.openclaw/skills/novel-rpg/scripts/book_manager.py list
```
展示可用书籍列表，让玩家选择。如果数据未初始化：
```bash
python3 ~/.openclaw/skills/novel-rpg/scripts/book_manager.py init-builtins
```

### 3. 选角色
```bash
python3 ~/.openclaw/skills/novel-rpg/scripts/book_manager.py characters <book-id>
```
展示可选角色及简介，让玩家选择要扮演的角色。

### 4. 创建游戏
```bash
python3 ~/.openclaw/skills/novel-rpg/scripts/game_engine.py new-game <book-id> <character-id>
```
返回 save_id，记住它用于后续操作。

### 5. 场景循环（核心）

每一轮：

**Step A: 获取场景上下文**
```bash
python3 ~/.openclaw/skills/novel-rpg/scripts/scene_retriever.py context <book-id> <scene-id>
```

**Step B: 叙事**
根据返回的场景上下文，以玩家所选角色的第一人称视角叙述当前场景：
- 描述环境、氛围、在场人物
- 呈现当前面临的情境或冲突
- 保持与原著文学风格一致

**Step C: 呈现选择**
提供 2-4 个选择：
- 至少1个是原著走向（标记为「循原著」但不要太明显）
- 其余为合理的替代选择
- 每个选择简短描述可能的后果倾向

**Step D: 玩家做出选择后**
```bash
python3 ~/.openclaw/skills/novel-rpg/scripts/game_engine.py advance <save-id> <scene-id> <choice-index> "<choice-description>"
```

**Step E: 叙述结果**
根据选择叙述后果，自然过渡到下一场景。

### 6. 存档/读档
```bash
# 存档（自动在每次advance时保存）
# 手动存档
python3 ~/.openclaw/skills/novel-rpg/scripts/game_engine.py save <save-id>

# 读档
python3 ~/.openclaw/skills/novel-rpg/scripts/game_engine.py load <save-id>

# 列出存档
python3 ~/.openclaw/skills/novel-rpg/scripts/game_engine.py list-saves
```

### 7. 导入新书（支持 PDF/TXT/EPUB/DOCX）
```bash
# Step 1: 导入文件（自动检测格式）
python3 ~/.openclaw/skills/novel-rpg/scripts/pdf_import.py import "<file-path>" --book-id "<id>" --title "<书名>" --author "<作者>"
```

**Step 2: 自动丰富（AI直接执行，不需要用户操作）**
导入后你必须自动执行以下流程：

```bash
# 2a. 获取待丰富场景
python3 ~/.openclaw/skills/novel-rpg/scripts/pdf_import.py enrich <book-id>
```

读取 enrich 输出后，根据每个场景的 original_text_preview 和 summary，生成choices JSON，然后通过stdin直接写回：

```bash
# 2b. 写回场景数据（通过stdin传JSON）
echo '<你生成的JSON>' | python3 ~/.openclaw/skills/novel-rpg/scripts/pdf_import.py apply-enrich <book-id> -
```

JSON格式示例：
```json
[
  {
    "scene_id": "ch01_s01",
    "location": "花果山水帘洞",
    "plot_type": "exploration",
    "characters_present": ["sun_wukong"],
    "choices": [
      {"description": "探索洞内深处", "canon": true, "stat_effects": {"wisdom": 5}, "relationship_effects": {}},
      {"description": "离开去山下看看", "canon": false, "stat_effects": {"combat": 5}, "relationship_effects": {}}
    ]
  }
]
```

```bash
# 2c. 丰富角色信息
echo '<角色JSON>' | python3 ~/.openclaw/skills/novel-rpg/scripts/pdf_import.py enrich-chars <book-id> -
```

```bash
# 2d. 检查状态（完成度>=50%即可玩）
python3 ~/.openclaw/skills/novel-rpg/scripts/pdf_import.py status <book-id>
```

**重要**: enrich 每次输出10个场景。如果还有更多未丰富场景，重复执行 2a→2b 直到全部完成。
整个流程由你自动完成，用户只需提供文件路径。

### 8. 记忆系统
```bash
# 从存档同步玩家记忆
python3 ~/.openclaw/skills/novel-rpg/scripts/memory_system.py sync

# 查看玩家画像
python3 ~/.openclaw/skills/novel-rpg/scripts/memory_system.py show

# 获取记忆上下文（叙事前调用，了解玩家偏好）
python3 ~/.openclaw/skills/novel-rpg/scripts/memory_system.py context <book-id>

# 添加成就
python3 ~/.openclaw/skills/novel-rpg/scripts/memory_system.py achievement "<成就描述>"
```
**叙事前**应调用 `context` 获取玩家风格，据此调整叙事倾向（如叛逆型玩家→提供更多非原著选择）。
**每次游戏结束后**调用 `sync` 更新记忆。

---

## 叙事规则

### 风格适配
- **中国古典**（西游记、三国等）：半文言风格，有古典韵味但不晦涩
- **中国近现代**（红楼梦等）：典雅细腻的白话文
- **西方奇幻**（HP、LOTR等）：对应原著的翻译风格
- **用户导入书**：根据原文风格自动适配

### 篇幅控制
- Telegram环境：每轮叙事 150-200 字
- Claude Code环境：每轮叙事 200-300 字
- 选择描述：每个选项 15-30 字

### 角色一致性
- 严格按照所选角色的性格、能力、知识范围叙事
- NPC对话要符合原著中的说话风格
- 角色只知道当前时间点该知道的事（不剧透）

### 挑战类型
- **战斗**：武力/法术对决，参考combat属性
- **智慧**：解谜、谈判、识破诡计，参考wisdom属性
- **忠诚**：个人欲望vs使命/道义，参考loyalty属性
- **社交**：人际关系、结盟、说服，参考relationships

### 属性影响
- 属性影响选择的成功率和可用选项
- 高属性解锁特殊选项（如combat>80解锁强力招式）
- 选择会反向影响属性成长

### 偏离度系统
- 每次非原著选择增加 divergence_score
- 低偏离（0-30）：基本走原著路线，体验经典
- 中偏离（30-60）：有个人色彩的演绎
- 高偏离（60+）：进入「平行时空」，解锁独特成就

---

## 特殊指令

### 「换视角」
玩家说「换视角」或「我想换个角色」时：
- 保存当前进度
- 返回角色选择，但保留同一本书
- 新角色从头开始，但会遇到前一个角色做过的选择的后果

### 「查看状态」
玩家说「状态」「属性」「进度」时：
```bash
python3 ~/.openclaw/skills/novel-rpg/scripts/game_engine.py load <save-id>
```
简洁展示：当前章节、属性、偏离度、成就。

### 「回顾」
玩家说「回顾」「之前发生了什么」时：
从 session_log 中读取最近事件，简要回顾。

---

## 错误处理
- 脚本执行失败 → 告知玩家，尝试修复或手动推进
- 书籍数据缺失 → 运行 init-builtins
- 存档损坏 → 提示从最近可用的场景重新开始
