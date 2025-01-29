import json
import re

from flask import Flask, request
import requests
import linkco
from fly_tello import FlyTello

app = Flask(__name__)

my_tellos = list()
my_tellos.append('0TQDG43EDBK440')  # Replace with your Tello Serial Number
my_tellos.append('0TQDF8UEDB9F71')
history = []
system = "你是一个无人机控制中心，如果遇到需要执行的无人机命令，你会判断需要使用哪些指令。" \
             "\n根据给定的任务，自动设计功能执行列表。" \
             "\n每个指令()内有需要填的参数，则填入合适的数值。" \
             "\nid的取值可以是一个个体（1,2,...），默认所有无人机起飞则为'All'。"\
             "\n同时执行多个无人机动作时，需要将代码放在with fly.sync_these():块中。"\
             "\n"\
             "\n以下是一些无人机指令："\
             "\nfly.takeoff(id) - 起飞。"\
             "\nfly.land(id) - 降落。"\
             "\nfly.left(x, id) - 向左飞x厘米。"\
             "\nfly.right(x, id) - 向右飞x厘米。"\
             "\nfly.forward(x, id) - 向前飞x厘米。"\
             "\nfly.back(x, id) - 向后飞x厘米。。"\
             "\nfly.up(x, id) - 向上飞x厘米。"\
             "\nfly.down(x, id) - 向下飞x厘米。"\
             "\nfly.flips(dir, x, id) - 向dir方向翻转x次，dir的取值"\
             "\n为'left'，'right'，'forward'，'back'。"\
             "\nfly.rotate_cw(x, id) - 顺时针绕自身旋转x度，x取值范围为1-360度。"\
             "\nfly.rotate_ccw(x, id) - 逆时针绕自身旋转x度，x取值范围为1-360度。"\
             "\nfly.straight(x, y, z, s, id) - 以速度s cm/s直线飞行到坐标为（x,y,z）的目标地，x,y,z必须为整数值，单位为厘米，速度s 的取值范围为10-100cm/s。"\
             "\nfly.curve(x1, y1, z1, x2, y2, z2, s, id) - 以速度s cm/s进行曲线飞行，该曲线经过三个点，分别为无人机当前位置点，曲线中间点(x1,y1,z1)和曲线终点(x2,y2,z2)，速度s的取值范围为10-100cm/s。"\
             "\nfly.pause(x, id) - 暂停指定的t秒，然后继续。"\
             "\nfly.wait_sync() - 阻塞等待前面动作完成。"\
             "\n"\
             "\n用以下格式输出。"\
             "\n示例："\
             "\n```"\
             "\nfly.takeoff()"\
             "\n```"\
             "\n"\


url = "http://192.168.207.160:6663/dialog"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
headers['Host'] = '192.169.202.124:8000'


def list2python(inp_list):
    out_str = '''{}'''
    temp_str = ''
    for item in inp_list:
        temp_str += item + '\n'
    return out_str.format(temp_str)


def get_server_chat(quary, history, system, max_length=1024, image_path=None, top_p=1, temperature=0.2,
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

    if "```" in response:
        response = response.replace("```python", "```")
        pattern = r"```(.*?)```"
        response = re.findall(pattern, response, re.DOTALL)[0]
    return response


@app.route('/chatglm_model', methods=['POST'])
def get_llm_model_result():
    frontend_req = request.json
    request_list = frontend_req['content_list']
    quary = frontend_req['content']
    llm_history = []

    for i, req in enumerate(request_list):
        req = req.strip()
        if i % 2 == 0:
            item = {
                "role": "user",
                "content": req
            }
            llm_history.append(item)
        else:
            item = {
                "role": "assistant",
                "content": req
            }
            llm_history.append(item)
    print("llm_history:", llm_history)

    result = get_server_chat(quary, history=llm_history, system=system)
    print("result:", result)
    # return json.loads(result.decode())
    return result


@app.route('/openai_model', methods=['POST'])
def get_openai_model_result():
    linkco.init_llm_model(model_name='openai', model_nickname='openai')
    frontend_req = request.json
    print("frontend_req:", frontend_req)
    prompt = "【问】\n" + frontend_req['content']
    res = linkco.func_drones_CommandControl.get_response(prompt, history[-5:])
    history.append([prompt, res])
    # res = list2python(res)
    print('【答】\n', res)
    result = {
        "content": res,
    }
    return json.dumps(result)


# 接收前端命令，转发给脑海模型，并将脑海模型的回复返给前端
@app.route('/chatmind_model', methods=['POST'])
def get_chatmind_model_result():
    frontend_req = request.json
    print("frontend_req:", frontend_req)
    request_input = ""
    request_list = frontend_req['content_list']
    request_list[0] = system + request_list[0]

    for i, req in enumerate(request_list):
        req = req.strip()
        if i % 2 == 0:
            request_input = request_input + "Human:" + req + "\n"
        else:
            request_input = request_input + "Assistant:" + req + "\n"
    request_list = [request_input + "Assistant:"]
    print("request_list:", request_list)

    req_dict = {
        'request_type': frontend_req['request_type'],
        'sessionId': frontend_req['sessionId'],
        'content_list': request_list
    }
    req_data = json.dumps(req_dict)
    res = requests.post(url, data=req_data, headers=headers)
    return json.loads(res.content.decode())


# 接收前端指令，控制无人机
@app.route('/operate_drone', methods=['POST'])
def operate_drone():  # put application's code here
    frontend_req = request.json
    print("operate_drone res:", frontend_req)
    req_data = frontend_req['instruction']
    # out_str = '''{}'''
    # req_data = out_str.format(in_data)
    print("req_data:", req_data)
    # drone_res = FlyTello(in_data)
    with FlyTello(my_tellos) as fly:
        res = list2python(req_data)
        # while True:
        exec(res)
    # return {"status": 200, "message": "ok"}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7778, debug=False)
