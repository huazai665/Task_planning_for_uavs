import os
import json
import time
import torch
import faiss
import pickle
import queue
import threading
from tqdm import tqdm

import numpy as np

import sys
sys.path.append('/Users/wenlong/opt/anaconda3/lib/python3.9/site-packages')
# sys.path.append('../../../../../../opt/anaconda3/lib/python3.9/site-packages')

import sentence_transformers as st

from ...main import setting, vector_database_path, vector_dbs
from .utils_file import read_file
from .utils_data import get_text_split

# embedding 模型
default_model = None
default_model_config = None


# 初始化文本向量化模型
def init_vector_model(model_config=None):
    temp_config = setting['vector_model']
    print('【temp_config】', temp_config)
    if model_config is not None:
        for key in model_config:
            temp_config[key] = model_config[key]
    temp_model = st.SentenceTransformer(
        temp_config['model_path'], device=temp_config['device'])
    return temp_model


# 设置默认的vector_model
def set_default_vector_model(model_config=None):
    global default_model, default_model_config

    if default_model is None or (model_config is not None and model_config != default_model_config):
        default_model_config = model_config or setting['vector_model']
        default_model = init_vector_model(default_model_config)


# 将文本转换为向量
def get_text_to_vector(text: str, model=None) -> np.ndarray:
    global default_model
    if model is None:
        if default_model is None:
            set_default_vector_model()
        temp_model = default_model
    elif isinstance(model, str):
        temp_model = init_vector_model(model)
    else:
        temp_model = model

    return temp_model.encode(text)


# 保存向量库到本地文件
def save_vector_to_database(database_name: str):
    global default_model_config
    temp_database_path = vector_database_path + database_name
    if not os.path.exists(temp_database_path):
        os.mkdir(temp_database_path)
    with open(os.path.join(temp_database_path, 'texts.pkl'), 'wb') as f:
        pickle.dump(vector_dbs[database_name]['texts'], f)
    faiss.write_index(vector_dbs[database_name]['index'], os.path.join(temp_database_path, 'index.index'))
    with open(os.path.join(temp_database_path, 'config.json'), 'w', encoding='utf-8') as f:
        json.dump(default_model_config, f, ensure_ascii=False)
    f.close()


# 【增】从文本创建向量并将其添加到向量库中
# 【增】从文本创建向量并将其添加到向量库中
def add_vector(database_name: str, data):
    if not isinstance(data, (str, dict)):
        raise ValueError("Invalid data format. Expected 'str' or 'dict'.")

    if database_name not in vector_dbs:
        try:
            load_vector_database(database_name)
            print('【加载成功】', database_name)
        except:
            print('【创建新数据库】', database_name)
            vector = get_text_to_vector('test')
            dimension = len(vector)
            vector_dbs[database_name] = {
                'index': faiss.IndexFlatL2(dimension),
                'texts': [],
            }
    if isinstance(data, str):
        if data not in vector_dbs[database_name]['texts']:
            print('【数据不存在，添加】', data)
            vector = get_text_to_vector(data)
            vector_dbs[database_name]['index'].add(np.array([vector]))
            vector_dbs[database_name]['texts'].append(data)
    elif isinstance(data, dict):
        if 'texts' not in data or 'vectors' not in data:
            raise ValueError("Invalid data format for dict. 'texts' and 'vectors' keys are required.")

        texts = data['texts']
        vectors = data['vectors']

        if not isinstance(texts, list) or not isinstance(vectors, list):
            raise ValueError("Invalid data format for dict. 'texts' and 'vectors' should be lists.")

        if len(texts) != len(vectors):
            raise ValueError("Invalid data format for dict. 'texts' and 'vectors' should have the same length.")

        unique_texts = []
        unique_vectors = []
        for text in texts:
            if text not in vector_dbs[database_name]['texts']:
                # print('【数据不存在，添加】', text)
                unique_texts.append(text)
                unique_vectors.append(vectors[texts.index(text)])
        print('【unique_vectors】', len(unique_vectors))
        if len(unique_vectors) > 0:
            vector_dbs[database_name]['index'].add(np.array(unique_vectors))
            vector_dbs[database_name]['texts'].extend(unique_texts)

        # 保存到本地数据库
        # save_to_vector_database(database_name)
    # else:
    #     print('【数据已存在】', database_name)


# 【删】删除向量库中的向量
def delete_vector(database_name: str, data):
    if database_name not in vector_dbs:
        try:
            load_vector_database(database_name)
            print('【加载成功】', database_name)
        except:
            raise ValueError(f"Cannot find the database {database_name}")

    index = vector_dbs[database_name]['index']
    texts = vector_dbs[database_name]['texts']

    if isinstance(data, str):
        vector = get_text_to_vector(data)
    elif isinstance(data, np.ndarray):
        vector = data
    else:
        raise ValueError(f"delete_vector Input data mistake!")

    D, I = index.search(np.array([vector]), 1)
    remove_index = int(I[0][0])
    num_vectors = index.ntotal

    if np.array_equal(index.reconstruct(remove_index), vector):
        vectors = np.empty((num_vectors, len(vector)), dtype=np.float32)
        for i in range(num_vectors):
            vector = index.reconstruct(i)
            vectors[i] = vector
        del texts[remove_index]
        vectors = np.delete(vectors, remove_index, axis=0)
        index = faiss.IndexFlatL2(len(vector))
        index.add(vectors)
        vector_dbs[database_name] = {'index': index, 'texts': texts}
    else:
        raise ValueError(f"数据库中没找到: {data}")
    # vector_dbs[database_name] = {'index': index, 'texts': texts}


