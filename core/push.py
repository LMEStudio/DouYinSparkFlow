import requests
import os, sys, json
import uuid
import asyncio
from rich.console import Console
from utils.config import get_pushConfig

'''
消息推送模块
本地: 配置 config.json 文件内的 token
gh-actions: 配置新 env: server_chan 并填入 token, config.json 内 token 留空
packed: 
'''

pushConfigJson = get_pushConfig()
console = Console()

LOGFILE = "logs\\app.log"

def composeMessage(LOGFILE):
    logFile = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), LOGFILE)
    with open(logFile, 'r', encoding='utf-8') as f:
        return f.read()
    message = readLog(LOGFILE)
    return message

def serverChan(message, pushToken):
    url = f"https://sctapi.ftqq.com/{pushToken}.send"

    if "失败" not in message:
        data = {'title': '自动续火花全部成功', 'desp': message}
    else:
        data = {'title': '自动续火花失败，详见日志', 'desp': message}
    
    response = requests.post(url, data=data)
    return response.text

def configPush(pushProvider, pushToken):
    if os.path.exists("pushConfig.json"):
        with open("pushConfig.json", "r", encoding="utf-8") as f:
            pushConfigJson = json.load(f)
    else:
        pushConfigJson = []
    pushConfigJson.append(
        {
            "provider": pushProvider,
            "token": pushToken
        }
    )
    # "uuid": str(uuid.uuid4())
    with open("pushConfig.json", "w", encoding="utf-8") as f:
        json.dump(pushConfigJson, f, ensure_ascii=False, indent=4)
    console.rule(f"[bold cyan]PUSH_CONFIG[/bold cyan]")
    console.print(f"[bold green]{pushConfigJson}[/bold green]")
    # return pushConfigJson


def pushMessage():
    message = composeMessage(LOGFILE)
    for provider in pushConfigJson:
        pushToken = provider["token"]
        if provider["provider"] == "server_chan":
            console.rule(f"[bold cyan]{serverChan(message, pushToken)}[/bold cyan]")
    console.rule(f"[bold cyan]消息推送全部完成[/bold cyan]")