#!/usr/bin/python3
# -*- coding: utf-8 -*-
from io import BytesIO
import base64
import requests
from PIL import Image
import ddddocr
import logging

logging.basicConfig(level=logging.INFO,  # 设置日志级别为DEBUG，可以根据需要修改
                    format='%(asctime)s - %(levelname)s - %(message)s')


ocr = ddddocr.DdddOcr(beta=True)

class yaohaocheck(object):
    """docstring for yaohaocheck"""
    def __init__(self, phone, pwd, ding_token):
        self.phone = phone
        self.pwd = pwd
        self.dingding_url = f"https://oapi.dingtalk.com/robot/send?access_token={ding_token}"
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Origin': 'https://apply.jtj.gz.gov.cn',
            'Referer': 'https://apply.jtj.gz.gov.cn/apply/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"'
        }
    def login(self):
        captcha = self.getCaptcha()
        url = 'https://apply.jtj.gz.gov.cn/applyw/common/person/login'
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Cookie': 'UqZBpD3n3iPIDwJU=v1NLXsg++Cl24; TS013e880d=01b7e13970fc379a05e11f05f731817b57f74ed52fd493cfe6e808abb99e37297f985d137b9e64d3660112e7aae02a1e0d8edc70d1; TS3825868a027=08436d0b3cab200053fde26ac88ca951bd51553b245bcd6c40fb145ef23a2494ba380d5962f981e808d9d3a11911300003bfe9c14efa54aa7bf6a9f94584987fe73290e13796d21eff8af365577adb52a8f590df8c45f490ec8bb1ea7d375f79',
            'Origin': 'https://apply.jtj.gz.gov.cn',
            'Referer': 'https://apply.jtj.gz.gov.cn/apply/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }

        data = {
            'loginType': 'MOBILE',
            'userType': 'PERSON',
            'mobile': self.phone,
            'orgCode': '',
            'password': self.pwd,
            "validCode": captcha["validCode"],
            "validCodeKey": captcha["validCodeKey"]
        }
        response = requests.post(url, headers=headers, json=data)
        # 打印响应内容
        logging.info(f"登录响应:{response.text}")
        return response.json()['data']['token']

    def getCaptcha(self):
        response = requests.post("https://apply.jtj.gz.gov.cn/applyw/common/validCodeImage", {}, headers=self.headers)
        # 解析响应
        json_response = response.json()
        base64_string = json_response['data']['base64String']
        validCodeKey = json_response['data']['validCodeKey']
        # 解码 base64 字符串为二进制数据
        binary_data = BytesIO(base64.b64decode(base64_string))
        # 使用 PIL 打开图像
        image = Image.open(binary_data)
        res = ocr.classification(image)
        return {
            "validCode": res,
            "validCodeKey": validCodeKey
        }

    def check_apply_status(self):
        try:
            token = self.login()
            # 请求头
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Authorization': f'{token}',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Connection': 'keep-alive',
                'Origin': 'https://apply.jtj.gz.gov.cn',
                'Referer': 'https://apply.jtj.gz.gov.cn/apply/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"'
            }
            # 请求地址
            url = 'https://apply.jtj.gz.gov.cn/applyw/person/increment/query/apply'

            # 发起 GET 请求
            response = requests.get(url, headers=headers)

            # 检查请求是否成功
            if response.status_code == 200:
                # 将返回的 JSON 数据解析为字典
                data = response.json()

                # 提取 applyStatus
                apply_status = data.get('data', {}).get('model', {}).get('personApply', {}).get('applyStatus')
                logging.info(f"apply_status: {apply_status}")

                if not apply_status:
                    message = f"广州牌摇号情况查询异常报警 response: {response.text}!"
                    logging.info(message)
                    requests.post(self.dingding_url, json={"msgtype": "text", "text": {"content": message}})
                # 判断是否为 NEW 或 CENSOR_APPROVED
                elif apply_status not in ["NEW", "CENSOR_APPROVED"]:
                    # 发送钉钉消息报警的代码（替换成你的实际代码）
                    message = f"广州牌摇号报警 applyStatus is {apply_status}!"
                    logging.info(message)
                    requests.post(self.dingding_url, json={"msgtype": "text", "text": {"content": message}})
                    
                return True
            else:
                # 请求失败，输出错误信息
                logging.info(f"Request failed with status code: {response.status_code}, response:{response.text}")
                # 发送钉钉消息报警的代码（替换成你的实际代码）
                message = f"广州牌摇号情况查询异常报警 Request failed with status code: {response.status_code}!"
                logging.info(message)
                requests.post(self.dingding_url, json={"msgtype": "text", "text": {"content": message}})
        except Exception as e:
            logging.error(f'An error occurred: {e}', exc_info=True)
            message = f"广州牌摇号情况查询异常报警 未知异常: {e}"
            requests.post(self.dingding_url, json={"msgtype": "text", "text": {"content": message}})
        return False