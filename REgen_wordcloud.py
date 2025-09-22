# 全都是 GPT-5 写的
# -*- coding: utf-8 -*-
"""
根据当前目录下的 .md 标题（文件名 + 文内第一个#标题），
统计算法类别关键词频次（空格不敏感/英文大小写不敏感），
生成 PNG 词云： ./images/00.png

依赖：pip install wordcloud pillow
"""

import sys
sys.dont_write_bytecode = True

import os
import re
from collections import Counter

try:
    from wordcloud import WordCloud
except ImportError:
    raise SystemExit("缺少依赖：wordcloud\n请先安装：pip install wordcloud pillow")

OUTPUT_DIR = "./images"
TITLE_PNG = os.path.join(OUTPUT_DIR, "00.png")

"""
根据当前目录下的 .md 标题（文件名 + 文内第一个#标题），
统计算法类别关键词频次（空格不敏感/英文大小写不敏感），
生成 PNG 词云： ./images/00.png

依赖：pip install wordcloud pillow
"""

import sys
sys.dont_write_bytecode = True

import os
import re
from collections import Counter

try:
    from wordcloud import WordCloud
except ImportError:
    raise SystemExit("缺少依赖：wordcloud\n请先安装：pip install wordcloud pillow")

OUTPUT_DIR = "./images"
TITLE_PNG = os.path.join(OUTPUT_DIR, "00.png")

# ================ 关键词分类（可自行扩展/修改） ================
KW_MAP = {
    # —— 搜索 / 图 —— 
    "BFS": ["bfs", "广度优先", "广搜", "层序遍历"],
    "DFS": ["dfs", "深度优先", "深搜", "先序遍历", "后序遍历", "中序遍历"],
    "双向BFS": ["双向bfs", "双端bfs", "bidirectional bfs"],
    "拓扑排序": ["拓扑排序", "kahn", "kahn算法", "kahn 算法", "入度", "有向无环"],
    "最短路/Dijkstra": ["最短路", "最短路径", "dijkstra", "dijsktra"],
    "最短路/其他": ["bellman-ford", "spfa", "floyd", "floyd-warshall"],
    "最小生成树": ["最小生成树", "kruskal", "prim"],
    "二分图/匹配/流": ["二分图", "最大匹配", "匈牙利", "hopcroft-karp", "网络流", "dinic", "最大流", "最小割"],
    "图论": ["图论", "强连通", "scc", "tarjan"],

    # —— 数据结构 —— 
    "单调栈": ["单调栈", "NGE", "PGE", "next greater", "previous smaller"],
    "单调队列": ["单调队列", "滑动窗口最大值", "mono queue"],
    "堆/优先队列": ["堆", "优先队列", "小根堆", "大根堆", "heap", "priority queue"],
    "并查集": ["并查集", "union find", "dsu", "带权并查集", "种类并查集"],
    "树状数组/BIT": ["树状数组", "fenwick", "bit", "binary indexed tree", "lowbit"],
    "线段树": ["线段树", "segment tree"],
    "可持久化": ["可持久化", "主席树", "persistent segment tree"],
    "分块/莫队": ["分块", "块状", "莫队", "mo's algorithm", "离线查询"],
    "RMQ/倍增": ["rmq", "稀疏表", "sparse table", "倍增", "binary lifting", "跳表?"],
    "LCA": ["lca", "最近公共祖先", "binary lifting", "倍增lca"],
    "树上算法": ["树上差分", "树上路径", "树链剖分", "重链剖分", "hld"],

    # —— 动态规划 —— 
    "动态规划": ["dp", "动态规划", "记忆化", "滚动数组", "一维dp", "二维动态规划"],
    "区间DP": ["区间dp", "区间 dp"],
    "数位DP": ["数位dp", "数位 dp"],
    "树形DP": ["树形dp", "树型dp", "树 形 dp", "树 型 dp"],
    "状压DP": ["状压", "状态压缩", "bitmask", "subset dp", "子集dp"],
    "背包DP": ["背包", "0-1背包", "完全背包", "多重背包", "分组背包"],
    "概率/期望DP": ["期望", "概率dp", "概率 动态规划"],

    # —— 字符串 —— 
    "Trie/字典树": ["trie", "字典树", "前缀树"],
    "KMP": ["kmp", "前缀函数", "失配函数"],
    "Z-Algorithm": ["z 函数", "z-algorithm", "扩展kmp"],
    "字符串哈希": ["字符串哈希", "rolling hash", "字符串 hash"],
    "AC自动机": ["ac 自动机", "aho-corasick", "多模式匹配"],
    "后缀数组/自动机": ["后缀数组", "sa", "后缀自动机", "sam", "suffix automaton"],
    "Manacher": ["manacher", "马拉车"],

    # —— 数学/数论/构造 —— 
    "数论/筛": ["数论", "质数", "筛质数", "埃氏筛", "线性筛", "欧拉筛"],
    "位运算": ["位运算", "bitwise", "异或", "xor", "lowbit", "移位"],
    "组合数学": ["组合数", "排列数", "卡特兰", "lucas", "逆元"],
    "博弈论": ["博弈", "sg", "nim", "必败态", "mex"],
    "构造/思维": ["构造", "脑洞", "构造题", "思维题", "技巧题"],
    "Meet-in-the-middle": ["meet-in-the-middle", "中途相遇", "折半搜索"],
    "计算几何": ["计算几何", "凸包", "graham", "andrew", "旋转卡壳", "叉积", "点线面", "半平面交"],

    # —— 数组/二分/指针/窗口 —— 
    "双指针": ["双指针", "快慢指针", "相向双指针", "逆向双指针", "三指针"],
    "滑动窗口": ["滑动窗口", "窗口", "固定窗口", "可变窗口"],
    "二分查找": ["二分", "二分查找", "值域二分", "二分答案", "三分法"],
    "前缀和/差分": ["前缀和", "差分", "前后缀", "差分数组"],

    # —— 排序/Top-K —— 
    "快速选择/Top-K": ["快速选择", "快选", "quickselect", "top-k", "topk"],
    "经典排序": ["快速排序", "归并排序", "堆排序", "桶排序", "计数排序", "三向切分"],

    # —— 回溯/枚举 —— 
    "回溯": ["回溯", "回溯算法", "搜索", "n 皇后", "全排列", "组合", "子集"],
    "枚举/暴力": ["枚举", "暴力", "穷举", "全搜"],

    # —— 贪心/栈队列 —— 
    "贪心": ["贪心", "贪心算法"],
    "栈/括号": ["栈", "括号", "下推自动机", "表达式求值"],

    # —— 「模拟」与「状态机」 —— 
    "模拟": ["模拟", "implementation", "simulation", "按题意模拟", "细节实现"],
    "状态机/FSM": ["状态机", "有限状态机", "fsm", "dfa", "nfa", "状态转移", "自动机模型"],

    # —— 其他常见专项 —— 
    "Kadane/最大子数组": ["kadane", "最大子数组和"],
    "回文相关": ["回文", "最长回文", "回文子串", "回文子序列"],
    "洗牌/随机化": ["洗牌", "knuth-shuffle", "shuffle", "rand"],
    "数据结构设计": ["设计", "lru", "lfu", "缓存", "设计哈希映射"],
    "扫描线/区间": ["扫描线", "区间合并", "差分约束", "线段树分治", "cdq 分治"],
}

