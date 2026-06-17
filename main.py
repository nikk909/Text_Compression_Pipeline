#import numpy as np
#import pandas as pd
#1.下载数据库
from sklearn.datasets import fetch_20newsgroups
#2.文本数据预处理
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
#3.倒排索引
from collections import defaultdict

#这个数据库是一堆1990 年代 Usenet 论坛上的真实讨论帖
#头规模：大约 1.8 万篇 英文文章（训练集约 1.1 万，测试集约 7.5 千）
#类别：20 个主题，每个主题一类，例如：
#sci.space（太空）
#rec.sport.hockey（冰球）
#comp.graphics（计算机图形）
#talk.politics.misc（政治杂谈）
#每篇就是 一封邮件/帖子正文（字符串），带一个 类别标签（这篇属于哪个新闻组）。

#1.数据加载
# 去掉开头结尾和引用
# 不打乱，或者给个固定的随机种子，可重复实现，默认shuffle=True也就是会打乱
text = fetch_20newsgroups(
    subset="train",
    remove = ("headers","footers","quotes"),
    shuffle = False,
    ).data
#print(text[0])
# morgan and guzman will have era's 1 run higher than last year, and
#  the cubs will be idiots and not pitch harkey as much as hibbard.
#  castillo won't be good (i think he's a stud pitcher)

#print(len(text))
#11314

#2.数据预处理

#下载停用词
#nltk.download("stopwords")
#终端 python -c "import nltk; nltk.download('stopwords')"
_STOP_WORD = set(stopwords.words("english"))
#词干提取类对象
#nltk.download("wordnet")
#终端 python -c "import nltk; nltk.download('wordnet')"
_STEMMER_WORD = WordNetLemmatizer()

text_preprocessed:list[list[str]] = []

for doc in text:
    #分词
    tokens = word_tokenize(doc)
    #大小写统一：避免 "The" 去不掉停用词、"Camera"/"camera" 被当成两个词
    tokens = [t.lower() for t in tokens]
    #只保留字母，去掉标点和数字；去掉停用词;返回一个包含所有单词的列表
    tokens = [
        t for t in tokens 
        if t.isalpha() 
        and t not in _STOP_WORD
    ]
    #stemming词干提取，把每一个单词变成词干
    tokens = [_STEMMER_WORD.lemmatize(t) for t in tokens]
    #将处理后的单词列表添加到text_preprocessed列表中
    text_preprocessed.append(tokens)

# print(len(text_preprocessed))
#11314

# print(text_preprocessed[0])
# ['morgan', 'guzman', 'era', 'run', 'higher', 'last', 'year', 'cub',
#  'idiot', 'pitch', 'harkey', 'much', 'hibbard', 'castillo', 'wo', 'good', 
#  'think', 'stud', 'pitcher']

#3.倒排索引 dict[str, list[int]] 字符串"cat"，出现文档int值类似于[5,25,89...]

#defaultdict(list) 表示：创建一个字典，且
#第一次访问某个还不存在的键时，自动用 list() 创建一个空列表当作该键的值
inverted_index = defaultdict(list)

#enumerate(可迭代对象),等价手动写法（不用 enumerate）：
# doc_id = 0
# for tokens in text_preprocessed:
#     doc_id +=1

for doc_id, tokens in enumerate(text_preprocessed):
    # 同一篇里同一个词只记一次 doc_id（用 set 去重）
    for term in set(tokens):
        inverted_index[term].append(doc_id)
# 每个词的 posting 列表按 doc_id 升序（后面 gap 编码要求有序）
#Posting 列表 = 某个(单词出现过的所有文档 ID 的有序列表
inverted_index = dict(inverted_index)
for term in inverted_index:
    inverted_index[term].sort()

#print(len(inverted_index))
#73198

#这里不用[]直接取是因为会报错，get只会返回null
#print(inverted_index.get("morgan"))
#[0, 5608]

#4.Compute Index Statistics 统计一些值

# 词表大小（不同词有多少个）
vocabulary_length = len(inverted_index)

