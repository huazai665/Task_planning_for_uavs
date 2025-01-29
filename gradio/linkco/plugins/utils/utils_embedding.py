import torch
import sentence_transformers

from ...main import setting

model = ''


# 初始化文本向量化模型
def init_emb_model(emb_config=None):
    global model
    temp_config = setting['embedding_model']
    if emb_config is not None:
        for key in emb_config:
            temp_config[key] = emb_config[key]
    model = sentence_transformers.SentenceTransformer(
        temp_config['model_path'], device=temp_config['device'])

    return model


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


# 转换成向量
def get_embedding(inp_data):
    global model
    if model == '':
        model = init_emb_model()
    return model.encode(inp_data, convert_to_tensor=True)


# 获取评分
def get_score(inp_data, tar_data):
    global model
    if model == '':
        model = init_emb_model()
    if inp_data == tar_data:
        return 1
    q_emb = model.encode(inp_data, convert_to_tensor=True)
    c_emb = model.encode(tar_data, convert_to_tensor=True)
    cosine_scores = cos_sim(q_emb, c_emb)[0]
    cosine_scores = cosine_scores.item()
    return cosine_scores


# 对一个list计算与q的计算相似度分数排序(正序)
def get_score_list(q, inp_datas, min_score=0.50):
    # print('【当前问题】', q)
    global model
    if model == '':
        model = init_emb_model()
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