from ...plugins import *

# 获取回答
def get_response(prompt, history=[], system='', image_path=None):
    tool_list = ['天气搜索', '聊天对话']
    tools = get_switch_tool(prompt, history, system, tool_dict_list=tool_list)
    print('【工具】')
    tool_result = ''
    for tool in tools:
        print(tool['name'])
        temp_result = tool['module'].get_response(prompt, history, system)
        if len(temp_result) > 0:
            tool_result += '{}:\n{}\n'.format(tool['name'], temp_result)

    role_system = get_switch_role(prompt, history, system)
    print('【身份】\n', role_system)

    if len(tool_result) > 0:
        quary = '{}\n请结合上述内容回答：{}'.format(tool_result, prompt)
    else:
        quary = prompt

    print('【问题】\n', quary)
    result = get_chat(quary, history, system + '\n' + role_system, image_path, temperature=0.9, top_p=0.9)
    if len(result) < 2:
        result = get_chat(prompt, history, system + '\n' + role_system, image_path, temperature=0.9, top_p=0.9)
    print('【回答】\n', result)
    return result