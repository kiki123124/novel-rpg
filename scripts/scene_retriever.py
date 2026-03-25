#!/usr/bin/env python3
"""场景上下文检索 - 省token核心组件"""

import json
import os
import sys

DATA_DIR = os.path.expanduser("~/.openclaw/skills/novel-rpg/data")
BOOKS_DIR = os.path.join(DATA_DIR, "books")


def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_scene(plot, scene_id):
    for s in plot.get("scenes", []):
        if s["id"] == scene_id:
            return s
    return None


def get_adjacent_scenes(plot, scene_id):
    """获取前后场景的摘要"""
    scenes = plot.get("scenes", [])
    prev_scene = None
    next_scene = None
    for i, s in enumerate(scenes):
        if s["id"] == scene_id:
            if i > 0:
                prev_scene = scenes[i - 1]
            if i < len(scenes) - 1:
                next_scene = scenes[i + 1]
            break
    return prev_scene, next_scene


def context(book_id, scene_id):
    """获取场景完整上下文（给AI用的）"""
    book_dir = os.path.join(BOOKS_DIR, book_id)
    meta = load_json(os.path.join(book_dir, "meta.json"))
    chars = load_json(os.path.join(book_dir, "characters.json"))
    plot = load_json(os.path.join(book_dir, "plot_graph.json"))

    if not plot:
        print(f"书籍 {book_id} 数据不存在")
        sys.exit(1)

    scene = get_scene(plot, scene_id)
    if not scene:
        print(f"场景 {scene_id} 不存在")
        sys.exit(1)

    prev_scene, next_scene = get_adjacent_scenes(plot, scene_id)

    # 获取章节信息
    chapter_info = None
    if meta:
        for ch in meta.get("chapters", []):
            if ch["number"] == scene.get("chapter"):
                chapter_info = ch
                break

    # 获取在场角色信息
    present_chars = []
    if chars:
        char_ids = scene.get("characters_present", [])
        for c in chars.get("characters", []):
            if c["id"] in char_ids:
                present_chars.append({
                    "name": c["name"],
                    "personality": c["personality"],
                    "abilities": c.get("abilities", []),
                })

    # 检查是否有文本分块（导入书）
    chunk_file = os.path.join(book_dir, "chunks", f"{scene_id}.txt")
    chunk_text = None
    if os.path.exists(chunk_file):
        with open(chunk_file, "r", encoding="utf-8") as f:
            chunk_text = f.read()

    # 输出结构化上下文
    output = {
        "book": meta.get("title", book_id) if meta else book_id,
        "chapter": chapter_info.get("title", "") if chapter_info else "",
        "chapter_number": scene.get("chapter", 0),
        "scene": {
            "id": scene["id"],
            "title": scene["title"],
            "location": scene.get("location", ""),
            "summary": scene.get("summary", ""),
            "plot_type": scene.get("plot_type", ""),
            "challenge_potential": scene.get("challenge_potential", 3),
        },
        "characters_present": present_chars,
        "choices": scene.get("choices", []),
        "previous_scene": prev_scene["summary"] if prev_scene else None,
        "next_scene_hint": next_scene["title"] if next_scene else "故事终章",
    }

    if chunk_text:
        output["original_text"] = chunk_text

    print(json.dumps(output, ensure_ascii=False, indent=2))


def character(book_id, character_id, scene_id=None):
    """获取角色信息"""
    book_dir = os.path.join(BOOKS_DIR, book_id)
    chars = load_json(os.path.join(book_dir, "characters.json"))

    if not chars:
        print(f"书籍 {book_id} 角色数据不存在")
        sys.exit(1)

    for c in chars.get("characters", []):
        if c["id"] == character_id:
            output = {
                "name": c["name"],
                "aliases": c.get("aliases", []),
                "personality": c["personality"],
                "abilities": c.get("abilities", []),
                "relationships": c.get("relationships", {}),
                "arc_summary": c.get("arc_summary", ""),
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))
            return

    print(f"角色 {character_id} 不存在")


def lookahead(book_id, scene_id, count=3):
    """预览后续场景（用于AI规划挑战）"""
    book_dir = os.path.join(BOOKS_DIR, book_id)
    plot = load_json(os.path.join(book_dir, "plot_graph.json"))

    if not plot:
        print(f"书籍 {book_id} 数据不存在")
        sys.exit(1)

    scenes = plot.get("scenes", [])
    found = False
    upcoming = []

    for s in scenes:
        if found:
            upcoming.append({
                "id": s["id"],
                "title": s["title"],
                "plot_type": s.get("plot_type", ""),
                "challenge_potential": s.get("challenge_potential", 3),
                "summary": s.get("summary", "")[:60] + "...",
            })
            if len(upcoming) >= count:
                break
        if s["id"] == scene_id:
            found = True

    if not upcoming:
        print("已是最后场景")
    else:
        print(json.dumps(upcoming, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: scene_retriever.py <command> [args]")
        print("命令:")
        print("  context <book-id> <scene-id>                    获取场景上下文")
        print("  character <book-id> <character-id> [scene-id]   获取角色信息")
        print("  lookahead <book-id> <scene-id> [count]          预览后续场景")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "context":
        if len(sys.argv) < 4:
            print("用法: scene_retriever.py context <book-id> <scene-id>")
            sys.exit(1)
        context(sys.argv[2], sys.argv[3])
    elif cmd == "character":
        if len(sys.argv) < 4:
            print("用法: scene_retriever.py character <book-id> <character-id> [scene-id]")
            sys.exit(1)
        sid = sys.argv[4] if len(sys.argv) > 4 else None
        character(sys.argv[2], sys.argv[3], sid)
    elif cmd == "lookahead":
        if len(sys.argv) < 4:
            print("用法: scene_retriever.py lookahead <book-id> <scene-id> [count]")
            sys.exit(1)
        cnt = int(sys.argv[4]) if len(sys.argv) > 4 else 3
        lookahead(sys.argv[2], sys.argv[3], cnt)
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)
