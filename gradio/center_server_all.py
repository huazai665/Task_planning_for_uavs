import linkco as linkco
import time
import os
import random
import gradio as gr
import mdtex2html
import threading
import json
import asyncio
import traceback
# import wenetruntime as wenet
from transformers import pipeline

p = pipeline("automatic-speech-recognition", model="facebook/wav2vec2-base-960h")
p = pipeline("automatic-speech-recognition")
def transcribe(audio, state=""):
    print(audio)
    time.sleep(2)
    text = p(audio)["text"]
    state += text + " "
    print("state:", state)
    return state, state

from fastapi import FastAPI, Request
import uvicorn

lock = threading.Lock()

# ip = '192.168.62.179'
ip = '127.0.0.1'

# 与底层大模型交互的端口，微信机器人用到的/chat  /voice就是这个端口
llm_server = 5001

# 网页端聊天服务
chat_server = 5002

# 数据标注服务
data_server = 5003

# 管理员界面
admin_server = 5004

top_p = 0.9

temperature = 0.95

app = FastAPI()

db_name = 'news_db'
with open('linkco/function/drones/command.txt', 'r', encoding='utf-8') as f:
    drones_system = f.read()
f.close()
system_role = linkco.tool_chat_role.get_role_dict()

data_count_limit = 1




# 底层模型调用接口部分
def get_chat(quary,
             history,
             system,
             max_length,
             image_path,
             top_p,
             temperature,
             model_nickname):
    response = linkco.get_chat(quary,
                               history,
                               system,
                               max_length=max_length,
                               image_path=image_path,
                               top_p=top_p,
                               temperature=temperature,
                               model_nickname=model_nickname)
    return response


@app.post("/chat")
async def create_item(request: Request):
    json_post_raw = await request.json()
    json_post = json.dumps(json_post_raw)
    json_post_list = json.loads(json_post)
    quary = json_post_list.get('quary')
    history = json_post_list.get('history')
    system = json_post_list.get('system')
    max_length = json_post_list.get('max_length')
    top_p = json_post_list.get('top_p')
    temperature = json_post_list.get('temperature')
    image_path = json_post_list.get('image_path')
    model_nickname = json_post_list.get('model_nickname')
    print(model_nickname)
    response = ''
    print('【问】\n{}'.format(quary))
    count = 5
    while count > 0:
        try:
            response = get_chat(quary,
                                 history,
                                 system,
                                 max_length,
                                 image_path,
                                 top_p,
                                 temperature,
                                 model_nickname)
            break
        except Exception as e:
            traceback.print_exc()
            print(e)
            count -= 1
            time.sleep(3)
    result = {
        "response": response
    }
    print('【答】\n{}\n======================================='.format(result['response']))
    return result

@app.post("/voice")
async def create_item(request: Request):
    json_post_raw = await request.json()
    json_post = json.dumps(json_post_raw)
    json_post_list = json.loads(json_post)
    file_path = json_post_list.get('file_path')

    # print('【语音文件】\n{}'.format(file_path))
    response = ''
    count = 5
    while count > 0:
        try:
            response = linkco.get_voice_to_text(file_path)
            break
        except Exception as e:
            traceback.print_exc()
            print(e)
            count -= 1
            time.sleep(3)

    result = {
        "response": response
    }
    # print('【语音识别】\n{}'.format(result['response']))
    return result









# 网页聊天实现部分

def postprocess(self, y):
    if y is None:
        return []
    for i, (message, response) in enumerate(y):
        y[i] = (
            None if message is None else mdtex2html.convert((message)),
            None if response is None else mdtex2html.convert(response),
        )
    return y


gr.Chatbot.postprocess = postprocess


