<p align="center">
  <img src="logo.png" width="160" alt="Novel RPG - AI-powered interactive fiction and classic novel role-playing game"/>
</p>

<h1 align="center">Novel RPG - 名著角色扮演闯关</h1>
<p align="center"><strong>AI Interactive Fiction Engine | AI 交互式小说角色扮演引擎</strong></p>

<p align="center">
  <a href="https://www.npmjs.com/package/novel-rpg-skill"><img src="https://img.shields.io/npm/v/novel-rpg-skill?color=e2b04a&label=npm&logo=npm" alt="novel-rpg-skill npm package version"/></a>
  <a href="https://github.com/kiki123124/novel-rpg/stargazers"><img src="https://img.shields.io/github/stars/kiki123124/novel-rpg?style=social" alt="GitHub stars for novel-rpg"/></a>
  <a href="https://github.com/kiki123124/novel-rpg/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License"/></a>
  <a href="https://www.npmjs.com/package/novel-rpg-skill"><img src="https://img.shields.io/npm/dm/novel-rpg-skill?color=green&label=downloads" alt="npm monthly downloads"/></a>
</p>

<p align="center">
  Turn classic novels into playable RPG adventures. Role-play as Heathcliff from <em>Wuthering Heights</em>, Sun Wukong from <em>Journey to the West</em>, or import any PDF novel and play as its characters. Powered by AI — works with <strong>Claude Code</strong>, <strong>OpenClaw</strong>, <strong>ChatGPT</strong>, and any LLM.
</p>

---

## Why Novel RPG? 为什么选择 Novel RPG？

Most AI role-playing tools are generic — you describe a character and chat. **Novel RPG is different**: it's grounded in real literature. The AI knows the actual plot, characters, relationships, and turning points of each novel. Your choices diverge from the original story, creating a personal "what-if" timeline.

传统 AI 角色扮演只是自由对话。**Novel RPG 不同**：它基于真实文学作品。AI 了解原著的情节、人物关系和转折点。你的每个选择都可能改写经典，创造属于你的"平行时空"。

**Think of it as**: *Choose Your Own Adventure* meets classic literature, powered by AI.

---

## Quick Demo 快速体验

```
You: 开始名著RPG

AI: 📚 Available books:
    1. Wuthering Heights (呼啸山庄) - Emily Brontë
    2. Journey to the West (西游记) - 吴承恩

You: Wuthering Heights, I'll play as Heathcliff

AI: Yorkshire, 1801. You stand at the threshold of Wuthering Heights.
    The moor wind howls through the crags as a stranger approaches...

    What do you do?
    1. Greet him with cold indifference
    2. Show a reluctant hint of courtesy
    3. Refuse him entry entirely

    [Stats: wisdom 55 | combat 70 | loyalty 90 | reputation 20]
```

---

## Features 核心功能

### Built-in Classic Novels 内置经典名著

| Novel | Author | Characters | Scenes | Themes |
|-------|--------|-----------|--------|--------|
| **Wuthering Heights** 呼啸山庄 | Emily Brontë | Heathcliff, Catherine, Nelly, Edgar | 30 | Love, revenge, class, obsession |
| **Journey to the West** 西游记 | 吴承恩 | 孙悟空, 唐僧, 猪八戒, 沙僧 | 27 | Adventure, loyalty, enlightenment |

### PDF Novel Import 导入自定义小说
Import **any novel as PDF** — the engine auto-detects chapters, extracts character candidates, and generates a playable scene graph. Works with English, Chinese, and other languages.

### Multi-Perspective Replay 多视角重玩
Play the same story as different characters. Experience *Wuthering Heights* as the vengeful Heathcliff, the torn Catherine, the observant Nelly, or the gentle Edgar — each with unique choices and narrative voice.

### RPG Stats & Divergence 属性系统与偏离度
- **4 stats**: Wisdom, Combat, Loyalty, Reputation — affect available choices
- **Divergence score**: Track how far you've strayed from the original plot (0–100)
- **Achievements**: Unlock milestones for both canon and alternate paths

### Persistent Save System 持久存档
Save and resume across sessions. Your choices, stats, and relationships persist.

---

## Install 安装

### npx (recommended)

```bash
npx novel-rpg-skill
```

### curl one-liner

