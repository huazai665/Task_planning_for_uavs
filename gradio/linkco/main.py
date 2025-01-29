import os
import json

split_line_1 = '---------------------\n'
split_line_2 = '=====================\n'

linkco_path = os.path.abspath(__file__).replace('main.py', '').replace('\\', '/')
linkco_module_path = linkco_path.replace(os.getcwd().replace('\\', '/'), '').replace('/', '.')[1:]

# 基础的配置参数
with open(linkco_path + '/config.json', 'r', encoding='utf-8') as f:
    setting = json.load(f)
f.close()

base_path = setting['save_data']['base_path']
cash_path = base_path + setting['save_data']['cash_path']
vector_database_path = base_path + setting['save_data']['vector_database_path']
llm_response_path = base_path + setting['save_data']['llm_response_path']

if not os.path.exists(base_path):
    os.makedirs(base_path)
if not os.path.exists(vector_database_path):
    os.makedirs(vector_database_path)

# 大模型统一管理字典
llm_module = {}
# 语音转文字模型统一管理字典
v2t_module = {}
# 文字转语音模型统一管理字典
t2v_module = {}
# 向量库统一管理字典中
vector_dbs = {}