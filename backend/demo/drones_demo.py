# -*- coding: utf-8 -*-
import linkco
import time

# 基于网络搜索的新闻生成demo，只要输入一个标题即可
if __name__ == '__main__':
    # 初始化使用的大模型

    print('【脑海 RobotMind7B-0.1】初始化...')
    linkco.init_llm_model('mind7b')

    history = []
    # 加载功能
    while True:
        prompt = input('【问】\n')
        while True:
            try:
                res = linkco.func_drones_CommandControl.get_response(prompt, history)
                # res = eval()
                # 这里做数据处理

                break
            except Exception as e:
                time.sleep(3)
                print(e)

        history.append({'role': 'user', 'content': prompt})
        history.append({'role': 'assistant', 'content': res})

        # 进行无人机执行命令

        print('【答】\n', res)

    # 请起飞，右翻1次，右飞20cm，左翻3次，左飞20cm，前翻1次，前飞20cm，后翻1次，后飞20cm，再降落。
