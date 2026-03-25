#!/usr/bin/env python3
"""PDF导入 - 提取文本→分章→分场景→生成元数据骨架"""

import json
import os
import re
import sys
from datetime import datetime

DATA_DIR = os.path.expanduser("~/.openclaw/skills/novel-rpg/data")
BOOKS_DIR = os.path.join(DATA_DIR, "books")
INDEX_FILE = os.path.join(BOOKS_DIR, "_index.json")

# 章节标题正则模式
CHAPTER_PATTERNS = [
    r'^第[一二三四五六七八九十百千零\d]+[回章节卷篇]',  # 中文：第X回/章/节
    r'^Chapter\s+\d+',                                    # English
    r'^CHAPTER\s+\d+',
    r'^\d+\.\s+\S',                                       # 1. Title
    r'^Part\s+\d+',
    r'^卷[一二三四五六七八九十\d]+',                        # 卷X
]


def check_pymupdf():
    try:
        import fitz  # noqa: F401
        return True
    except ImportError:
        print("需要安装 PyMuPDF: pip3 install PyMuPDF")
        return False


def extract_text(pdf_path):
    """从PDF提取全文"""
    import fitz
    doc = fitz.open(pdf_path)
    pages = []
    for page in doc:
        text = page.get_text()
        if text.strip():
            pages.append(text)
    doc.close()
    return pages


def detect_chapters(full_text):
    """检测章节边界"""
    lines = full_text.split('\n')
    chapters = []
    current_chapter = {"title": "序章", "lines": []}

    for line in lines:
        stripped = line.strip()
        if not stripped:
            current_chapter["lines"].append(line)
            continue

        is_chapter = False
        for pattern in CHAPTER_PATTERNS:
            if re.match(pattern, stripped):
                is_chapter = True
                break

        if is_chapter and len(current_chapter["lines"]) > 5:
            chapters.append(current_chapter)
            current_chapter = {"title": stripped, "lines": []}
        else:
            current_chapter["lines"].append(line)

    if current_chapter["lines"]:
        chapters.append(current_chapter)

    return chapters


def split_scenes(chapter_text, max_tokens=800):
    """将章节分割为场景块"""
    # 按空行或分隔符切分
    paragraphs = re.split(r'\n\s*\n|\n---\n|\n\*\*\*\n', chapter_text)
    scenes = []
    current = []
    current_len = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        # 粗略估算token：中文1字≈1.5token，英文1词≈1token
        est_tokens = len(para) if any('\u4e00' <= c <= '\u9fff' for c in para) else len(para.split())
        if current_len + est_tokens > max_tokens and current:
            scenes.append('\n\n'.join(current))
            current = [para]
            current_len = est_tokens
        else:
            current.append(para)
            current_len += est_tokens

    if current:
        scenes.append('\n\n'.join(current))

    return scenes