# ================ 字体（可选） ================
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    r"/System/Library/Fonts/PingFang.ttc",
    r"/System/Library/Fonts/STHeiti Medium.ttc",
    r"/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]

def pick_font():
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            return p
    return None

# ================ 工具函数 ================
def list_markdown_files():
    return [f for f in os.listdir(".") if os.path.isfile(f) and f.lower().endswith(".md")]

def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def first_md_header(text: str) -> str:
    for line in text.splitlines():
        if line.strip().startswith("#"):
            return re.sub(r"^#+\s*", "", line.strip())
    return ""

def normalize_for_match(s: str) -> str:
    s2 = s.lower()

    def to_halfwidth(u):
        code = ord(u)
        if 0xFF01 <= code <= 0xFF5E:
            return chr(code - 0xFEE0)
        if code == 0x3000:
            return " "
        return u

    s2 = "".join(to_halfwidth(ch) for ch in s2)
    s2 = re.sub(r"\s+", "", s2)
    return s2

def normalize_kw(v: str) -> str:
    return re.sub(r"\s+", "", v.lower())

def build_variant_index():
    idx = {}
    for canon, vars_ in KW_MAP.items():
        idx[canon] = [normalize_kw(v) for v in vars_ if v.strip()]
    return idx

# --------------- 原有汇总函数（保留，不再在 main 中使用） ---------------
def collect_titles_text():
    chunks = []
    for f in list_markdown_files():
        chunks.append(os.path.splitext(os.path.basename(f))[0])
        h1 = first_md_header(read_file(f))
        if h1:
            chunks.append(h1)
    return "\n".join(chunks)

def count_by_categories(text: str) -> Counter:
    normalized_text = normalize_for_match(text)
    idx = build_variant_index()

    freq = Counter()
    for canon, variants in idx.items():
        total = 0
        for v in variants:
            if not v:
                continue
            total += normalized_text.count(v)
        if total > 0:
            freq[canon] = total
    return freq

# --------------- 新增：按文件去重统计（同一文件同一分类最多+1） ---------------
def iterate_file_title_texts():
    """逐文件返回“文件名 + 第一条H1”的归一化文本"""
    for f in list_markdown_files():
        name = os.path.splitext(os.path.basename(f))[0]
        # h1 = first_md_header(read_file(f)) or ""
        # yield normalize_for_match(name + "\n" + h1)
        yield normalize_for_match(name)

def count_by_categories_one_per_file() -> Counter:
    """
    对每个文件：若某类别任一变体命中，则该类别计数 +1（同一文件最多一次）。
    """
    idx = build_variant_index()
    freq = Counter()
    for norm in iterate_file_title_texts():
        matched = set()
        for canon, variants in idx.items():
            if any(v and v in norm for v in variants):
                matched.add(canon)
        for canon in matched:
            freq[canon] += 1
    return freq

# ================ 生成词云（PNG） ================
def make_wordcloud_png(counter: Counter, save_path: str, title_hint: str = None):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    if not counter:
        counter = Counter({"NoKeywords": 1})

    max_words = len(counter)

    wc = WordCloud(
        width=1600,
        height=1000,
        background_color="white",
        prefer_horizontal=0.9,
        font_path=pick_font(),
        collocations=False,
        max_words=max_words,
    ).generate_from_frequencies(dict(counter))

    wc.to_file(save_path)

def main():
    # 原逻辑（整段文本计数）保留在函数里，这里改为“按文件去重统计”
    freq = count_by_categories_one_per_file()
    make_wordcloud_png(freq, TITLE_PNG)
    print(f"[OK] 词云已生成：{TITLE_PNG}")
    if not pick_font():
        print("提示：未发现中文字体，若中文显示为方框，请在脚本顶部 FONT_CANDIDATES 中加入你的字体路径。")

if __name__ == "__main__":
    main()