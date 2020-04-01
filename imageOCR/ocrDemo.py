# coding:UTF-8
# 通用文字识别

import requests
import base64
import os
import dbManager


# 将句子拼接在一起
def words_together(words_res):
    words_concat_res = ''
    for word in words_res:
        words_concat_res += word['words']
    return words_concat_res


# 单个图片通用识别 百度api
def do_ocr_file(file_path):
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
    # 二进制方式打开图片文件
    f = open(file_path, 'rb')
    img = base64.b64encode(f.read())
    params = {"image": img}
    # 授权密钥
    access_token = '24.238aa753d943330ceb37cdb14e65a949.2592000.1588268975' \
                   '.282335-17008029 '
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    ocr_response = requests.post(request_url, data=params, headers=headers)
    return ocr_response


# 插入数据库记录
def insert_description(item_id, name, description):
    db = dbManager.DbManager()
    sql = "INSERT INTO basic_info(id,name,geng) VALUES (%s,%s,%s)"
    params = (item_id, name, description)
    db.edit(sql, params)
    print("插入成功")


# 文件夹批量识别
def do_ocr_dir(dir_path):
    i = 0
    for file_path in os.listdir(dir_path):
        response = do_ocr_file(dir_path + file_path)
        if response:
            i += 1
            res = response.json()
            insert_description(i, file_path,
                               words_together(res['words_result']))


# 查找漏网之鱼
def seek_left(dir_path):
    i = 6434
    for file_path in os.listdir(dir_path):
        sql = "SELECT COUNT(*) FROM basic_info WHERE name = %s"
        db = dbManager.DbManager()
        if db.fetchone(sql, file_path)[0] == 0:
            print(file_path + "还不存在！")
            response = do_ocr_file(dir_path + file_path)
            if response:
                i += 1
                res = response.json()
                insert_description(i, file_path,
                                   words_together(res['words_result']))


if __name__ == "__main__":
    # 存放图片的文件夹路径
    dirPath = '/Users/leverest/Documents/02_ProgramProject/08_Projects' \
              '/ISRproject/bqbSource/'
    # 对文件夹中所有的图片进行标记
    # do_ocr_dir(dirPath)
    # 查找上一次漏标记的
    seek_left(dirPath)
