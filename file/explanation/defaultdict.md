# `from collections import defaultdict` 是什么

`from collections import defaultdict` 是从 Python **标准库** 里导入 **`defaultdict`**：一种 **带默认值的字典**。

---

## 普通 `dict` vs `defaultdict`

**普通 dict：**

```python
d = {}
d["cat"].append(0)   # KeyError: 还没有 "cat" 这个键
```

要先建键：

```python
d = {}
if "cat" not in d:
    d["cat"] = []
d["cat"].append(0)
```

**`defaultdict(list)`：**

```python
from collections import defaultdict

d = defaultdict(list)
d["cat"].append(0)   # 可以！自动先有 d["cat"] = []
```

第一次访问不存在的键时，会 **自动** 用 `list()` 建一个空列表，再 `.append(0)`。

---

## 和建倒排索引的关系

```python
inverted_index = defaultdict(list)

inverted_index["morgan"].append(0)   # 第一次见 "morgan" → 自动 []
inverted_index["morgan"].append(5)   # 已有列表，继续 append
# 结果: {"morgan": [0, 5]}
```

不用每次写：

```python
if term not in inverted_index:
    inverted_index[term] = []
inverted_index[term].append(doc_id)
```

---

## `defaultdict(list)` 里的 `list` 是啥

`defaultdict(list)` 表示：**缺键时，默认值 = 调用 `list()` 得到的空列表**。

也可以是别的，例如：

```python
defaultdict(int)    # 缺键 → 0
defaultdict(set)    # 缺键 → set()
```

建倒排索引时用 **`list`**，因为每个词对应 **doc_id 的列表**（postings）。

---

## 最后为什么 `dict(inverted_index)`

`defaultdict` 打印时类型还是 `defaultdict`；转成普通 `dict` 只是习惯，后面代码用起来一样：

```python
inverted_index = dict(inverted_index)
```

不转也可以继续用。

---

## 一句话

**`defaultdict(list)` = 字典；键第一次出现时自动配一个空列表，适合「每个词往列表里追加 doc_id」的倒排索引写法。**
