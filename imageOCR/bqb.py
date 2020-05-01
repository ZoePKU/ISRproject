# 表情包class，具有存储一个表情包基本信息，控制修改等功能

class bqb:
    def __init__(self, _id=1):
        # 编号
        self.bqbId = _id
        #
        self.name = get_name(self.id)
        # 角色
        self.role = []
        # 主题
        self.topic = []
        # 风格
        self.style = []
        # 描述
        self.description = ''


def get_name(_id):
    return _id +
