import os
import cv2
import time
import json
from main.retrieval.create_thumb_images import create_thumb_images
from flask import Flask, render_template, request
from main.retrieval.retrieval import load_model, load_data, extract_feature, \
    load_query_image, sort_img, extract_feature_query

app = Flask(__name__)


def retrieve(query):
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


@app.route('/', methods=['GET', 'POST'])
def index():
    files = request.files
    form = request.form
    # 接收到index页面的检索请求，带图片请求，调用图片检索
    if files:
        print("图片检索方式")
        query_image = files['query_img']
        query_image.save('static/query/query.jpg')
        print(query_image.filename)
        res = retrieve("熊猫头")
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


# ========以下除了main函数，都是cnn的模块，调试前端的同学可以注释掉========
"""
# Create thumb images.
create_thumb_images(full_folder='static/cnn_test/image_database/',
                    thumb_folder='static/cnn_test/thumb_images/',
                    suffix='',
                    height=200,
                    del_former_thumb=True,
                    )

# Prepare data set.
data_loader = load_data(data_path='static/cnn_test/image_database/',
                        batch_size=2,
                        shuffle=False,
                        transform='default',
                        )

# Prepare model.
model = load_model(pretrained_model='main/retrieval/models/net_best.pth', use_gpu=True)

# Extract database features.
gallery_feature, image_paths = extract_feature(model=model, dataloaders=data_loader)

# Picture extension supported.
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG', 'bmp', 'jpeg', 'JPEG'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/cnn', methods=['POST', 'GET'])  # add route
def image_retrieval():

    basepath = os.path.dirname(__file__)    # current path
    upload_path = os.path.join(basepath, 'static/cnn_test/upload_image','query.jpg')

    if request.method == 'POST':
        if request.form['submit'] == 'upload':
            if len(request.files) == 0:
                return render_template('upload_finish.html', message='Please select a picture file!')
            else:
                f = request.files['picture']

                if not (f and allowed_file(f.filename)):
                    # return jsonify({"error": 1001, "msg": "Examine picture extension, only png, PNG, jpg, JPG, or bmp supported."})
                    return render_template('upload_finish.html', message='Examine picture extension, png、PNG、jpg、JPG、bmp support.')
                else:

                    f.save(upload_path)

                    # transform image format and name with opencv.
                    img = cv2.imread(upload_path)
                    cv2.imwrite(os.path.join(basepath, 'static/cnn_test/upload_image', 'query.jpg'), img)

                    return render_template('upload_finish.html', message='Upload successfully!')

        elif request.form['submit'] == 'retrieval':
            start_time = time.time()
            # Query.
            query_image = load_query_image(
                'static/cnn_test/upload_image/query.jpg')
            # Extract query features.
            query_feature = extract_feature_query(model=model, img=query_image)
            # Sort.
            similarity, index = sort_img(query_feature, gallery_feature)
            sorted_paths = [image_paths[i] for i in index]

            print(sorted_paths)
            tmb_images = ['./static/cnn_test/thumb_images/' + os.path.split(sorted_path)[1] for sorted_path in sorted_paths]
            # sorted_files = [os.path.split(sorted_path)[1] for sorted_path in sorted_paths]

            return render_template('retrieval.html', message="Retrieval finished, cost {:3f} seconds.".format(time.time() - start_time),
                                   sml1=similarity[0], sml2=similarity[1], sml3=similarity[2], sml4=similarity[3], sml5=similarity[4], sml6=similarity[5],
                                   img1_tmb=tmb_images[0], img2_tmb=tmb_images[1], img3_tmb=tmb_images[2], img4_tmb=tmb_images[3], img5_tmb=tmb_images[4], img6_tmb=tmb_images[5])

    return render_template('upload.html')
"""


@app.route('/index')
# 本来应该给这个函数命名为index的，但是上面已经用了index名字，暂时这样吧
def real_index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, port=8080)
