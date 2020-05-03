# 表情包检索系统

信息存储与检索课程 检索项目实验

#### 主要工作分类

- 前端编写（2个人？）
- 后端编写（2个人？）
- 框架管理（前后端接口、数据库、测试）（1个人？）
- 算法和功能（1个人？）

使用python3 flask架构，可以算是MVC吧



# 项目结构（大概）

```
ISRproject/  <-- 根目录
|
+- conf/                 <-- 配置文件（比如数据库参数啥的）
|
+- dist/                 <-- 打包目录（部署的时候的事情）
|
+- www/                  <-- Web目录，存放.py文件
|  |
|  +- static/            <-- 存放静态文件（比如4000张表情包）
|  |
|  +- templates/         <-- 存放前端模板文件
```



# 前端编写

大约需要2人左右。总共两个页面，一个是检索入口页面，一个是结果展示页面。所谓的前端和UI还是不一样的，更多的工作其实还是写js来实现交互功能。

- 页面具体功能见线框图

#### 使用的技术

- `html/css/javascript`（JS部分可能需要使用jQuery等库，这个由前端同学来决定就行，独立的。）
- `python3 flask web架构中的 jinja2 模板` （html模板，供后端渲染数据）

#### 可能需要学习的知识

- `python jinja2 `的原理（本质上就是html，加上`控制结构 {% %}`，`变量取值 {{ }}`，`注释 {# #}`这几个用来更方便渲染、有助于前后端分离的功能性语句）

  - [这个教程](https://www.cnblogs.com/dachenzi/p/8242713.html)比较简洁

  - 最好还是全面了解一下[python的flask使用jinja模板的具体原理](https://www.liaoxuefeng.com/wiki/1016959663602400/1017806952856928)

#### 接口

主要需要跟后端交互的数据有

- 发给后端：检索式
- 发给后端：图片（可以用base64来传图片）

- 每个（检索到的）表情包的全套信息，以及相关系数的信息（用来排序）

用flask的话，前端模板的测试还是要用python来进行的，具体见上面的教程，核心的渲染就是这么一个flask的函数：

```python
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/query', methods=['POST']) # 这里是设置路由，意思就是说如果浏览器要访问/query这个网页，我就执行下面这个query函数
def query():
  query_str = request.form['query'] # 前端页面发送post请求时会带有一些参数
  query_mode = request.form['queryMode']
	return render_template('result.html', message='success', imageData=getResult(query)) # return就是请求返回的返回
```

##### 接口数据格式（暂定）

form['query'] `是前端的请求参数中的检索式，前端请求结构大概这样（用json表示）：

```json
{
    "queryMode":"",
    "query":"",
    "picContent":""
}
```

模板的返回数据用json来表示应该是这样

```json
{
    "message":"seccess",
    "imageData":[
        {
            "picId":"",
            "picName":"",
            "picType":"",
            "picRole":[

            ],
            "picStyle":[

            ],
            "picDescription":"",
            "rankValue":10
        }
    ]
}
```



# 后端编写（还不太完善）

大约需要2个人实现后端算法

后端太复杂了，flask我也还不熟悉，怎么架构还没确定，先把需要实现的功能梳理一下吧，领锅的人可以先独立地函数，前提是“后端1”要尽快完成

#### 后端0 编写web框架

可以让管理框架的人做一下，需要系统学一下flask



#### 后端1 和数据库交互（ORM框架）

- 用`sqlalchemy`来实现数据库关系和python类的映射关系，产生通用的数据库的接口，供所有后端使用



#### 后端2 切词

- 使用jieba等工具对检索式和图片实现切词功能
- 对切词结果进行评价，效果不好还需要手工修改



#### 后端3 标引

- 切词：同“后端2”
- 使用tf-idf处理切词结果



#### 后端4 词表

- 使用word2vec建立相关词表
- 扩充现有的词表



#### 后端5 处理检索式

- 去停用词
- 切词（见“后端2”）



#### 后端6 倒排档

- 建立倒排档
- 根据检索式去匹配倒排档



#### 后端7 以图搜图

这个部分比较独立，暂时不展开了，使用CNN，也要建数据表



#### 后端8 图文结合

算法还未确定



# 框架管理

### 前后端接口、测试

- 考虑接口规范
- 编写测试样例（上面的接口写的还很粗糙）
- 整理代码结构

### 数据库管理

- 考虑为倒排档、建表



# 算法和功能

主要是要考虑图文结合的问题
