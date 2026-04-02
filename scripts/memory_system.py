#!/usr/bin/env python3
"""记忆系统 - 跨存档的长期记忆、关系追踪、玩家画像"""

import json
import os
import sys
from datetime import datetime

DATA_DIR = os.path.expanduser("~/.openclaw/skills/novel-rpg/data")
MEMORY_DIR = os.path.join(DATA_DIR, "memory")
SAVES_DIR = os.path.join(DATA_DIR, "saves")


def ensure_dirs():
    os.makedirs(MEMORY_DIR, exist_ok=True)


def load_memory():
    ensure_dirs()
    path = os.path.join(MEMORY_DIR, "player_memory.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "player_profile": {
            "play_style": [],
            "preferred_genres": [],
            "total_games": 0,
            "total_choices": 0,
            "canon_ratio": 0.0,
        },
        "relationship_history": {},
        "book_memories": {},
        "achievements": [],
        "updated_at": None,
    }


def save_memory(mem):
    mem["updated_at"] = datetime.now().isoformat()
    path = os.path.join(MEMORY_DIR, "player_memory.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(mem, f, ensure_ascii=False, indent=2)


def sync_from_saves():
    """从所有存档同步记忆"""
    mem = load_memory()
    if not os.path.exists(SAVES_DIR):
        print("暂无存档")
        return

    all_choices = []
    canon_count = 0
    books_played = set()

    for f in os.listdir(SAVES_DIR):
        if not f.endswith(".json"):
            continue
        path = os.path.join(SAVES_DIR, f)
        with open(path, "r", encoding="utf-8") as fp:
            save = json.load(fp)

        book_id = save.get("book_id", "unknown")
        char_name = save.get("character_name", "unknown")
        books_played.add(book_id)

        # 收集选择数据
        for choice in save.get("choices_made", []):
            all_choices.append(choice)
            if choice.get("is_canon"):
                canon_count += 1

        # 收集关系数据
        for name, rel in save.get("relationships", {}).items():
            key = f"{book_id}:{name}"
            if key not in mem["relationship_history"]:
                mem["relationship_history"][key] = []
            mem["relationship_history"][key].append({
                "character": char_name,
                "trust": rel.get("trust", 50),
                "save_id": save.get("save_id"),
            })

        # 书籍记忆
        if book_id not in mem["book_memories"]:
            mem["book_memories"][book_id] = {
                "times_played": 0,
                "characters_tried": [],
                "best_divergence": 100,
                "endings_seen": [],
            }
        bm = mem["book_memories"][book_id]
        bm["times_played"] = max(bm["times_played"], 1)
        if char_name not in bm["characters_tried"]:
            bm["characters_tried"].append(char_name)
        bm["best_divergence"] = min(bm["best_divergence"], save.get("divergence_score", 100))
        if save.get("current_scene") == "END" and save.get("save_id") not in bm["endings_seen"]:
            bm["endings_seen"].append(save["save_id"])

    # 更新玩家画像
    total = len(all_choices)
    mem["player_profile"]["total_games"] = len(books_played)
    mem["player_profile"]["total_choices"] = total
    mem["player_profile"]["canon_ratio"] = round(canon_count / total, 2) if total > 0 else 0.0

    # 推断玩家风格
    styles = []
    if mem["player_profile"]["canon_ratio"] > 0.7:
        styles.append("忠于原著型")
    elif mem["player_profile"]["canon_ratio"] < 0.3:
        styles.append("叛逆冒险型")
    else:
        styles.append("平衡探索型")
    mem["player_profile"]["play_style"] = styles

    save_memory(mem)
    print(f"记忆同步完成！")
    print(f"  总游戏: {len(books_played)}")
    print(f"  总选择: {total}")
    print(f"  原著忠实度: {mem['player_profile']['canon_ratio']*100:.0f}%")
    print(f"  玩家风格: {'、'.join(styles)}")


def show():
    """显示玩家记忆"""
    mem = load_memory()
    profile = mem["player_profile"]

    print(f"=== 玩家记忆 ===")
    print(f"风格: {'、'.join(profile.get('play_style', ['未知']))}")
    print(f"总游戏: {profile['total_games']} | 总选择: {profile['total_choices']}")
    print(f"原著忠实度: {profile['canon_ratio']*100:.0f}%")

    if mem["book_memories"]:
        print(f"\n--- 书籍记录 ---")
        for book_id, bm in mem["book_memories"].items():
            chars = '、'.join(bm['characters_tried'][:5])
            endings = len(bm['endings_seen'])
            print(f"  {book_id}: {chars} | 通关{endings}次 | 最低偏离{bm['best_divergence']}")

    if mem["relationship_history"]:
        print(f"\n--- 关系记录 ---")
        for key, history in list(mem["relationship_history"].items())[:10]:
            latest = history[-1] if history else {}
            print(f"  {key}: 信任度 {latest.get('trust', '?')}")


def get_context(book_id=None, character_id=None):
    """获取记忆上下文（供AI生成叙事时参考）"""
    mem = load_memory()
    context = {
        "player_style": mem["player_profile"].get("play_style", []),
        "canon_ratio": mem["player_profile"]["canon_ratio"],
    }

    if book_id and book_id in mem["book_memories"]:
        bm = mem["book_memories"][book_id]
        context["book_history"] = {
            "times_played": bm["times_played"],
            "characters_tried": bm["characters_tried"],
            "is_replay": bm["times_played"] > 1,
        }

    # 相关关系
    if book_id:
        relevant_rels = {}
        for key, history in mem["relationship_history"].items():
            if key.startswith(f"{book_id}:"):
                char_name = key.split(":", 1)[1]
                latest = history[-1] if history else {}
                relevant_rels[char_name] = latest.get("trust", 50)
        if relevant_rels:
            context["known_relationships"] = relevant_rels

    print(json.dumps(context, ensure_ascii=False, indent=2))


def add_achievement(achievement):
    """添加成就"""
    mem = load_memory()
    if achievement not in mem["achievements"]:
        mem["achievements"].append(achievement)
        save_memory(mem)
        print(f"获得成就: {achievement}")
    else:
        print(f"成就已存在: {achievement}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: memory_system.py <command> [args]")
        print("命令:")
        print("  sync                            从存档同步记忆")
        print("  show                            显示玩家记忆")
        print("  context [book-id] [char-id]     获取记忆上下文（供AI用）")
        print("  achievement <text>              添加成就")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "sync":
        sync_from_saves()
    elif cmd == "show":
        show()
    elif cmd == "context":
        bid = sys.argv[2] if len(sys.argv) > 2 else None
        cid = sys.argv[3] if len(sys.argv) > 3 else None
        get_context(bid, cid)
    elif cmd == "achievement":
        if len(sys.argv) < 3:
            print("用法: memory_system.py achievement <text>")
            sys.exit(1)
        add_achievement(sys.argv[2])
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)
