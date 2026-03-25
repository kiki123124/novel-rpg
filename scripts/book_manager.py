#!/usr/bin/env python3
"""书籍管理器 - 初始化内置书、列表、查询角色"""

import json
import os
import sys

DATA_DIR = os.path.expanduser("~/.openclaw/skills/novel-rpg/data")
BOOKS_DIR = os.path.join(DATA_DIR, "books")
INDEX_FILE = os.path.join(BOOKS_DIR, "_index.json")


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
    """初始化内置名著数据"""
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
    """返回内置书数据"""
    return [_xiyouji()]


def _xiyouji():
    """西游记 - 前10回数据"""
    return {
        "id": "xiyouji",
        "meta": {
            "id": "xiyouji",
            "title": "西游记",
            "author": "吴承恩",
            "language": "zh",
            "total_chapters": 100,
            "playable_characters": ["sun_wukong", "tang_seng", "zhu_bajie", "sha_wujing"],
            "arcs": [
                {"name": "石猴出世", "chapters": [1, 2, 3], "description": "石猴诞生、求仙访道、学艺归来"},
                {"name": "大闹天宫", "chapters": [4, 5, 6, 7], "description": "封官受辱、偷桃盗丹、大战天兵、被压五行山"},
                {"name": "取经缘起", "chapters": [8, 9, 10], "description": "观音寻人、唐僧身世、阴司地府"},
            ],
            "chapters": [
                {"number": 1, "title": "灵根育孕源流出 心性修持大道生",
                 "scene_count": 3, "key_characters": ["sun_wukong"],
                 "summary": "花果山仙石崩裂，石猴出世，入水帘洞称王，后漂洋过海拜菩提祖师为师"},
                {"number": 2, "title": "悟彻菩提真妙理 断魔归本合元神",
                 "scene_count": 3, "key_characters": ["sun_wukong"],
                 "summary": "悟空学得七十二变和筋斗云，被祖师逐出师门，回花果山"},
                {"number": 3, "title": "四海千山皆拱伏 九幽十类尽除名",
                 "scene_count": 3, "key_characters": ["sun_wukong"],
                 "summary": "悟空龙宫取金箍棒，地府勾生死簿，惊动天庭"},
                {"number": 4, "title": "官封弼马心何足 名注齐天意未宁",
                 "scene_count": 3, "key_characters": ["sun_wukong"],
                 "summary": "天庭封弼马温，悟空嫌官小反下天庭，自封齐天大圣"},
                {"number": 5, "title": "乱蟠桃大圣偷丹 反天宫诸神捉怪",
                 "scene_count": 3, "key_characters": ["sun_wukong"],
                 "summary": "悟空偷吃蟠桃、偷饮御酒、偷吃仙丹，大闹天宫"},
                {"number": 6, "title": "观音赴会问原因 小圣施威降大圣",
                 "scene_count": 3, "key_characters": ["sun_wukong"],
                 "summary": "二郎神与悟空斗法，太上老君暗算，悟空被擒"},
                {"number": 7, "title": "八卦炉中逃大圣 五行山下定心猿",
                 "scene_count": 3, "key_characters": ["sun_wukong"],
                 "summary": "悟空在八卦炉中炼出火眼金睛，再闹天宫，如来压于五行山下"},
                {"number": 8, "title": "我佛造经传极乐 观音奉旨上长安",
                 "scene_count": 2, "key_characters": ["tang_seng"],
                 "summary": "如来传经，观音东行寻取经人，沿途收服各路妖怪为候选"},
                {"number": 9, "title": "袁守诚妙算无私曲 老龙王拙计犯天条",
                 "scene_count": 2, "key_characters": ["tang_seng"],
                 "summary": "泾河龙王因赌气违旨降雨被斩，托梦唐太宗"},
                {"number": 10, "title": "二将军宫门镇鬼 唐太宗地府还魂",
                 "scene_count": 2, "key_characters": ["tang_seng"],
                 "summary": "唐太宗游地府，还魂后举办水陆大会，玄奘被选为取经人"},
            ],
        },
        "characters": {
            "characters": [
                {
                    "id": "sun_wukong",
                    "name": "孙悟空",
                    "aliases": ["齐天大圣", "美猴王", "行者", "斗战胜佛"],
                    "personality": "桀骜不驯、重情重义、机智勇敢、急躁冲动",
                    "abilities": ["七十二变", "筋斗云", "金箍棒", "火眼金睛"],
                    "relationships": {
                        "唐僧": "师父，又敬又怨",
                        "猪八戒": "师弟，嫌他懒但有情义",
                        "沙僧": "师弟，可靠的伙伴",
                        "菩提祖师": "启蒙恩师",
                        "如来佛祖": "曾被其镇压，后皈依"
                    },
                    "initial_stats": {"wisdom": 60, "combat": 95, "loyalty": 50, "reputation": 80},
                    "arc_summary": "从桀骜猴王到斗战胜佛的成长之路",
                    "first_appearance_chapter": 1,
                    "playable": True
                },
                {
                    "id": "tang_seng",
                    "name": "唐僧",
                    "aliases": ["玄奘", "唐三藏", "金蝉子"],
                    "personality": "慈悲为怀、意志坚定、不辨妖邪、优柔寡断",
                    "abilities": ["诵经", "感化众生"],
                    "relationships": {
                        "孙悟空": "大徒弟，又爱又怕",
                        "猪八戒": "二徒弟，常被其蒙蔽",
                        "沙僧": "三徒弟，最听话的",
                        "观音菩萨": "指引者"
                    },
                    "initial_stats": {"wisdom": 80, "combat": 5, "loyalty": 90, "reputation": 70},
                    "arc_summary": "凡人之躯踏上西天取经的信念之旅",
                    "first_appearance_chapter": 8,
                    "playable": True
                },
                {
                    "id": "zhu_bajie",
                    "name": "猪八戒",
                    "aliases": ["天蓬元帅", "猪悟能", "呆子"],
                    "personality": "好吃懒做、贪财好色、憨厚可爱、关键时刻靠得住",
                    "abilities": ["天罡三十六变", "九齿钉耙", "水性好"],
                    "relationships": {
                        "孙悟空": "师兄，又怕又服",
                        "唐僧": "师父，常在师父面前告状",
                        "沙僧": "师弟"
                    },
                    "initial_stats": {"wisdom": 30, "combat": 70, "loyalty": 40, "reputation": 30},
                    "arc_summary": "从天蓬元帅贬入凡间，在取经路上磨炼心性",
                    "first_appearance_chapter": 18,
                    "playable": True
                },
                {
                    "id": "sha_wujing",
                    "name": "沙僧",
                    "aliases": ["卷帘大将", "沙悟净", "沙和尚"],
                    "personality": "忠厚老实、任劳任怨、存在感低但不可或缺",
                    "abilities": ["降妖宝杖", "水性极佳"],
                    "relationships": {
                        "孙悟空": "大师兄",
                        "猪八戒": "二师兄，常劝和",
                        "唐僧": "师父，最听话"
                    },
                    "initial_stats": {"wisdom": 50, "combat": 55, "loyalty": 95, "reputation": 20},
                    "arc_summary": "沉默守护者，在取经路上默默奉献",
                    "first_appearance_chapter": 22,
                    "playable": True
                }
            ]
        },
        "plot_graph": {
            "scenes": [
                # === 第一回 ===
                {
                    "id": "ch01_s01", "chapter": 1, "scene_index": 1,
                    "title": "石猴出世",
                    "characters_present": ["sun_wukong"],
                    "location": "花果山",
                    "summary": "东胜神洲花果山顶仙石崩裂，化出一个石猴。石猴与群猴嬉戏玩耍。",
                    "plot_type": "origin",
                    "challenge_potential": 2,
                    "choices": [
                        {"description": "主动探索水帘洞", "canon": True, "stat_effects": {"combat": 0, "wisdom": 5, "reputation": 10}},
                        {"description": "让其他猴子先探路", "canon": False, "stat_effects": {"wisdom": 10, "loyalty": 5}},
                        {"description": "独自离开猴群探索山脉", "canon": False, "stat_effects": {"combat": 5, "wisdom": 5}}
                    ],
                    "next_scenes": ["ch01_s02"]
                },
                {
                    "id": "ch01_s02", "chapter": 1, "scene_index": 2,
                    "title": "水帘洞称王",
                    "characters_present": ["sun_wukong"],
                    "location": "水帘洞",
                    "summary": "石猴率先跳入瀑布，发现水帘洞天，被群猴拥戴为美猴王。",
                    "plot_type": "origin",
                    "challenge_potential": 3,
                    "choices": [
                        {"description": "接受猴群拥戴，称王花果山", "canon": True, "stat_effects": {"reputation": 15, "loyalty": 5}},
                        {"description": "虽称王但立即寻求长生之道", "canon": False, "stat_effects": {"wisdom": 15}},
                        {"description": "与猴群平等相处，不称王", "canon": False, "stat_effects": {"loyalty": 15, "reputation": -5}}
                    ],
                    "next_scenes": ["ch01_s03"]
                },
                {
                    "id": "ch01_s03", "chapter": 1, "scene_index": 3,
                    "title": "漂洋求仙",
                    "characters_present": ["sun_wukong"],
                    "location": "南赡部洲 → 西牛贺洲",
                    "summary": "美猴王感叹生死无常，立志求仙访道，扎木筏漂洋过海，历经人间，终到灵台方寸山。",
                    "plot_type": "journey",
                    "challenge_potential": 4,
                    "choices": [
                        {"description": "拜菩提祖师为师，虔心求学", "canon": True, "stat_effects": {"wisdom": 20, "loyalty": 10}},
                        {"description": "先在人间历练一番再求仙", "canon": False, "stat_effects": {"combat": 10, "wisdom": 5, "reputation": 5}},
                        {"description": "质疑祖师，要求先展示法术", "canon": False, "stat_effects": {"combat": 5, "wisdom": -5}}
                    ],
                    "next_scenes": ["ch02_s01"]
                },
                # === 第二回 ===
                {
                    "id": "ch02_s01", "chapter": 2, "scene_index": 1,
                    "title": "悟彻妙理",
                    "characters_present": ["sun_wukong"],
                    "location": "灵台方寸山·斜月三星洞",
                    "summary": "菩提祖师讲道，悟空悟性过人，祖师夜半秘传七十二变之术。",
                    "plot_type": "origin",
                    "challenge_potential": 4,
                    "choices": [
                        {"description": "专心修炼，不在同门面前卖弄", "canon": False, "stat_effects": {"wisdom": 20, "loyalty": 10}},
                        {"description": "忍不住在师兄弟面前展示变化", "canon": True, "stat_effects": {"combat": 10, "reputation": 5, "wisdom": -5}},
                        {"description": "请求祖师传授更多法术", "canon": False, "stat_effects": {"combat": 15, "loyalty": -5}}
                    ],
                    "next_scenes": ["ch02_s02"]
                },
                {
                    "id": "ch02_s02", "chapter": 2, "scene_index": 2,
                    "title": "学筋斗云",
                    "characters_present": ["sun_wukong"],
                    "location": "灵台方寸山",
                    "summary": "祖师教授筋斗云，一个跟头十万八千里。",
                    "plot_type": "origin",
                    "challenge_potential": 3,
                    "choices": [
                        {"description": "刻苦练习直到精通", "canon": True, "stat_effects": {"combat": 15, "wisdom": 5}},
                        {"description": "偷偷用筋斗云探索外面的世界", "canon": False, "stat_effects": {"combat": 5, "wisdom": 10, "reputation": 5}},
                        {"description": "向祖师请教筋斗云的更深奥义", "canon": False, "stat_effects": {"wisdom": 20}}
                    ],
                    "next_scenes": ["ch02_s03"]
                },
                {
                    "id": "ch02_s03", "chapter": 2, "scene_index": 3,
                    "title": "被逐出师门",
                    "characters_present": ["sun_wukong"],
                    "location": "灵台方寸山",
                    "summary": "悟空卖弄变化被祖师发现，祖师将其逐出，嘱其不可说出师承。",
                    "plot_type": "conflict",
                    "challenge_potential": 5,
                    "choices": [
                        {"description": "含泪拜别，遵师命绝口不提", "canon": True, "stat_effects": {"loyalty": 20, "wisdom": 10}},
                        {"description": "恳求留下，愿受任何惩罚", "canon": False, "stat_effects": {"loyalty": 15, "reputation": -5}},
                        {"description": "愤然离去，觉得祖师薄情", "canon": False, "stat_effects": {"combat": 5, "loyalty": -10, "wisdom": -10}}
                    ],
                    "next_scenes": ["ch03_s01"]
                },
                # === 第三回 ===
                {
                    "id": "ch03_s01", "chapter": 3, "scene_index": 1,
                    "title": "龙宫取宝",
                    "characters_present": ["sun_wukong"],
                    "location": "东海龙宫",
                    "summary": "悟空回花果山后闯入东海龙宫，试遍兵器，唯有定海神针如意金箍棒称手。",
                    "plot_type": "conflict",
                    "challenge_potential": 5,
                    "choices": [
                        {"description": "强取金箍棒，再索要披挂", "canon": True, "stat_effects": {"combat": 20, "reputation": 10, "wisdom": -5}},
                        {"description": "以礼相求，只取金箍棒", "canon": False, "stat_effects": {"combat": 15, "wisdom": 10, "loyalty": 5}},
                        {"description": "大闹龙宫，把四海龙王都叫来", "canon": False, "stat_effects": {"combat": 15, "reputation": 15, "wisdom": -10}}
                    ],
                    "next_scenes": ["ch03_s02"]
                },
                {
                    "id": "ch03_s02", "chapter": 3, "scene_index": 2,
                    "title": "勾销生死簿",
                    "characters_present": ["sun_wukong"],
                    "location": "地府",
                    "summary": "悟空魂游地府，发现自己在生死簿上，一怒之下将猴属名字全部勾销。",
                    "plot_type": "conflict",
                    "challenge_potential": 5,
                    "choices": [
                        {"description": "大笔一挥，勾销所有猴属生死", "canon": True, "stat_effects": {"reputation": 20, "loyalty": 10, "wisdom": -10}},
                        {"description": "只勾销自己的名字", "canon": False, "stat_effects": {"reputation": 5, "wisdom": 5}},
                        {"description": "与阎王讲理，要求合法免死", "canon": False, "stat_effects": {"wisdom": 20, "reputation": -5}}
                    ],
                    "next_scenes": ["ch03_s03"]
                },
                {
                    "id": "ch03_s03", "chapter": 3, "scene_index": 3,
                    "title": "惊动天庭",
                    "characters_present": ["sun_wukong"],
                    "location": "花果山/天庭",
                    "summary": "龙王和阎王上天告状，玉帝震怒，太白金星建议招安。",
                    "plot_type": "conflict",
                    "challenge_potential": 3,
                    "choices": [
                        {"description": "接受天庭招安，上天赴任", "canon": True, "stat_effects": {"wisdom": 5, "reputation": 10}},
                        {"description": "拒绝招安，继续在花果山称王", "canon": False, "stat_effects": {"combat": 10, "loyalty": 10, "reputation": 15}},
                        {"description": "提出条件：要封大官才去", "canon": False, "stat_effects": {"wisdom": 10, "reputation": 5}}
                    ],
                    "next_scenes": ["ch04_s01"]
                },
                # === 第四回 ===
                {
                    "id": "ch04_s01", "chapter": 4, "scene_index": 1,
                    "title": "弼马温",
                    "characters_present": ["sun_wukong"],
                    "location": "天庭·御马监",
                    "summary": "悟空被封弼马温，尽心养马，后知此乃未入流小官，大怒。",
                    "plot_type": "conflict",
                    "challenge_potential": 5,
                    "choices": [
                        {"description": "愤然打出南天门，回花果山", "canon": True, "stat_effects": {"combat": 5, "reputation": 15, "wisdom": -5}},
                        {"description": "忍辱负重，在天庭暗中积蓄力量", "canon": False, "stat_effects": {"wisdom": 20, "loyalty": -5}},
                        {"description": "直接去找玉帝理论", "canon": False, "stat_effects": {"combat": 5, "wisdom": 5, "reputation": 10}}
                    ],
                    "next_scenes": ["ch04_s02"]
                },
                {
                    "id": "ch04_s02", "chapter": 4, "scene_index": 2,
                    "title": "齐天大圣",
                    "characters_present": ["sun_wukong"],
                    "location": "花果山",
                    "summary": "悟空回花果山竖起齐天大圣旗，天庭派兵讨伐，悟空大胜。",
                    "plot_type": "battle",
                    "challenge_potential": 5,
                    "choices": [
                        {"description": "击败天兵后接受齐天大圣封号", "canon": True, "stat_effects": {"combat": 10, "reputation": 20}},
                        {"description": "乘胜追击，反攻天庭", "canon": False, "stat_effects": {"combat": 20, "reputation": 10, "wisdom": -15}},
                        {"description": "打退天兵后主动求和", "canon": False, "stat_effects": {"wisdom": 15, "reputation": -5}}
                    ],
                    "next_scenes": ["ch04_s03"]
                },
                {
                    "id": "ch04_s03", "chapter": 4, "scene_index": 3,
                    "title": "有名无实",
                    "characters_present": ["sun_wukong"],
                    "location": "天庭·齐天大圣府",
                    "summary": "天庭封悟空为齐天大圣，但不给实权，只是空衔。悟空日日游荡。",
                    "plot_type": "conflict",
                    "challenge_potential": 3,
                    "choices": [
                        {"description": "安于现状，游手好闲", "canon": True, "stat_effects": {"wisdom": -5}},
                        {"description": "主动找事做，融入天庭", "canon": False, "stat_effects": {"wisdom": 15, "loyalty": 10}},
                        {"description": "四处结交神仙，扩大人脉", "canon": False, "stat_effects": {"reputation": 15, "wisdom": 10}}
                    ],
                    "next_scenes": ["ch05_s01"]
                },
                # === 第五回 ===
                {
                    "id": "ch05_s01", "chapter": 5, "scene_index": 1,
                    "title": "偷吃蟠桃",
                    "characters_present": ["sun_wukong"],
                    "location": "天庭·蟠桃园",
                    "summary": "悟空被派看管蟠桃园，得知蟠桃会未请自己，大怒，偷吃仙桃。",
                    "plot_type": "conflict",
                    "challenge_potential": 5,
                    "choices": [
                        {"description": "大吃特吃，把最好的蟠桃都吃了", "canon": True, "stat_effects": {"combat": 15, "wisdom": -10}},
                        {"description": "只吃几个尝尝味道，保持克制", "canon": False, "stat_effects": {"wisdom": 15, "loyalty": 5}},
                        {"description": "质问为何不请自己参加蟠桃会", "canon": False, "stat_effects": {"wisdom": 10, "reputation": 5}}
                    ],
                    "next_scenes": ["ch05_s02"]
                },
                {
                    "id": "ch05_s02", "chapter": 5, "scene_index": 2,
                    "title": "盗饮御酒偷吃仙丹",
                    "characters_present": ["sun_wukong"],
                    "location": "天庭·瑶池/兜率宫",
                    "summary": "悟空变化混入蟠桃宴偷喝御酒，醉后闯入兜率宫偷吃太上老君仙丹。",
                    "plot_type": "conflict",
                    "challenge_potential": 5,
                    "choices": [
                        {"description": "酒醉后继续闯祸，偷吃仙丹", "canon": True, "stat_effects": {"combat": 20, "wisdom": -15, "reputation": 10}},
                        {"description": "酒醒后意识到闯祸了，赶紧逃回花果山", "canon": False, "stat_effects": {"wisdom": 10}},
                        {"description": "醉中大闹蟠桃宴，当众宣战", "canon": False, "stat_effects": {"combat": 10, "reputation": 15, "wisdom": -10}}
                    ],
                    "next_scenes": ["ch05_s03"]
                },
                {
                    "id": "ch05_s03", "chapter": 5, "scene_index": 3,
                    "title": "逃回花果山",
                    "characters_present": ["sun_wukong"],
                    "location": "花果山",
                    "summary": "悟空知道闯了大祸，带着仙丹逃回花果山，与众猴分享。",
                    "plot_type": "journey",
                    "challenge_potential": 3,
                    "choices": [
                        {"description": "回花果山分享仙丹，备战天庭", "canon": True, "stat_effects": {"loyalty": 15, "combat": 5}},
                        {"description": "独自找个地方躲起来", "canon": False, "stat_effects": {"wisdom": 5, "loyalty": -15}},
                        {"description": "主动回天庭请罪", "canon": False, "stat_effects": {"wisdom": 20, "loyalty": 5, "reputation": -10}}
                    ],
                    "next_scenes": ["ch06_s01"]
                },
                # === 第六回 ===
                {
                    "id": "ch06_s01", "chapter": 6, "scene_index": 1,
                    "title": "大战二郎神",
                    "characters_present": ["sun_wukong"],
                    "location": "花果山",
                    "summary": "天庭派十万天兵围攻花果山，悟空与二郎神杨戬展开变化斗法。",
                    "plot_type": "battle",
                    "challenge_potential": 5,
                    "choices": [
                        {"description": "与二郎神正面斗法，比拼变化", "canon": True, "stat_effects": {"combat": 20, "reputation": 10}},
                        {"description": "用计谋引二郎神入陷阱", "canon": False, "stat_effects": {"wisdom": 20, "combat": 5}},
                        {"description": "变化逃走，不正面对抗", "canon": False, "stat_effects": {"wisdom": 10, "reputation": -10}}
                    ],
                    "next_scenes": ["ch06_s02"]
                },
                {
                    "id": "ch06_s02", "chapter": 6, "scene_index": 2,
                    "title": "被擒",
                    "characters_present": ["sun_wukong"],
                    "location": "花果山",
                    "summary": "太上老君趁悟空与二郎神斗法，暗中用金刚琢偷袭，悟空被擒。",
                    "plot_type": "conflict",
                    "challenge_potential": 4,
                    "choices": [
                        {"description": "被暗算击中，英雄末路", "canon": True, "stat_effects": {"combat": -5}},
                        {"description": "察觉暗器及时躲避（高combat可选）", "canon": False, "stat_effects": {"combat": 10, "wisdom": 10}, "requires": {"combat": 90}},
                        {"description": "假装被擒，暗中筹谋", "canon": False, "stat_effects": {"wisdom": 15}}
                    ],
                    "next_scenes": ["ch06_s03"]
                },
                {
                    "id": "ch06_s03", "chapter": 6, "scene_index": 3,
                    "title": "刀斧不伤",
                    "characters_present": ["sun_wukong"],
                    "location": "天庭·斩妖台",
                    "summary": "天庭用各种方法处决悟空，刀砍斧剁雷劈火烧皆不能伤。",
                    "plot_type": "conflict",
                    "challenge_potential": 3,
                    "choices": [
                        {"description": "坦然受刑，展示不死之身", "canon": True, "stat_effects": {"reputation": 15, "combat": 5}},
                        {"description": "趁机挣脱束缚反抗", "canon": False, "stat_effects": {"combat": 15, "wisdom": -5}},
                        {"description": "嘲讽行刑者，展现藐视一切的气魄", "canon": False, "stat_effects": {"reputation": 20, "wisdom": -10}}
                    ],
                    "next_scenes": ["ch07_s01"]
                },
                # === 第七回 ===
                {
                    "id": "ch07_s01", "chapter": 7, "scene_index": 1,
                    "title": "八卦炉炼丹",
                    "characters_present": ["sun_wukong"],
                    "location": "天庭·兜率宫",
                    "summary": "太上老君将悟空放入八卦炉中炼化，四十九天后悟空非但未死，反炼出火眼金睛。",
                    "plot_type": "origin",
                    "challenge_potential": 5,
                    "choices": [
                        {"description": "在炉中苦熬，最终炼出火眼金睛", "canon": True, "stat_effects": {"combat": 15, "wisdom": 15}},
                        {"description": "在炉中参悟大道，心境升华", "canon": False, "stat_effects": {"wisdom": 25, "combat": 5}},
                        {"description": "设法从炉中破出，不等炼化完成", "canon": False, "stat_effects": {"combat": 20, "wisdom": -5}}
                    ],
                    "next_scenes": ["ch07_s02"]
                },
                {
                    "id": "ch07_s02", "chapter": 7, "scene_index": 2,
                    "title": "再闹天宫",
                    "characters_present": ["sun_wukong"],
                    "location": "天庭",
                    "summary": "悟空踢翻八卦炉，手持金箍棒打遍天宫，无人能挡。",
                    "plot_type": "battle",
                    "challenge_potential": 5,
                    "choices": [
                        {"description": "打上凌霄宝殿，挑战玉帝", "canon": True, "stat_effects": {"combat": 15, "reputation": 25, "wisdom": -15}},
                        {"description": "适可而止，趁机逃离天庭", "canon": False, "stat_effects": {"wisdom": 20, "reputation": 5}},
                        {"description": "宣告自己要做天帝", "canon": False, "stat_effects": {"reputation": 20, "combat": 5, "wisdom": -20}}
                    ],
                    "next_scenes": ["ch07_s03"]
                },
                {
                    "id": "ch07_s03", "chapter": 7, "scene_index": 3,
                    "title": "五行山下",
                    "characters_present": ["sun_wukong"],
                    "location": "五行山",
                    "summary": "如来佛祖以掌化五行山，将悟空压在山下五百年。",
                    "plot_type": "resolution",
                    "challenge_potential": 5,
                    "choices": [
                        {"description": "与如来打赌翻出手掌，落入陷阱", "canon": True, "stat_effects": {"wisdom": -10, "combat": 5}},
                        {"description": "识破如来的手段，拒绝打赌", "canon": False, "stat_effects": {"wisdom": 25}, "requires": {"wisdom": 80}},
                        {"description": "认输求饶，请求从轻发落", "canon": False, "stat_effects": {"wisdom": 15, "loyalty": 10, "reputation": -15}}
                    ],
                    "next_scenes": ["ch08_s01"]
                },
                # === 第八回 ===
                {
                    "id": "ch08_s01", "chapter": 8, "scene_index": 1,
                    "title": "观音东行",
                    "characters_present": ["tang_seng"],
                    "location": "灵山 → 东土",
                    "summary": "如来讲经，观音菩萨奉旨前往东土寻找取经人。",
                    "plot_type": "journey",
                    "challenge_potential": 2,
                    "choices": [
                        {"description": "（唐僧视角）在寺中潜心修行", "canon": True, "stat_effects": {"wisdom": 10, "loyalty": 5}},
                        {"description": "（唐僧视角）对佛法产生疑问，渴望求证", "canon": False, "stat_effects": {"wisdom": 15}}
                    ],
                    "next_scenes": ["ch08_s02"]
                },
                {
                    "id": "ch08_s02", "chapter": 8, "scene_index": 2,
                    "title": "收服沿途妖怪",
                    "characters_present": [],
                    "location": "取经路沿途",
                    "summary": "观音沿途收服沙悟净、猪悟能、小白龙，安排他们等候取经人。",
                    "plot_type": "journey",
                    "challenge_potential": 2,
                    "choices": [
                        {"description": "继续修行等待命运安排", "canon": True, "stat_effects": {"wisdom": 5, "loyalty": 10}},
                        {"description": "主动寻找人生的更高意义", "canon": False, "stat_effects": {"wisdom": 10}}
                    ],
                    "next_scenes": ["ch09_s01"]
                },
                # === 第九回 ===
                {
                    "id": "ch09_s01", "chapter": 9, "scene_index": 1,
                    "title": "江流儿身世",
                    "characters_present": ["tang_seng"],
                    "location": "长安/金山寺",
                    "summary": "玄奘身世揭晓：父亲被害，母亲忍辱，自己被放入江中漂流，被金山寺长老收养。",
                    "plot_type": "origin",
                    "challenge_potential": 4,
                    "choices": [
                        {"description": "得知身世后决心为父报仇", "canon": True, "stat_effects": {"loyalty": 15, "combat": 5}},
                        {"description": "悲痛但选择以佛法化解仇恨", "canon": False, "stat_effects": {"wisdom": 20, "loyalty": 5}},
                        {"description": "质疑命运，对佛法产生动摇", "canon": False, "stat_effects": {"wisdom": 5, "loyalty": -10}}
                    ],
                    "next_scenes": ["ch09_s02"]
                },
                {
                    "id": "ch09_s02", "chapter": 9, "scene_index": 2,
                    "title": "泾河龙王之死",
                    "characters_present": ["tang_seng"],
                    "location": "长安",
                    "summary": "泾河龙王因违旨被魏征梦中所斩，托梦唐太宗求救未果。",
                    "plot_type": "conflict",
                    "challenge_potential": 3,
                    "choices": [
                        {"description": "为龙王超度祈福", "canon": True, "stat_effects": {"wisdom": 10, "loyalty": 5}},
                        {"description": "思考天命与因果的道理", "canon": False, "stat_effects": {"wisdom": 15}},
                        {"description": "对天庭的严酷法则感到不安", "canon": False, "stat_effects": {"wisdom": 5, "loyalty": -5}}
                    ],
                    "next_scenes": ["ch10_s01"]
                },
                # === 第十回 ===
                {
                    "id": "ch10_s01", "chapter": 10, "scene_index": 1,
                    "title": "太宗游地府",
                    "characters_present": ["tang_seng"],
                    "location": "长安/地府",
                    "summary": "唐太宗因龙王之事魂游地府，见识因果报应，还魂后举办水陆大会。",
                    "plot_type": "journey",
                    "challenge_potential": 3,
                    "choices": [
                        {"description": "主持水陆大会，展现佛法修为", "canon": True, "stat_effects": {"wisdom": 10, "reputation": 15}},
                        {"description": "在大会上质疑：超度真能解脱？", "canon": False, "stat_effects": {"wisdom": 15, "reputation": -5}},
                        {"description": "借此机会宣扬大乘佛法", "canon": False, "stat_effects": {"wisdom": 10, "reputation": 10}}
                    ],
                    "next_scenes": ["ch10_s02"]
                },
                {
                    "id": "ch10_s02", "chapter": 10, "scene_index": 2,
                    "title": "踏上取经路",
                    "characters_present": ["tang_seng"],
                    "location": "长安城外",
                    "summary": "观音点化，玄奘被选为取经人，唐太宗亲送出城，赐号三藏。",
                    "plot_type": "journey",
                    "challenge_potential": 5,
                    "choices": [
                        {"description": "义无反顾踏上西行之路", "canon": True, "stat_effects": {"loyalty": 20, "wisdom": 10, "reputation": 10}},
                        {"description": "心中忐忑但仍坚定出发", "canon": False, "stat_effects": {"wisdom": 15, "loyalty": 10}},
                        {"description": "请求多带几个随从保护", "canon": False, "stat_effects": {"wisdom": 5, "combat": 5, "loyalty": -5}}
                    ],
                    "next_scenes": []
                }
            ]
        }
    }


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
