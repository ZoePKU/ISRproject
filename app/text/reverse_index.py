import jieba
import openpyxl
from collections import Counter
import json

def parse(dict):
    cut_dict = {}
    for id in dict:
        if dict[id]:
            cut_list = jieba.lcut(dict[id])
            new_cut_list = []
            for i in range(len(cut_list)):
                word = cut_list[i]
                if word in thes_words:
                    word = thes_dict[word]
                if word not in stop_words:
                    new_cut_list.append(word)
            cut_dict[id] = new_cut_list
        else:
            cut_dict[id] = ""
    return cut_dict

def revert(cut_dict):
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
        idf = 1     #待定
        for id in cut_dict:
            if word in cut_dict[id]:
                temp[id] = tf * idf
        reverse_index[word] = temp
    return reverse_index

if __name__ == '__main__':
    #读取同义词表
    thes = openpyxl.load_workbook('thesaurus.xlsx')['replace']
    thes_dict = {}
    for i in range(640):
        formal = thes.cell(row=i+1, column=1).value
        informal = thes.cell(row=i+1, column=2).value
        if informal:
            informal_list = informal.split(';')
            for word in informal_list:
                thes_dict[word] = formal
    thes_words = set(thes_dict.keys())
    print("完成读取同义词表")

    #读取停用词表
    stop_words = set()
    with open('stop_words.txt', 'r', encoding='UTF-8') as f:
        for line in f.readlines():
            stop_words.add(line.rstrip('\n'))
    stop_words.update([' ', '\n'])
    print("完成读取停用词表")

    #读取图片描述
    des = openpyxl.load_workbook('bqb_description.xlsx')['bqb_description']
    des_dict = {}
    for i in range(4000):
        id = des.cell(row=i+1, column=1).value
        description = des.cell(row=i+1, column=2).value
        des_dict[id] = description
    print("完成读取图片描述")

    #分词
    cut_dict = parse(des_dict)
    print("完成分词")

    #建倒排索引
    reverse_index = revert(cut_dict)
    print("完成建立倒排档")

    #输出到文件
    index_json = json.dumps(reverse_index, sort_keys=True, ensure_ascii=False, indent=4)
    with open('reverse_index.json', 'w') as f:
        json.dump(index_json, f)
        print("输出完毕")