```bash
curl -fsSL https://raw.githubusercontent.com/kiki123124/novel-rpg/main/install.sh | bash
```

### git clone

```bash
git clone https://github.com/kiki123124/novel-rpg.git ~/.openclaw/skills/novel-rpg
python3 ~/.openclaw/skills/novel-rpg/scripts/book_manager.py init-builtins
```

### Update & Uninstall

```bash
npx novel-rpg-skill update      # Update to latest version
npx novel-rpg-skill uninstall   # Remove completely
```

### Optional: PDF Import Dependency

```bash
pip3 install PyMuPDF    # Required only for importing PDF novels
```

---

## Usage 使用方式

### Start a Game 开始游戏

Tell your AI assistant any of these trigger phrases:

- English: `"novel rpg"`, `"start adventure"`, `"book rpg"`
- 中文: `"名著RPG"`, `"开始冒险"`, `"小说闯关"`

### Import Your Own Novel 导入你的小说

```bash
python3 scripts/pdf_import.py import "my-novel.pdf" --book-id "my-novel" --title "My Novel" --author "Author Name"
```

After import, ask the AI to enrich the character profiles and add choice points to scenes.

---

## How It Works 工作原理

```
Choose a book → Choose a character → Play through scenes
     ↓                  ↓                    ↓
  Loads scene       Initializes          AI narrates from
  graph (not        your POV,            your perspective,
  full text =       stats, and           presents 2-4
  token efficient)  relationships        choices per scene
                                              ↓
                                    Choices affect stats,
                                    relationships, and
                                    story divergence
                                              ↓
                                    Save progress, replay
                                    as different characters
```

**Token efficient by design**: Built-in novels use structured metadata (not full text), so the AI leverages its training knowledge. Only imported PDFs store text chunks.

---

## CLI Reference 命令参考

```bash
# Book management
python3 scripts/book_manager.py list                              # List all books
python3 scripts/book_manager.py characters wuthering-heights      # Show playable characters
python3 scripts/book_manager.py init-builtins                     # Initialize built-in novels

# Game engine
python3 scripts/game_engine.py new-game wuthering-heights heathcliff  # Start new game
python3 scripts/game_engine.py list-saves                             # List all saves
python3 scripts/game_engine.py load <save-id>                         # Load a save
python3 scripts/game_engine.py delete <save-id>                       # Delete a save

# Scene retrieval
python3 scripts/scene_retriever.py context wuthering-heights ch09_s01     # Get scene context
python3 scripts/scene_retriever.py character wuthering-heights heathcliff # Get character info
python3 scripts/scene_retriever.py lookahead wuthering-heights ch09_s01   # Preview next scenes

# PDF import
python3 scripts/pdf_import.py import "book.pdf" --book-id id --title "Title"
python3 scripts/pdf_import.py status <book-id>                    # Check import status
```

---

## Compatibility 兼容平台

| Platform | Status | Notes |
|----------|--------|-------|
| **Claude Code** | Fully supported | Install as skill, trigger with natural language |
| **OpenClaw** (Telegram) | Fully supported | Auto-detected from `~/.openclaw/skills/` |
| **ChatGPT** | Compatible | Copy SKILL.md as custom instructions + run scripts manually |
| **Any LLM** | Compatible | Use SKILL.md as system prompt, scripts as tools |

---

## FAQ 常见问题

**Q: Do I need the original novel text for built-in books?**
No. Built-in novels (Wuthering Heights, Journey to the West) use structured metadata only. The AI uses its training knowledge to narrate scenes. This saves tokens and storage.

**Q: What languages are supported for PDF import?**
The chapter detection supports Chinese (第X回/章) and English (Chapter X). Scene splitting works with any language.

**Q: Can I add my own books without PDF?**
Yes. Create `meta.json`, `characters.json`, and `plot_graph.json` in `data/books/<book-id>/` following the existing format.

**Q: How does the divergence system work?**
Every non-canon choice adds +5 to your divergence score (0–100). Low divergence = classic experience. High divergence = alternate timeline with unique achievements.

---

## Contributing 贡献

PRs welcome! Some ideas:
- Add more built-in novels (三国演义, Harry Potter, Pride and Prejudice...)
- Improve PDF chapter detection for more formats
- Add achievement definitions
- Multi-language narration support

---

## License

[MIT](LICENSE) - Use it however you want.
