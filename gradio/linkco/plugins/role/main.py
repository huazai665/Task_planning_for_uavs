from ...main import *
from ..utils.utils_chat import get_cut_history
from ..utils.utils_prompt import get_select_chat

role_path = linkco_path + 'plugins/role/role_rule/'

def get_role_dict(role_list=[]):
    defult_rule = '【text】'
    if os.path.exists(role_path + '默认规则.txt'):
        with open(role_path + '默认规则.txt', 'r', encoding='utf-8') as f:
            defult_rule = f.read()
        f.close()
        if len(defult_rule) == 0:
            defult_rule = '【text】'

    temp_dict = {}
    role_file_list = os.listdir(role_path)
    for role_name in role_file_list:
        temp_role_name = role_name.replace('.txt', '')
        if temp_role_name != '默认规则':
            with open(role_path + role_name, 'r', encoding='utf-8') as f:
                temp_data = f.read()
            f.close()
            if len(role_list) > 0:
                if temp_role_name in role_list:
                    temp_dict[temp_role_name] = defult_rule.replace('【text】', temp_data)
            else:
                temp_dict[temp_role_name] = defult_rule.replace('【text】', temp_data)
    return temp_dict


# 选择角色
def get_switch_role(prompt, history=[], system='', role_dict_list=[], model_nickname=None):
    temp_history = get_cut_history(history, 64, 2)
    role_dict = get_role_dict(role_dict_list)
    example_data = {'领域': '聊天对话'}
    rule_list = ['只能选一个', '只输出【】中的内容']
    response = get_select_chat(prompt, temp_history, system, example_data, list(role_dict.keys()), rule_list, model_nickname)
    role_name = response["领域"]

    if role_name not in role_dict.keys():
        for it in role_dict.keys():
            if role_name[:2] in it:
                role_name = it
    if role_name not in role_dict.keys():
        role_name = '聊天对话'

    return role_dict[role_name]