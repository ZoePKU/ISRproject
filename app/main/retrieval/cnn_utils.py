import numpy as np
import torch
from main.retrieval.retrieval import load_model, load_data, extract_feature, load_query_image, sort_img, extract_feature_query
from app import *

def cnn_load_data():
    return load_data(data_path='static/cnn_test/image_database/', batch_size=2, shuffle=False, transform='default')


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
    image_paths = cnn_load_image_paths()
    sorted_paths = [image_paths[i] for i in image_index]
    return sorted_paths


def cnn_text_retrieve(query_image_path,query):
    query_image = load_query_image(query_image_path)
    query_feature = extract_feature_query(model=cnn_load_model(), img=query_image)
    similarity, image_index = sort_img(query_feature, cnn_load_feature())
    text_res = text_retrieve(query)
    length = image_index.size()
    res = dict()
    for i in length:
        res[image_index[i]] = 2 * similarity[i] * text_res[image_index[i]]/similarity[i] + text_res[image_index[i]]
    res = sorted_dict_values(res)
    #image_paths = cnn_load_image_paths()
    #sorted_paths = {image_paths[i]:res[i] for i in res}
    return res

if __name__ == '__main__':
    cnn_build_feature()