def parse_text(text):
    """copy from https://github.com/GaiZhenbiao/ChuanhuChatGPT/"""
    lines = text.split("\n")
    lines = [line for line in lines if line != ""]
    count = 0
    for i, line in enumerate(lines):
        if "```" in line:
            count += 1
            items = line.split('`')
            if count % 2 == 1:
                lines[i] = f'<pre><code class="language-{items[-1]}">'
            else:
                lines[i] = f'<br></code></pre>'
        else:
            if i > 0:
                if count % 2 == 1:
                    line = line.replace("`", "\`")
                    line = line.replace("<", "&lt;")
                    line = line.replace(">", "&gt;")
                    line = line.replace(" ", "&nbsp;")
                    line = line.replace("*", "&ast;")
                    line = line.replace("_", "&lowbar;")
                    line = line.replace("-", "&#45;")
                    line = line.replace(".", "&#46;")
                    line = line.replace("!", "&#33;")
                    line = line.replace("(", "&#40;")
                    line = line.replace(")", "&#41;")
                    line = line.replace("$", "&#36;")
                lines[i] = "<br>"+line
    text = "".join(lines)
    return text


def predict(input, chatbot, history, drop, llm_drop):
    print('【input】', input)
    # print('【drop】', drop)
    chatbot.append((parse_text(input), ""))
    temp_his = linkco.get_cut_history(history, his_len=20)
    system = system_role['林可可']
    temp_response = ''
    if drop == '网络搜索':
        tool_info = '【工具】{}...'.format('网络搜索')
        temp_response += tool_info + '\n'
        print(tool_info)
        chatbot[-1] = (parse_text(input), parse_text(temp_response))
        yield chatbot, temp_his
        tool = linkco.tool_search_quark.Tool()
        tool_result = tool.get_response(input, history, if_query=False, model_nickname=llm_drop)
        temp_response += tool_result + '\n------以上是参考资料------\n'
        chatbot[-1] = (parse_text(input), parse_text(temp_response))
        yield chatbot, temp_his
        temp_his.append({'role': 'data', 'content': tool_result})
    elif drop == '天气查询':
        tool_info = '【工具】{}...'.format('天气查询')
        temp_response += tool_info + '\n'
        print(tool_info)
        chatbot[-1] = (parse_text(input), parse_text(temp_response))
        yield chatbot, temp_his
        tool = linkco.tool_search_weather.Tool()
        tool_result = tool.get_response(input, history, model_nickname=llm_drop)
        temp_response += tool_result + '\n------以上是参考资料------\n'
        chatbot[-1] = (parse_text(input), parse_text(temp_response))
        yield chatbot, temp_his
        temp_his.append({'role': 'data', 'content': tool_result})
    elif drop == '新闻写作':
        tool_info = '【工具】{}...'.format('新闻写作')
        if db_name not in linkco.vector_dbs.keys():
            linkco.load_vector_database(db_name, 'D:\\Linkco\\vector_database')
        temp_response += tool_info + '\n'
        print(tool_info)
        chatbot[-1] = (parse_text(input), parse_text(temp_response))
        yield chatbot, temp_his
        # 搜索最相关的文本
        start_time = time.time()
        result = linkco.search_from_vector_database(db_name, input, 3)
        print('【向量库搜索耗时】', time.time() - start_time)
        data_str = '\n'.join([it['content'] for it in result])
        for it in result:
            data_str += it['content']
            print(it['score'])
            print(it['content'])
            print('=========================')
        tool_result = data_str[:1024]
        temp_inp = input
        if len(tool_result) > 0:
            input = '根据上文内容，生成一篇关于{}的资讯新闻，要求内容丰富，字数多（800字），不可抄袭上文'.format(input)
        else:
            input = '生成一篇关于{}的资讯新闻，要求内容丰富，字数多（800字）'.format(input)
        temp_response += tool_result + '\n------以上是参考资料------\n'
        chatbot[-1] = (parse_text(temp_inp), parse_text(temp_response))
        yield chatbot, temp_his
        temp_his.append({'role': 'data', 'content': tool_result})
    elif drop == '智能聊天':
        tool_result = ''
        tools = linkco.get_switch_tool(input, history, model_nickname=llm_drop)
        for tool in tools:
            if tool.name != '聊天对话':
                tool_info = '【工具】{}...'.format(tool.name)
                temp_response += tool_info + '\n'
                print(tool_info)
                chatbot[-1] = (parse_text(input), parse_text(temp_response))
                yield chatbot, temp_his
                tool_result += tool.get_response(input, history, model_nickname=llm_drop)
                temp_response += tool_result + '\n----------------------\n'
                chatbot[-1] = (parse_text(input), parse_text(temp_response))
                yield chatbot, temp_his
        if len(tool_result) > 0:
            temp_his.append({'role': 'data', 'content': tool_result})
        else:
            system = system_role['林可可']
    elif drop == '无人机控制':
        system = drones_system
    else:
        system = system_role[drop]
    if llm_drop == 'lincoco':
        for response in linkco.llm_module['lincoco']['module'].stream_chat(input,
                                                                          temp_his,
                                                                          system,
                                                                          max_length=2048,
                                                                          top_p=top_p,
                                                                          temperature=temperature):
            out_response = temp_response + response
            chatbot[-1] = (parse_text(input), parse_text(out_response))
            # chatbot[-1] = ("", parse_text(response))
            new_history = temp_his + [{'role': 'user', 'content': input},
                                      {'role': 'assistant', 'content': response}]
    
            yield chatbot, new_history
    else:
        response = linkco.get_chat(input,
                                   temp_his,
                                   system,
                                   max_length=2048,
                                   top_p=top_p,
                                   temperature=temperature,
                                   model_nickname=llm_drop)
        out_response = temp_response + response
        chatbot[-1] = (parse_text(input), parse_text(out_response))
        # chatbot[-1] = ("", parse_text(response))
        new_history = temp_his + [{'role': 'user', 'content': input},
                                  {'role': 'assistant', 'content': response}]

        yield chatbot, new_history


