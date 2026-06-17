各步用什么类型（极简）

| 步骤 | 存什么 | Python 类型 | 代码里的变量名 | 依赖前面哪步 |
| ---- | ------ | ----------- | -------------- | ------------ |
| 1 加载 | 很多篇正文 | `list[str]` | `text` | — |
| 2 预处理 | 每篇变成一串词 | `list[list[str]]` | `text_preprocessed` | Step 1 `text` |
| **3 建索引** | **词 → 哪些文档里有** | **`dict[str, list[int]]`** | **`inverted_index`** | Step 2 `text_preprocessed` |
| 4 统计 | 词表大小、posting 总数等标量 | `int` / `str` | `vocabulary_length`, `postings_length`, `longest_term`, `longest_term_length` | Step 3 `inverted_index` |
| 5 gap | 同上键，值改成间隔 | `dict[str, list[int]]` | `gaps_index` | Step 3 `inverted_index` |
| 6 压缩 | 同上键，值变成字节 | `dict[str, bytes]` | `compressed_index` | Step 5 `gaps_index` |
| 7 解码验证 | 先还原 gap，再还原 doc_id | `dict[str, list[int]]` | `gaps_index_verify`, `reverse_index_verify` | Step 6 `compressed_index` |
| 8 TF 表 | 每篇文档里每个词出现几次 | `dict[int, dict[str, int]]` | `tf`（待实现） | Step 2 `text_preprocessed` |
| 9 IDF | 每个词的逆文档频率 | `dict[str, float]` | `idf`（待实现） | Step 3 `inverted_index` |
| 10 TF-IDF | 文档 / 查询的加权向量 | `dict[int, dict[str, float]]`, `dict[str, float]` | `tfidf_vectors`, `query_vector`（待实现） | Step 8 `tf` + Step 9 `idf` |
| 11 相似度 | 查询与每篇文档的余弦相似度 | `dict[int, float]` | `similarity_scores`（待实现） | Step 10 向量 |
| 12 排序结果 | 按分数排序的文档列表 | `list[tuple[int, float]]` | `ranked_results`（待实现） | Step 11 `similarity_scores` |
| 13 候选筛选 | 至少含一个查询词的文档 | `set[int]` | `candidate_docs`（待实现） | Step 3 `inverted_index` + 查询 |
| 14 忽略低 IDF | 查询里要跳过的常见词 | `set[str]` | `ignored_terms`（待实现） | Step 9 `idf` + 查询 |
| 15 Champion | 每个词保留的 top 文档 | `dict[str, list[int]]` | `champion_lists`（待实现） | Step 11 分数 + Step 3 |
| 16 压缩比 | 未压缩 / 压缩后字节数 | `int`, `float` | `uncompressed_bytes`, `compressed_bytes`, `compression_ratio`（待实现） | Step 4 `postings_length` + Step 6 `compressed_index` |
| 17 检索耗时 | 全量 vs 候选耗时（秒） | `float` | `full_scoring_time`, `candidate_scoring_time`（待实现） | Step 11 / 13 |
| 18 排序质量 | precision@k 等指标 | `float` | `precision_at_k`（待实现） | Step 12 + 标注 |

所以：**前面是列表装文档；Step 3 起索引线是「词 → posting」；Step 8 起检索线是「文档 → 词频 / 向量 → 分数」。**

---

## 总结构（19 步）

```text
                 Step 1 加载 text
                      ↓
                 Step 2 预处理 text_preprocessed
            （索引线与检索线共用 Step 2）
                      │
           ┌──────────┴──────────┐
           ↓                       ↓
      【索引线】               【检索线】
      Step 3–7                 Step 8–12
   inverted_index →          tf → idf → tfidf
   gaps → compressed              → ranked_results
           │                       │
           │                  Step 13–15 加速
           │                       │
           └───────────┬───────────┘
                       ↓
                 【评估线】Step 16–19
              压缩比 / 耗时 / 质量 / RAG
```

## 两条线怎么衔接

```text
Step 1–2   text → text_preprocessed
Step 3–7   inverted_index → … → compressed_index   （索引压缩线，词 → doc_id）
Step 8–12  tf → idf → tfidf → ranked_results       （排序检索线，doc_id → 分数）
Step 13–15 用 inverted_index 加速 Step 11–12
Step 16    用 compressed_index 证明 Step 5–6 省了空间
```

## 数据从哪来到哪去

```text
Step 1–2
  text_preprocessed  ──────────────────────→  Step 8  tf
         │                                              │
         └→  Step 3  inverted_index  ──→  Step 9  idf  ─┘
                    │                              │
                    ├→ Step 5–7 压缩/解码           ├→ Step 10–12 打分排序
                    │                              │
                    └→ Step 13 找候选文档 ←────────┘
                    │
                    └→ Step 16 算压缩比（和 compressed_index 比）
```

**压缩索引和 TF-IDF 检索可以并存：** 查词时用 `inverted_index`（或从 `compressed_index` decode）找候选文档，用 `tf` / `idf` 打分排序。

---

