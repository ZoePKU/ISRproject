# -*- coding: utf-8 -*

import numpy as np
import torch
import sys
sys.path.append('main/retrieval')
sys.path.append('./')
from cnn_retrieval import load_model, load_data, extract_feature, load_query_image, sort_img, extract_feature_query
from app import *

def cnn_load_data():
    return load_data(data_path='static/bqbSource/', batch_size=2, shuffle=False, transform='default')


def cnn_load_model():
    return load_model(pretrained_model='main/retrieval/models/net_best.pth', use_gpu=True)


def cnn_build_feature():
    data_loader = cnn_load_data()
    model = cnn_load_model()
    gallery_feature, image_paths = extract_feature(model=model, dataloaders=data_loader)
    enc = gallery_feature.detach().cpu().numpy()
    np.savez("main/retrieval/models/enc.npz", enc=enc)
    print("===图片库特征提取并保存===")
    return gallery_feature


def cnn_load_image_paths():
    path_list = []
    for img, path in cnn_load_data():
        path_list += list(path)
    return path_list


def cnn_load_feature():
    feat = np.load("main/retrieval/models/enc.npz")
    return torch.tensor(feat['enc'])


def cnn_retrieve(query_image_path):
    query_image = load_query_image(query_image_path)
    query_feature = extract_feature_query(model=cnn_load_model(), img=query_image)
    similarity, image_index = sort_img(query_feature, cnn_load_feature())
    #image_paths = cnn_load_image_paths()
    length = int(image_index.size()[0])
    print(image_index.size())
    sorted_paths = [(image_index[i].item() + 1, similarity[i]) for i in range(length) if similarity[i] > 0.85]
    return sorted_paths


def cnn_text_retrieve(query_image_path,query):
    query_image = load_query_image(query_image_path)
    query_feature = extract_feature_query(model=cnn_load_model(), img=query_image)
    similarity, image_index = sort_img(query_feature, cnn_load_feature())
    text_res = text_retrieve(query)
    text_res = {i[0]: i[1] for i in text_res}
    length = int(image_index.size()[0])
    res = dict()
    for i in range(length):
        if image_index[i].item() in text_res:
            res[image_index[i].item() + 1] = similarity[i] + 2 * text_res[image_index[i].item() + 1]/ 3
        else:
            res[image_index[i].item() + 1] = similarity[i]/ 3
    res = sorted_dict_values(res)
    #image_paths = cnn_load_image_paths()
    #sorted_paths = {image_paths[i]:res[i] for i in res}
    print("结果",res)
    return res

if __name__ == '__main__':
    cnn_build_feature()
