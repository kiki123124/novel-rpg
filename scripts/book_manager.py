#!/usr/bin/env python3
"""书籍管理器 - 初始化内置书、列表、查询角色"""

import json
import os
import sys

DATA_DIR = os.path.expanduser("~/.openclaw/skills/novel-rpg/data")
BOOKS_DIR = os.path.join(DATA_DIR, "books")
INDEX_FILE = os.path.join(BOOKS_DIR, "_index.json")
# 内置数据源目录（repo中的data/books/）
REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_BOOKS_DIR = os.path.join(REPO_DIR, "data", "books")


def ensure_dirs():
    os.makedirs(BOOKS_DIR, exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, "saves"), exist_ok=True)


def load_index():
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"books": []}


def save_index(index):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def init_builtins():
    """初始化内置小说数据"""
    ensure_dirs()
    index = load_index()
    existing_ids = {b["id"] for b in index["books"]}

    builtins = get_builtin_books()
    added = 0

    for book in builtins:
        if book["id"] in existing_ids:
            continue

        book_dir = os.path.join(BOOKS_DIR, book["id"])
        os.makedirs(book_dir, exist_ok=True)
        os.makedirs(os.path.join(book_dir, "chunks"), exist_ok=True)

        # 写入 meta.json
        with open(os.path.join(book_dir, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(book["meta"], f, ensure_ascii=False, indent=2)

        # 写入 characters.json
        with open(os.path.join(book_dir, "characters.json"), "w", encoding="utf-8") as f:
            json.dump(book["characters"], f, ensure_ascii=False, indent=2)

        # 写入 plot_graph.json
        with open(os.path.join(book_dir, "plot_graph.json"), "w", encoding="utf-8") as f:
            json.dump(book["plot_graph"], f, ensure_ascii=False, indent=2)

        index["books"].append({
            "id": book["id"],
            "title": book["meta"]["title"],
            "author": book["meta"]["author"],
            "type": "builtin",
            "status": "ready",
            "character_count": len(book["characters"]["characters"]),
            "chapter_count": len(book["meta"]["chapters"]),
        })
        added += 1

    save_index(index)
    print(f"初始化完成，新增 {added} 本书，共 {len(index['books'])} 本")


def list_books():
    index = load_index()
    if not index["books"]:
        print("暂无书籍。运行 `init-builtins` 初始化内置书。")
        return
    print(f"共 {len(index['books'])} 本书：\n")
    for b in index["books"]:
        status = "✓" if b["status"] == "ready" else "..."
        print(f"  [{status}] {b['id']} - {b['title']}（{b['author']}）"
              f"  角色:{b['character_count']} 章节:{b['chapter_count']}")


def show_characters(book_id):
    char_file = os.path.join(BOOKS_DIR, book_id, "characters.json")
    if not os.path.exists(char_file):
        print(f"书籍 {book_id} 不存在或未初始化")
        sys.exit(1)

    with open(char_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"可选角色（{book_id}）：\n")
    for c in data["characters"]:
        if c.get("playable", True):
            aliases = "、".join(c.get("aliases", []))
            alias_str = f"（{aliases}）" if aliases else ""
            print(f"  {c['id']} - {c['name']}{alias_str}")
            print(f"    性格：{c['personality']}")
            if c.get("abilities"):
                print(f"    能力：{'、'.join(c['abilities'])}")
            print()


def get_builtin_books():
    """从JSON文件加载内置书数据"""
    builtin_ids = ["xiyouji", "wuthering-heights"]
    books = []
    for book_id in builtin_ids:
        json_path = os.path.join(REPO_BOOKS_DIR, book_id, "builtin_data.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                books.append(json.load(f))
    return books


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: book_manager.py <command> [args]")
        print("命令: init-builtins | list | characters <book-id>")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "init-builtins":
        init_builtins()
    elif cmd == "list":
        list_books()
    elif cmd == "characters":
        if len(sys.argv) < 3:
            print("用法: book_manager.py characters <book-id>")
            sys.exit(1)
        show_characters(sys.argv[2])
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)
