import linkco
from fly_tello import FlyTello




my_tellos = list()
my_tellos.append('0TQDG43EDBK440')  # Replace with your Tello Serial Number
my_tellos.append('0TQDF8UEDB9F71')

def list2python(inp_list):
    out_str = '''{}'''
    temp_str = ''
    for item in inp_list:
        temp_str += item + '\n'
    return out_str.format(temp_str)

# 基于网络搜索的新闻生成demo，只要输入一个标题即可
if __name__ == '__main__':
    # 初始化使用的大模型
    # print('【脑海 RobotMind7B-0.1】初始化...')
    # linkco.init_llm_model(model_name='mind7b', model_nickname='mind7b')

    print('【chatgpt 3.5】初始化...')
    linkco.init_llm_model(model_name='openai', model_nickname='openai')

    # 构建测试数据集
    history = []
    system = "You are an assistant helping me with the Tello simulator for drones." \
             "\nWhen I ask you to do something, you are supposed to give me Python code that is needed to achieve that task using Tello and then an explanation of what that code does." \
             "\nYou are only allowed to use the functions I have defined for you." \
             "\nYou are not to use any other hypothetical functions that you think might exist." \
             "\nYou can use simple Python functions from libraries such as math and numpy."

    # print(f"Initializing Tello...")请起飞，右翻1次，右飞40cm，左翻1次，左飞40cm，前翻1次，后翻1次，再降落
    # aw = TelloWrapper()
    # print(f"Done.")

    # 加载功能
    while True:
        prompt = input('【问】\n')
        res = linkco.func_drones_CommandControl.get_response(prompt, history[-5:], system)
        history.append([prompt, '\n'.join(res)])
        res = list2python(res)
        print('【答】\n', res)
        if res is not None:
            print('正在启动无人机...')
            with FlyTello(my_tellos) as fly:
                
                exec(res)
            print('完成')



    # 请起飞，右翻1次，右飞20cm，左翻1次，左飞20cm，前翻1次，前飞20cm，后翻1次，后飞20cm，再降落。