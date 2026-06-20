## Step 9：Compute IDF

给每个词一个权重——越常见的词权重越低。

**idf(t) = log( N / df(t) )**

- **N**：文档总数，`len(text_preprocessed)`
- **df(t)**：包含词 t 的文档数，`len(inverted_index[term])`
