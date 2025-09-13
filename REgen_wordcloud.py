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

# ================ 关键词分类（可自行扩展/修改） ================
# 设计说明：
# - 左边是“规范类别名”（会出现在词云里）
# - 右边是该类的所有“变体/同义词/常见写法”
# - 匹配规则：统一转小写 + 去空格 后做子串计数，因此“区间 dp”“区间DP”“区间dp”都能匹配
KW_MAP = {
    "BFS": ["bfs", "广度优先", "广搜", "层序遍历"],
    "DFS": ["dfs", "深度优先", "深搜", "先序遍历", "后序遍历", "中序遍历"],
    "回溯": ["回溯", "回溯算法", "搜索", "n 皇后", "全排列", "组合", "子集"],
    "动态规划": ["dp", "动态规划", "记忆化", "滚动数组", "一维dp", "二维动态规划"],
    "区间DP": ["区间dp", "区间 dp"],
    "数位DP": ["数位dp", "数位 dp"],
    "树形DP": ["树形dp", "树型dp", "树 形 dp", "树 型 dp"],
    "贪心": ["贪心", "贪心算法"],
    "双指针": ["双指针", "快慢指针", "相向双指针", "逆向双指针", "三指针"],
    "滑动窗口": ["滑动窗口"],
    "二分查找": ["二分", "二分查找", "值域二分"],
    "单调栈": ["单调栈", "NGE", "PGE"],
    "单调队列": ["单调队列", "滑动窗口最大值"],
    "前缀和/差分": ["前缀和", "差分"],
    "哈希表": ["哈希", "哈希表", "hash", "hashmap", "map", "频次哈希"],
    "并查集": ["并查集", "union find", "dsu"],
    "拓扑排序": ["拓扑排序", "kahn", "kahn算法", "kahn 算法"],
    "最短路/Dijkstra": ["最短路", "最短路径", "dijkstra", "dijsktra"],
    "Trie/字典树": ["trie", "字典树", "前缀树"],
    "KMP": ["kmp", "前缀函数"],
    "字符串哈希": ["字符串哈希", "rolling hash", "字符串 hash"],
    "Manacher": ["manacher", "马拉车"],
    "树状数组/BIT": ["树状数组", "fenwick", "bit", "binary indexed tree"],
    "线段树": ["线段树", "segment tree"],
    "堆/优先队列": ["堆", "优先队列", "小根堆", "大根堆", "heap", "priority queue"],
    "快速选择/Top-K": ["快速选择", "快选", "quickselect", "top-k", "topk"],
    "经典排序": ["快速排序", "归并排序", "堆排序", "桶排序", "计数排序", "三向切分"],
    "回文相关": ["回文", "最长回文", "回文子串", "回文子序列"],
    "Kadane/最大子数组": ["kadane", "最大子数组和"],
    "数论/筛": ["数论", "质数", "筛质数", "埃氏筛", "线性筛"],
    "洗牌/随机化": ["洗牌", "knuth-shuffle", "shuffle", "rand"],
    "最小生成树": ["最小生成树", "kruskal", "prim"],
    "图论": ["图论"],
}

# ================ 字体（可选） ================
# 中文词云需要 CJK 字体；Windows 上你可以用：
# C:\Windows\Fonts\msyh.ttc 或 simhei.ttf
# 若留空，wordcloud 会用默认字体，中文可能显示为方框
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
    return None  # 用默认（英文 OK，中文可能不完美）

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
    """
    归一化匹配文本：
    - 全部转小写
    - 全角转半角
    - 删除所有空白（空格不敏感）
    """
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
    """
    构造：规范标签 -> 变体列表（统一小写+去空格）
    同时返回“显示用”的规范标签列表
    """
    idx = {}
    for canon, vars_ in KW_MAP.items():
        idx[canon] = [normalize_kw(v) for v in vars_ if v.strip()]
    return idx

# ================ 统计主流程（仅标题） ================
def collect_titles_text():
    chunks = []
    for f in list_markdown_files():
        # 文件名（去扩展名）
        chunks.append(os.path.splitext(os.path.basename(f))[0])
        # 文内第一条 Markdown 标题
        h1 = first_md_header(read_file(f))
        if h1:
            chunks.append(h1)
    return "\n".join(chunks)

def count_by_categories(text: str) -> Counter:
    """
    在“去空格+小写”的文本上，对每个类别的所有变体进行子串计数并累加。
    不重叠计数：str.count 的语义。
    """
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

# ================ 生成词云（PNG） ================
def make_wordcloud_png(counter: Counter, save_path: str, title_hint: str = None):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    if not counter:
        # 空数据也生成一张占位图（WordCloud 需要至少一个词）
        counter = Counter({"NoKeywords": 1})

    # 不截断：把全部出现的类别都画进去
    max_words = len(counter)

    wc = WordCloud(
        width=1600,
        height=1000,
        background_color="white",
        prefer_horizontal=0.9,
        font_path=pick_font(),
        collocations=False,
        max_words=max_words,
        # 注意：在 SVG 版本中会嵌入位图；这里我们直接导出 PNG
    ).generate_from_frequencies(dict(counter))

    wc.to_file(save_path)

def main():
    titles_text = collect_titles_text()
    freq = count_by_categories(titles_text)
    make_wordcloud_png(freq, TITLE_PNG)
    print(f"[OK] 词云已生成：{TITLE_PNG}")
    if not pick_font():
        print("提示：未发现中文字体，若中文显示为方框，请在脚本顶部 FONT_CANDIDATES 中加入你的字体路径。")

if __name__ == "__main__":
    main()
