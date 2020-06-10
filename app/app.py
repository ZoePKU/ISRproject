# -*- coding: utf-8 -*
import os
import numpy
from base64 import b64encode
from flask import Flask, render_template, request, redirect, make_response
from main.cnn_retrieval.cnn_utils import *
from main.text_retrieval.retrieval import *
from main.utils import pic_info, in_filter, CacheHandle
from db_init import *




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
    print(tmb_images)
    res = pic_info(tmb_images)
    return res


def res_from_session(handle, page=1, filter_dict={}):
    """
    从session读取上一次检索的结果，并使用过滤器进行筛选
    @param page: 查看第几页，每页20个
    @param filter_dict: 过滤器字典
    @return: 结果图片列表
    """
    tmp_res = [item_res for item_res in handle.data['last_res']['data'] if in_filter(item_res, filter_dict)]
    total_len = len(tmp_res)
    tmp_res = tmp_res[(page - 1) * 20:page * 20]
    return tmp_res, total_len


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
    total_len = len(tmp_res)
    tmp_res = tmp_res[(page - 1) * 20:page * 20]
    return tmp_res, total_len


def page_filter(res, page=1):
    """
    筛选页数
    @param res: 待筛选的查询结果的列表
    @param page: 待筛选的页数
    @return:
    """
    if len(res) > 20:
        tmp_res = res[(page - 1) * 20:page * 20]
    else:
        tmp_res = res
    return tmp_res


app = Flask(__name__)
app.config['SECRET_KEY'] = 'A0Zr98j/3yXR~XHH!jmN]LWX/,?RT'


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
    flag_first = False
    resp = None
    if 'sid' in request.cookies:
        sid = request.cookies['sid']
    else:
        flag_first = True
        sid = b64encode(os.urandom(24)).decode('utf-8')
        sid = ''.join(list(filter(str.isalnum, sid)))
    cache_handle = CacheHandle(sid)

    if request.method == 'POST':
        files = request.files
        form = request.form
        query_mode_flag = 0
        resp = None
        if form.get("query_text"):
            query_mode_flag += 1
        if files and files['query_img'] and files['query_img'].filename:
            query_mode_flag += 2

        # 接收到index页面的检索请求，图文都有
        if query_mode_flag == 3:
            print("混合检索方式")
            query_text = form.get("query_text")
            print("检索词为：" + query_text)
            res = mix_retrieve(query_text)
            total_length = len(res)
            part_res = page_filter(res)
            cache_handle.data['last_res'] = {}
            cache_handle.data['last_res']['query_mode'] = 3
            cache_handle.data['last_res']['query_info'] = {'query_text':query_text,'query_pic':'query/query.jpg'}
            cache_handle.data['last_res']['total_length'] = total_length
            cache_handle.data['last_res']['data'] = res
            cache_handle.save_data()
            resp = make_response(render_template('search_result.html',
                                                 success=True,
                                                 request_type='search',
                                                 query_mode=3,
                                                 query_info={'query_text':query_text,'query_pic':'query/query.jpg'},
                                                 total_length=total_length,
                                                 length=len(part_res),
                                                 page=1,
                                                 data=part_res))

        # 接收到index页面的检索请求，带图片请求，调用图片检索
        elif query_mode_flag == 2:
            print("图片检索方式")
            query_image = files['query_img']
            query_image.save('static/query/query.jpg')
            print(query_image.filename)
            res = pic_retrieve()
            total_length = len(res)
            part_res = page_filter(res)
            cache_handle.data['last_res'] = {}
            cache_handle.data['last_res']['query_mode'] = 2
            cache_handle.data['last_res']['query_info'] = {'query_pic':'query/query.jpg'}
            cache_handle.data['last_res']['total_length'] = total_length
            cache_handle.data['last_res']['data'] = res
            cache_handle.save_data()
            resp = make_response(render_template('search_result.html',
                                                 success=True,
                                                 request_type='search',
                                                 query_mode=2,
                                                 query_info={'query_pic': 'query/query.jpg'},
                                                 total_length=total_length,
                                                 length=len(part_res),
                                                 page=1,
                                                 data=part_res))

        # 接收到index页面的检索请求，没有图片的请求，返回文字检索的结果
        elif query_mode_flag == 1:
            print("文字检索")
            query_text = form.get("query_text")
            print("检索词为：" + query_text)
            res = retrieve(query_text)
            total_length = len(res)
            part_res = page_filter(res)
            cache_handle.data['last_res'] = {}
            cache_handle.data['last_res']['query_mode'] = 1
            cache_handle.data['last_res']['query_info'] = {'query_text':query_text}
            cache_handle.data['last_res']['total_length'] = total_length
            cache_handle.data['last_res']['data'] = res
            cache_handle.save_data()
            resp = make_response(render_template('search_result.html',
                                                 success=True,
                                                 request_type='search',
                                                 query_mode=1,
                                                 query_info={'query_text':query_text},
                                                 total_length=total_length,
                                                 page=1,
                                                 length=len(part_res),
                                                 data=part_res))

    elif request.method == 'GET':
        get_mode = request.args.get('get_mode')
        if get_mode == 'filter':
            print("筛选请求")
            filter_dict = {}
            filter_dict_str = request.args.get('filter')
            if filter_dict_str:
                filter_dict = eval(filter_dict_str)
            page = eval(request.args.get('page'))
            res, total_len = res_from_session(cache_handle, page, filter_dict=filter_dict)
            resp = make_response(render_template('search_result.html',
                                                 success=True,
                                                 request_type='filter',
                                                 query_mode=cache_handle.data['last_res']['query_mode'],
                                                 query_info=cache_handle.data['last_res']['query_info'],
                                                 total_length=total_len,
                                                 page=page,
                                                 filter_dict=filter_dict,
                                                 length=len(res),
                                                 data=res))

        elif get_mode == 'browse':
            filter_dict = eval(request.args.get('filter'))
            page = eval(request.args.get('page'))
            print("浏览")
            cache_handle.data['last_status'] = 0
            cache_handle.data['last_res'] = {}
            res, total_len = res_browse(page, filter_dict=filter_dict)
            resp = make_response(render_template('search_result.html',
                                                 success=True,
                                                 request_type='browse',
                                                 query_mode=-1,
                                                 query_info='',
                                                 total_length=total_len,
                                                 length=len(res),
                                                 page=page,
                                                 filter_dict=filter_dict,
                                                 data=res))
        else:
            print("啥都不干")
            resp = make_response(render_template('search_result.html',
                                                 success=True,
                                                 query_mode=0,
                                                 query_info='',
                                                 total_length=0,
                                                 page=-1,
                                                 data={},
                                                 length=0))

    if flag_first:
        resp.set_cookie("sid", value=sid)
    return resp