# 所有 posting 条数之和,字典里 一个key对应一个value,keys values就是对应集合
postings_length = sum(len(v) for v in inverted_index.values())

#最长的 posting 列表
#lambda对简单函数的输入输出的规定,输入变量 ： 输出简单的函数值，包含变量
#又名，匿名函数（没有名字的临时小函数）
#字典遍历默认为遍历key,max函数通过key的值遍历前面那个迭代器输出最大值
longest_term = max(inverted_index,key = lambda t : len(inverted_index[t]))
longest_term_length = len(inverted_index[longest_term])

#5.gap编码

#字典初始化，也可以d = dict() 
gaps_index = {}

#.items()返回 (key, value) 元组
#key:"cat" doc_ids: [2,4,7,45...]
for term,doc_ids in inverted_index.items():
    #不可能为空，每个词至少会出现一次因为前面的逻辑就是出现了才写，为空判定去掉了
    #第一个直接写进去
    gaps = [doc_ids[0]]
    #从第二个开始算插值，就是后面的减去前面的
    for i in range(1,len(doc_ids)):
        gaps.append(doc_ids[i] - doc_ids[i-1])
    gaps_index[term] = gaps

# print(inverted_index.get("pitch"))
# [0, 281, 578, 702, 758, 994, 1226, 1293, 1302, 1346, 1634, 
# 1709, 2430, 2445, 2485, 3289, 3434, 3460, 3554, 3563, 3574, 
# 3881, 4389, 4726, 4832, 4952, 5028, 5059, 5472, 7029, 7205, 
# 7306, 7483, 7679, 7724, 7884, 7917, 8153, 8764, 9323, 9426, 
# 9729, 9756, 10047, 10083, 10363, 10933, 10990, 11039, 11051, 11113]
 
# print(gaps_index.get("pitch"))
# [0, 281, 297, 124, 56, 236, 232, 67, 9, 44, 288, 75, 721, 15,
#  40, 804, 145, 26, 94, 9, 11, 307, 508, 337, 106, 120, 76, 31, 413,
#   1557, 176, 101, 177, 196, 45, 160, 33, 236, 611, 559, 103, 303, 27, 
#   291, 36, 280, 570, 57, 49, 12, 62]
#看着是没问题

#6.VByte（Variable Byte） compression压缩
#这里与md中略有出入，约定最高位为1表示继续，0表示结束
compressed_index = {}

def encode_vbyte(n : int) ->bytes:
    result = []
    #128 也就是 1000|0000 
    while n>= 128:
        #n & 127 表示n和127（01111111）按位与，也就是保留后七位
        #n | 128 表示n和128（10000000）按位或，也就是后七位不变，最高位补1
        #0|1 = 1 1|1 =1 所以最高位为1 0|1 = 1 0|0 = 0所以与按位或，保持不变
        result.append(n & 127 | 128)
        #n >>= 7 表示将n右移7位，也就是去掉后七位，原本的变成后七位
        n >>= 7
    result.append(n)
    return bytes(result)

#压缩的原理在于，一个int固定4个字节(32位)，最大可以表示2^32-1
#现在可以让小一点的数字，用更少的字节表示
#主要适配于小数，也就是2^28-1以下的数字，如果更大的话，
#因为本来需要一位去表示是否结束，所以会让原本2^28-1 到2^32-1的数字存储五位反而变多
#VByte 的优势不在「每个数都更小」，而在「小数字特别多时，平均更小」。
for term,gaps in gaps_index.items():
    #b"" 返回bytes对象
    buf = b""
    for g in gaps:
        #对于byetes 加法表示拼接
        buf += encode_vbyte(g)
        #gap 0   →  [0b00000000]原本32个0现在变成8位
        #gap 281 →  [0b10001001 00000010]原本32位现在变成16位
        #25+2*128 = 281
        #gap 297 →  [0b10101001 00000010]原本32位现在变成16位
        #32 + 9 + 2*128 = 297 低位在前高位在后
        #根据首位是否为0来反编码
    compressed_index[term] = buf

