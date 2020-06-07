from sklearn.cluster import KMeans
import numpy as np
from gensim import models
import json
from main.text_retrieval.utils import *
# 实现词向量的聚类，讲所有检索词的词向量聚类 输入的是一列词
def cal_text_clustering(lst,model):
    # 首先从一列词产生词向量
    res = []
    word = []
    for i in lst:
        if i in model:
            res.append(model[i])
            word.append(i)
    res = np.array(res)
    clf = KMeans(n_clusters=8, init='k-means++', n_init=10, max_iter=300, tol=0.0001,
            precompute_distances='auto', verbose=0, random_state=None,
            copy_x=True, n_jobs=None, algorithm='auto').fit(res)
    clustering_dict = dict()
    print(type(clf.cluster_centers_))
    print(type(clf.cluster_centers_.tolist()))
    nd_list = clf.cluster_centers_.tolist()
    print(nd_list)
    clustering_dict['cluster_center'] = nd_list
    length = len(word)
    for i in range(8):
        clustering_dict[i] = list()
    res = res.tolist()
    for i in range(length):
        # print(clf.predict(res[i]))
        clustering_dict[clf.predict([res[i]]).tolist()[0]].append(word[i])
    clustering_dict['label'] = clf.labels_.tolist()
    print(clf.labels_)
    return clustering_dict


print("开始加载w2v模型")
model = models.KeyedVectors.load_word2vec_format('main/text_retrieval/word2vec.bin',
                                                 binary=True)
print("w2v模型加载完成")

my_dict = json_input("main/text_retrieval/reverse_index.json")
lst = [x for x in my_dict]
cl_dict = cal_text_clustering(lst,model)
print(cl_dict)
output('main/text_retrieval/clustering.json', cl_dict)

