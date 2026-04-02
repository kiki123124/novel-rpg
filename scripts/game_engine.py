#!/usr/bin/env python3
"""游戏引擎 - 存档管理、状态推进、属性计算"""

import json
import os
import sys
import uuid
from datetime import datetime

DATA_DIR = os.path.expanduser("~/.openclaw/skills/novel-rpg/data")
SAVES_DIR = os.path.join(DATA_DIR, "saves")
BOOKS_DIR = os.path.join(DATA_DIR, "books")


def ensure_dirs():
    os.makedirs(SAVES_DIR, exist_ok=True)


def load_save(save_id):
    path = os.path.join(SAVES_DIR, f"{save_id}.json")
    if not os.path.exists(path):
        print(f"存档 {save_id} 不存在")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_save(save_id, data):
    data["updated_at"] = datetime.now().isoformat()
    path = os.path.join(SAVES_DIR, f"{save_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_book_data(book_id):
    """加载书籍的角色和场景数据"""
    book_dir = os.path.join(BOOKS_DIR, book_id)
    chars = {}
    plot = {}
    char_file = os.path.join(book_dir, "characters.json")
    plot_file = os.path.join(book_dir, "plot_graph.json")
    if os.path.exists(char_file):
        with open(char_file, "r", encoding="utf-8") as f:
            chars = json.load(f)
    if os.path.exists(plot_file):
        with open(plot_file, "r", encoding="utf-8") as f:
            plot = json.load(f)
    return chars, plot


def new_game(book_id, character_id):
    """创建新游戏"""
    ensure_dirs()
    chars, plot = load_book_data(book_id)

    # 查找角色初始属性
    char_data = None
    for c in chars.get("characters", []):
        if c["id"] == character_id:
            char_data = c
            break
    if not char_data:
        print(f"角色 {character_id} 不存在于 {book_id}")
        sys.exit(1)

    # 找到第一个场景
    scenes = plot.get("scenes", [])
    first_scene = scenes[0]["id"] if scenes else "ch01_s01"

    save_id = str(uuid.uuid4())[:8]
    save_data = {
        "save_id": save_id,
        "book_id": book_id,
        "character_id": character_id,
        "character_name": char_data["name"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "current_scene": first_scene,
        "chapter_progress": 1,
        "stats": dict(char_data.get("initial_stats", {
            "wisdom": 50, "combat": 50, "loyalty": 50, "reputation": 50
        })),
        "choices_made": [],
        "relationships": {},
        "divergence_score": 0,
        "achievements": [],
        "inventory": list(char_data.get("abilities", [])),
        "session_log": []
    }

    # 初始化关系
    for name, desc in char_data.get("relationships", {}).items():
        save_data["relationships"][name] = {"trust": 50, "status": desc}

    write_save(save_id, save_data)

    meta_file = os.path.join(BOOKS_DIR, book_id, "meta.json")
    book_title = book_id
    if os.path.exists(meta_file):
        with open(meta_file, "r", encoding="utf-8") as f:
            book_title = json.load(f).get("title", book_id)

    print(f"新游戏创建成功！")
    print(f"  存档ID: {save_id}")
    print(f"  书籍: {book_title}")
    print(f"  角色: {char_data['name']}")
    print(f"  起始场景: {first_scene}")
    print(f"  属性: {json.dumps(save_data['stats'], ensure_ascii=False)}")


def advance(save_id, scene_id, choice_index, choice_desc=""):
    """推进游戏状态"""
    save = load_save(save_id)
    chars, plot = load_book_data(save["book_id"])

    # 查找场景
    scene = None
    for s in plot.get("scenes", []):
        if s["id"] == scene_id:
            scene = s
            break

    if not scene:
        print(f"警告: 场景 {scene_id} 未找到，使用自由模式推进")

    choice_index = int(choice_index)

    # 获取选择的属性效果
    is_canon = False
    stat_effects = {}
    relationship_effects = {}
    choices = scene.get("choices", []) if scene else []
    if choices and choice_index < len(choices):
        choice = choices[choice_index]
        is_canon = choice.get("canon", False)
        stat_effects = choice.get("stat_effects", {})
        relationship_effects = choice.get("relationship_effects", {})
        if not choice_desc:
            choice_desc = choice.get("description", "")

    # 更新属性
    for stat, delta in stat_effects.items():
        if stat in save["stats"]:
            save["stats"][stat] = max(0, min(100, save["stats"][stat] + delta))

    # 更新关系
    for name, delta in relationship_effects.items():
        if name in save["relationships"]:
            old_trust = save["relationships"][name]["trust"]
            save["relationships"][name]["trust"] = max(0, min(100, old_trust + delta))
        else:
            save["relationships"][name] = {"trust": 50 + delta, "status": "新认识"}

    # 更新偏离度
    if not is_canon:
        save["divergence_score"] = min(100, save["divergence_score"] + 5)

    # 记录选择
    save["choices_made"].append({
        "scene_id": scene_id,
        "choice_index": choice_index,
        "choice": choice_desc,
        "is_canon": is_canon,
    })

    # 更新session_log（保留最近10条）
    save["session_log"].append({
        "scene": scene_id,
        "action": choice_desc,
        "result": f"{'循原著' if is_canon else '偏离原著'}",
        "stat_effects": stat_effects,
        "relationship_effects": relationship_effects,
    })
    save["session_log"] = save["session_log"][-10:]

    # 推进到下一场景（支持分支）
    next_scenes = scene.get("next_scenes", []) if scene else []
    if next_scenes:
        # 如果有多条分支路径，根据choice_index选择
        if len(next_scenes) > 1 and choice_index < len(next_scenes):
            save["current_scene"] = next_scenes[choice_index]
        else:
            save["current_scene"] = next_scenes[0]
        # 更新章节进度
        next_scene_data = None
        for s in plot.get("scenes", []):
            if s["id"] == save["current_scene"]:
                next_scene_data = s
                break
        if next_scene_data:
            save["chapter_progress"] = next_scene_data.get("chapter", save["chapter_progress"])
    else:
        save["current_scene"] = "END"

    write_save(save_id, save)

    print(f"游戏推进成功！")
    print(f"  选择: {choice_desc}")
    print(f"  {'✓ 循原著' if is_canon else '✗ 偏离原著 (偏离度+5)'}")
    print(f"  属性变化: {json.dumps(stat_effects, ensure_ascii=False)}")
    if relationship_effects:
        print(f"  关系变化: {json.dumps(relationship_effects, ensure_ascii=False)}")
    print(f"  当前属性: {json.dumps(save['stats'], ensure_ascii=False)}")
    print(f"  下一场景: {save['current_scene']}")
    print(f"  偏离度: {save['divergence_score']}/100")


def load_game(save_id):
    """加载存档并显示状态"""
    save = load_save(save_id)

    meta_file = os.path.join(BOOKS_DIR, save["book_id"], "meta.json")
    book_title = save["book_id"]
    if os.path.exists(meta_file):
        with open(meta_file, "r", encoding="utf-8") as f:
            book_title = json.load(f).get("title", save["book_id"])

    print(f"存档: {save['save_id']}")
    print(f"书籍: {book_title}")
    print(f"角色: {save['character_name']}")
    print(f"章节: 第{save['chapter_progress']}回")
    print(f"当前场景: {save['current_scene']}")
    print(f"属性: {json.dumps(save['stats'], ensure_ascii=False)}")
    print(f"偏离度: {save['divergence_score']}/100")
    print(f"已做选择: {len(save['choices_made'])}次")
    if save.get("achievements"):
        print(f"成就: {'、'.join(save['achievements'])}")
    if save.get("session_log"):
        print(f"\n最近事件:")
        for log in save["session_log"][-3:]:
            print(f"  [{log['scene']}] {log['action']} → {log['result']}")


def list_saves():
    """列出所有存档"""
    ensure_dirs()
    saves = []
    for f in os.listdir(SAVES_DIR):
        if f.endswith(".json"):
            path = os.path.join(SAVES_DIR, f)
            with open(path, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                saves.append(data)

    if not saves:
        print("暂无存档。")
        return

    saves.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    print(f"共 {len(saves)} 个存档：\n")
    for s in saves:
        meta_file = os.path.join(BOOKS_DIR, s["book_id"], "meta.json")
        book_title = s["book_id"]
        if os.path.exists(meta_file):
            with open(meta_file, "r", encoding="utf-8") as f:
                book_title = json.load(f).get("title", s["book_id"])

        status = "已通关" if s["current_scene"] == "END" else f"第{s['chapter_progress']}回"
        print(f"  {s['save_id']} | {book_title} · {s['character_name']} | {status} | 偏离度:{s['divergence_score']}")


def delete_save(save_id):
    """删除存档"""
    path = os.path.join(SAVES_DIR, f"{save_id}.json")
    if os.path.exists(path):
        os.remove(path)
        print(f"存档 {save_id} 已删除")
    else:
        print(f"存档 {save_id} 不存在")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: game_engine.py <command> [args]")
        print("命令:")
        print("  new-game <book-id> <character-id>  创建新游戏")
        print("  advance <save-id> <scene-id> <choice-index> [choice-desc]  推进")
        print("  load <save-id>                     加载存档")
        print("  list-saves                         列出存档")
        print("  delete <save-id>                   删除存档")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "new-game":
        if len(sys.argv) < 4:
            print("用法: game_engine.py new-game <book-id> <character-id>")
            sys.exit(1)
        new_game(sys.argv[2], sys.argv[3])
    elif cmd == "advance":
        if len(sys.argv) < 5:
            print("用法: game_engine.py advance <save-id> <scene-id> <choice-index> [choice-desc]")
            sys.exit(1)
        desc = sys.argv[5] if len(sys.argv) > 5 else ""
        advance(sys.argv[2], sys.argv[3], sys.argv[4], desc)
    elif cmd == "load":
        if len(sys.argv) < 3:
            print("用法: game_engine.py load <save-id>")
            sys.exit(1)
        load_game(sys.argv[2])
    elif cmd == "list-saves":
        list_saves()
    elif cmd == "delete":
        if len(sys.argv) < 3:
            print("用法: game_engine.py delete <save-id>")
            sys.exit(1)
        delete_save(sys.argv[2])
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)