# print(compressed_index.get("pitch"))
# b'\x00\x99\x02\xa9\x02|8\xec\x01\xe8\x01C\t,
# \xa0\x02K\xd1\x05\x0f(\xa4\x06\x91\x01\x1a^\t
# \x0b\xb3\x02\xfc\x03\xd1\x02jxL\x1f\x9d\x03\x95
# \x0c\xb0\x01e\xb1\x01\xc4\x01-\xa0\x01!\xec\x01
# \xe3\x04\xaf\x04g\xaf\x02\x1b\xa3\x02$\x98\x02\xba\x0491\x0c>'

# gap 列表（用逗号分隔，给人看）:
# [0] [281] [297] [124] [56] ... [44] [288] ...
#   |    |     |     |    |         |    |
#   v    v     v     v    v         v    v
# bytes（无逗号，首尾相接）:
# \x00 \x99\x02 \xa9\x02 \x7c 8 ... , \xa0\x02 ...
#                               ↑
#                          这是 gap=44，不是分隔符

#7.Decode and Verify 反编码验证一下
def decode_vbyte(buf : bytes) -> list[int]:
    #乘法 power *= 128 改成左移 shift += 7，很多情况下稍快，逻辑不变
    gaps = []
    shift = 0
    result = 0

    for b in buf:
        result += (b & 127) << shift

        if b & 128 == 0:
            gaps.append(result)
            result = 0
            shift = 0
        else:
            shift += 7

    return gaps

gaps_index_verify = {}
for term,buf in compressed_index.items():
    gaps_index_verify[term] = decode_vbyte(buf)

# print(gaps_index_verify.get("pitch"))
# [0, 281, 297, 124, 56, 236, 232, 67, 9, 44, 288, 75,
#  721, 15, 40, 804, 145, 26, 94, 9, 11, 307, 508, 337,
#   106, 120, 76, 31, 413, 1557, 176, 101, 177, 196, 45, 
#   160, 33, 236, 611, 559, 103, 303, 27, 291, 36, 280, 570, 
#   57, 49, 12, 62]
reverse_index_verify = {}
def gaps_to_doc_ids(gaps : list[int]) -> list[int]:
    result = [gaps[0]]  
    for gap in gaps[1:]:
        result.append(result[-1] + gap)
    return result

for term,gaps in gaps_index_verify.items():
    reverse_index_verify[term] = gaps_to_doc_ids(gaps)

#print(reverse_index_verify.get("pitch"))
# [0, 281, 578, 702, 758, 994, 1226, 1293, 1302, 1346, 
# 1634, 1709, 2430, 2445, 2485, 3289, 3434, 3460, 3554, 3563, 
# 3574, 3881, 4389, 4726, 4832, 4952, 5028,5059, 5472, 7029, 
# 7205, 7306, 7483, 7679, 7724, 7884, 7917, 8153, 8764, 9323, 
# 9426, 9729, 9756, 10047, 10083, 10363, 10933, 10990, 11039, 
# 11051, 11113]    
   

#8.build TF Table统计每个词在每篇文档里出现几次
#TF Term Frequency（词频
#tf[doc_id][term] = 次数
#dict[str, list[int]]    这个词在哪些文档？inverted_index["cat"] = [0, 1, 2]   # 词 → 哪些 doc_id
#dict[int, dict[str, int]]   这篇里这个词几次？tf[0]["cat"] = 2   # doc → 这个词出现几次
tf:dict[int, dict[str, int]] = {}
for doc_id,tokens in enumerate(text_preprocessed):
    tf[doc_id] = {}
    #对于每一个dog cat统计个数
    for term in tokens:
        #这个取法就是经典的有则+1 无则取0+1
        tf[doc_id][term] = tf[doc_id].get(term,0) + 1