def re_predict(chatbot, history, drop, llm_drop):
    input = history[-2]['content']
    history = history[:-2]
    chatbot = chatbot[:-1]
    print('【input】', input)
    chatbot.append((parse_text(input), ""))
    temp_his = linkco.get_cut_history(history, his_len=20)
    system = system_role['林可可']
    temp_response = ''
    if drop == '网络搜索':
        tool_info = '【工具】{}...'.format('网络搜索')
        temp_response += tool_info + '\n'
        print(tool_info)
        chatbot[-1] = (parse_text(input), parse_text(temp_response))
        yield chatbot, temp_his
        tool = linkco.tool_search_quark.Tool()
        tool_result = tool.get_response(input, history, if_query=False, model_nickname=llm_drop)
        temp_response += tool_result + '\n------以上是参考资料------\n'
        chatbot[-1] = (parse_text(input), parse_text(temp_response))
        yield chatbot, temp_his
        temp_his.append({'role': 'data', 'content': tool_result})
    elif drop == '天气查询':
        tool_info = '【工具】{}...'.format('天气查询')
        temp_response += tool_info + '\n'
        print(tool_info)
        chatbot[-1] = (parse_text(input), parse_text(temp_response))
        yield chatbot, temp_his
        tool = linkco.tool_search_weather.Tool()
        tool_result = tool.get_response(input, history, model_nickname=llm_drop)
        temp_response += tool_result + '\n------以上是参考资料------\n'
        chatbot[-1] = (parse_text(input), parse_text(temp_response))
        yield chatbot, temp_his
        temp_his.append({'role': 'data', 'content': tool_result})
    elif drop == '新闻写作':
        tool_info = '【工具】{}...'.format('新闻写作')
        if db_name not in linkco.vector_dbs.keys():
            linkco.load_vector_database(db_name, 'D:\\Linkco\\vector_database')
        temp_response += tool_info + '\n'
        print(tool_info)
        chatbot[-1] = (parse_text(input), parse_text(temp_response))
        yield chatbot, temp_his
        # 搜索最相关的文本
        start_time = time.time()
        result = linkco.search_from_vector_database(db_name, input, 3)
        print('【向量库搜索耗时】', time.time() - start_time)
        data_str = '\n'.join([it['content'] for it in result])
        for it in result:
            data_str += it['content']
            print(it['score'])
            print(it['content'])
            print('=========================')
        tool_result = data_str[:1024]
        temp_inp = input
        if len(tool_result) > 0:
            input = '根据上文内容，生成一篇关于{}的资讯新闻，要求内容丰富，字数多（800字），不可抄袭上文'.format(input)
        else:
            input = '生成一篇关于{}的资讯新闻，要求内容丰富，字数多（800字）'.format(input)
        temp_response += tool_result + '\n------以上是参考资料------\n'
        chatbot[-1] = (parse_text(temp_inp), parse_text(temp_response))
        yield chatbot, temp_his
        temp_his.append({'role': 'data', 'content': tool_result})
    elif drop == '智能聊天':
        tool_result = ''
        tools = linkco.get_switch_tool(input, history, model_nickname=llm_drop)
        for tool in tools:
            if tool.name != '聊天对话':
                tool_info = '【工具】{}...'.format(tool.name)
                temp_response += tool_info + '\n'
                print(tool_info)
                chatbot[-1] = (parse_text(input), parse_text(temp_response))
                yield chatbot, temp_his
                tool_result += tool.get_response(input, history, model_nickname=llm_drop)
                temp_response += tool_result + '\n----------------------\n'
                chatbot[-1] = (parse_text(input), parse_text(temp_response))
                yield chatbot, temp_his
        if len(tool_result) > 0:
            temp_his.append({'role': 'data', 'content': tool_result})
        else:
            system = system_role['林可可']
    elif drop == '无人机控制':
        system = drones_system
    else:
        system = system_role[drop]
    if llm_drop == 'lincoco':
        for response in linkco.llm_module['lincoco']['module'].stream_chat(input,
                                                                           temp_his,
                                                                           system,
                                                                           max_length=2048,
                                                                           top_p=top_p,
                                                                           temperature=temperature):
            out_response = temp_response + response
            chatbot[-1] = (parse_text(input), parse_text(out_response))
            # chatbot[-1] = ("", parse_text(response))
            new_history = temp_his + [{'role': 'user', 'content': input},
                                      {'role': 'assistant', 'content': response}]

            yield chatbot, new_history
    else:
        response = linkco.get_chat(input,
                                   temp_his,
                                   system,
                                   max_length=2048,
                                   top_p=top_p,
                                   temperature=temperature,
                                   model_nickname=llm_drop)
        out_response = temp_response + response
        chatbot[-1] = (parse_text(input), parse_text(out_response))
        # chatbot[-1] = ("", parse_text(response))
        new_history = temp_his + [{'role': 'user', 'content': input},
                                  {'role': 'assistant', 'content': response}]

        yield chatbot, new_history


