from main.text_retrieval.utils import parse, init_thes, json_input
from main.utils import sorted_dict_values
from gensim import models
import numpy as np

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

    # w2v匹配
    # 首先读入聚类json
    cl_dict = json_input("main/text_retrieval/clustering.json")
    # clustering_center属性是聚类中心，0-7对应聚类词
    # model = models.KeyedVectors.load_word2vec_format('word2vec_779845.bin', binary=True)
    simi_res = []
    for y in cut_list:
        # 先计算和哪个聚类中心最接近
        max_simi = 0
        max_index = 0
        if y in model:
            for i in range(8):
                v1 = np.array(model[y])
                v2 = np.array(cl_dict['cluster_center'][i])
                # print(x)
                # print(y)
                # print(x,y)
                Lx = np.sqrt(v1.dot(v1))
                Ly = np.sqrt(v2.dot(v2))
                cos_angle = v1.dot(v2) / (Lx * Ly)
                if cos_angle > max_simi:
                    max_simi = cos_angle
                    max_index = i
            simi_res += [(x, y, model.similarity(x, y)) for x in cl_dict[str(max_index)] if
                    x in model and model.similarity(x, y) > 0.6]

    for i in simi_res:
        for j in reverse_dict[i[0]]:  # i[0]是x
            if j in Res:
                Res[j] += reverse_dict[i[0]][j] * i[2]
            else:
                Res[j] = reverse_dict[i[0]][j] * i[2]

    res_list = sorted_dict_values(Res, True)
    return res_list