## 3 篇文档的最小例子（Step 1–7）

3 篇文档（`doc_id` 就是 0、1、2）：

```text
doc 0: "cat sat"
doc 1: "cat dog"
doc 2: "dog sat"
```

**Step 2 之后** → `text_preprocessed`：

```python
[
  ["cat", "sat"],   # doc 0
  ["cat", "dog"],   # doc 1
  ["dog", "sat"],   # doc 2
]
```

类型：`list[list[str]]`

---

**Step 3 倒排索引** → `inverted_index`：

```python
{
  "cat": [0, 1],
  "dog": [1, 2],
  "sat": [0, 2],
}
```

类型：`dict[str, list[int]]`
含义：键是词，值是 **有序的** 文档编号列表（postings）。

---

**Step 5 gap** → `gaps_index`（键不变，值的含义变成间隔）：

```python
{
  "cat": [0, 1],    # 0, 1-0=1
  "dog": [1, 1],    # 1, 2-1=1
  "sat": [0, 2],    # 0, 2-0=2
}
```

类型：仍是 `dict[str, list[int]]`

---

**Step 6 压缩** → `compressed_index`：

```python
{
  "cat": b'\x00\x01',
  "dog": b'...',
  "sat": b'...',
}
```

类型：`dict[str, bytes]`

---

**Step 7 验证** → `gaps_index_verify` → `reverse_index_verify`：

```python
# gaps_index_verify["cat"] == gaps_index["cat"]
# reverse_index_verify["cat"] == inverted_index["cat"]  →  [0, 1]
```

类型：又回到 `dict[str, list[int]]`

---

## 3 篇文档的最小例子（Step 8–12）

仍用上面的 `text_preprocessed`。

**Step 8 TF 表** → `tf`（注意：来自 `text_preprocessed`，不是 `gaps_index`）：

```python
{
  0: {"cat": 1, "sat": 1},
  1: {"cat": 1, "dog": 1},
  2: {"dog": 1, "sat": 1},
}
```

类型：`dict[int, dict[str, int]]`
含义：外层键是 `doc_id`，内层是 **该文档内** 每个词的出现次数。
访问：`tf[1]["cat"]` → `1`；若词不在文档里可视为 `0`。

---

**Step 9 IDF** → `idf`（来自 `inverted_index`，`df = len(posting)`，`N = 文档总数`）：

```python
# N = 3
{
  "cat": log(3 / 2),   # 出现在 doc 0,1 → df=2
  "dog": log(3 / 2),
  "sat": log(3 / 2),
}
```

类型：`dict[str, float]`

---

**Step 10 TF-IDF 向量** → `tfidf_vectors`, `query_vector`：

```python
# 文档 0 在词 "cat" 上的权重
tfidf_vectors[0]["cat"] = tf[0]["cat"] * idf["cat"]

# 查询 "cat dog" 预处理后的 query_vector
query_vector = {"cat": 1 * idf["cat"], "dog": 1 * idf["dog"]}
```

类型：文档 `dict[int, dict[str, float]]`，查询 `dict[str, float]`

---

**Step 11 余弦相似度** → `similarity_scores`：

```python
{
  0: 0.71,   # cos(query, doc0)
  1: 0.92,   # cos(query, doc1)  最高
  2: 0.71,
}
```

类型：`dict[int, float]`

---

**Step 12 排序结果** → `ranked_results`：

```python
[(1, 0.92), (0, 0.71), (2, 0.71)]   # (doc_id, score) 按 score 降序
```

类型：`list[tuple[int, float]]`

---

## Step 13–18 数据结构（简表）

| 步骤 | 变量名 | 类型 | 例子 |
| ---- | ------ | ---- | ---- |
| 13 候选 | `candidate_docs` | `set[int]` | `{0, 1, 2}` |
| 14 忽略词 | `ignored_terms` | `set[str]` | `{"the", "of"}` |
| 15 Champion | `champion_lists` | `dict[str, list[int]]` | `"cat": [1, 0]` |
| 16 压缩比 | `compression_ratio` | `float` | `3.33` |
| 17 耗时 | `full_scoring_time` | `float` | `1.2` |
| 18 质量 | `precision_at_k` | `float` | `0.8` |

---

## 直接回答你的两个问题

1. **核心数据结构只有一个吗？**

   - **不完全是。**
   - 文档侧：`text` → `text_preprocessed`
   - 索引侧：`inverted_index` → `gaps_index` → `compressed_index`（编解码回到 `dict[str, list[int]]`）
   - 检索侧：`tf` + `idf` → 向量 → `similarity_scores` → `ranked_results`

2. **都是列表吗？**

   - **不是。** 文档用列表；索引用字典 + 列表或 bytes；TF/IDF/分数用嵌套字典或 `(doc_id, score)` 列表。

如果你只记一句：

- **倒排索引** = `inverted_index`，词 → doc_id 列表
- **TF 表** = `tf`，doc_id → {词: 次数}，**必须来自 `text_preprocessed`**
- **检索结果** = `ranked_results`，有序的 `(doc_id, score)` 列表