# 【改】更新向量库中的向量
def update_vector_to_database(database_name: str, old_text: str, new_text: str):
    delete_vector(database_name, old_text)
    add_vector(database_name, new_text)
    save_vector_to_database(database_name)


# 【查】查询最相关的文本
def search_from_vector_database(database_name: str, query: str, top_k: int = 1):
    if database_name not in vector_dbs:
        load_vector_database(database_name)

    query_vector = get_text_to_vector(query)

    index = vector_dbs[database_name]['index']
    texts = vector_dbs[database_name]['texts']

    D, I = index.search(np.array([query_vector]), top_k)
    # print('【D】', D)
    # print('【I】', I)
    return [{'score': D[0][idx], 'content':texts[i]} for idx, i in enumerate(I[0])]


# 加载向量库
def load_vector_database(database_name: str):
    temp_database_path = vector_database_path + database_name
    if not os.path.exists(temp_database_path):
        raise ValueError(f"Cannot find the database {temp_database_path}")

    vector_dbs[database_name] = {
        'index': faiss.read_index(os.path.join(temp_database_path, 'index.index')),
        'texts': pickle.load(open(os.path.join(temp_database_path, 'texts.pkl'), 'rb'))
    }
    if os.path.exists(os.path.join(temp_database_path, 'config.json')):
        with open(os.path.join(temp_database_path, 'config.json'), 'r', encoding='utf-8') as f:
            model_config = eval(f.read())
            set_default_vector_model(model_config)
        f.close()


# 创建数据库
def create_vector_database(database_name: str, source_folder: str, split_len: int = 512, thread_num=1):
    source_folder_path = os.path.join(os.getcwd(), source_folder)
    all_files = []
    for root, dirs, files in os.walk(source_folder_path):
        for file in files:
            all_files.append([root, file])

    total_files = len(all_files)
    files_processed = 0
    thread_lock = threading.Lock()

    # 定义处理文件的函数
    def process_files(files, result_event, result_queue):
        nonlocal files_processed
        temp_model = init_vector_model()
        temp_vector_dbs = {
            'texts': [],
            'vectors': [],
        }

        for file in files:
            try:
                file_path = os.path.join(file[0], file[1])
                datas = get_text_split(read_file(file_path), split_len)
                for data in datas:
                    if data not in temp_vector_dbs['texts']:
                        vector = get_text_to_vector(data, temp_model)
                        temp_vector_dbs['texts'].append(data)
                        temp_vector_dbs['vectors'].append(np.array(vector))
            except Exception as e:
                print(e)
            with thread_lock:  # 使用线程锁保护并发访问
                files_processed += 1

        result_queue.put(temp_vector_dbs)
        result_event.set()

    # 计算每个线程处理的文件数量
    file_count = len(all_files)
    files_per_thread = file_count // thread_num

    # 创建并启动线程
    threads = []
    result_queue = queue.Queue()
    result_event = threading.Event()

    for i in range(thread_num):
        start_index = i * files_per_thread
        end_index = (i + 1) * files_per_thread if i < thread_num - 1 else file_count
        files = all_files[start_index:end_index]
        thread = threading.Thread(target=process_files, args=(files, result_event, result_queue))
        threads.append(thread)
        thread.start()

    output_data = []  # 存储每个线程的结果

    # 使用tqdm显示进度条
    with tqdm(total=total_files) as pbar:
        while files_processed < total_files:
            pbar.set_description()
            pbar.update(files_processed - pbar.n)
            time.sleep(1)  # 每秒更新一次进度

            if result_event.is_set():
                result_event.clear()
                temp_vector_dbs = result_queue.get()
                output_data.append(temp_vector_dbs)  # 将结果添加到 output_data 列表中

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    for item in output_data:
        add_vector(database_name, item)
    save_vector_to_database(database_name)


# 计算向量距离
def cos_sim(a, b):
    if not isinstance(a, torch.Tensor):
        a = torch.tensor(a)
    if not isinstance(b, torch.Tensor):
        b = torch.tensor(b)
    if len(a.shape) == 1:
        a = a.unsqueeze(0)
    if len(b.shape) == 1:
        b = b.unsqueeze(0)
    a_norm = torch.nn.functional.normalize(a, p=2, dim=1)
    b_norm = torch.nn.functional.normalize(b, p=2, dim=1)
    return torch.mm(a_norm, b_norm.transpose(0, 1))


# 获取评分
def get_score(inp_data, tar_data):
    global default_model
    if default_model == '':
        default_model = init_vector_model()
    if inp_data == tar_data:
        return 1
    q_emb = default_model.encode(inp_data, convert_to_tensor=True)
    c_emb = default_model.encode(tar_data, convert_to_tensor=True)
    cosine_scores = cos_sim(q_emb, c_emb)[0]
    cosine_scores = cosine_scores.item()
    return cosine_scores


# 对一个list计算与q的计算相似度分数排序(正序)
def get_score_list(q, inp_datas, min_score=0.50):
    # print('【当前问题】', q)
    global default_model
    if default_model == '':
        default_model = init_vector_model()
    socre_list = []
    content_list = []
    for item in inp_datas:
        score = get_score(q, item)
        if score > min_score:
            socre_list.append(score)
            content_list.append(item)
            # print('【分数】{}\t{}'.format(score, item))
    result_list = [i for _, i in sorted(zip(socre_list, content_list), key=lambda x: x[0])]
    result_list.reverse()
    return result_list

