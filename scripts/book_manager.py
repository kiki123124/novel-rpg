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
    return [_xiyouji(), _wuthering_heights()]


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


def _wuthering_heights():
    """呼啸山庄 - 前10章数据"""
    return {
        "id": "wuthering-heights",
        "meta": {
            "id": "wuthering-heights",
            "title": "呼啸山庄",
            "author": "Emily Brontë",
            "language": "en",
            "total_chapters": 34,
            "playable_characters": ["heathcliff", "catherine", "nelly", "linton_heathcliff"],
            "arcs": [
                {"name": "荒原孤儿", "chapters": [1, 2, 3, 4], "description": "希斯克利夫被收养，与凯瑟琳的童年羁绊"},
                {"name": "爱与背叛", "chapters": [5, 6, 7, 8, 9], "description": "凯瑟琳选择林顿，希斯克利夫出走"},
                {"name": "复仇归来", "chapters": [10, 11, 12], "description": "希斯克利夫归来，风暴降临两个庄园"},
            ],
            "chapters": [
                {"number": 1, "title": "洛克伍德造访呼啸山庄",
                 "scene_count": 3, "key_characters": ["heathcliff"],
                 "summary": "新房客洛克伍德拜访房东希斯克利夫，见识呼啸山庄的阴郁古怪"},
                {"number": 2, "title": "暴风雪中的噩梦",
                 "scene_count": 2, "key_characters": ["heathcliff", "catherine"],
                 "summary": "洛克伍德被困呼啸山庄过夜，梦见凯瑟琳的幽灵在窗外哭泣"},
                {"number": 3, "title": "耐莉开始讲述",
                 "scene_count": 2, "key_characters": ["nelly"],
                 "summary": "管家耐莉·丁恩向洛克伍德讲述呼啸山庄的往事"},
                {"number": 4, "title": "荒原上的孤儿",
                 "scene_count": 3, "key_characters": ["heathcliff", "catherine"],
                 "summary": "恩肖先生从利物浦带回流浪儿希斯克利夫，辛德雷嫉恨，凯瑟琳与之结为挚友"},
                {"number": 5, "title": "恩肖先生之死",
                 "scene_count": 2, "key_characters": ["heathcliff", "catherine"],
                 "summary": "老恩肖去世，辛德雷继承庄园，将希斯克利夫贬为仆人"},
                {"number": 6, "title": "画眉田庄的诱惑",
                 "scene_count": 3, "key_characters": ["heathcliff", "catherine"],
                 "summary": "凯瑟琳和希斯克利夫偷窥画眉田庄，凯瑟琳被狗咬伤留在林顿家养伤，接触上流社会"},
                {"number": 7, "title": "凯瑟琳的蜕变",
                 "scene_count": 3, "key_characters": ["heathcliff", "catherine"],
                 "summary": "凯瑟琳从画眉田庄归来已成淑女，希斯克利夫感到被抛弃的痛苦"},
                {"number": 8, "title": "圣诞宴会的屈辱",
                 "scene_count": 3, "key_characters": ["heathcliff", "catherine"],
                 "summary": "林顿兄妹来访，辛德雷羞辱希斯克利夫，希斯克利夫心中种下复仇的种子"},
                {"number": 9, "title": "凯瑟琳的抉择",
                 "scene_count": 3, "key_characters": ["heathcliff", "catherine", "nelly"],
                 "summary": "凯瑟琳向耐莉倾诉：嫁给林顿是为了地位，但她的灵魂属于希斯克利夫。希斯克利夫只听到前半句，愤然出走"},
                {"number": 10, "title": "三年后的归来",
                 "scene_count": 3, "key_characters": ["heathcliff", "catherine"],
                 "summary": "希斯克利夫神秘归来，衣着体面、腰缠万贯，凯瑟琳狂喜，林顿不安"},
            ],
        },
        "characters": {
            "characters": [
                {
                    "id": "heathcliff",
                    "name": "希斯克利夫",
                    "aliases": ["Heathcliff"],
                    "personality": "阴郁偏执、爱恨极端、坚韧不屈、复仇心切",
                    "abilities": ["坚忍意志", "商业手腕", "操控人心"],
                    "relationships": {
                        "凯瑟琳": "灵魂伴侣，此生唯一所爱",
                        "辛德雷": "仇人，夺我尊严之人",
                        "埃德加·林顿": "情敌，夺我所爱之人",
                        "耐莉": "旧日知情人，又恨又需要",
                        "伊莎贝拉": "复仇工具"
                    },
                    "initial_stats": {"wisdom": 55, "combat": 70, "loyalty": 90, "reputation": 20},
                    "arc_summary": "从被遗弃的孤儿到被仇恨吞噬的复仇者，最终在爱与死之间寻找解脱",
                    "first_appearance_chapter": 1,
                    "playable": True
                },
                {
                    "id": "catherine",
                    "name": "凯瑟琳·恩肖",
                    "aliases": ["Catherine Earnshaw", "Cathy"],
                    "personality": "野性自由、热情奔放、虚荣矛盾、爱得炽烈",
                    "abilities": ["感染力", "操控情感", "不屈的意志"],
                    "relationships": {
                        "希斯克利夫": "灵魂的另一半，'我就是希斯克利夫'",
                        "埃德加·林顿": "丈夫，代表体面与安稳",
                        "辛德雷": "兄长，又怕又厌",
                        "耐莉": "自幼陪伴的仆人与倾诉对象"
                    },
                    "initial_stats": {"wisdom": 40, "combat": 30, "loyalty": 60, "reputation": 70},
                    "arc_summary": "在野性与文明、爱情与地位之间撕裂，最终被自己的选择毁灭",
                    "first_appearance_chapter": 2,
                    "playable": True
                },
                {
                    "id": "nelly",
                    "name": "耐莉·丁恩",
                    "aliases": ["Nelly Dean", "Ellen"],
                    "personality": "务实精明、善于观察、有自己的偏见、忠于职守",
                    "abilities": ["洞察人心", "斡旋调停", "叙事者的全知视角"],
                    "relationships": {
                        "凯瑟琳": "从小看着长大，又爱又恨",
                        "希斯克利夫": "同情与恐惧并存",
                        "埃德加·林顿": "尊敬的主人",
                        "辛德雷": "一同长大的少爷"
                    },
                    "initial_stats": {"wisdom": 80, "combat": 15, "loyalty": 75, "reputation": 60},
                    "arc_summary": "作为旁观者见证两个家族的悲剧，她的每个选择都悄然改变着他人的命运",
                    "first_appearance_chapter": 3,
                    "playable": True
                },
                {
                    "id": "linton_heathcliff",
                    "name": "埃德加·林顿",
                    "aliases": ["Edgar Linton"],
                    "personality": "温文尔雅、懦弱善良、深情专一、缺乏魄力",
                    "abilities": ["教养与学识", "财富与地位", "温柔的爱"],
                    "relationships": {
                        "凯瑟琳": "妻子，深爱却无法理解",
                        "希斯克利夫": "恐惧与嫉妒的对象",
                        "伊莎贝拉": "妹妹",
                        "耐莉": "信赖的管家"
                    },
                    "initial_stats": {"wisdom": 65, "combat": 20, "loyalty": 85, "reputation": 90},
                    "arc_summary": "用温柔对抗荒原的风暴，却发现爱无法被驯服",
                    "first_appearance_chapter": 6,
                    "playable": True
                }
            ]
        },
        "plot_graph": {
            "scenes": [
                # === 第1章 ===
                {
                    "id": "ch01_s01", "chapter": 1, "scene_index": 1,
                    "title": "初到呼啸山庄",
                    "characters_present": ["heathcliff"],
                    "location": "呼啸山庄",
                    "summary": "1801年，洛克伍德拜访房东希斯克利夫，呼啸山庄荒凉阴沉，主人冷漠粗暴。",
                    "plot_type": "origin",
                    "challenge_potential": 2,
                    "choices": [
                        {"description": "以冷漠回应来客，维持孤僻形象", "canon": True, "stat_effects": {"reputation": -5, "wisdom": 5}},
                        {"description": "试着对来客表现出一丝礼貌", "canon": False, "stat_effects": {"reputation": 10, "loyalty": -5}},
                        {"description": "直接拒绝来客进门", "canon": False, "stat_effects": {"combat": 5, "reputation": -10}}
                    ],
                    "next_scenes": ["ch01_s02"]
                },
                {
                    "id": "ch01_s02", "chapter": 1, "scene_index": 2,
                    "title": "山庄中的怪异住客",
                    "characters_present": ["heathcliff"],
                    "location": "呼啸山庄·客厅",
                    "summary": "洛克伍德见到哈里顿、小凯瑟琳和约瑟夫，山庄气氛压抑古怪。",
                    "plot_type": "origin",
                    "challenge_potential": 2,
                    "choices": [
                        {"description": "无视他们的存在，沉浸在自己的世界", "canon": True, "stat_effects": {"wisdom": 5}},
                        {"description": "观察这些人之间的关系", "canon": False, "stat_effects": {"wisdom": 15}},
                        {"description": "粗暴地命令他们各安其位", "canon": False, "stat_effects": {"combat": 5, "reputation": -5}}
                    ],
                    "next_scenes": ["ch01_s03"]
                },
                {
                    "id": "ch01_s03", "chapter": 1, "scene_index": 3,
                    "title": "荒原上的狂犬",
                    "characters_present": ["heathcliff"],
                    "location": "呼啸山庄",
                    "summary": "洛克伍德被狗攻击，希斯克利夫冷眼旁观，耐莉出手相救。",
                    "plot_type": "conflict",
                    "challenge_potential": 3,
                    "choices": [
                        {"description": "冷眼旁观，不为所动", "canon": True, "stat_effects": {"combat": 5, "loyalty": -5}},
                        {"description": "喝止恶犬，展示主人的权威", "canon": False, "stat_effects": {"reputation": 10, "loyalty": 5}},
                        {"description": "嘲讽来客的狼狈", "canon": False, "stat_effects": {"reputation": -10, "wisdom": -5}}
                    ],
                    "next_scenes": ["ch02_s01"]
                },
                # === 第2章 ===
                {
                    "id": "ch02_s01", "chapter": 2, "scene_index": 1,
                    "title": "暴风雪之夜",
                    "characters_present": ["heathcliff"],
                    "location": "呼啸山庄",
                    "summary": "洛克伍德再次来访被暴风雪困住，被安排在一间尘封的房间过夜。",
                    "plot_type": "journey",
                    "challenge_potential": 3,
                    "choices": [
                        {"description": "不愿让人住进那个房间，但不说原因", "canon": True, "stat_effects": {"wisdom": 5, "loyalty": 5}},
                        {"description": "警告来客不要动房间里的东西", "canon": False, "stat_effects": {"wisdom": 10}},
                        {"description": "无所谓，随便他住哪", "canon": False, "stat_effects": {"loyalty": -10}}
                    ],
                    "next_scenes": ["ch02_s02"]
                },
                {
                    "id": "ch02_s02", "chapter": 2, "scene_index": 2,
                    "title": "凯瑟琳的幽灵",
                    "characters_present": ["heathcliff", "catherine"],
                    "location": "呼啸山庄·凯瑟琳旧房间",
                    "summary": "洛克伍德在梦中听到凯瑟琳的幽灵在窗外哭喊'让我进去'。希斯克利夫冲进房间，对着空无一人的窗口痛哭呼唤凯瑟琳。",
                    "plot_type": "conflict",
                    "challenge_potential": 5,
                    "choices": [
                        {"description": "推开来客，扑向窗口哭喊'凯西，回来！'", "canon": True, "stat_effects": {"loyalty": 15, "reputation": -10, "wisdom": -5}},
                        {"description": "强忍悲痛，假装只是被噩梦吵醒", "canon": False, "stat_effects": {"wisdom": 15, "reputation": 5}},
                        {"description": "独自留在房间，整夜对着窗外低语", "canon": False, "stat_effects": {"loyalty": 20, "combat": -5}}
                    ],
                    "next_scenes": ["ch03_s01"]
                },
                # === 第3章 ===
                {
                    "id": "ch03_s01", "chapter": 3, "scene_index": 1,
                    "title": "耐莉开始讲述",
                    "characters_present": ["nelly"],
                    "location": "画眉田庄",
                    "summary": "洛克伍德回到画眉田庄，请求管家耐莉讲述呼啸山庄的故事。",
                    "plot_type": "origin",
                    "challenge_potential": 2,
                    "choices": [
                        {"description": "从头讲起，不遗漏任何细节", "canon": True, "stat_effects": {"wisdom": 10}},
                        {"description": "只讲希斯克利夫的部分，回避自己的过错", "canon": False, "stat_effects": {"wisdom": -5, "reputation": 5}},
                        {"description": "犹豫是否该揭开旧伤疤", "canon": False, "stat_effects": {"wisdom": 5, "loyalty": 10}}
                    ],
                    "next_scenes": ["ch03_s02"]
                },
                {
                    "id": "ch03_s02", "chapter": 3, "scene_index": 2,
                    "title": "记忆的起点",
                    "characters_present": ["nelly"],
                    "location": "画眉田庄",
                    "summary": "耐莉回忆起三十年前的呼啸山庄，恩肖一家的旧日时光。",
                    "plot_type": "origin",
                    "challenge_potential": 2,
                    "choices": [
                        {"description": "如实叙述，包括自己对希斯克利夫最初的厌恶", "canon": True, "stat_effects": {"wisdom": 10, "loyalty": 5}},
                        {"description": "美化记忆，把自己塑造得更善良", "canon": False, "stat_effects": {"reputation": 10, "wisdom": -10}},
                        {"description": "坦承自己也是悲剧的一部分", "canon": False, "stat_effects": {"wisdom": 15, "loyalty": 10}}
                    ],
                    "next_scenes": ["ch04_s01"]
                },
                # === 第4章 ===
                {
                    "id": "ch04_s01", "chapter": 4, "scene_index": 1,
                    "title": "利物浦的弃儿",
                    "characters_present": ["heathcliff", "catherine"],
                    "location": "呼啸山庄",
                    "summary": "恩肖先生从利物浦带回一个脏兮兮的黑发男孩——希斯克利夫。辛德雷和凯瑟琳的态度截然不同。",
                    "plot_type": "origin",
                    "challenge_potential": 4,
                    "choices": [
                        {"description": "沉默承受所有人的敌意，只记住凯瑟琳的善意", "canon": True, "stat_effects": {"loyalty": 15, "wisdom": 5}},
                        {"description": "以牙还牙，对辛德雷的欺负奋起反抗", "canon": False, "stat_effects": {"combat": 15, "reputation": 5, "wisdom": -5}},
                        {"description": "讨好所有人，试图融入这个家", "canon": False, "stat_effects": {"reputation": 10, "loyalty": -5}}
                    ],
                    "next_scenes": ["ch04_s02"]
                },
                {
                    "id": "ch04_s02", "chapter": 4, "scene_index": 2,
                    "title": "荒原上的野孩子",
                    "characters_present": ["heathcliff", "catherine"],
                    "location": "约克郡荒原",
                    "summary": "希斯克利夫与凯瑟琳在荒原上奔跑嬉戏，两个不羁的灵魂在风中结盟。",
                    "plot_type": "origin",
                    "challenge_potential": 3,
                    "choices": [
                        {"description": "与凯瑟琳并肩在荒原上奔跑，忘记一切痛苦", "canon": True, "stat_effects": {"loyalty": 20, "combat": 5}},
                        {"description": "带凯瑟琳去探索从未去过的荒原深处", "canon": False, "stat_effects": {"combat": 10, "wisdom": 10}},
                        {"description": "向凯瑟琳倾诉自己的身世之谜", "canon": False, "stat_effects": {"loyalty": 15, "wisdom": 5}}
                    ],
                    "next_scenes": ["ch04_s03"]
                },
                {
                    "id": "ch04_s03", "chapter": 4, "scene_index": 3,
                    "title": "辛德雷的毒打",
                    "characters_present": ["heathcliff"],
                    "location": "呼啸山庄",
                    "summary": "辛德雷趁父亲不在殴打希斯克利夫，希斯克利夫用恩肖先生的偏爱作为武器威胁辛德雷。",
                    "plot_type": "conflict",
                    "challenge_potential": 4,
                    "choices": [
                        {"description": "用恩肖先生的偏爱要挟辛德雷，换取他的马", "canon": True, "stat_effects": {"wisdom": 10, "combat": 5, "reputation": -5}},
                        {"description": "默默忍受，把仇恨埋在心底", "canon": False, "stat_effects": {"wisdom": 5, "loyalty": 5, "combat": -5}},
                        {"description": "正面还击，即使打不过也不低头", "canon": False, "stat_effects": {"combat": 15, "reputation": 10, "wisdom": -10}}
                    ],
                    "next_scenes": ["ch05_s01"]
                },
                # === 第5章 ===
                {
                    "id": "ch05_s01", "chapter": 5, "scene_index": 1,
                    "title": "恩肖先生之死",
                    "characters_present": ["heathcliff", "catherine"],
                    "location": "呼啸山庄",
                    "summary": "老恩肖在炉火旁安详去世，凯瑟琳和希斯克利夫在窗台上互相安慰。",
                    "plot_type": "conflict",
                    "challenge_potential": 4,
                    "choices": [
                        {"description": "与凯瑟琳相拥而泣，幻想天堂", "canon": True, "stat_effects": {"loyalty": 15, "wisdom": 5}},
                        {"description": "意识到失去保护者，开始为未来担忧", "canon": False, "stat_effects": {"wisdom": 20}},
                        {"description": "表面平静，内心已在准备面对辛德雷的统治", "canon": False, "stat_effects": {"wisdom": 15, "combat": 5}}
                    ],
                    "next_scenes": ["ch05_s02"]
                },
                {
                    "id": "ch05_s02", "chapter": 5, "scene_index": 2,
                    "title": "辛德雷的统治",
                    "characters_present": ["heathcliff"],
                    "location": "呼啸山庄",
                    "summary": "辛德雷继承庄园，将希斯克利夫贬为仆人，禁止他受教育，与凯瑟琳隔离。",
                    "plot_type": "conflict",
                    "challenge_potential": 5,
                    "choices": [
                        {"description": "忍辱负重，暗中与凯瑟琳保持联系", "canon": True, "stat_effects": {"loyalty": 15, "wisdom": 10}},
                        {"description": "公然反抗辛德雷的命令", "canon": False, "stat_effects": {"combat": 15, "reputation": 10, "wisdom": -10}},
                        {"description": "表面顺从，暗中计划离开这里", "canon": False, "stat_effects": {"wisdom": 20, "loyalty": -10}}
                    ],
                    "next_scenes": ["ch06_s01"]
                },
                # === 第6章 ===
                {
                    "id": "ch06_s01", "chapter": 6, "scene_index": 1,
                    "title": "偷窥画眉田庄",
                    "characters_present": ["heathcliff", "catherine"],
                    "location": "画眉田庄外",
                    "summary": "希斯克利夫和凯瑟琳偷偷跑到画眉田庄，透过窗户窥见林顿家的富裕优雅生活。",
                    "plot_type": "journey",
                    "challenge_potential": 4,
                    "choices": [
                        {"description": "嘲笑林顿兄妹的娇气，与凯瑟琳一起大笑", "canon": True, "stat_effects": {"loyalty": 10, "reputation": -5}},
                        {"description": "沉默地注视着那个自己永远无法拥有的世界", "canon": False, "stat_effects": {"wisdom": 15, "combat": 5}},
                        {"description": "拉凯瑟琳离开，这里不属于他们", "canon": False, "stat_effects": {"wisdom": 10, "loyalty": 10}}
                    ],
                    "next_scenes": ["ch06_s02"]
                },
                {
                    "id": "ch06_s02", "chapter": 6, "scene_index": 2,
                    "title": "凯瑟琳被留下",
                    "characters_present": ["heathcliff", "catherine"],
                    "location": "画眉田庄",
                    "summary": "凯瑟琳被狗咬伤，林顿家收留她养伤。希斯克利夫被赶走，独自回到黑暗中。",
                    "plot_type": "conflict",
                    "challenge_potential": 5,
                    "choices": [
                        {"description": "被赶走，独自在黑暗中等凯瑟琳回来", "canon": True, "stat_effects": {"loyalty": 20, "reputation": -5}},
                        {"description": "强行闯入要带凯瑟琳走", "canon": False, "stat_effects": {"combat": 15, "loyalty": 10, "wisdom": -10}},
                        {"description": "悄悄每天来窗外看她是否安好", "canon": False, "stat_effects": {"loyalty": 15, "wisdom": 5}}
                    ],
                    "next_scenes": ["ch06_s03"]
                },
                {
                    "id": "ch06_s03", "chapter": 6, "scene_index": 3,
                    "title": "五周的分离",
                    "characters_present": ["heathcliff"],
                    "location": "呼啸山庄",
                    "summary": "凯瑟琳在画眉田庄住了五周，希斯克利夫在呼啸山庄独自承受辛德雷的虐待。",
                    "plot_type": "conflict",
                    "challenge_potential": 3,
                    "choices": [
                        {"description": "默默等待，把痛苦化为对凯瑟琳的思念", "canon": True, "stat_effects": {"loyalty": 10, "wisdom": 5}},
                        {"description": "趁辛德雷酗酒时偷偷去画眉田庄看她", "canon": False, "stat_effects": {"loyalty": 15, "combat": 5, "wisdom": -5}},
                        {"description": "开始自学读书认字，不让自己被彻底碾碎", "canon": False, "stat_effects": {"wisdom": 20}}
                    ],
                    "next_scenes": ["ch07_s01"]
                },
                # === 第7章 ===
                {
                    "id": "ch07_s01", "chapter": 7, "scene_index": 1,
                    "title": "淑女归来",
                    "characters_present": ["heathcliff", "catherine"],
                    "location": "呼啸山庄",
                    "summary": "凯瑟琳归来已判若两人：穿着华丽、举止优雅。她看到希斯克利夫的邋遢模样，忍不住笑了。",
                    "plot_type": "conflict",
                    "challenge_potential": 5,
                    "choices": [
                        {"description": "羞愤交加，夺门而出", "canon": True, "stat_effects": {"combat": 5, "loyalty": -5, "reputation": -10}},
                        {"description": "强装无所谓，假装她的变化不影响自己", "canon": False, "stat_effects": {"wisdom": 10, "loyalty": 5}},
                        {"description": "质问她：你还是那个荒原上的凯瑟琳吗？", "canon": False, "stat_effects": {"loyalty": 10, "wisdom": 5, "reputation": -5}}
                    ],
                    "next_scenes": ["ch07_s02"]
                },
                {
                    "id": "ch07_s02", "chapter": 7, "scene_index": 2,
                    "title": "耐莉的安慰",
                    "characters_present": ["heathcliff", "nelly"],
                    "location": "呼啸山庄·厨房",
                    "summary": "耐莉给希斯克利夫洗脸梳头，安慰他'你其实很英俊'，鼓励他振作。",
                    "plot_type": "origin",
                    "challenge_potential": 3,
                    "choices": [
                        {"description": "让耐莉收拾自己，暗暗发誓要变强", "canon": True, "stat_effects": {"wisdom": 10, "reputation": 10}},
                        {"description": "拒绝同情，粗暴地推开耐莉", "canon": False, "stat_effects": {"combat": 10, "loyalty": -10}},
                        {"description": "向耐莉倾诉对凯瑟琳变化的痛苦", "canon": False, "stat_effects": {"wisdom": 5, "loyalty": 10}}
                    ],
                    "next_scenes": ["ch07_s03"]
                },
                {
                    "id": "ch07_s03", "chapter": 7, "scene_index": 3,
                    "title": "我要让辛德雷付出代价",
                    "characters_present": ["heathcliff"],
                    "location": "呼啸山庄",
                    "summary": "希斯克利夫对耐莉说出那句话：'我在想怎么报复辛德雷。我不在乎要等多久。'",
                    "plot_type": "conflict",
                    "challenge_potential": 5,
                    "choices": [
                        {"description": "冷静地说出复仇的誓言", "canon": True, "stat_effects": {"combat": 10, "wisdom": 10}},
                        {"description": "把仇恨咽回去，决定用行动证明自己", "canon": False, "stat_effects": {"wisdom": 20, "combat": -5}},
                        {"description": "不只是辛德雷——要让所有看不起自己的人付出代价", "canon": False, "stat_effects": {"combat": 15, "wisdom": -5, "reputation": -5}}
                    ],
                    "next_scenes": ["ch08_s01"]
                },
                # === 第8章 ===
                {
                    "id": "ch08_s01", "chapter": 8, "scene_index": 1,
                    "title": "圣诞宴会",
                    "characters_present": ["heathcliff", "catherine"],
                    "location": "呼啸山庄",
                    "summary": "林顿兄妹来呼啸山庄过圣诞，辛德雷命令希斯克利夫不准出现在客人面前。",
                    "plot_type": "conflict",
                    "challenge_potential": 5,
                    "choices": [
                        {"description": "试图挤进宴会却被辛德雷当众羞辱", "canon": True, "stat_effects": {"reputation": -10, "combat": 10}},
                        {"description": "躲在暗处观察，记住每一个羞辱自己的人", "canon": False, "stat_effects": {"wisdom": 15, "combat": 5}},
                        {"description": "根本不去，一个人在荒原上度过圣诞夜", "canon": False, "stat_effects": {"loyalty": -5, "wisdom": 10}}
                    ],
                    "next_scenes": ["ch08_s02"]
                },
                {
                    "id": "ch08_s02", "chapter": 8, "scene_index": 2,
                    "title": "泼在脸上的苹果酱",
                    "characters_present": ["heathcliff", "catherine"],
                    "location": "呼啸山庄",
                    "summary": "辛德雷将希斯克利夫赶出餐厅，希斯克利夫愤怒地把热苹果酱泼向埃德加·林顿。",
                    "plot_type": "battle",
                    "challenge_potential": 5,
                    "choices": [
                        {"description": "把苹果酱泼向埃德加，宣泄怒火", "canon": True, "stat_effects": {"combat": 10, "reputation": -15, "wisdom": -10}},
                        {"description": "忍住怒火，默默退出，把屈辱刻进骨头", "canon": False, "stat_effects": {"wisdom": 20, "combat": 5}},
                        {"description": "把怒气对准辛德雷而不是无辜的埃德加", "canon": False, "stat_effects": {"wisdom": 10, "combat": 10, "reputation": -5}}
                    ],
                    "next_scenes": ["ch08_s03"]
                },
                {
                    "id": "ch08_s03", "chapter": 8, "scene_index": 3,
                    "title": "阁楼上的对话",
                    "characters_present": ["heathcliff", "nelly"],
                    "location": "呼啸山庄·阁楼",
                    "summary": "被关在阁楼的希斯克利夫向耐莉诉说：'我要报复，我不在乎等多久。'复仇的种子彻底扎根。",
                    "plot_type": "resolution",
                    "challenge_potential": 4,
                    "choices": [
                        {"description": "让仇恨在心中生根：总有一天他们都会后悔", "canon": True, "stat_effects": {"combat": 15, "wisdom": 5}},
                        {"description": "决定离开这里，出去闯荡，靠自己的力量回来", "canon": False, "stat_effects": {"wisdom": 15, "reputation": 10}},
                        {"description": "伤心地想：只要凯瑟琳还在意我，其他都不重要", "canon": False, "stat_effects": {"loyalty": 20, "wisdom": -5}}
                    ],
                    "next_scenes": ["ch09_s01"]
                },
                # === 第9章 ===
                {
                    "id": "ch09_s01", "chapter": 9, "scene_index": 1,
                    "title": "凯瑟琳的告白",
                    "characters_present": ["catherine", "nelly", "heathcliff"],
                    "location": "呼啸山庄·厨房",
                    "summary": "凯瑟琳向耐莉倾诉：埃德加向她求婚了，她准备接受。'嫁给希斯克利夫会降低我的身份。'",
                    "plot_type": "conflict",
                    "challenge_potential": 5,
                    "choices": [
                        {"description": "（希斯克利夫）听到'降低身份'后愤然离去，不等听完", "canon": True, "stat_effects": {"loyalty": -15, "combat": 10, "wisdom": -10}},
                        {"description": "（希斯克利夫）忍痛听完全部——包括'我就是希斯克利夫'", "canon": False, "stat_effects": {"wisdom": 25, "loyalty": 10}},
                        {"description": "（希斯克利夫）当场现身质问凯瑟琳", "canon": False, "stat_effects": {"combat": 15, "loyalty": 5, "reputation": -10}}
                    ],
                    "next_scenes": ["ch09_s02"]
                },
                {
                    "id": "ch09_s02", "chapter": 9, "scene_index": 2,
                    "title": "'我就是希斯克利夫'",
                    "characters_present": ["catherine", "nelly"],
                    "location": "呼啸山庄·厨房",
                    "summary": "凯瑟琳说出经典独白：'耐莉，我就是希斯克利夫！他永远在我心里。'但希斯克利夫已经走了。",
                    "plot_type": "conflict",
                    "challenge_potential": 5,
                    "choices": [
                        {"description": "（凯瑟琳视角）说出心底的真话，却不知他已离去", "canon": True, "stat_effects": {"loyalty": 15, "wisdom": -5}},
                        {"description": "（凯瑟琳视角）意识到话说错了，冲出去找他", "canon": False, "stat_effects": {"loyalty": 20, "reputation": -10}},
                        {"description": "（凯瑟琳视角）告诉耐莉：帮我把两个世界都留住", "canon": False, "stat_effects": {"wisdom": 10, "loyalty": 5}}
                    ],
                    "next_scenes": ["ch09_s03"]
                },
                {
                    "id": "ch09_s03", "chapter": 9, "scene_index": 3,
                    "title": "暴风雨之夜的出走",
                    "characters_present": ["heathcliff"],
                    "location": "荒原",
                    "summary": "暴风雨之夜，希斯克利夫消失在荒原上。凯瑟琳在暴雨中疯狂寻找，淋病了一场。",
                    "plot_type": "resolution",
                    "challenge_potential": 5,
                    "choices": [
                        {"description": "消失在暴风雨中，带着破碎的心离开", "canon": True, "stat_effects": {"combat": 10, "wisdom": 5, "loyalty": -10}},
                        {"description": "在荒原上徘徊一夜，最终还是回去", "canon": False, "stat_effects": {"loyalty": 15, "wisdom": 10}},
                        {"description": "走之前在凯瑟琳窗下留下一个记号", "canon": False, "stat_effects": {"loyalty": 20, "wisdom": 5}}
                    ],
                    "next_scenes": ["ch10_s01"]
                },
                # === 第10章 ===
                {
                    "id": "ch10_s01", "chapter": 10, "scene_index": 1,
                    "title": "三年后的归来",
                    "characters_present": ["heathcliff", "catherine"],
                    "location": "画眉田庄",
                    "summary": "三年后，希斯克利夫突然出现在画眉田庄门口。衣着体面，举止从容，眼神却更加阴暗。",
                    "plot_type": "conflict",
                    "challenge_potential": 5,
                    "choices": [
                        {"description": "以全新姿态出现，让所有人震惊", "canon": True, "stat_effects": {"reputation": 20, "combat": 5}},
                        {"description": "先暗中观察凯瑟琳的生活，再决定是否现身", "canon": False, "stat_effects": {"wisdom": 20}},
                        {"description": "直接找凯瑟琳，不理会其他人", "canon": False, "stat_effects": {"loyalty": 15, "reputation": -5}}
                    ],
                    "next_scenes": ["ch10_s02"]
                },
                {
                    "id": "ch10_s02", "chapter": 10, "scene_index": 2,
                    "title": "重逢",
                    "characters_present": ["heathcliff", "catherine"],
                    "location": "画眉田庄",
                    "summary": "凯瑟琳见到希斯克利夫狂喜不已，不顾丈夫在场紧紧抓住他的手。埃德加震惊而不安。",
                    "plot_type": "conflict",
                    "challenge_potential": 5,
                    "choices": [
                        {"description": "压抑内心的激荡，以绅士姿态回应", "canon": True, "stat_effects": {"wisdom": 15, "reputation": 10}},
                        {"description": "不顾一切抱住凯瑟琳", "canon": False, "stat_effects": {"loyalty": 25, "reputation": -15, "wisdom": -10}},
                        {"description": "冷淡回应，让她感受自己三年的痛苦", "canon": False, "stat_effects": {"combat": 10, "wisdom": 5, "loyalty": -10}}
                    ],
                    "next_scenes": ["ch10_s03"]
                },
                {
                    "id": "ch10_s03", "chapter": 10, "scene_index": 3,
                    "title": "复仇的序幕",
                    "characters_present": ["heathcliff"],
                    "location": "呼啸山庄",
                    "summary": "希斯克利夫住进呼啸山庄，开始接近已经酗酒堕落的辛德雷，用赌博慢慢吞噬他的财产。复仇正式开始。",
                    "plot_type": "conflict",
                    "challenge_potential": 5,
                    "choices": [
                        {"description": "用赌博一步步掏空辛德雷，冷酷而有耐心", "canon": True, "stat_effects": {"wisdom": 15, "combat": 5, "reputation": -5}},
                        {"description": "直接与辛德雷摊牌：你欠我的该还了", "canon": False, "stat_effects": {"combat": 15, "reputation": 5, "wisdom": -5}},
                        {"description": "犹豫了——复仇真的能填满心中的空洞吗？", "canon": False, "stat_effects": {"wisdom": 20, "loyalty": 10, "combat": -10}}
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
