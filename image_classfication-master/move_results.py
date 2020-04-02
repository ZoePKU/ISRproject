#-*- encoding:utf-8 -*-
__date__ = '19/03/21'
import os
import numpy as np
import shutil

#导入所需要的模块，numpy科学计算库，cv2图像处理库，os，对操作系统进行操作（保存文件等）的库，codes是处理任意编码的模块，shutil模块是移动文件的
isExists = os.path.exists(r'./0')
# 判断结果
if not isExists:
    for i in range(3000):
        os.makedirs((r'./' + str(i)))
    #os.makedirs((r'./0'))
    #os.makedirs(r'./1')

txt_file = open(r"./results.txt") #打开文件
line = txt_file.readline() #读取每一行
data_list = []

path = ".\\picture"
while line:
    #print(line.split()[1])
    num = int(line.split()[1]) #找到txt文件中的shu
    filename = line.split()[0].split('\\')[1]
    print(filename)
    print(num)
    path2 = "./" + str(num)
    shutil.copyfile(os.path.join(path, filename), os.path.join(path2, filename))
    print(filename + "成功")
    #print(num)
    #data_list.append(num)
    line = txt_file.readline()
txt_file.close() #关闭文件



