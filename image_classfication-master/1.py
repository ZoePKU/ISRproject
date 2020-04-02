import re
import os.path,shutil


if __name__ == '__main__':
    #num = 0
    path = "E:\\大二下\\python\\image_classfication-master"
    path2 = "C:/Users/Thinkpad/Documents/WeChat Files/wxid_3gcbtvbyhtcy22/FileStorage/File/2020-03/表情包/new_class"
    l = []
    for foldName, subfolders, filenames in os.walk(path):  # 用os.walk方法取得path路径下的文件夹路径，子文件夹名，所有文件名
        num = 0
        for filename in filenames:  # 遍历列表下的所有文件名
            if filename.endswith('.jpg'):  # 当文件名以.jpg后缀结尾时
                l.append(filename)


    #old_names = os.listdir(path)  # 取路径下的文件名，生成列表
    #for old_name in old_names:  # 遍历列表下的文件名
    #    if old_name != sys.argv[0]:  # 代码本身文件路径，防止脚本文件放在path路径下时，被一起重命名
     #       os.rename(os.path.join(path, old_name), os.path.join(path, mark + old_name))  # 子文件夹重命名
      #      print(old_name, "has been renamed successfully! New name is: ", mark + old_name)