# 用于查看前端
@app.route('/debug')
def debug():
    return render_template('search_result.html',
                           success=True,
                           request_type='filter',
                           query_mode=1,
                           query_info='开心',
                           total_length=100,
                           page=1,
                           filter_dict={
                               'role': ['熊猫头'],
                               'emotion': ['开心']
                           },
                           length=3,
                           data=[
                               {
                                   "name": "2280.jpg",
                                   "src_path": "static/bqbSource/2280.jpg",
                                   "score": 0.014422482809179831,
                                   "role": [
                                       "女孩"
                                   ],
                                   "emotion": [],
                                   "style": [
                                       "丧",
                                       "可爱",
                                       "真人"
                                   ],
                                   "topic": [
                                       "自恋"
                                   ],
                                   "description": "我超开心的 追我的人超多 我好幸福 吃了好多零食 我好棒 一点也没长胖呢 这个世界真美好 新的一天新的快乐 我超有钱 工作真的好轻松 我从来不用考虑下一顿吃啥 喜欢的东西随便买 笑容洋溢在我脸上 我从来不会感觉到生无可恋"
                               },
                               {
                                   "name": "0450.jpg",
                                   "src_path": "static/bqbSource/0450.jpg",
                                   "score": 0.012038112280989733,
                                   "role": [
                                       "猫"
                                   ],
                                   "emotion": [
                                       "悲伤"
                                   ],
                                   "style": [
                                       "丧"
                                   ],
                                   "topic": [],
                                   "description": "我真没哭 Im fine happy 我没说 真的快乐 我很好 满脸都是开心 我哭一个月就好"
                               },
                               {
                                   "name": "3609.jpg",
                                   "src_path": "static/bqbSource/3609.jpg",
                                   "score": 0.005985294902678634,
                                   "role": [
                                       "柯基",
                                       "狗"
                                   ],
                                   "emotion": [
                                       "快乐"
                                   ],
                                   "style": [
                                       "可爱"
                                   ],
                                   "topic": [],
                                   "description": "悠闲 开心 自得 "
                               }
                           ])


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')

