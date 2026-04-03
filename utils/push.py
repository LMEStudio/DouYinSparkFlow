import requests
import os, sys
from datetime import date
import asyncio
import logging

from utils.config import get_secret, get_config

'''
消息推送模块
'''

configJson = get_config()

current_date = date.today().strftime('%Y-%m-%d')
LOGFILE = f"logs/{current_date}.log"

titleSuccess = f"抖音自动续火花成功 - {current_date}"
titleFailed = f"抖音自动续火花结果 - {current_date}"


#TODO: 自定义推送内容
def composeMessage(LOGFILE):
    logFile = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), LOGFILE)
    with open(logFile, 'r', encoding='utf-8') as f:
        message = f.read()
    return message

def _format_serverchan_desp(message) -> str:
    if not message:
        return '今日无可用账号或无输出'
    message = message.splitlines()
    lines: list[str] = []
    for item in message:
        text = item.replace('\r\n', '\n')
        parts = text.split('\n\n')
        if not parts:
            lines.append('')
            continue
        lines.extend(parts)

    # Server酱 desp 使用 Markdown，单换行会折叠为一个空格，需要显式换行。
    return '  \n'.join(line.rstrip() for line in lines)

def serverChanTurbo(message, pushToken):
    url = f"https://sctapi.ftqq.com/{pushToken}.send"
    title = titleSuccess if "失败" not in message else titleFailed
    data = {
        'title': title or "通知",
        'desp': message
        }

    response = requests.post(url, data=data)
    if not response.status_code == 200:
        logging.error(f"Server Chan Turbo 推送失败: {response.status_code}, {response.text}")
    else:
        logging.info(f"Server Chan Turbo 推送成功: {response.status_code}")

def serverChanCubed(message, pushToken, uid):
    url = f"https://{uid}.push.ft07.com/send/{pushToken}.send"
    title = titleSuccess if "失败" not in message else titleFailed
    data = {
        "title": title or "通知",
        "desp": message or "",
        }   

    response = requests.post(url, json=data)
    if not response.status_code == 200:
        logging.error(f"Server Chan Cubed 推送失败: {response.status_code}, {response.text}")
    else:
        logging.info(f"Server Chan Cubed 推送成功: {response.status_code}")

def pushplus(message, pushToken, topic):
    url = f"https://www.pushplus.plus/send?token={pushToken}"
    title = titleSuccess if "失败" not in message else titleFailed
    data = {
        'title': title or "通知", 
        "content": message or "",
        "topic": topic or "",
        }
    
    response = requests.post(url, json=data)
    if not response.status_code == 200:
        logging.error(f"pushplus 推送失败: {response.status_code}, {response.text}")
    else:
        logging.info(f"pushplus 推送成功: {response.status_code}")

def qmsg(message, pushToken, qq, bot, type):
    if type == "send":
        url = f"https://qmsg.zendee.cn/jsend/{pushToken}" #私聊
    elif type == "group":
        url = f"https://qmsg.zendee.cn/jgroup/{pushToken}" #群聊
    title = titleSuccess if "失败" not in message else titleFailed
    data = {
        "msg": f"{title}\n{message}",
        "qq": qq,
        "bot": bot,
        }

    response = requests.post(url, json=data)
    if not response.status_code == 200:
        logging.error(f"qmsg 推送失败: {response.status_code}, {response.text}")
    else:
        logging.info(f"qmsg 推送成功: {response.status_code}")


# 输出推送结果到日志内，但不会将该部分推送出去
async def pushMessage(message: str | None = None):
    if not configJson.get("messagePush", {}).get("enabled", False):
        logging.info("消息推送未启用，跳过推送")
        return

    secretJson = get_secret()
    providers = secretJson.get("pushProvider", []) or []
    if not providers:
        logging.info("未配置任何推送提供商，跳过推送")
        return

    if message is None:
        try:
            message = composeMessage(LOGFILE)
        except FileNotFoundError:
            message = ""
        except Exception as e:
            logging.error(f"读取日志内容失败，错误：{e}")
            message = ""

    async def _send_one(provider_config: dict):
        pushToken = provider_config.get("token", "")
        provider = provider_config.get("provider", "")

        if provider == "server_chan_turbo":
            desp = _format_serverchan_desp(message)
            await asyncio.to_thread(serverChanTurbo, desp, pushToken)
        elif provider == "server_chan_cubed":
            desp = _format_serverchan_desp(message)
            uid = provider_config.get("uid", "")
            await asyncio.to_thread(serverChanCubed, desp, pushToken, uid)
        elif provider == "pushplus":
            topic = provider_config.get("topic", "")
            await asyncio.to_thread(pushplus, message, pushToken, topic)
        elif provider == "qmsg":
            qtype = provider_config.get("type", "send")
            qq = provider_config.get("qq", "")
            bot = provider_config.get("bot", "")
            await asyncio.to_thread(qmsg, message, pushToken, qq, bot, qtype)
        else:
            logging.warning(f"未知推送提供商: {provider}，已跳过")

    results = await asyncio.gather(*(_send_one(p) for p in providers), return_exceptions=True)
    for r in results:
        if isinstance(r, Exception):
            logging.error(f"消息推送任务异常：{r}")

    logging.info("消息推送全部完成")