def change_response(input, chatbot, history):
    if input is None or len(input) == 0:
        yield chatbot, history, history[-1]['content']
    else:
        chatbot[-1] = (parse_text(history[-2]['content']), parse_text(input))
        # chatbot[-1] = ("", parse_text(response))
        new_history = history[:-2] + [{'role': 'user', 'content': history[-2]['content']},
                                  {'role': 'assistant', 'content': input}]
        # save_state(new_history, drop, user_name)
        yield chatbot, new_history, ''


def reset_user_input():
    return gr.update(value='')


def reset_state():
    return [], []


def save_state(history, drop, user_name):
    if len(history) >= 2:
        res = history[-1]['content']
        prompt = history[-2]['content']
        system = ''
        if drop == '无人机控制':
            system = drones_system
        elif drop == '林可可':
            system = system_role[drop]
        linkco.save_data(res, prompt, history[:-2], system, 'linkco_data/llm_response_{}{}.json'.format(drop, user_name))

def run_gradio_linkco():
    asyncio.set_event_loop(asyncio.new_event_loop())

    with gr.Blocks() as demo:
        state = gr.State(value="")
        gr.HTML("""<h1 align="center">鹏城脑海·具身智能平台</h1>""")

        chatbot = gr.Chatbot()
        with gr.Row():
            with gr.Column(scale=4):
                user_input = gr.Textbox(show_label=False, placeholder="请输入...", lines=2).style(
                    container=False)
                submitBtn = gr.Button("发送", variant="primary")
                textbox = gr.Textbox(show_label=False).style(container=False)
                audio = gr.Audio(source="microphone", type="filepath")
                saveBtn = gr.Button("保存对话")
                with gr.Row():
                    rewriteBtn = gr.Button("重新生成")
                    changeBtn = gr.Button("修改回答")


            with gr.Column(scale=1):
                # role_list = ['聊天对话', '智能聊天', '网络搜索', '天气查询', '新闻写作', '林可可', '无人机控制']
                role_list = ['聊天对话', '新闻写作', '网络搜索', '天气查询', '林可可', '无人机控制']
                drop = gr.Dropdown(role_list, value='聊天对话', label="功能")
                emptyBtn = gr.Button("清除历史对话")
                user_name = gr.Textbox(show_label=False, placeholder="当前使用者", lines=1).style(
                    container=False)
                llm_list = ['lincoco', 'vlincoco', 'openai']
                llm_drop = gr.Dropdown(llm_list, value='mind7b', label="模型")

        history = gr.State([])
        audio.stream(fn=transcribe, inputs=[audio, state], outputs=[textbox, state], show_progress=True)

        submitBtn.click(predict, [user_input, chatbot, history, drop, llm_drop], [chatbot, history],
                        show_progress=True)
        submitBtn.click(reset_user_input, [], [user_input])

        rewriteBtn.click(re_predict, [chatbot, history, drop, llm_drop], [chatbot, history],
                            show_progress=True)

        changeBtn.click(change_response, [user_input, chatbot, history], [chatbot, history, user_input],
                         show_progress=True)


        emptyBtn.click(reset_state, outputs=[chatbot, history], show_progress=True)
        saveBtn.click(save_state, inputs=[history, drop, user_name], show_progress=True)
        saveBtn.click(reset_state, outputs=[chatbot, history], show_progress=True)

    demo.queue().launch(share=False, inbrowser=True, server_name=ip, server_port=chat_server)







