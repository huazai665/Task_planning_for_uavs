from ..utils.utils_chat import get_cut_history
from ..utils.utils_time import get_now_datetime
from ..utils.utils_prompt import get_info_extraction_chat

def init():
    out_dict = {
        'name': '时间查询',
        'desc': '当遇到询问时间的时候，可以使用该功能进行时间查询',
    }
    return out_dict


# 根据城市名字获取时间
def get_now_time(country='北京'):

    return get_now_datetime()


def get_response(prompt, history=[], system='', model_nickname=None):
    print('【查询时间】')
    temp_his = get_cut_history(history, 64, 2)
    system_str = system + "\n当前时间{}".format(get_now_datetime())
    example_data = {'国家': '中国'}
    response = get_info_extraction_chat(prompt, temp_his, system_str, example_data, model_nickname)
    if response != example_data:
        country = response["国家"]
    else:
        country = '中国'

    return get_now_time(country)


