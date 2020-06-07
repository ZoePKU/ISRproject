from main.text_retrieval.utils import parse, init_thes, json_input
from main.utils import sorted_dict_values
from gensim import models


thes_words, thes_dict, stop_words = init_thes()
print("开始加载w2v模型")
model = models.KeyedVectors.load_word2vec_format('main/text_retrieval/word2vec.bin',
                                                 binary=True)
print("w2v模型加载完成")


def text_retrieve(query):
    # 得到分词的列表
    cut_list = parse(query, thes_words, thes_dict, stop_words)
    # 读入倒排档json
    reverse_dict = json_input('main/text_retrieval/reverse_index.json')
    Res = dict()
    # 匹配函数
    for i in cut_list:
        if i in reverse_dict:
            for j in reverse_dict[i]:
                if j in Res:
                    Res[j] += reverse_dict[i][j]
                else:
                    Res[j] = reverse_dict[i][j]

    # w2v匹配(这个应该读入set，然后每个词和set里面的词匹配，但是考虑到优化，可能得先对set里的词聚类，这里没做)
    # 暂时没有聚类
    # model = models.KeyedVectors.load_word2vec_format('word2vec_779845.bin', binary=True)
    for y in cut_list:
        simi_res = [(x, y, model.similarity(x, y)) for x in reverse_dict if
                    x in model and y in model and model.similarity(x, y) > 0.6]
    for i in simi_res:
        for j in reverse_dict[i[0]]:  # i[0]是x
            if j in Res:
                Res[j] += reverse_dict[i[0]][j] * i[2]
            else:
                Res[j] = reverse_dict[i[0]][j] * i[2]

    res_list = sorted_dict_values(Res, True)
    return res_list