# 数据标注系统网页实现部分

def get_linkco_json(inp_path):
    with open(inp_path, 'r', encoding='utf-8') as f:
        data = f.read().split('\n')
        data = [eval(it) for it in data if len(it) > 0]
    f.close()
    return data

all_datas = {}
ok_file_names = os.listdir('train_data/dict/')
for file_name in ok_file_names:
    print(file_name)
    with open('train_data/dict/' + file_name, 'r', encoding='utf-8') as f:
        temp_data = json.load(f)
    f.close()
    all_datas[file_name] = temp_data


raw_file_names = os.listdir('train_data/raw/')

for file_name in raw_file_names:
    temp_data = get_linkco_json('train_data/raw/' + file_name)
    if file_name not in all_datas.keys():
        all_datas[file_name] = {}
    for it_data in temp_data:
        temp_str = it_data['prompt'] + it_data['response']
        if temp_str not in all_datas[file_name].keys():
            all_datas[file_name][temp_str] = {
                '占用': False,
                '计数': 0,
                '数据': it_data
            }
        else:
            if all_datas[file_name][temp_str]['计数'] == 0 and all_datas[file_name][temp_str]['占用']:
                all_datas[file_name][temp_str]['占用'] = False
    with open('train_data/dict/{}'.format(file_name), 'w', encoding='utf-8') as f2:
        json.dump(all_datas[file_name], f2, ensure_ascii=False, indent=2)
    f2.close()

data_list = list(all_datas.keys())

def data_re_predict(chatbot, inp_data, llm_drop):
    out_json = {}
    if inp_data != {} or len(chatbot) > 0:
        history = inp_data['history']
        prompt = inp_data['prompt']
        system = inp_data['system']

        if llm_drop == 'lincoco':
            for response in linkco.llm_module['lincoco']['module'].stream_chat(prompt,
                                                                               history,
                                                                               system,
                                                                               max_length=2048,
                                                                               top_p=top_p,
                                                                               temperature=temperature):
                chatbot[-1] = (parse_text(prompt), parse_text(response))
                out_json = {
                    'system': system,
                    'prompt': prompt,
                    'response': response,
                    'history': history
                }

                yield chatbot, out_json
        else:
            response = linkco.get_chat(prompt,
                                       history,
                                       system,
                                       max_length=2048,
                                       top_p=top_p,
                                       temperature=temperature,
                                       model_nickname=llm_drop)
            chatbot[-1] = (parse_text(prompt), parse_text(response))
            out_json = {
                'system': system,
                'prompt': prompt,
                'response': response,
                'history': history
            }

            yield chatbot, out_json
    else:
        yield chatbot, out_json


