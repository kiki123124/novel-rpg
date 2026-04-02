#!/usr/bin/env python3
"""小说导入器 - 支持 PDF/TXT/EPUB/DOCX，提取文本→分章→分场景→生成元数据"""

import json
import os
import re
import sys
from collections import Counter
from datetime import datetime

DATA_DIR = os.path.expanduser("~/.openclaw/skills/novel-rpg/data")
BOOKS_DIR = os.path.join(DATA_DIR, "books")
INDEX_FILE = os.path.join(BOOKS_DIR, "_index.json")

# 支持的格式
SUPPORTED_FORMATS = {".pdf", ".txt", ".epub", ".docx"}

# 章节标题正则模式
CHAPTER_PATTERNS = [
    r'^第[一二三四五六七八九十百千零\d]+[回章节卷篇]',
    r'^Chapter\s+\d+',
    r'^CHAPTER\s+\d+',
    r'^\d+\.\s+\S',
    r'^Part\s+\d+',
    r'^PART\s+\d+',
    r'^卷[一二三四五六七八九十\d]+',
    r'^Prologue|^Epilogue',
    r'^序[章言]|^尾声|^楔子',
]

# ============================================================
# 多格式文本提取
# ============================================================

def extract_text_from_file(file_path):
    """根据文件扩展名自动选择提取方式，返回文本字符串"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_FORMATS:
        print(f"不支持的格式: {ext}")
        print(f"支持: {', '.join(sorted(SUPPORTED_FORMATS))}")
        sys.exit(1)

    extractors = {
        ".pdf": _extract_pdf,
        ".txt": _extract_txt,
        ".epub": _extract_epub,
        ".docx": _extract_docx,
    }
    return extractors[ext](file_path)


def _extract_pdf(path):
    try:
        import fitz
    except ImportError:
        print("需要安装 PyMuPDF: pip3 install PyMuPDF")
        sys.exit(1)
    doc = fitz.open(path)
    pages = [page.get_text() for page in doc if page.get_text().strip()]
    doc.close()
    print(f"  PDF: {len(pages)} 页")
    return '\n'.join(pages)


def _extract_txt(path):
    # 自动检测编码
    for enc in ['utf-8', 'gbk', 'gb18030', 'big5', 'latin-1']:
        try:
            with open(path, 'r', encoding=enc) as f:
                text = f.read()
            print(f"  TXT: 编码 {enc}, {len(text)} 字符")
            return text
        except (UnicodeDecodeError, UnicodeError):
            continue
    print("无法检测文件编码")
    sys.exit(1)


def _extract_epub(path):
    try:
        import zipfile
        from html.parser import HTMLParser
    except ImportError:
        print("EPUB解析需要标准库 zipfile + html.parser（已内置）")
        sys.exit(1)

    class HTMLTextExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.parts = []
            self._skip = False
        def handle_starttag(self, tag, attrs):
            if tag in ('script', 'style'):
                self._skip = True
            elif tag in ('p', 'div', 'br', 'h1', 'h2', 'h3', 'h4'):
                self.parts.append('\n')
        def handle_endtag(self, tag):
            if tag in ('script', 'style'):
                self._skip = False
        def handle_data(self, data):
            if not self._skip:
                self.parts.append(data)
        def get_text(self):
            return ''.join(self.parts)

    texts = []
    with zipfile.ZipFile(path, 'r') as zf:
        # 读取spine顺序
        content_opf = None
        for name in zf.namelist():
            if name.endswith('.opf'):
                content_opf = name
                break

        html_files = []
        if content_opf:
            # 从OPF解析阅读顺序
            opf_text = zf.read(content_opf).decode('utf-8', errors='replace')
            opf_dir = os.path.dirname(content_opf)
            # 提取manifest id→href映射
            manifest = {}
            for m in re.finditer(r'<item\s+[^>]*id="([^"]+)"[^>]*href="([^"]+)"', opf_text):
                manifest[m.group(1)] = m.group(2)
            # 提取spine顺序
            for m in re.finditer(r'<itemref\s+[^>]*idref="([^"]+)"', opf_text):
                href = manifest.get(m.group(1), "")
                if href:
                    full = os.path.join(opf_dir, href) if opf_dir else href
                    # 标准化路径
                    full = os.path.normpath(full)
                    html_files.append(full)

        if not html_files:
            # fallback: 按名称排序所有html/xhtml
            html_files = sorted([n for n in zf.namelist()
                                if n.endswith(('.html', '.xhtml', '.htm'))])

        for hf in html_files:
            try:
                raw = zf.read(hf).decode('utf-8', errors='replace')
                extractor = HTMLTextExtractor()
                extractor.feed(raw)
                t = extractor.get_text().strip()
                if t and len(t) > 50:
                    texts.append(t)
            except KeyError:
                continue

    full = '\n\n'.join(texts)
    print(f"  EPUB: {len(html_files)} 个文档, {len(full)} 字符")
    return full


def _extract_docx(path):
    try:
        import zipfile
        from xml.etree import ElementTree
    except ImportError:
        sys.exit(1)

    WORD_NS = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    paragraphs = []
    with zipfile.ZipFile(path, 'r') as zf:
        try:
            xml_content = zf.read('word/document.xml')
        except KeyError:
            print("无效的DOCX文件")
            sys.exit(1)
        tree = ElementTree.fromstring(xml_content)
        for para in tree.iter(f'{WORD_NS}p'):
            texts = [node.text for node in para.iter(f'{WORD_NS}t') if node.text]
            if texts:
                paragraphs.append(''.join(texts))

    full = '\n'.join(paragraphs)
    print(f"  DOCX: {len(paragraphs)} 段落, {len(full)} 字符")
    return full


# ============================================================
# 章节检测 & 场景切分（保持不变）
# ============================================================

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

        is_chapter = any(re.match(p, stripped) for p in CHAPTER_PATTERNS)

        if is_chapter and len(current_chapter["lines"]) > 5:
            chapters.append(current_chapter)
            current_chapter = {"title": stripped, "lines": []}
        else:
            current_chapter["lines"].append(line)

    if current_chapter["lines"]:
        chapters.append(current_chapter)

    # 如果只检测到1章（没识别到章节标题），按字数自动切分
    if len(chapters) <= 1 and len(full_text) > 5000:
        chapters = _auto_split_chapters(full_text)

    return chapters


def _auto_split_chapters(text, target_chars=3000):
    """无章节标记时按段落+字数自动切分"""
    paragraphs = re.split(r'\n\s*\n', text)
    chapters = []
    current = {"title": "第1章", "lines": []}
    current_len = 0
    ch_num = 1

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        current["lines"].append(para)
        current_len += len(para)
        if current_len >= target_chars:
            chapters.append(current)
            ch_num += 1
            current = {"title": f"第{ch_num}章", "lines": []}
            current_len = 0

    if current["lines"]:
        chapters.append(current)

    print(f"  未检测到章节标题，按字数自动分为 {len(chapters)} 章")
    return chapters


def split_scenes(chapter_text, max_tokens=800):
    """将章节分割为场景块"""
    paragraphs = re.split(r'\n\s*\n|\n---\n|\n\*\*\*\n', chapter_text)
    scenes = []
    current = []
    current_len = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        has_cjk = any('\u4e00' <= c <= '\u9fff' for c in para[:20])
        est_tokens = int(len(para) * 1.5) if has_cjk else len(para.split())
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


# ============================================================
# 角色提取（大幅改进）
# ============================================================

# 中文动作/对话动词
ZH_SPEECH_VERBS = (
    '说|道|笑道|怒道|叫道|问道|答道|喊道|叹道|哭道|骂道|'
    '大喊|低声|呵斥|命令|吩咐|央求|恳求|冷笑|微笑|大笑|'
    '回答|反驳|提议|补充|解释|感叹|质问|追问|嘟囔|嘀咕|'
    '思忖|暗想|心想|自语|念道|吟道|唱道|续道'
)
ZH_ACTION_VERBS = (
    '走|跑|站|坐|看|听|拿|放|打|踢|跳|飞|骑|拉|推|抱|'
    '举|挥|舞|转身|回头|抬头|低头|点头|摇头|皱眉|叹息'
)

# 英文常见非人名词汇（扩展过滤列表）
EN_STOP_NAMES = {
    'The', 'This', 'That', 'But', 'And', 'Chapter', 'Part', 'Book',
    'Then', 'There', 'Here', 'What', 'When', 'Where', 'Who', 'How',
    'Why', 'With', 'From', 'Into', 'Upon', 'About', 'After', 'Before',
    'Between', 'Through', 'During', 'Without', 'Against', 'Along',
    'January', 'February', 'March', 'April', 'May', 'June', 'July',
    'August', 'September', 'October', 'November', 'December',
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
    'North', 'South', 'East', 'West', 'Street', 'Road', 'House', 'Room',
    'Lord', 'Lady', 'Sir', 'Madam', 'King', 'Queen', 'Prince', 'Princess',
    'However', 'Perhaps', 'Indeed', 'Meanwhile', 'Nevertheless', 'Furthermore',
    'Chapter', 'Volume', 'Section', 'Prologue', 'Epilogue',
    'God', 'Heaven', 'Earth', 'English', 'French', 'German', 'London', 'Paris',
}


def extract_character_candidates(text):
    """改进的角色提取：多策略投票"""
    candidates = Counter()

    _extract_zh_characters(text, candidates)
    _extract_en_characters(text, candidates)
    _boost_by_dialogue(text, candidates)
    _boost_by_cooccurrence(text, candidates)

    # 过滤低频（至少出现3次）+ 排序
    result = [(name, score) for name, score in candidates.most_common(30) if score >= 3]

    # 去重：如果"孙悟空"和"悟空"都在，合并到长名
    final = []
    seen = set()
    for name, score in result:
        is_substring = False
        for other_name, _ in result:
            if name != other_name and name in other_name and len(other_name) - len(name) <= 2:
                is_substring = True
                break
        if not is_substring and name not in seen:
            final.append(name)
            seen.add(name)

    return final[:15]


def _extract_zh_characters(text, candidates):
    """中文角色提取：对话+动作+称谓模式"""
    # 对话模式：名字2-4字 + 紧跟说话动词
    # 用肯定前瞻确保动词完整匹配（不被名字吃掉）
    for verb in ZH_SPEECH_VERBS.split('|'):
        if not verb:
            continue
        pat = rf'([\u4e00-\u9fff]{{2,4}}){re.escape(verb)}'
        for m in re.finditer(pat, text):
            name = m.group(1)
            # 确保名字最后一个字不是动词的一部分：名字不应以常见动词字结尾
            if name[-1] not in '说道笑怒叫问答喊叹哭骂大低呵命吩央恳冷微回反提补解感质追嘟嘀思暗心自念吟唱续':
                candidates[name] += 3

    # 动作模式（权重较低）
    for verb in ZH_ACTION_VERBS.split('|'):
        if not verb:
            continue
        pat = rf'([\u4e00-\u9fff]{{2,4}}){re.escape(verb)}(?:[了着过]|[，。])'
        for m in re.finditer(pat, text):
            name = m.group(1)
            if name[-1] not in '走跑站坐看听拿放打踢跳飞骑拉推抱举挥舞转回抬低点摇皱叹':
                candidates[name] += 1

    # 称谓模式：XX先生/小姐/大人/师父/...
    for m in re.finditer(r'([\u4e00-\u9fff]{1,4})(先生|小姐|夫人|大人|师父|师兄|公子|姑娘|老爷|太太)', text):
        full_name = m.group(1) + m.group(2)
        candidates[m.group(1)] += 2
        candidates[full_name] += 1

    # 引号对话前的名字：XXX："..."  或 XXX：「...」
    # 名字前必须是行首、标点或空白，避免截取词尾
    for m in re.finditer(r'(?:^|[。！？\s，；])[\s]*([\u4e00-\u9fff]{2,4})[：:][\s]*["「『]', text, re.MULTILINE):
        candidates[m.group(1)] += 3

    # 过滤明显非人名的词
    zh_stop = {'但是', '因为', '所以', '如果', '这个', '那个', '什么', '怎么', '为什么',
               '已经', '可以', '不是', '就是', '只是', '还是', '或者', '虽然', '然而',
               '忽然', '突然', '果然', '居然', '竟然', '原来', '只见', '却说', '一个',
               '于是', '不过', '之后', '以后', '大家', '众人', '有人', '此时', '那时'}
    for word in list(candidates.keys()):
        # 在停用词中
        if word in zh_stop:
            del candidates[word]
            continue
        # 名字中包含动词字的组合（如"唐僧叹道"、"悟空笑道"、"悟净也不"）
        # 超过2字的名字，末尾2字如果像动词短语就删掉
        if len(word) > 2:
            tail2 = word[-2:]
            verb_tails = {'笑道', '叹道', '怒道', '问道', '答道', '嘟囔', '也不', '大喊',
                          '冷笑', '点头', '回头', '不说', '小心', '笑着', '哭着'}
            if tail2 in verb_tails:
                del candidates[word]
                continue
        # 3-4字名字，最后一个字是常见动词/副词
        if len(word) >= 3 and word[-1] in '道说的了也不着过来去':
            del candidates[word]
            continue
        # 名字开头不应是介词/助词/量词
        if word[0] in '的了过着在从到对把被给让向往用以为':
            del candidates[word]


def _extract_en_characters(text, candidates):
    """英文角色提取：专有名词+对话标记"""
    # "Name said/asked/replied/..."
    en_speech = r'(?:said|asked|replied|answered|cried|whispered|shouted|exclaimed|murmured|muttered|called|spoke|told|demanded)'
    for m in re.finditer(rf'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+{en_speech}', text):
        name = m.group(1)
        if name not in EN_STOP_NAMES:
            candidates[name] += 3

    # ... said Name
    for m in re.finditer(rf'{en_speech}\s+([A-Z][a-z]+)', text):
        name = m.group(1)
        if name not in EN_STOP_NAMES:
            candidates[name] += 3

    # Mr./Mrs./Miss/Dr. Name
    for m in re.finditer(r'(?:Mr|Mrs|Miss|Ms|Dr|Professor|Captain|Colonel)\.\s*([A-Z][a-z]+)', text):
        candidates[m.group(1)] += 2

    # 反复出现的大写名字（句首除外，通过检查前面不是句号来判断）
    for m in re.finditer(r'(?<![.!?]\s)([A-Z][a-z]{2,})', text):
        name = m.group(1)
        if name not in EN_STOP_NAMES and len(name) > 2:
            candidates[name] += 0.5


def _boost_by_dialogue(text, candidates):
    """对话密度加分：被引号包裹的内容前后的名字"""
    # 中文引号：名字前需要是行首/标点/空白
    for m in re.finditer(r'(?:^|[。！？\s，；])([\u4e00-\u9fff]{2,4})[，,]?\s*["「『]([^"」』]{5,100})["」』]', text, re.MULTILINE):
        candidates[m.group(1)] += 2
    # 英文引号
    for m in re.finditer(r'([A-Z][a-z]+)\s*[,]?\s*"[^"]{5,200}"', text):
        if m.group(1) not in EN_STOP_NAMES:
            candidates[m.group(1)] += 2


def _boost_by_cooccurrence(text, candidates):
    """共现关系加分：经常一起出现的名字更可能是角色"""
    top_names = [name for name, _ in candidates.most_common(20)]
    if len(top_names) < 2:
        return
    # 按段落检查共现
    paragraphs = text.split('\n')
    for para in paragraphs:
        names_in_para = [n for n in top_names if n in para]
        if len(names_in_para) >= 2:
            for n in names_in_para:
                candidates[n] += 1


# ============================================================
# 导入主函数
# ============================================================

def import_book(file_path, book_id, title, author="未知"):
    """导入任意格式小说并生成数据骨架"""
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        sys.exit(1)

    ext = os.path.splitext(file_path)[1].lower()
    print(f"正在导入: {file_path} ({ext})")

    # 1. 提取文本
    full_text = extract_text_from_file(file_path)
    print(f"  共 {len(full_text)} 字符")

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

        for i in range(len(scene_ids) - 1):
            all_scenes[-len(scene_ids) + i]["next_scenes"] = [scene_ids[i + 1]]

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

    # 5. 提取角色
    char_candidates = extract_character_candidates(full_text)
    print(f"  候选角色 ({len(char_candidates)}): {', '.join(char_candidates[:10])}")

    # 6. 写入元数据
    meta = {
        "id": book_id,
        "title": title,
        "author": author,
        "source_format": ext,
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
                "id": re.sub(r'[\s\W]+', '_', name.lower()).strip('_'),
                "name": name,
                "aliases": [],
                "personality": "待补充",
                "abilities": [],
                "relationships": {},
                "initial_stats": {"wisdom": 50, "combat": 50, "loyalty": 50, "reputation": 50},
                "arc_summary": "待补充",
                "first_appearance_chapter": 1,
                "playable": i < 5,
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
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            index = json.load(f)
    else:
        index = {"books": []}

    index["books"] = [b for b in index["books"] if b["id"] != book_id]
    index["books"].append({
        "id": book_id,
        "title": title,
        "author": author,
        "type": "imported",
        "source_format": ext,
        "status": "skeleton",
        "character_count": len(char_candidates[:10]),
        "chapter_count": len(chapters),
    })
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"\n导入完成！")
    print(f"  数据: {book_dir}")
    print(f"  状态: skeleton")
    print(f"  下一步: 运行 enrich {book_id} 让AI自动补充选择点")


# ============================================================
# Enrich 系统
# ============================================================

def enrich(book_id, scene_id=None):
    """输出待丰富的场景数据，供AI补充choices和角色信息"""
    book_dir = os.path.join(BOOKS_DIR, book_id)
    if not os.path.exists(book_dir):
        print(f"书籍 {book_id} 不存在")
        sys.exit(1)

    plot_path = os.path.join(book_dir, "plot_graph.json")
    chars_path = os.path.join(book_dir, "characters.json")
    if not os.path.exists(plot_path):
        print(f"场景数据不存在")
        sys.exit(1)

    with open(plot_path, "r", encoding="utf-8") as f:
        plot = json.load(f)
    with open(chars_path, "r", encoding="utf-8") as f:
        chars = json.load(f)

    scenes = plot.get("scenes", [])

    if scene_id:
        targets = [s for s in scenes if s["id"] == scene_id]
    else:
        targets = [s for s in scenes if not s.get("choices")]

    if not targets:
        print("所有场景已有选择点，无需丰富。")
        return

    chunks_dir = os.path.join(book_dir, "chunks")
    output = []
    for s in targets[:10]:
        chunk_path = os.path.join(chunks_dir, f"{s['id']}.txt")
        chunk_text = ""
        if os.path.exists(chunk_path):
            with open(chunk_path, "r", encoding="utf-8") as f:
                chunk_text = f.read()[:500]

        output.append({
            "scene_id": s["id"],
            "title": s["title"],
            "summary": s["summary"],
            "original_text_preview": chunk_text,
            "characters_present": s.get("characters_present", []),
            "needs": ["choices", "characters_present", "location", "plot_type"],
        })

    char_names = [c["name"] for c in chars.get("characters", [])]
    char_ids = [c["id"] for c in chars.get("characters", [])]
    unenriched_chars = [c for c in chars.get("characters", []) if c.get("personality") == "待补充"]

    result = {
        "book_id": book_id,
        "total_scenes": len(scenes),
        "scenes_without_choices": len([s for s in scenes if not s.get("choices")]),
        "available_characters": char_names,
        "character_ids": char_ids,
        "unenriched_characters": len(unenriched_chars),
        "scenes_to_enrich": output,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def apply_enrich(book_id, source):
    """将丰富数据写回场景图。source 可以是文件路径或 '-'（从stdin读取）"""
    book_dir = os.path.join(BOOKS_DIR, book_id)
    plot_path = os.path.join(book_dir, "plot_graph.json")

    if not os.path.exists(plot_path):
        print(f"场景数据不存在")
        sys.exit(1)

    with open(plot_path, "r", encoding="utf-8") as f:
        plot = json.load(f)

    if source == '-':
        enrichments = json.load(sys.stdin)
    else:
        with open(source, "r", encoding="utf-8") as f:
            enrichments = json.load(f)

    # 支持两种格式：直接数组 或 {"scenes": [...]}
    if isinstance(enrichments, dict):
        enrichments = enrichments.get("scenes", enrichments.get("scenes_to_enrich", []))

    scenes_map = {s["id"]: s for s in plot.get("scenes", [])}
    updated = 0

    for item in enrichments:
        sid = item.get("scene_id")
        if sid not in scenes_map:
            continue
        scene = scenes_map[sid]
        for key in ("choices", "characters_present", "location", "plot_type"):
            if key in item:
                scene[key] = item[key]
        updated += 1

    plot["scenes"] = list(scenes_map.values())
    with open(plot_path, "w", encoding="utf-8") as f:
        json.dump(plot, f, ensure_ascii=False, indent=2)

    # 同时更新角色数据（如果提供）
    chars_path = os.path.join(book_dir, "characters.json")
    if any("character_updates" in item for item in enrichments if isinstance(item, dict)):
        pass  # 未来扩展

    print(f"已更新 {updated} 个场景")

    # 更新索引状态
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            index = json.load(f)
        for b in index["books"]:
            if b["id"] == book_id:
                total = len(plot.get("scenes", []))
                with_choices = sum(1 for s in plot.get("scenes", []) if s.get("choices"))
                b["status"] = "ready" if with_choices >= total * 0.5 else "skeleton"
                break
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        print(f"状态: {'ready' if with_choices >= total * 0.5 else 'skeleton'} ({with_choices}/{total} 场景有选择点)")


def enrich_characters(book_id, source):
    """更新角色信息。source 可以是文件路径或 '-'（从stdin）"""
    book_dir = os.path.join(BOOKS_DIR, book_id)
    chars_path = os.path.join(book_dir, "characters.json")

    if not os.path.exists(chars_path):
        print(f"角色数据不存在")
        sys.exit(1)

    with open(chars_path, "r", encoding="utf-8") as f:
        chars = json.load(f)

    if source == '-':
        updates = json.load(sys.stdin)
    else:
        with open(source, "r", encoding="utf-8") as f:
            updates = json.load(f)

    if isinstance(updates, dict):
        updates = updates.get("characters", [updates])

    chars_map = {c["id"]: c for c in chars.get("characters", [])}
    updated = 0
    for item in updates:
        cid = item.get("id")
        if cid not in chars_map:
            continue
        for key in ("personality", "abilities", "relationships", "arc_summary", "aliases", "initial_stats"):
            if key in item and item[key]:
                chars_map[cid][key] = item[key]
        updated += 1

    chars["characters"] = list(chars_map.values())
    with open(chars_path, "w", encoding="utf-8") as f:
        json.dump(chars, f, ensure_ascii=False, indent=2)

    enriched = sum(1 for c in chars["characters"] if c.get("personality") != "待补充")
    print(f"已更新 {updated} 个角色 ({enriched}/{len(chars['characters'])} 已丰富)")


def status(book_id):
    """检查书籍导入状态"""
    book_dir = os.path.join(BOOKS_DIR, book_id)
    if not os.path.exists(book_dir):
        print(f"书籍 {book_id} 不存在")
        sys.exit(1)

    meta_path = os.path.join(book_dir, "meta.json")
    meta = None
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
    fmt = meta.get("source_format", "unknown") if meta else "unknown"
    print(f"书籍: {title} ({fmt})")
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
    print(f"可玩: {'是' if completeness >= 50 else '否（需要 enrich）'}")


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: pdf_import.py <command> [args]")
        print("命令:")
        print(f'  import "<file-path>" --book-id <id> --title "<title>" [--author "<author>"]')
        print(f"  支持格式: {', '.join(sorted(SUPPORTED_FORMATS))}")
        print("  enrich <book-id> [scene-id]                输出待丰富数据")
        print("  apply-enrich <book-id> <json-path|->        写回场景数据（-=stdin）")
        print("  enrich-chars <book-id> <json-path|->        写回角色数据（-=stdin）")
        print("  status <book-id>                            检查状态")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "import":
        args = sys.argv[2:]
        file_path = args[0] if args else ""
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

        if not file_path or not book_id or not title:
            print(f'用法: pdf_import.py import "<file-path>" --book-id <id> --title "<title>"')
            sys.exit(1)

        import_book(file_path, book_id, title, author)

    elif cmd == "enrich":
        if len(sys.argv) < 3:
            print("用法: pdf_import.py enrich <book-id> [scene-id]")
            sys.exit(1)
        sid = sys.argv[3] if len(sys.argv) > 3 else None
        enrich(sys.argv[2], sid)

    elif cmd == "apply-enrich":
        if len(sys.argv) < 4:
            print("用法: pdf_import.py apply-enrich <book-id> <json-path|->")
            sys.exit(1)
        apply_enrich(sys.argv[2], sys.argv[3])

    elif cmd == "enrich-chars":
        if len(sys.argv) < 4:
            print("用法: pdf_import.py enrich-chars <book-id> <json-path|->")
            sys.exit(1)
        enrich_characters(sys.argv[2], sys.argv[3])

    elif cmd == "status":
        if len(sys.argv) < 3:
            print("用法: pdf_import.py status <book-id>")
            sys.exit(1)
        status(sys.argv[2])
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)
