import os
import json
from functools import cmp_to_key
from db_init import res_role, res_emotion, res_style, res_topic, res_description


def cmp(i, j):
    return i['score'] < j['score']


def pic_info(res_list):
    """
    由一张图的序号获得这张图的所有信息的json
    @param res_list: 数字列表
    @return: 结果列表
    """
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
    # i是一个tuple("0001.jpg")  res_list也是一个tuple(“1”,score)
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

    # 排序
    res.sort(key=cmp_to_key(cmp))
    print(res)
    return res


def in_filter(pic_item, filter_dict):
    """
    检查一个图片是否符合特征过滤器
    @param pic_item: 检查的图片（字典）
    @param filter_dict: 过滤器（字典）
    @return: 是否符合
    """
    feature_list = ['role', 'emotion', 'style', 'topic']
    feature_flag = {k: False for k in feature_list if k in filter_dict}  # 过滤器中存在项目的特征才检查
    for feature_item in feature_flag:  # 依次查看每一个特征
        for feature in pic_item[feature_item]:
            if feature in filter_dict[feature_item]:
                feature_flag[feature_item] = True  # 只要有一个值是符合的，那么该特征检查通过
    # 所有特征都通过的才行
    for flag_item in feature_flag.values():
        if not flag_item:  # 有一个检查没通过就不行
            return False
    return True


# 返回list
def sorted_dict_values(a_dict, reverse=False):
    lst = sorted(a_dict.items(), key=lambda item: item[1], reverse=reverse)
    # 先转换为lst，然后根据第二个元素排序
    return lst


class CacheHandle(object):
    def __init__(self, sid):
        self.sid = sid
        self.filepath = 'cache/' + self.sid + '.json'
        if os.path.exists(self.filepath):
            self.data = f = open(self.filepath, encoding="utf-8")
            self.data = json.load(f, encoding="utf-8")
            f.close()
        else:
            self.data = {}

    def save_data(self):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)
