from collections import Counter
from main.text_retrieval.utils import *
import math
from main.utils import *

def description_parse(dict,thes_words,thes_dict, stop_words):
    cut_dict = {}
    for id in dict:
        if dict[id]:
            cut_dict[id] = parse(dict[id],thes_words,thes_dict,stop_words)
        else:
            cut_dict[id] = ""
    return cut_dict


def cal_idf(cut_dict):
    # print(cut_dict)
    # id:切词list
    idf = dict()
    N = len(cut_dict)
    # 计算每个词的idf
    for i in cut_dict:
        for j in cut_dict[i]:
            #print(j)
            if j in idf:
                idf[j] += 1
            else:
                idf[j] = 1
    for i in idf:
        idf[i] = math.log(N/idf[i], 10)
    # print("idf", idf)
    return idf


def revert(cut_dict):
    idf = cal_idf(cut_dict)
    reverse_index = {}
    all_words = Counter()
    words_num = 0
    for id in cut_dict:
        words_num += len(cut_dict[id])
        all_words.update(cut_dict[id])
    set_all_words = set(all_words.elements())
    for word in set_all_words:
        temp = {}
        tf = all_words[word] / words_num
        for id in cut_dict:
            if word in cut_dict[id]:
                temp[id] = tf * idf[word] if word in idf else 0.1
        reverse_index[word] = temp
    return reverse_index


if __name__ == '__main__':

    # 生成词表
    thes_words, thes_dict, stop_words = init_thes()

    # 读取图片描述
    des = openpyxl.load_workbook('main/text_retrieval/bqb_description.xlsx')['bqb_description']
    des_dict = {}
    ban_lst = ['0228', '0230', '0372', '0405', '0510', '0574', '0641', '0678', '0762', '0809', '0817', '0838', '0854', '0911', '0932', '0936', '0955', '0993', '1088', '1089', '1156', '1166', '1179', '1190', '1221', '1295', '1386', '1407', '1419', '1426', '1468', '1482', '1484', '1486', '1581', '1598', '1633', '1639', '1641', '1651', '1666', '1711', '1753', '1762', '1765', '1781', '1808', '1834', '1838', '1856', '1885', '1913', '1919', '1936', '1954', '1976', '1997', '2019', '2031', '2032', '2067', '2077', '2114', '2144', '2152', '2163', '2180', '2205', '2224', '2232', '2260', '2277', '2294', '2296', '2335', '2342', '2382', '2384', '2396', '2404', '2407', '2415', '2426', '2446', '2474', '2479', '2501', '2505', '2506', '2516', '2521', '2545', '2556', '2557', '2563', '2564', '2578', '2600', '2636', '2639', '2641', '2660', '2667', '2677', '2678', '2684', '2686', '2704', '2739', '2747', '2766', '2779', '2781', '2795', '2805', '2819', '2821', '2865', '2887', '2896', '2897', '2911', '2934', '2976', '2991', '3015', '3046', '3054',  '3060', '3061', '3066', '3075', '3095', '3098', '3099', '3102', '3124', '3125', '3141', '3161', '3166', '3167', '3193', '3202', '3216', '3219', '3241', '3250', '3266', '3268', '3269', '3273', '3316', '3320', '3322', '3326', '3327', '3328', '3345', '3354', '3360', '3365', '3381', '3402', '3409', '3420', '3434', '3440', '3454', '3457', '3458', '3460', '3470', '3478', '3492', '3496', '3511', '3520', '3536', '3537', '3553', '3595', '3613', '3621', '3626', '3629', '3634', '3638', '3640', '3642', '3644', '3651', '3653', '3658', '3663', '3674', '3702', '3710', '3711', '3713', '3723', '3725', '3727', '3738', '3740', '3745', '3754', '3764', '3773', '3777', '3784', '3786', '3787', '3806', '3812', '3814', '3853', '3862', '3874', '3911', '3921', '3926', '3928', '3930', '3939', '3940', '3945', '3951', '3954', '3974', '3984', '3993', '3996', '3998']
    # print(len(ban_lst))
    for i in range(4000):
        '''
        这段不知道为啥没用
        if "{:0>4}".format(str(i+1)) in ban_lst:
            print(str(i + 1))
            continue
        '''
        id = des.cell(row=i + 1, column=1).value
        if "{:0>4}".format(id) in ban_lst:
            print(id)
            continue
        description = des.cell(row=i + 1, column=2).value
        des_dict[id] = description
    print("完成读取图片描述")
    # print(3440, des_dict['3440'])
    # print(len(des_dict))
    #分词
    cut_dict = description_parse(des_dict,thes_words,thes_dict,stop_words)
    print("完成分词")
    print(cut_dict)
    # 把其他字段加入检索式
    res_lst = [(i,0) for i in cut_dict]
    res = pic_info(res_lst)
    num = 0
    for i in cut_dict:
        if i not in ban_lst:
            if cut_dict[i] == "":
                cut_dict[i] = list()
            cut_dict[i].append(res[num]['role'])
            cut_dict[i].append(res[num]['emotion'])
            cut_dict[i].append(res[num]['style'])
            cut_dict[i].append(res[num]['topic'])
            num += 1
    # 建倒排索引
    reverse_index = revert(cut_dict)
    print("完成建立倒排档")

    # index_json = json.dumps(reverse_index, sort_keys=True, ensure_ascii=False, indent=4)
    # 输出到文件
    output('main/text_retrieval/reverse_index.json', reverse_index)
    load_dict = json_input('main/text_retrieval/reverse_index.json')
    # print(load_dict)