def data_change_response(chatbot, inp_data, inp_text):
    if len(inp_text) == 0 and inp_data != {}:
        return chatbot, inp_data, inp_data['response']
    else:
        out_json = {}
        if inp_data != {} or len(chatbot) > 0:
            history = inp_data['history']
            prompt = inp_data['prompt']
            system = inp_data['system']
            # print('【prompt】', prompt)

            chatbot[-1] = (parse_text(prompt), parse_text(inp_text))
            # chatbot[-1] = ("", parse_text(response))
            out_json = {
                'system': system,
                'prompt': prompt,
                'response': inp_text,
                'history': history
            }
            # save_state(out_json, drop)
        return chatbot, out_json, gr.update(value='')


def data_save_state(now_name, out_json, old_drop, user_name):
    if out_json != {} or len(now_name) > 0:
        all_datas[old_drop][now_name]['计数'] += 1
        # 保存数据
        with open('train_data/ok/{}{}.json'.format(old_drop.replace('.json', ''), user_name), 'a', encoding='utf-8') as f2:
            json.dump(out_json, f2, ensure_ascii=False)
            f2.write('\n')
        f2.close()
        with open('train_data/dict/{}'.format(old_drop), 'w', encoding='utf-8') as f2:
            json.dump(all_datas[old_drop], f2, ensure_ascii=False, indent=2)
        f2.close()
        all_datas[old_drop][now_name]['占用'] = False


def data_loss_state(now_name, out_json, old_drop):
    if out_json != {} or len(now_name) > 0:
        all_datas[old_drop][now_name]['计数'] += 1
        # 保存数据
        with open('train_data/dict/{}'.format(old_drop), 'w', encoding='utf-8') as f2:
            json.dump(all_datas[old_drop], f2, ensure_ascii=False, indent=2)
        f2.close()
        all_datas[old_drop][now_name]['占用'] = False


def get_chatbot_his(inp_data):
    history = inp_data['history']
    prompt = inp_data['prompt']
    system = inp_data['system']
    response = inp_data['response']
    temp_his = []

    if len(system) > 0:
        temp_his.append([system, ''])

    his_item = []
    for item in history:
        if isinstance(item, dict):

            if item['role'] == 'assistant' and len(his_item) == 1:
                his_item.append(item['content'])
            else:
                if len(his_item) == 0:
                    if item['role'] == 'user':
                        his_item.append(item['content'])
                    else:
                        his_item.append('[{}]:{}'.format(item['role'], item['content']))
                else:
                    if item['role'] == 'user':
                        his_item[0] += '\n' + item['content']
                    else:
                        his_item[0] += '\n' + '[{}]:{}'.format(item['role'], item['content'])
        else:
            if len(his_item) == 0:
                his_item = item[:2]
            elif len(his_item) == 1:
                his_item[0] += item[0]
                his_item.append(item[1])

        if len(his_item) == 2:
            temp_his.append(his_item)
            his_item = []

    temp_his.append([prompt, response])
    return temp_his

def next_data(now_name, old_drop, drop):
    if len(old_drop) > 0 and len(now_name) > 0:
        all_datas[old_drop][now_name]['占用'] = False
    chatbot = []

    if '问题关联回溯判断' in drop:
        # temp_dict = dict(filter(lambda x: x[1]['占用'] == False and x[1]['计数'] < data_count_limit and "\"判断\": \"yes\"" in x[1]['数据']['response'], all_datas[drop].items()))
        temp_dict = dict(filter(lambda x: x[1]['占用'] == False and x[1]['计数'] < data_count_limit, all_datas[drop].items()))
    else:
        temp_dict = dict(filter(lambda x: x[1]['占用'] == False and x[1]['计数'] < data_count_limit, all_datas[drop].items()))

    now_list = list(temp_dict.keys())

    if len(now_list) == 0:
        return chatbot, {}, '', drop
    else:
        now_item_name = random.sample(now_list, 1)[0]

        all_datas[drop][now_item_name]['占用'] = True

        json_data = all_datas[drop][now_item_name]['数据']
        temp_his = get_chatbot_his(json_data)
        for it in temp_his:
            chatbot.append((parse_text(it[0]), parse_text(it[1])))
        return chatbot, json_data, now_item_name, drop



