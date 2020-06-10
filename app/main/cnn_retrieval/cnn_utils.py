# -*- coding: utf-8 -*
import sys
sys.path.append('main/cnn_retrieval')
sys.path.append('./')
import numpy as np
import torch
from main.cnn_retrieval.cnn_retrieval import load_model, load_data, extract_feature, load_query_image, sort_img, extract_feature_query
from main.text_retrieval.retrieval import text_retrieve
from main.utils import sorted_dict_values

def cnn_load_data():
    return load_data(data_path='static/bqbSource/', batch_size=2, shuffle=False, transform='default')


def cnn_load_model():
    return load_model(pretrained_model='main/cnn_retrieval/models/net_best.pth') # , use_gpu=True


def cnn_build_feature():
    data_loader = cnn_load_data()
    model = cnn_load_model()
    gallery_feature, image_paths = extract_feature(model=model, dataloaders=data_loader)
    enc = gallery_feature.detach().cpu().numpy()
    np.savez("main/cnn_retrieval/models/enc.npz", enc=enc)
    print("===图片库特征提取并保存===")
    return gallery_feature


def cnn_load_image_paths():
    path_list = []
    for img, path in cnn_load_data():
        path_list += list(path)
    return path_list


def cnn_load_feature():
    feat = np.load("main/cnn_retrieval/models/enc.npz")
    return torch.tensor(feat['enc'])


# 读取检索图 -> 提取卷积特征 -> 计算相似性 -> 排序输出
def cnn_retrieve(query_image_path):
    query_image = load_query_image(query_image_path)
    query_feature = extract_feature_query(model=cnn_load_model(), img=query_image)
    # print(query_feature)
    # print(len(query_feature.tolist()))
    similarity, image_index = sort_img(query_feature, cnn_load_feature())
    #image_paths = cnn_load_image_paths()
    length = int(image_index.size()[0])
    print(image_index.size())
    sorted_paths = [(image_index[i].item() + 1, similarity[i].item()) for i in range(length) if similarity[i] > 0.85]
    print(sorted_paths)
    return sorted_paths


# 图文分别检索排序 -> 加权筛选 -> 排序输出
def cnn_text_retrieve(query_image_path,query):
    cnn_res = cnn_retrieve(query_image_path)
    text_res = text_retrieve(query)

    text_res = {i[0]: i[1] for i in text_res}
    print(text_res)
    print(len(text_res))
    print(len(cnn_res))
    # length = len(text_res)
    print(cnn_res)
    res = dict()
    for i in cnn_res:
        if "{:0>4}".format(str(i[0])) in text_res:
            res[i[0]] = (i[1] + 2 * text_res["{:0>4}".format(str(i[0]))])/ 3
            print(i[0],res[i[0]])
    res = sorted_dict_values(res,reverse=True)

    #image_paths = cnn_load_image_paths()
    #sorted_paths = {image_paths[i]:res[i] for i in res}
    print("结果",res)

    return res

if __name__ == '__main__':
    cnn_build_feature()
