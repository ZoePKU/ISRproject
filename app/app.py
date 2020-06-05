# -*- coding: utf-8 -*
import os
from flask import Flask, render_template, request, redirect, session
from main.retrieval.cnn_utils import *
from text.utils import *
from main.db import *
from gensim import models


# 返回list
def sorted_dict_values(a_dict, reverse=False):
    lst = sorted(a_dict.items(), key=lambda item: item[1], reverse=reverse)
    # 先转换为lst，然后根据第二个元素排序
    return lst


def consult_db(db_session, table, field):
    sql_gen = "select name," + field + " from " + table
    cursor_gen = db_session.execute(sql_gen)
    res = cursor_gen.fetchall()  # 这是bqb描述
    return res


def text_retrieve(query):
    # 得到分词的列表
    cut_list = parse(query, thes_words, thes_dict, stop_words)
    # 读入倒排档json
    reverse_dict = input('text/reverse_index.json')
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
                Res[j] += reverse_dict[i[0]][j] * i[2]  # 这里应该还要乘以idf，暂时没有
            else:
                Res[j] = reverse_dict[i[0]][j] * i[2]

    res_list = sorted_dict_values(Res, True)
    return res_list


# 由一张图的序号获得这张图的所有信息的json
def pic_info(res_list):
    # 连接数据库
    db_session = connect_db("129.211.91.153:3306", "isrbqb", 'admin', 'abcd')
    # 查出所有的description,role,emotion,style,topic
    res_description = consult_db(db_session, "bqb_description", "geng")
    res_role = consult_db(db_session, "bqb_role", "role")
    res_emotion = consult_db(db_session, "bqb_emotion", "emotion")
    res_style = consult_db(db_session, "bqb_style", "style")
    res_topic = consult_db(db_session, "bqb_context", "context")
    # 生成匹配的Res
    res = [{'name': str("{:0>4}".format(str(i[0]))) + '.jpg',
            'src_path': 'static/bqbSource/' + str(
                "{:0>4}".format(str(i[0]))) + '.jpg',
            'score': i[1],
            'role': [],
            'emotion': [],
            'style': [],
            'topic': []
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
    return res


# 这里是单独的文字检索
def retrieve(query):
    res_list = text_retrieve(query)
    res = pic_info(res_list)
    return res


def pic_retrieve():
    tmb_images = cnn_retrieve('static/query/query.jpg')
    print(tmb_images)
    # static/cnn_test/image_database/0001.jpg'
    # res_list = [(i[0].split('/')[3].split('.')[0],i[1]) for i in tmb_images]
    res_list = tmb_images
    print(res_list)
    res = pic_info(res_list)
    return res


def mix_retrieve(query_text):
    tmb_images = cnn_text_retrieve('static/query/query.jpg', query_text)
    res = pic_info(tmb_images)
    return res


def in_filter(pic_item, filter_dict):
    """
    检查一个图片是否符合特征过滤器
    @param pic_item: 检查的图片（字典）
    @param filter_dict: 过滤器（字典）
    @return: 是否符合
    """
    feature_list = ['role', 'emotion', 'style', 'topic']
    feature_flag = {k: False for k in feature_list if
                    filter_dict[k]}  # 过滤器中存在项目的特征才检查
    for feature_item in feature_list:  # 依次查看每一个特征
        for feature in pic_item[feature_item]:
            if feature in filter_dict[feature_item]:
                feature_flag[feature_item] = True  # 只要有一个值是符合的，那么该特征检查通过
    # 所有特征都通过的才行
    for flag_item in feature_flag.values():
        if not flag_item:  # 有一个检查没通过就不行
            return False
    return True


def res_from_session(page=1, filter_dict={}):
    """
    从session读取上一次检索的结果，并使用过滤器进行筛选
    @param page: 查看第几页，每页20个
    @param filter_dict: 过滤器字典
    @return: 结果图片列表
    """
    tmp_res = [item_res for item_res in session['last_res']['data'] if
               in_filter(item_res, filter_dict)]
    tmp_res = tmp_res[(page - 1) * 20:page * 20]
    return tmp_res


def res_browse(page=1, filter_dict={}):
    """
    不检索情况下浏览
    @param page: 查看的页数
    @param filter_dict: 筛选器的字典
    @return:
    """
    all_pic_no_list = list(range(4000))
    all_pic_list = pic_info(all_pic_no_list)
    tmp_res = [item_res for item_res in all_pic_list if in_filter(item_res, filter_dict)]
    tmp_res = tmp_res[(page - 1) * 20:page * 20]
    return tmp_res


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)


# 下面是flask的路由部分
@app.route('/')
def root():
    return redirect('index')


@app.route('/index')
# 本来应该给这个函数命名为index的，但是上面已经用了index名字，暂时这样吧
def index():
    return render_template('index.html')


@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        files = request.files
        form = request.form
        query_mode_flag = 0
        if form.get("query_text"):
            query_mode_flag += 1
        if files and files['query_img'] and files['query_img'].filename:
            query_mode_flag += 2

        # 接收到index页面的检索请求，图文都有
        if query_mode_flag == 3:
            print("混合检索方式")
            query_text = form.get("query_text")
            res = mix_retrieve(query_text)
            session['last_res'] = {}
            session['last_res']['query_mode'] = 3
            session['last_res']['query_info'] = query/query.jpg
            session['last_res']['data'] = res
            return render_template('search_result.html',
                                   success=True,
                                   query_mode=3,
                                   query_info='query/query.jpg',
                                   length=len(res),
                                   data=res)

        # 接收到index页面的检索请求，带图片请求，调用图片检索
        elif query_mode_flag == 2:
            print("图片检索方式")
            query_image = files['query_img']
            query_image.save('static/query/query.jpg')
            print(query_image.filename)
            res = pic_retrieve()
            session['last_res'] = {}
            session['last_res']['query_mode'] = 2
            session['last_res']['query_info'] = 'query/query.jpg'
            session['last_res']['data'] = res
            return render_template('search_result.html',
                                   success=True,
                                   query_mode=2,
                                   query_info='query/query.jpg',
                                   length=len(res),
                                   data=res)
        # 接收到index页面的检索请求，没有图片的请求，返回文字检索的结果
        elif query_mode_flag == 1:
            print("文字检索方式")
            query_text = form.get("query_text")
            print(query_text)
            res = retrieve(query_text)
            session['last_res'] = {}
            session['last_res']['query_mode'] = 1
            session['last_res']['query_info'] = query_text
            session['last_res']['data'] = 1
            return render_template('search_result.html',
                                   success=True,
                                   query_mode=1,
                                   query_info=query_text,
                                   length=len(res),
                                   data=res)

    elif request.method == 'GET':
        get_type = request.args.get('get_type')
        if get_type == 'filter':
            print("筛选请求")
            filter_dict = request.args.get('filter')
            page = request.args.get('page')
            return render_template('search_result.html',
                                   success=True,
                                   query_mode=session['last_res']['query_mode'],
                                   query_info=session['last_res']['query_info'],
                                   page=page,
                                   data=res_from_session(page,
                                                         filter_dict=filter_dict))
        else:
            filter_dict = request.args.get('filter')
            page = request.args.get('page')
            print("浏览")
            session['last_status'] = 0
            session['last_res'] = {}
            return render_template('search_result.html',
                                   success=True,
                                   query_mode=0,
                                   query_info='',
                                   data=res_browse(page,
                                                   filter_dict=filter_dict),
                                   length=0)


# 生成词表
thes_words, thes_dict, stop_words = init_thes()
model = models.KeyedVectors.load_word2vec_format('word2vec_779845.bin',
                                                 binary=True)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
