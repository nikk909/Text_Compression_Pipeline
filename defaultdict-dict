defaultdict 完全能排序
第三步转换的原因是：

1、defaultdict → dict 真实 3 个原因
① 消除 default 自动创建 key 的副作用（最核心）
defaultdict(list)特性：随便取一个不存在的键，会自动创建空列表
python
运行
from collections import defaultdict
d = defaultdict(list)
print(d["abcdefg"]) # 键本来没有，直接凭空新增"abcdefg":[]
转成普通dict后：找不到键会返回报错 / 用.get()返回 None，不会乱新增无用词条。
你后面代码用 inverted_index.get("pitcher") 做查询，普通 dict 才符合正常词典查询逻辑。
② 索引构建完毕，不再需要自动 append 初始化
构建阶段需要defaultdict：新词第一次出现时自动生成空 list，方便.append(doc_id)。
索引全部建好后，不会再新增单词、不再往 posting 追加文档 ID，不需要 default 的默认初始化能力，换成原生 dict 更规范。
③ 数据结构轻量化
defaultdict是 dict 的子类，附带默认工厂函数逻辑，只读查询场景下原生 dict 开销更小。