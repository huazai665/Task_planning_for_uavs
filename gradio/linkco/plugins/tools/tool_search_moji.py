import json
import requests
from lxml.html import etree

from ..utils.utils_chat import get_cut_history
from ..utils.utils_time import get_now_datetime
from ..utils.utils_prompt import get_info_extraction_chat

wait_time = 3

def init():
    out_dict = {
        'name': '天气搜索',
        'desc': '只能提供天气查询功能。',
    }
    return out_dict

def search_city(city_name):  # 搜索这个城市
    index_url = "http://tianqi.moji.com/api/citysearch/%s" % city_name  # 构造查询相应城市天气的url
    response = requests.get(index_url,
                            timeout=wait_time,
                            verify=False)
    response.encoding = "utf-8"
    city_id = json.loads(response.text).get('city_list')[0].get('cityId')  # 通过上面的url获取城市的id
    city_url = "http://tianqi.moji.com/api/redirect/%s" % str(city_id)  # 通过城市id获取城市天气
    return city_url


def parse_forecast7(city_url):
    response = requests.get(city_url,
                            timeout=wait_time,
                            verify=False)
    response.encoding = 'utf-8'
    html = etree.HTML(response.text)

    week = html.xpath(
        "//div[@class='wea_list clearfix wea_list_seven']/ul[@class='clearfix']/li/span[@class='week']/text()")
    wea = html.xpath(
        "//div[@class='wea_list clearfix wea_list_seven']/ul[@class='clearfix']/li/span[@class='wea']/text()")
    high = html.xpath(
        "//div[@class='wea_list clearfix wea_list_seven']/ul[@class='clearfix']/li/div[@class='tree clearfix']/p/b/text()")
    low = html.xpath(
        "//div[@class='wea_list clearfix wea_list_seven']/ul[@class='clearfix']/li/div[@class='tree clearfix']/p/strong/text()")
    forecast7 = []
    for i in range(8):
        temp_dict = {}
        temp_dict["week"] = week[2 * i]
        temp_dict["date"] = week[2 * i + 1]
        temp_dict["daytime_weather"] = wea[2 * i]
        temp_dict["evening_weather"] = wea[2 * i]
        temp_dict["high_temperature"] = high[i]
        temp_dict["low_temperature"] = low[i]
        forecast7.append(temp_dict)
    return forecast7


def parse(city_url):  # 解析函数
    response = requests.get(city_url,
                            timeout=wait_time,
                            verify=False)
    response.encoding = 'utf-8'
    html = etree.HTML(response.text)
    current_url = html.xpath("//link[@rel='alternate']/@href")[0].replace("weather", "forecast7").replace("m.moji.com",
                                                                                                          "tianqi.moji.com")
    # print(current_url)
    current_city = html.xpath("//div[@class='search_default']/em/text()")[0]  # 下面都是利用xpath解析的
    # print('当前城市：'+current_city)
    current_kongqi = html.xpath("//div[@class='left']/div[@class='wea_alert clearfix']/ul/li/a/em/text()")[0]
    # print('空气质量：'+current_kongqi)
    current_wendu = html.xpath("//div[@class='left']/div[@class='wea_weather clearfix']/em/text()")[0]
    # print('当前温度：'+current_wendu+'℃')
    current_weather = html.xpath("//div[@class='wea_weather clearfix']/b/text()")[0]
    # print('天气状况：' + current_weather)
    current_shidu = html.xpath("//div[@class='left']/div[@class='wea_about clearfix']/span/text()")[0]
    # print('当前湿度：'+current_shidu)
    current_fengji = html.xpath("//div[@class='left']/div[@class='wea_about clearfix']/em/text()")[0]
    # print('当前风速：'+current_fengji)
    uptime = html.xpath("//strong[@class='info_uptime']/text()")[0]
    jingdian = html.xpath("//div[@class='right']/div[@class='near'][2]/div[@class='item clearfix']/ul/li/a/text()")
    #     print('附近景点：')
    #     for j in jingdian:
    #         print('\t\t'+j)

    temp_dict = {}
    forecast7 = parse_forecast7(current_url)
    temp_dict['city'] = current_city
    temp_dict['time'] = uptime
    temp_dict['air'] = current_kongqi
    temp_dict['temperature'] = current_wendu
    temp_dict['weather'] = current_weather
    temp_dict['wet'] = current_shidu
    temp_dict['wind'] = current_fengji
    temp_dict['forecast7'] = forecast7

    return temp_dict


def get_response(prompt, history=[], system='', model_nickname=None):
    temp_his = get_cut_history(history, 64, 1)
    system_str = system + "\n当前时间{}".format(get_now_datetime())
    example_data = {'城市': '北京', '时间': ['2000-01-01', '2000-01-02']}
    # 获取当前信息抽取结果
    response = get_info_extraction_chat(prompt, temp_his, system_str, example_data, model_nickname)
    if response != example_data:
        city_name = response["城市"]
        time_list = response["时间"]
        city_url = search_city(city_name)
        weather = parse(city_url)

        result = "城市地点：{}" \
                 "\n当前天气状况：空气指数{}，气温{}摄氏度，{}，湿度{}，风向{}" \
                 "\n预报：\n".format(weather['city'], weather['air'], weather['temperature'],
                                  weather['weather'],
                                  weather['wet'], weather['wind'])
        for f in weather['forecast7']:
            date = get_now_datetime()[:4] + '-' + f['date'].replace('/', '-')
            # print('【date】', date)
            if date in time_list:
                result = result + "{}，{}，白天{}，晚上{}，最高{}摄氏度，最低{}摄氏度\n".format(date, f['week'], f['daytime_weather'],
                                                                                 f['evening_weather'],
                                                                                 f['high_temperature'],
                                                                                 f['low_temperature'])
        return result + '\n今天是：{}'.format(get_now_datetime())
    else:
        return '没找到相关地区的天气'