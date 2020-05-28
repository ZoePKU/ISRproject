from flask import Flask, render_template, request, redirect
from main.retrieval.cnn_utils import cnn_retrieve
from text.utils import *
from main.db import *
import copy
from gensim import models

# 文字检索
def sorted_dict_values(a_dict, reverse=False):
    keys = list(a_dict.keys())
    keys.sort(reverse=reverse)
    return [(key, a_dict[key]) for key in keys]


def consult_db(session, table, field):
    sql_gen = "select name," + field + " from " + table
    cursor_gen = session.execute(sql_gen)
    res = cursor_gen.fetchall()  # 这是bqb描述
    return res

def text_retrieve(query):

    # 生成词表
    thes_words, thes_dict, stop_words = init_thes()
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
    model = models.KeyedVectors.load_word2vec_format('word2vec_779845.bin', binary=True)
    simi_res = [(x, y, model.cosine_similarities(x, y)) for x in thes_words if model.cosine_similarities(x, y) > 0.8 for
                y in cut_list]
    for i in simi_res:
        for j in reverse_dict[i[0]]:  # i[0]是x
            if j in Res:
                Res[j] += reverse_dict[i[0]][j] * i[2]  # 这里应该还要乘以idf，暂时没有
            else:
                Res[j] = reverse_dict[i[0]][j] * i[2]

    res_list = sorted_dict_values(Res)
    return res_list

# 由一张图的序号获得这张图的所有信息的json
def pic_info(res_list):
    # 连接数据库
    session = connect_db("129.211.91.153:3306", "isrbqb", 'admin', 'abcd')
    # 查出所有的description,role,emotion,style,topic
    res_description = consult_db(session, "bqb_description", "geng")
    res_role = consult_db(session, "bqb_role", "role")
    res_emotion = consult_db(session, "bqb_emotion", "emotion")
    res_style = consult_db(session, "bqb_style", "style")
    res_topic = consult_db(session, "bqb_context", "context")
    # 生成匹配的Res
    res = [{'name': i[0] + '.jpg',
            'src_path': 'static/bqbSource/' + i[0] + '.jpg',
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


def mix_retrieve(query_text):
    tmb_images = cnn_retrieve('static/query/query.jpg',query_text)
    res = pic_info(tmb_images)
    return res


app = Flask(__name__)


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
    app.run(debug=True, port=8080)
