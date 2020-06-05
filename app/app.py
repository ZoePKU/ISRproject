# -*- coding: utf-8 -*
import os
from flask import Flask, render_template, request, redirect, session
from main.cnn_retrieval.cnn_utils import *
from main.text_retrieval.retrieval import *
from main.utils import pic_info, in_filter


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
            session['last_res']['query_info'] = 'query/query.jpg'
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
            print("检索词为：" + query_text)
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
        elif get_type == 'filter':
            filter_dict = request.args.get('filter')
            page = request.args.get('page')
            print("浏览")
            session['last_status'] = 0
            session['last_res'] = {}
            return render_template('search_result.html',
                                   success=True,
                                   query_mode=0,
                                   query_info='',
                                   data=res_browse(page, filter_dict=filter_dict),
                                   length=0)
        else:
            return render_template('search_result.html',
                                          success=True,
                                          query_mode=0,
                                          query_info='',
                                          data={},
                                          length=0)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
