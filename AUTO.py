import urllib.request
from bs4 import BeautifulSoup
from html.parser import HTMLParser
import json
import concurrent.futures

ppp = "––––––––––––––––––––––––––––––––––––––––––––––––––"
BLUE_COLOR = '\033[34m'
RESET_COLOR = '\033[0m'

class ScoreParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_pre = False
        self.score_data = {}

    def handle_starttag(self, tag, attrs):
        if tag == 'pre':
            self.in_pre = True

    def handle_endtag(self, tag):
        if tag == 'pre' and self.in_pre:
            self.in_pre = False

    def handle_data(self, data):
        if self.in_pre:
            try:
                score_info = json.loads(data.strip())
                self.score_data['score'] = score_info['score']
            except json.JSONDecodeError:
                pass

print("自动检测HTTP代理欺诈数值工具 v1.0\nAuto check HTTP proxies fraud tool v1.0\n\n电报 @FengYL_BOT\nTelegram @FengYL_BOT\n")
print("请输入HTTP代理,回车结束输入\nPlease enter HTTP proxies,Enter to end the input\n")
proxy_list = []
while True:
    proxy_info = input().strip()
    if proxy_info.lower() in (""):
        break
    info = proxy_info.split(':')
    if len(info) != 4:
        print("输入的代理格式不正确，请重新输入")
        continue
    proxy = {
        'host': info[0],
        'port': info[1],
        'username': info[2],
        'password': info[3]
    }
    proxy_list.append(proxy)

print("\n请设置欺诈分数最大值：\nPlease set a maximum fraud score")
x = int(input())
print(f"\n{'ip':<16}{'fraud':<6}{'country':<8}{'region':<16}{'city':<18}\n{ppp}")

def process_proxy(proxy):
    try:
        proxy_host = proxy['host']
        proxy_port = proxy['port']
        proxy_username = proxy['username']
        proxy_password = proxy['password']
        proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"
        proxyinfo = f"{proxy_host}:{proxy_port}:{proxy_username}:{proxy_password}"
        proxy_handler = urllib.request.ProxyHandler({'http': proxy_url, 'https': proxy_url})
        opener = urllib.request.build_opener(proxy_handler)
        urllib.request.install_opener(opener)
        response = urllib.request.urlopen('https://ip.nf/me.json')

        if response.status == 200:
            data = json.loads(response.read().decode('utf-8'))
            ip_address = data['ip']['ip']
            url = f'https://scamalytics.com/ip/{ip_address}'
            response = urllib.request.urlopen(url)
            html_content = response.read().decode('utf-8')
            soup = BeautifulSoup(html_content, 'html.parser')
            pre_element = soup.find('pre')

            if pre_element:
                score_parser = ScoreParser()
                score_parser.feed(str(pre_element))
                score = score_parser.score_data.get('score', '')

                if score and int(score) < x:
                    table_element = soup.find('table')
                    if table_element:
                        data_dict = {}
                        rows = table_element.find_all('tr')
                        for row in rows:
                            th_element = row.find('th')
                            td_element = row.find('td')
                            if th_element and td_element:
                                key = th_element.get_text(strip=True)
                                value = td_element.get_text(strip=True)
                                data_dict[key] = value
                        country_code = data_dict.get('Country Code', '')
                        region = data_dict.get('Region', '')
                        city = data_dict.get('City', '')
                        print(f"{BLUE_COLOR}{ip_address:<16}{score:<6}{country_code:<8}{region:<16}{city:<18}{RESET_COLOR}\n{proxyinfo:<84}\n")

        return proxy

    except urllib.error.URLError as e:
        pass
    except Exception as e:
        pass

with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = []
    for proxy in proxy_list:
        futures.append(executor.submit(process_proxy, proxy))
    concurrent.futures.wait(futures)