def extract_character_candidates(text):
    """提取可能的角色名（简单启发式）"""
    candidates = set()

    # 中文：引号前的2-4字名字
    for m in re.finditer(r'([\u4e00-\u9fff]{2,4})(?:说|道|笑道|怒道|叫道|问道|答道|喊道)', text):
        candidates.add(m.group(1))

    # 英文：大写开头的连续词
    for m in re.finditer(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', text):
        name = m.group(1)
        if name not in {'The', 'This', 'That', 'But', 'And', 'Chapter', 'Part'}:
            candidates.add(name)

    # 按出现频率排序，取前20
    from collections import Counter
    freq = Counter()
    for name in candidates:
        freq[name] = text.count(name)

    return [name for name, _ in freq.most_common(20) if freq[name] >= 3]


def import_pdf(pdf_path, book_id, title, author="未知"):
    """导入PDF并生成数据骨架"""
    if not check_pymupdf():
        sys.exit(1)

    if not os.path.exists(pdf_path):
        print(f"文件不存在: {pdf_path}")
        sys.exit(1)

    print(f"正在导入: {pdf_path}")

    # 1. 提取文本
    pages = extract_text(pdf_path)
    full_text = '\n'.join(pages)
    print(f"  提取 {len(pages)} 页，共 {len(full_text)} 字符")

    # 2. 检测章节
    chapters = detect_chapters(full_text)
    print(f"  检测到 {len(chapters)} 个章节")

    # 3. 创建目录
    book_dir = os.path.join(BOOKS_DIR, book_id)
    chunks_dir = os.path.join(book_dir, "chunks")
    os.makedirs(chunks_dir, exist_ok=True)

    # 4. 分场景并写入chunks
    meta_chapters = []
    all_scenes = []
    scene_counter = 0

    for ch_idx, chapter in enumerate(chapters, 1):
        ch_text = '\n'.join(chapter["lines"])
        scenes = split_scenes(ch_text)

        scene_ids = []
        for sc_idx, scene_text in enumerate(scenes, 1):
            scene_id = f"ch{ch_idx:02d}_s{sc_idx:02d}"
            chunk_path = os.path.join(chunks_dir, f"{scene_id}.txt")
            with open(chunk_path, "w", encoding="utf-8") as f:
                f.write(scene_text)

            scene_ids.append(scene_id)
            all_scenes.append({
                "id": scene_id,
                "chapter": ch_idx,
                "scene_index": sc_idx,
                "title": f"{chapter['title']} - 场景{sc_idx}",
                "characters_present": [],
                "location": "",
                "summary": scene_text[:100] + "..." if len(scene_text) > 100 else scene_text,
                "plot_type": "unknown",
                "challenge_potential": 3,
                "choices": [],
                "next_scenes": [],
            })
            scene_counter += 1

        # 链接场景
        for i in range(len(scene_ids) - 1):
            all_scenes[-len(scene_ids) + i]["next_scenes"] = [scene_ids[i + 1]]
        if scene_ids and ch_idx < len(chapters):
            pass  # 跨章链接在最后处理

        meta_chapters.append({
            "number": ch_idx,
            "title": chapter["title"],
            "scene_count": len(scenes),
            "key_characters": [],
            "summary": ch_text[:150] + "..." if len(ch_text) > 150 else ch_text,
        })

    # 跨章节链接
    for i in range(len(all_scenes) - 1):
        if not all_scenes[i]["next_scenes"]:
            all_scenes[i]["next_scenes"] = [all_scenes[i + 1]["id"]]

    print(f"  生成 {scene_counter} 个场景块")

    # 5. 提取角色候选
    char_candidates = extract_character_candidates(full_text)
    print(f"  候选角色: {', '.join(char_candidates[:10])}")

    # 6. 写入元数据
    meta = {
        "id": book_id,
        "title": title,
        "author": author,
        "language": "auto",
        "total_chapters": len(chapters),
        "playable_characters": [],
        "chapters": meta_chapters,
    }
    with open(os.path.join(book_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    # 7. 写入角色骨架
    characters = {
        "characters": [
            {
                "id": re.sub(r'\s+', '_', name.lower()),
                "name": name,
                "aliases": [],
                "personality": "待补充",
                "abilities": [],
                "relationships": {},
                "initial_stats": {"wisdom": 50, "combat": 50, "loyalty": 50, "reputation": 50},
                "arc_summary": "待补充",
                "first_appearance_chapter": 1,
                "playable": True if i < 5 else False,
            }
            for i, name in enumerate(char_candidates[:10])
        ]
    }
    with open(os.path.join(book_dir, "characters.json"), "w", encoding="utf-8") as f:
        json.dump(characters, f, ensure_ascii=False, indent=2)

    # 8. 写入场景图
    with open(os.path.join(book_dir, "plot_graph.json"), "w", encoding="utf-8") as f:
        json.dump({"scenes": all_scenes}, f, ensure_ascii=False, indent=2)

    # 9. 更新索引
    index_path = INDEX_FILE
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            index = json.load(f)
    else:
        index = {"books": []}

    # 去重
    index["books"] = [b for b in index["books"] if b["id"] != book_id]
    index["books"].append({
        "id": book_id,
        "title": title,
        "author": author,
        "type": "imported",
        "status": "skeleton",
        "character_count": len(char_candidates[:10]),
        "chapter_count": len(chapters),
    })
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"\n导入完成！数据保存在: {book_dir}")
    print(f"状态: skeleton（骨架）")
    print(f"下一步: 请AI帮忙丰富角色信息和场景选择点")
    print(f"  - 补充 characters.json 中的性格、能力、关系")
    print(f"  - 补充 plot_graph.json 中的选择点")
    print(f"  - 将 playable_characters 添加到 meta.json")


def status(book_id):
    """检查书籍导入状态"""
    book_dir = os.path.join(BOOKS_DIR, book_id)
    if not os.path.exists(book_dir):
        print(f"书籍 {book_id} 不存在")
        sys.exit(1)

    meta = None
    meta_path = os.path.join(book_dir, "meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

    chunks_dir = os.path.join(book_dir, "chunks")
    chunk_count = len(os.listdir(chunks_dir)) if os.path.exists(chunks_dir) else 0

    chars_path = os.path.join(book_dir, "characters.json")
    char_count = 0
    enriched = 0
    if os.path.exists(chars_path):
        with open(chars_path, "r", encoding="utf-8") as f:
            chars = json.load(f)
            char_count = len(chars.get("characters", []))
            enriched = sum(1 for c in chars.get("characters", []) if c.get("personality") != "待补充")

    plot_path = os.path.join(book_dir, "plot_graph.json")
    scene_count = 0
    scenes_with_choices = 0
    if os.path.exists(plot_path):
        with open(plot_path, "r", encoding="utf-8") as f:
            plot = json.load(f)
            scene_count = len(plot.get("scenes", []))
            scenes_with_choices = sum(1 for s in plot.get("scenes", []) if s.get("choices"))

    title = meta.get("title", book_id) if meta else book_id
    print(f"书籍: {title}")
    print(f"章节: {meta.get('total_chapters', 0) if meta else 0}")
    print(f"场景: {scene_count} ({scenes_with_choices} 有选择点)")
    print(f"文本块: {chunk_count}")
    print(f"角色: {char_count} ({enriched} 已丰富)")

    completeness = 0
    if scene_count > 0:
        completeness += 30
    if scenes_with_choices > 0:
        completeness += 30 * (scenes_with_choices / max(scene_count, 1))
    if enriched > 0:
        completeness += 40 * (enriched / max(char_count, 1))
    print(f"完成度: {int(completeness)}%")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: pdf_import.py <command> [args]")
        print("命令:")
        print('  import "<pdf-path>" --book-id <id> --title "<title>" [--author "<author>"]')
        print("  status <book-id>")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "import":
        # 解析参数
        args = sys.argv[2:]
        pdf_path = args[0] if args else ""
        book_id = ""
        title = ""
        author = "未知"

        i = 1
        while i < len(args):
            if args[i] == "--book-id" and i + 1 < len(args):
                book_id = args[i + 1]
                i += 2
            elif args[i] == "--title" and i + 1 < len(args):
                title = args[i + 1]
                i += 2
            elif args[i] == "--author" and i + 1 < len(args):
                author = args[i + 1]
                i += 2
            else:
                i += 1

        if not pdf_path or not book_id or not title:
            print('用法: pdf_import.py import "<pdf-path>" --book-id <id> --title "<title>"')
            sys.exit(1)

        import_pdf(pdf_path, book_id, title, author)

    elif cmd == "status":
        if len(sys.argv) < 3:
            print("用法: pdf_import.py status <book-id>")
            sys.exit(1)
        status(sys.argv[2])
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)
