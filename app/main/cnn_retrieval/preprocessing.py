import sys
# 加入cwd app/
sys.path.append('./')
from main.cnn_retrieval.cnn_utils import cnn_load_feature
import numpy as np
def out(feat,i,j):
    x = np.array(feat[i - 1])
    y = np.array(feat[j - 1])
    # print(x)
    # print(y)
    # print(x,y)
    Lx = np.sqrt(x.dot(x))
    Ly = np.sqrt(y.dot(y))
    cos_angle = x.dot(y) / (Lx * Ly)
    # print(cos_angle)
    if cos_angle > 0.98:
        print(cos_angle, i, j)
feat = cnn_load_feature().tolist()
# print(feat)
#2660 2911 3457
'''
for j in range(i + 1, length):
    x = np.array(feat[i])
    y = np.array(feat[j])
    # print(x,y)
    Lx = np.sqrt(x.dot(x))
    Ly = np.sqrt(y.dot(y))
    cos_angle = x.dot(y) / (Lx * Ly)
    simi.append(cos_angle)
    # print(cos_angle)
    if cos_angle > 0.999999:
        print(cos_angle, i, j)
'''
for i in range(1,4001):
    if i % 100 == 0:
        print("finish")
    for j in range(i + 1,4001):
        out(feat,i,j)
