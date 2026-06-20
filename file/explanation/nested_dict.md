Step 8 的 TF 表类型是 `dict[int, dict[str, int]]`，访问写法像 `tf[0]["cat"]`。这篇说明：**嵌套字典是什么、为什么能连续用 `[]`、还有哪些常见用法**。

---

## 1. 普通字典：一个键对应一个值

```python
d = {"cat": 2, "dog": 1}
```

| 写法 | 含义 |
|------|------|
| `d["cat"]` | 键 `"cat"` 对应的值 → `2` |
| `d["dog"]` | → `1` |

字典 = **键 → 值** 的映射。键、值可以是不同类型；**值也可以是另一个字典**。

---

## 2. 嵌套字典：值里面还是字典

```python
tf = {
    0: {"cat": 2, "sat": 1},
    1: {"cat": 1, "dog": 1},
}
```

结构示意：

```text
tf
 ├── 键 0  →  值 {"cat": 2, "sat": 1}    ← 内层字典
 ├── 键 1  →  值 {"cat": 1, "dog": 1}
 └── ...
```

类型写法：`dict[int, dict[str, int]]`

| 层级 | 键类型 | 值类型 | 在本项目里表示 |
|------|--------|--------|----------------|
| 外层 | `int` | `dict[str, int]` | `doc_id` → 该文档的词频表 |
| 内层 | `str` | `int` | `term` → 出现次数 |

---

## 3. `tf[0]["cat"]` 怎么读？（核心）

**从外到内，分两步索引**，不能跳过外层：

```python
tf[0]          # 第 1 步：外层键 0 → {"cat": 2, "sat": 1}
tf[0]["cat"]   # 第 2 步：内层键 "cat" → 2
```

拆开写，完全等价：

```python
inner = tf[0]        # inner 是 dict[str, int]
count = inner["cat"] # count = 2
```

含义：**第 0 篇文档里，词 "cat" 出现了 2 次**。

---

## 4. 想成二维表（帮助记忆）

| doc_id | cat | sat | dog |
|--------|-----|-----|-----|
| 0 | 2 | 1 | — |
| 1 | 1 | — | 1 |

- `tf[0]` → 取 **第 0 行**（一整行是一个小字典）
- `tf[0]["cat"]` → 第 0 行、**cat 列** → `2`

Python 没有「必须用表格类」才能做二维结构；**字典套字典** 就是常用的二维映射。

---

## 5. 代码是怎么建出这个结构的（Step 8）

```python
tf = {}
for doc_id, tokens in enumerate(text_preprocessed):
    tf[doc_id] = {}
    for term in tokens:
        tf[doc_id][term] = tf[doc_id].get(term, 0) + 1
```

逐行含义：

| 代码 | 作用 |
|------|------|
| `tf = {}` | 建外层空字典 |
| `for doc_id, tokens in enumerate(...)` | 遍历每篇文档，得到编号和词列表 |
| `tf[doc_id] = {}` | 给这篇文档建 **内层** 空字典 |
| `tf[doc_id].get(term, 0) + 1` | 词每出现一次，计数 +1 |

走一遍 `doc 0`，`tokens = ["cat", "cat", "sat"]`：

```text
tf[0] = {}
读到 "cat" → tf[0]["cat"] = 0+1 = 1
读到 "cat" → tf[0]["cat"] = 1+1 = 2
读到 "sat" → tf[0]["sat"] = 0+1 = 1
结果：tf[0] = {"cat": 2, "sat": 1}
```

---

## 6. 其他常见用法

### 6.1 取值：直接 `[]` vs `.get()`

```python
tf[0]["cat"]           # 2（键必须存在，否则 KeyError）
tf[0].get("dog", 0)    # 0（没有 "dog" 时返回 0，不报错）
```

算 TF-IDF 时，某篇可能没有某个词，常用 `.get(term, 0)` 表示「出现 0 次」。

### 6.2 赋值、修改

```python
tf[0]["cat"] = 3              # 改成 3
tf[0]["new_word"] = 1         # 新增一个词
tf[doc_id][term] += 1         # 在 defaultdict 或已存在的键上 +1
```

### 6.3 遍历一篇文档里的所有词

```python
for term, count in tf[0].items():
    print(term, count)
# cat 2
# sat 1
```

### 6.4 遍历所有文档

```python
for doc_id, term_counts in tf.items():
    print(f"doc {doc_id}: {term_counts}")
```

### 6.5 判断键在不在

```python
0 in tf              # True，有 doc 0
"cat" in tf[0]       # True，doc 0 里有 cat
"dog" in tf[0]       # False
```

### 6.6 键的类型：外层 int、内层 str

```python
tf[0]       # 外层键：整数 doc_id
tf[0]["cat"] # 内层键：字符串 term
```

`enumerate` 给的 `doc_id` 是 `0, 1, 2...`，所以外层用 `int`；词是字符串，内层用 `str`。

---

## 7. 和倒排索引对比（方向相反）

本项目里两种「两层索引」，**第一次用谁、第二次用谁** 不同：

| 变量 | 类型 | 访问例子 | 问的问题 |
|------|------|----------|----------|
| `inverted_index` | `dict[str, list[int]]` | `inverted_index["cat"]` → `[0, 1, ...]` | 哪些文档 **有** 这个词？ |
| `tf` | `dict[int, dict[str, int]]` | `tf[0]["cat"]` → `2` | 这篇里这个词 **出现几次**？ |

```python
inverted_index["cat"]   # 词 → 文档列表
tf[0]["cat"]            # 文档 → 词 → 次数
```

都是「字典 + 再取一层」，只是 **外层键的含义对调**。

---

## 8. 可选写法：`defaultdict` 与 `Counter`

手写 `dict` + `.get(term, 0)` 可以；下面两种更短，本质仍是嵌套字典。

**`defaultdict`：**

```python
from collections import defaultdict

tf = defaultdict(lambda: defaultdict(int))
for doc_id, tokens in enumerate(text_preprocessed):
    for term in tokens:
        tf[doc_id][term] += 1
```

**`Counter`（每篇一个计数器）：**

```python
from collections import Counter

tf = {}
for doc_id, tokens in enumerate(text_preprocessed):
    tf[doc_id] = Counter(tokens)
```

`tf[0]["cat"]` 的用法不变。

---

## 9. 在本项目流水线里的位置

```text
text_preprocessed  (Step 2, list[list[str]])
        ↓
       tf            (Step 8, dict[int, dict[str, int]])
        ↓
    与 idf 合成 TF-IDF (Step 10)
```

TF **不能** 从 `inverted_index` / `gaps_index` 推出，因为倒排索引用 `set(tokens)` 去重后 **没有「出现几次」**。必须回到还保留重复的 `text_preprocessed`。

---

## 10. 一句话总结

- **嵌套字典** = 外层的值是另一个字典。
- **`tf[0]["cat"]`** = 先选文档 `0`，再选词 `"cat"`，得到次数。
- **连续两个 `[]`** = 两层字典各取一次键，顺序不能反。
- 在本项目里：**外层按文档，内层按词**；和 `inverted_index`（外层按词）方向相反。
