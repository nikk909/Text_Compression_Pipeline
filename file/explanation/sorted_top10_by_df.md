# sorted_top10_by_df 怎么理解

这行代码可以拆开理解，从左到右一共 4 步：

```python
top10_by_df = sorted(df_.items(), key=lambda x: x[1], reverse=True)[:10]
```

---

### 1. `df_.items()`

`df_` 是字典，例如：

```python
df_ = {
    "say": 5000,
    "would": 4800,
    "one": 4500,
    ...
}
```

`.items()` 会把字典变成一堆 **(词, df)** 元组：

```python
[("say", 5000), ("would", 4800), ("one", 4500), ...]
```

---

### 2. `sorted(..., key=lambda x: x[1], reverse=True)`

`sorted()` 负责排序。

- `key=lambda x: x[1]`：按每个元组的 **第 2 个元素** 排，也就是 **df 值**
  - `x` 是一个元组，比如 `("say", 5000)`
  - `x[0]` 是词 `"say"`
  - `x[1]` 是 df `5000`
- `reverse=True`：**从大到小** 排（df 最大的在前面）

排完后大致是：

```python
[("say", 5000), ("would", 4800), ("one", 4500), ...]
```

---

### 3. `[:10]`

列表切片，只取 **前 10 个**。

因为已经按 df 从大到小排好了，所以这就是 **df 最大的 10 个词**。

---

### 4. 整体含义

```python
top10_by_df = sorted(df_.items(), key=lambda x: x[1], reverse=True)[:10]
```

翻译成一句话：

> 把 `df_` 里所有 `(词, df)` 按 df 从大到小排序，取前 10 个，存到 `top10_by_df`。

---

### 打印时怎么用

```python
for term, df in top10_by_df:
    print(term, df)
```

这里 `term, df` 就是把每个元组拆开：
- `term` → 词
- `df` → 出现在多少篇文档里

---

### `lambda x: x[1]` 是什么

`lambda` 是 **匿名函数**，等价于：

```python
def get_df(x):
    return x[1]
```

`sorted` 需要知道“按什么排”，你就告诉它：**按元组的第二个数排**。

---

### 小对照

| 写法 | 含义 |
|------|------|
| `key=lambda x: x[1]` | 按 df 排 |
| `reverse=True` | 从大到小 |
| `[:10]` | 取前 10 个 |
| 结果类型 | `list[tuple[str, int]]` |
