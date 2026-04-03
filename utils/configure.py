import os, json
from datetime import date
import logging
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from utils.config import get_secret, get_config

configJson = get_config()
secretJson = get_secret()
console = Console()


def configPush(pushProvider):
    if os.path.exists("secret.json"):
        with open("secret.json", "r", encoding="utf-8", newline="\n") as f:
            secretJson = json.load(f)
    else:
        secretJson["pushProvider"] = []
    
    if pushProvider == "server_chan_turbo":
        pushToken = Prompt.ask("[bold green]请输入提供商提供的Token[/bold green]")
        pushConfig = {
            "provider": "server_chan_turbo",
            "token": pushToken
        }

    if pushProvider == "server_chan_cubed":
        pushToken = Prompt.ask("[bold green]请输入提供商提供的Token[/bold green]")
        pushUID = Prompt.ask("[bold green]请输入提供商提供的UID[/bold green]")
        pushConfig = {
            "provider": "server_chan_cubed",
            "token": pushToken,
            "uid": pushUID
        }

    if pushProvider == "pushplus":
        pushToken = Prompt.ask("[bold green]请输入提供商提供的Token[/bold green]")
        pushTopic = Prompt.ask("[bold green](可选)请指定群组编码, 不填仅发送给自己[/bold green]")
        pushConfig = {
            "provider": "pushplus",
            "topic": pushTopic,
            "token": pushToken
        }

    if pushProvider == "qmsg":
        # === QMSG 推送 ===
        # 在本地或 GitHub Actions 设置：
        #   TOKEN: 必填
        #   QQ: 可选，指定要接收消息的QQ号或者QQ群。多个以英文逗号分割，例如：12345,12346。
        #   BOT： 可选，机器人的QQ号。
        console.print("[bold yellow]请选择[/bold yellow]")
        console.print("[cyan]1.[/cyan] 使用QQ接收消息")
        console.print("[cyan]2.[/cyan] 使用QQ群接收消息")

        choice = Prompt.ask("[bold green]请输入选项编号[/bold green]", choices=["1", "2"])
        if choice == "1":
            pushType = "send"
        elif choice == "2":
            pushType = "group"
        pushToken = Prompt.ask("[bold green]请输入提供商提供的Token[/bold green]")
        pushQQ = Prompt.ask("[bold green](可选)请指定要接收消息的QQ号或者QQ群(多个以英文逗号分割)[/bold green]")
        pushBOT = Prompt.ask("[bold green](可选)请指定机器人的QQ号[/bold green]")
        pushConfig = {
            "provider": "qmsg",
            "type": pushType,
            "token": pushToken,
            "qq": pushQQ,
            "bot": pushBOT
        }

    secretJson["pushProvider"].append(pushConfig)

    # "uuid": str(uuid.uuid4())
    with open("secret.json", "w", encoding="utf-8") as f:
        json.dump(secretJson, f, ensure_ascii=False, indent=4)
    console.rule(f"[bold cyan]SECRET_JSON[/bold cyan]")
    console.print(f"[bold green]{secretJson}[/bold green]")

def initPushConfig():
    if configJson.get("messagePush", {}).get("enabled", False):
        while True:
            console.print("[bold yellow]请选择一个提供商[/bold yellow]")
            console.print("[cyan]1.[/cyan] Server Chan Turbo")
            console.print("[cyan]2.[/cyan] Server Chan Cubed (Server Chan 3)")
            console.print("[cyan]3.[/cyan] pushplus")
            console.print("[cyan]4.[/cyan] qmsg")

            choice = Prompt.ask("[bold green]请输入选项编号[/bold green]", choices=["1", "2", "3", "4"])
            if choice == "1":
                configPush("server_chan_turbo")
            elif choice == "2":
                configPush("server_chan_cubed")
            elif choice == "3":
                configPush("pushplus")
            elif choice == "4":
                configPush("qmsg")
            
            if (Prompt.ask("[bold yellow]是否继续添加消息推送？[/bold yellow]", choices=["y", "n"]) == "n"):
                break
    else:
        steps = (
            "0. 请在 [bold yellow]config.json[/bold yellow] 内启用 [bold yellow]messagePush[/bold yellow]"
        )
        console.print(Panel(steps, title="未启用消息推送", expand=False, style="bold red"))
        exit