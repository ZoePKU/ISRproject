import os
import copy
from flask import Flask, render_template, request, redirect, url_for
from main.retrieval.retrieval import load_model, load_data, extract_feature, load_query_image, sort_img, extract_feature_query
from text.utils import *
from main.db import *
import numpy as np
import torch
import codecs


# 下面部分是为了解决cwd路径问题，我在pycharm设置了cwd为app，直接直接命令行启动会出问题
# cwd = os.getcwd()
# if os.path.split(cwd)[-1] == 'ISRproject':
#     os.chdir('app')
def sortedDictValues(adict,reverse=False):
    keys = list(adict.keys())
    keys.sort(reverse=reverse)
    return [(key,adict[key]) for key in keys]


def consult_db(session,table,field):
    sql_gen = "select name," + field + " from " + table
    cursor_gen = session.execute(sql_gen)
    res = cursor_gen.fetchall()  # 这是bqb描述
    return res

#这里是单独的文字检索
def retrieve(query):
    #连接数据库
    session = connect_db("129.211.91.153:3306", "isrbqb", 'admin', 'abcd')
    #查出所有的description,role,emotion,style,topic
    res_description = consult_db(session,"bqb_description","geng")
    res_role = consult_db(session,"bqb_role","role")
    res_emotion = consult_db(session,"bqb_emotion","emotion")
    res_style = consult_db(session,"bqb_style","style")
    res_topic = consult_db(session,"bqb_context","context")


    #生成词表
    thes_words,thes_dict, stop_words = init_thes()
    #得到分词的列表
    cut_list = parse(query,thes_words,thes_dict, stop_words)
    #读入倒排档json
    reverse_dict = input('text/reverse_index.json')
    Res = dict()
    #匹配函数
    for i in cut_list:
        if(i in reverse_dict):
            for j in reverse_dict[i]:
                if j in Res:
                    Res[j] += reverse_dict[i][j]
                else:
                    Res[j] = reverse_dict[i][j]
    res_list = sortedDictValues(Res)

    #w2v匹配(这个应该读入set，然后每个词和set里面的词匹配，但是考虑到优化，可能得先对set里的词聚类，这里没做)

    #生成匹配的Res
    res = [{'name': i[0] + '.jpg',
            'src_path': 'static/bqbSource/' + i[0] + '.jpg',
            'score':i[1],
            'role':[],
            'emotion':[],
            'style':[],
            'topic':[]
            } for i in res_list]
    for i in res_description:
        for j in res:
            if i[0] == j['name']:
                j['description'] = i[1]

    for i in res_role:
        for j in res:
            if i[0] == j['name']:
                j['role'].append(i[1])
    for i in res_emotion:
        for j in res:
            if i[0] == j['name']:
                j['emotion'].append(i[1])
    for i in res_style:
        for j in res:
            if i[0] == j['name']:
                j['style'].append(i[1])
    for i in res_topic:
        for j in res:
            if i[0] == j['name']:
                j['topic'].append(i[1])
    print(res)
    res = [
        {
            'name': '0001.jpg',
            'src_path': 'static/bqbSource/0001.jpg',
            'score': 78.8,
            'description': 'it is a description',
            'role': ['熊猫头', '黄脸'],
            'emotion': ['开心', '愤怒'],
            'style': ['沙雕', '睿智'],
            'topic': ['怼人']
        },
        {
            'name': '0002.jpg',
            'src_path': 'static/bqbSource/0002.jpg',
            'score': 71.8,
            'description': 'it is a description',
            'role': ['熊猫头', '黄脸'],
            'emotion': ['开心', '愤怒'],
            'style': ['沙雕', '睿智'],
            'topic': ['怼人']
        },
        {
            'name': '0003.jpg',
            'src_path': 'static/bqbSource/0003.jpg',
            'score': 68.8,
            'description': 'it is a description',
            'role': ['熊猫头', '黄脸'],
            'emotion': ['开心', '愤怒'],
            'style': ['沙雕', '睿智'],
            'topic': ['怼人']
        }
    ]
    return res

#retrieve("漂亮宝贝")

def CNN_prepararation():
    # ======== cnn模块的准备工作 ========
    # Prepare data set.
    print(os.getcwd())
    data_loader = load_data(data_path='static/cnn_test/image_database/', batch_size=2, shuffle=False,
                            transform='default')
    print("===图片库加载完成===")
    # Prepare model.
    model = load_model(pretrained_model='main/retrieval/models/net_best.pth', use_gpu=True)
    print("===模型加载完成===")
    # Extract database features.
    gallery_feature, image_paths = extract_feature(model=model, dataloaders=data_loader)
    # print(gallery_feature)
    # 存储
    enc = gallery_feature.detach().cpu().numpy()
    np.savez("enc.npz", enc=enc)
    print("===图片库特征提取完成===")

def pic_retrieve():
    query_image = load_query_image('static/query/query.jpg')
    query_feature = extract_feature_query(model=model, img=query_image)
    similarity, image_index = sort_img(query_feature, gallery_feature)
    sorted_paths = [image_paths[i] for i in image_index]
    print(sorted_paths)
    tmb_images = [
        './static/cnn_test/image_database/' + os.path.split(sorted_path)[1] for
        sorted_path in sorted_paths]
    res_tmp = {
        'name': '0001.jpg',
        'src_path': 'static/bqbSource/0001.jpg',
        'score': 78.8,
        'description': 'it is a description',
        'role': ['熊猫头', '黄脸'],
        'emotion': ['开心', '愤怒'],
        'style': ['沙雕', '睿智'],
        'topic': ['怼人']
    }
    res = []
    for i in range(5):
        res_tmp['src_path'] = tmb_images[i]
        res.append(copy.deepcopy(res_tmp))
    return res


app = Flask(__name__)
# 下面是flask的路由部分


@app.route('/')
def root():
    # return redirect(url_for(index))
    return render_template('index.html')


@app.route('/index')
# 本来应该给这个函数命名为index的，但是上面已经用了index名字，暂时这样吧
def index():
    return render_template('index.html')


@app.route('/result', methods=['GET', 'POST'])
def result():
    files = request.files
    form = request.form
    # 接收到index页面的检索请求，带图片请求，调用图片检索
    if files:
        print("图片检索方式")
        query_image = files['query_img']
        query_image.save('static/query/query.jpg')
        print(query_image.filename)
        res = pic_retrieve()
        return render_template('search_result.html',
                               success=True,
                               query_mode=2,
                               query_info='query/query.jpg',
                               length=len(res),
                               data=res)
    # 接收到index页面的检索请求，没有图片的请求，返回文字检索的结果
    elif form.get("query_text"):
        print("文字检索方式")
        query_text = form.get("query_text")
        print(query_text)
        res = retrieve(query_text)
        return render_template('search_result.html',
                               success=True,
                               query_mode=1,
                               query_info=query_text,
                               length=len(res),
                               data=res)
    # 结果页面的展示，既没有图片也没有文字，返回空白的页面,这里目前是不返回图片
    else:
        print("屁都不是")
        return render_template('search_result.html',
                               success=True,
                               query_mode=0,
                               query_info='',
                               length=0)


if __name__ == '__main__':
    CNN_prepararation()
    #读取图片特征
    feat = np.load("enc.npz")
    # print(feat['enc'])
    gallery_feature = torch.tensor(feat)
    print(gallery_feature)
    app.run(debug=True, port=8080)
