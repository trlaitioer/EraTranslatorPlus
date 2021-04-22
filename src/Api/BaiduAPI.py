from hashlib import md5
from Config import getConfig
import random
import typing
import requests

url = "http://api.fanyi.baidu.com/api/trans/vip/translate"
appid = getConfig("BaiduAPI", "appid")
key = getConfig("BaiduAPI", "key")
para = {"appid": appid, "from": getConfig("BaiduAPI", "from"), "to": getConfig("BaiduAPI", "to")}

errorSolution = {
    "52000": "成功",
    "52001": "请求超时，请重试",
    "52002": "系统错误，请重试",
    "52003": "未授权用户，请检查账号",
    "54000": "参数缺失，遇此错误请反馈",
    "54001": "签名错误，遇此错误请反馈",
    "54003": "频率过快",
    "54004": "API账号余额不足",
    "54005": "长请求频率过快",
    "58000": "客户端IP非法",
    "58001": "译文语言错误，遇此错误请反馈",
    "58002": "API服务关闭，请检查账号",
    "90107": "认证失败，请检查账号"
}


def translate(query: str) -> typing.Optional[str]:
    if not query:
        return None
    if not appid or not key:
        print(f"未设置API账号(appid:{appid},key:{key})")
        return None
    salt = random.randint(32768, 65536)
    sign = md5((appid + query + str(salt) + key).encode("utf-8")).hexdigest()
    result = requests.post(url, params=para | {"q": query, "salt": salt, "sign": sign}).json()
    try:
        return result["trans_result"][0]["dst"]
    except Exception:
        try:
            print(f"ApiError:{result['error_code']}:{errorSolution[result['error_code']]}")
            if result['error_code'] in ["54000", "54001", "58001"]:
                print(f"\trequests params:{para}\n\tresult:{result}")
        except Exception:
            print(f"发生未知错误:\n\trequests params:{para}\n\tresult:{result}")
        finally:
            return None
