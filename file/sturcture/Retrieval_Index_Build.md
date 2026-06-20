## Build the Retrieval Index

1. **Load Dataset**
   - Example: Use sklearn's 20 Newsgroups fetch_20newsgroups()

2. **Preprocess Text**
   - Example: Tokenization, Stop-word removal, Lemmatization or stemming

3. **Build Inverted Index**
   - Example: retrieval -> [1, 2], index -> [1]

4. **Compute Index Statistics**
   - Example: vocabulary = 6,000 terms, postings = 120,000, longest list = data

---

## Compress the Index

5. **Apply Gap Encoding**
   - Example: [3, 10, 15, 21] -> [3, 7, 5, 6]

6. **Apply Variable Byte Encoding**
   - Example: gap 3 -> 10000011, gap 825 -> 00000110 10111001

7. **Decode and Verify**
   - Example: bytes -> gaps -> postings [3, 7, 5, 6] -> [3, 10, 15, 21]

---

## Implement Ranked Retrieval

8. **Build TF Table**
   - Example: tf(doc1, t1) = 2, tf(science, d2) = 1

9. **Compute IDF**
   - Example: idf(term) = log(N / df), common terms get lower weight

10. **Build TF-IDF Vectors**
    - Example: d1 = (3.12, 1.00, 0.68), q = (3.12, 0.00, 0.00)

11. **Compare Cosine Similarity**
    - Example: cos(q, d1) = 0.92, cos(q, d2) = 0.47

12. **Return Ranked Results**
    - Example: query: computer graphics, Top docs: d7, d12, d3

---

## Speed up Retrieval

13. **Candidate Selection**
    - Example: Only score docs that contain at least one query term

14. **Ignore Low IDF Terms**
    - Example: Ignore very common words such as the, of, is

15. **Champion Lists or Tiered Index**
    - Example: Keep top documents per term: data -> [d1, d8, d11]

---

## Evaluate and Reflect

16. **Measure Compression**
    - Example: original = 4000 bytes, compressed = 1200 bytes, ratio = 3.33x

17. **Measure Retrieval Time**
    - Example: full scoring = 1.2s, candidate scoring = 0.3s

18. **Evaluate Ranking Quality**
    - Example: Are top documents relevant? Compute precision@k

19. **Connect to AI/RAG**
    - Example: smaller index -> faster retrieval; faster retrieval -> lower RAG latency. PLUS: https://www.youtube.com/watch?v=7-D1QNd9V6M