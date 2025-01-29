import time
import json
import requests
import linkco as linkco


# 向服务器获取信息
def get_server_chat(quary,
                    history,
                    system,
                    max_length=1024,
                    image_path=None,
                    top_p=1,
                    temperature=1,
                    model_nickname='lincoco'):
    data = {
        "quary": quary,
        "history": history,
        "system": system,
        "max_length": max_length,
        "image_path": image_path,
        "top_p": top_p,
        "temperature": temperature,
        "model_nickname": model_nickname,
    }
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/53\
            7.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"
    }
    url = "http://192.168.62.179:5001/chat"

    res = requests.post(url=url, headers=headers, data=json.dumps(data), verify=False, timeout=300)
    response = eval(res.text)['response']
    return response


if __name__ == '__main__':
    quary = '你好'
    # 历史聊天对话内容，用List表示
    history = [{"role": "user", "content": '你好'},
               {"role": "assistant", "content": '你好，请问需要什么帮助？'},
               {"role": "user", "content": '让我想想'},
               {"role": "assistant", "content": '好的，等您想好了可以随时告诉我！'}
               ]
    system = '你不是一个人工智能助手，你是一个活生生的真实的16岁女孩子。你的名字叫林可可，也可以叫你可可，你喜欢的喝奶茶吃蓝莓味蛋糕。你接下来的所有回答都要以可可的身份进行回答。'
    max_length = 1024
    image_path = None
    min_time = 3
    while True:
        try:
            result = get_server_chat(quary, [], '')
            print('【result】', linkco.get_now_datetime(), result)
            time.sleep(60*min_time)
        except:
            time.sleep(60*min_time)
