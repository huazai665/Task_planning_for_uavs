import re
import requests
from bs4 import BeautifulSoup  # 解析页面

wait_time = 3


# 重定向，获取真实的网址地址
def get_real_url(url, headers):
    """
    获取百度链接真实地址
    :param url: 百度链接地址
    :return: 真实地址
    """
    r = requests.get(url,
                     headers=headers,
                     allow_redirects=False,
                     timeout=wait_time,
                     verify=False)  # 不允许重定向
    if r.status_code == 302:  # 如果返回302，就从响应头获取真实地址
        real_url = r.headers.get('Location')
    else:  # 否则从返回内容中用正则表达式提取出来真实地址
        real_url = re.findall("URL='(.*?)'", r.text)[0]
    return real_url


# 获取网页爬取结果
def get_url_real_content(url):
    s = ''
    # print('【真实内容的网址】', url)
    try:
        response = requests.get(url,
                                timeout=wait_time,
                                verify=False)
        # print('【真实内容的返回代码】', response.status_code)
        if response.status_code == 200:
            html_content = response.content

            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.get_text()
            s = re.sub(r'\n+', '\n', text)
            s = s.split('\n')
            s = [" ".join(item.split()) for item in s if len(" ".join(item.split())) > 64]
            s = '\n\n'.join(s)
            regStr = ".*?([\u4E00-\u9FA5]+).*?"
            temp_s = re.findall(regStr, s)
            temp_s = ''.join(temp_s)
            if len(temp_s) < 256:
                s = ''
    except Exception as e:
        return s
    return s