# print(len(tf))
# #11314
# print(tf.get(0))
# {'morgan': 1, 'guzman': 1, 'era': 1, 'run': 1, 'higher': 1, 
# 'last': 1, 'year':1, 'cub': 1, 'idiot': 1, 'pitch': 1, 
# 'harkey': 1, 'much': 1, 'hibbard': 1, 'castillo': 1, 'wo': 1, 
# 'good': 1, 'think': 1, 'stud': 1, 'pitcher': 1}

# print(tf.get(45))
# {'I': 1, 'one': 2, 'complaint': 1, 'cameraman': 1, 'series': 1,
#  'Show': 1, 'shot': 1, 'hit': 1, 'On': 1, 'occassion': 1, 
#  'camera': 2, 'zoomed': 1, 'check': 1, 'along': 1, 'board': 1, 
#  'puck': 1, 'slot': 1, 'They': 1, 'panned': 1, 'back':1, 'show': 1,
#   'rebound': 1, 'Maybe': 1, 'Mom': 1, 'people': 1, 'little': 1,
#    'experienced': 1}

#9.idf Inverse Document Frequency 
# 对 DF 做「逆」变换 
#还是基于inverted_index

import math#要用log

idf:dict[str,float] = {}
# df_:dict[str,int] = {}

N = len(text_preprocessed)#一共有多少篇文档

for term,doc_ids in inverted_index.items():
    df = len(doc_ids)#这个词在多少篇文档里出现过
    # df_[term] = df
    idf[term] = math.log(N/df)
    #df document frequency,词频，越大说明在越多文档里出现过，
    #说明这个词越常见，给的idf越小

#这一行之前都是忘记去掉大小写了，现在才开始加上，之前的输出可能有问题
# print(idf.get("the"))
# #None 作为停用词被删掉了
# print(idf.get("year"))
# #2.0746800478060003
# print(idf.get("camera"))
# #5.22292231172979
# 0.09531017980432493

# top10_by_df = sorted(df_.items(),key = lambda x:x[1],reverse=True)
# print(top10_by_df[:10])
# [('would', 3298), ('one', 3246), ('like', 2539), ('know', 2405), 
# ('get', 2333), ('time', 1972), ('also', 1944), ('think', 1923), 
# ('could', 1831), ('people', 1824)]
# print(top10_by_df[-10:])
# [('spacesuit', 1), ('wallengren', 1), ('univel', 1), 
# ('recntly', 1), ('wkshtree', 1), ('magzines', 1), 
# ('weightless', 1), ('capping', 1), ('foregone', 1), 
# ('brainstorm', 1)]

#10.TF-IDF计算
# tf[0] = {"cat": 1, "sat": 1}
# tf[1] = {"cat": 1, "dog": 1}
# idf["cat"] = 0.41
# idf["dog"] = 0.41
# idf["sat"] = 0.41

# tfidf_vectors[0]["cat"] = 1 * 0.41 = 0.41
# tfidf_vectors[0]["sat"] = 1 * 0.41 = 0.41
# tfidf_vectors[1]["cat"] = 1 * 0.41 = 0.41
# tfidf_vectors[1]["dog"] = 1 * 0.41 = 0.41

tf_idf:dict[int,dict[str,float]] = {}

for doc_id,term_counts in tf.items():
    tf_idf[doc_id] = {}
    for term,count in term_counts.items():
        tf_idf[doc_id][term] = count * idf[term]

# print(tf_idf.get(0))
# {'morgan': 6.768846818441564, 'guzman': 7.947501814783211, 
# 'era': 5.382552457321673, 'run': 2.789884330338309, 
# 'higher': 4.025528478501896, 'last':2.515965604448951, 
# 'year': 2.0746800478060003, 'cub': 5.696210016176716, 
# 'idiot': 5.382552457321673, 'pitch': 5.401970543178775,
#  'harkey': 8.640648995343156, 'much': 2.051034996297508, 
#  'hibbard': 8.640648995343156, 'castillo': 8.640648995343156,
#   'wo': 3.357445266605167, 'good': 1.966719116022089,
#    'think': 1.7721544303143213, 'stud': 7.542036706675046,
#     'pitcher': 5.273353165356681}