def save_file(upload):
    if upload is not None:
        file_path = os.path.join("uploads", upload.name)
        upload.save(file_path)
        return "文件已保存为: {}".format(file_path)
    else:
        return "没有选择文件。"

# def run_gradio_data():
#
#     asyncio.set_event_loop(asyncio.new_event_loop())
#
#
#     with gr.Blocks() as demo:
#         gr.HTML("""<h1 align="center">数据标注</h1>""")
#
#         start_now_item_name = ''
#         now_data = {}
#         json_data = gr.State(now_data)
#         now_item_name = gr.State(start_now_item_name)
#         old_drop = gr.State('')
#         # temp_his = get_chatbot_his(now_data)
#         # chatbot = gr.Chatbot(temp_his)
#         chatbot = gr.Chatbot()
#
#         with gr.Row():
#             with gr.Column(scale=4):
#                 user_input = gr.Textbox(show_label=False, placeholder="请输入...", lines=2).style(
#                     container=False)
#                 saveBtn = gr.Button("保存", variant="primary")
#                 with gr.Row():
#                     rewriteBtn = gr.Button("重新生成")
#                     changeBtn = gr.Button("修改回答")
#
#
#             with gr.Column(scale=1):
#                 drop = gr.Dropdown(data_list, value=data_list[0], label="数据库")
#                 with gr.Row():
#                     nextBtn = gr.Button("换一条")
#                     lossBtn = gr.Button("丢弃")
#                 user_name = gr.Textbox(show_label=False, placeholder="当前使用者", lines=1).style(
#                     container=False)
#                 llm_list = ['lincoco', 'vlincoco', 'openai']
#                 llm_drop = gr.Dropdown(llm_list, value='lincoco', label="模型")
#
#
#         rewriteBtn.click(data_re_predict, [chatbot, json_data, llm_drop], [chatbot, json_data],
#                             show_progress=True)
#
#         changeBtn.click(data_change_response, [chatbot, json_data, user_input], [chatbot, json_data, user_input],
#                          show_progress=True)
#         # changeBtn.click(reset_user_input, [], [user_input])
#
#         nextBtn.click(next_data, [now_item_name, old_drop, drop], [chatbot, json_data, now_item_name, old_drop], show_progress=True)
#
#         saveBtn.click(data_save_state, [now_item_name, json_data, old_drop, user_name], show_progress=True)
#         saveBtn.click(next_data, [now_item_name, old_drop, drop], [chatbot, json_data, now_item_name, old_drop], show_progress=True)
#
#         lossBtn.click(data_loss_state, [now_item_name, json_data, old_drop], show_progress=True)
#         lossBtn.click(next_data, [now_item_name, old_drop, drop], [chatbot, json_data, now_item_name, old_drop],
#                       show_progress=True)
#
#     demo.queue().launch(share=False, inbrowser=True, server_name=ip, server_port=data_server)
#






if __name__ == '__main__':


    model_config = {
        "device": "cuda:1",
        # "lora_path": "Z:\\ChatGLM-6B\\ptuning\\output\\keke-chatglm-6b-v6\\checkpoint-500",
        "lora_path": "./output",
    }

    # linkco.init_llm_model(model_name='glm6b', model_nickname='lincoco', model_config={"device": "cuda:2"})
    # linkco.init_llm_model(model_name='vglm6b', model_nickname='vlincoco', model_config={"device": "cuda:2"})

    linkco.init_llm_model(model_name='openai', model_nickname='openai')


    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)

    t0 = threading.Thread(target=run_gradio_linkco, args=())
    t0.start()

    time.sleep(5)

    # t1 = threading.Thread(target=run_gradio_data, args=())
    # t1.start()

    # uvicorn.run(app, host=ip, port=llm_server, workers=1)
