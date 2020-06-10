from main.db import *
global res_description,res_role,res_emotion,res_style,res_topic


print("加载数据库")
# 连接数据库
db_cursor = connect_db("129.211.91.153", 3306, "isrbqb", 'admin', 'abcd')
# 查出所有的description,role,emotion,style,topic
global res_description, res_role, res_emotion, res_style, res_topic
res_description = consult_db(db_cursor, "bqb_description", "geng")
res_role = consult_db(db_cursor, "bqb_role", "role")
res_emotion = consult_db(db_cursor, "bqb_emotion", "emotion")
res_style = consult_db(db_cursor, "bqb_style", "style")
res_topic = consult_db(db_cursor, "bqb_context", "context")
db_cursor.close()
print("数据库加载完成")



