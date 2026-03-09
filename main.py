import json
import asyncio
import argparse
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from core.login import userLogin
from core.push import configPush
from utils.config import get_config
from utils.github_action_config import print_github_action_config, print_github_action_push_config

# 初始化 rich 控制台
console = Console()
config = get_config()

def main():
    console.print("[bold green]欢迎使用 DouYin Spark Flow[/bold green]")
    console.print("[bold yellow]请选择一个操作：[/bold yellow]")
    console.print("[cyan]1.[/cyan] 添加用户登录")
    console.print("[cyan]2.[/cyan] 本地运行任务")
    console.print("[cyan]3.[/cyan] 配置消息推送")
    console.print("[cyan]4.[/cyan] 获取 Github Action 配置")
    console.print("[cyan]5.[/cyan] 获取 Github Action 消息推送配置")

    # 获取用户选择
    choice = Prompt.ask(
        "[bold green]请输入选项编号 (1/2/3/4/5)[/bold green]", choices=["1", "2", "3", "4" ,"5"]
    )

    if choice == "1":
        console.print("[bold blue]正在添加登录，请稍候...[/bold blue]")
        while True:
            asyncio.run(userLogin())
            if (Prompt.ask("[bold yellow]是否继续添加用户登录？(y/n)[/bold yellow]", choices=["y", "n"]) == "n"):
                break

    elif choice == "2":
        from core.tasks import runTasks
        asyncio.run(runTasks())

    elif choice == "3":
        if config["messagePush"]["enabled"]:
            while True:
                # if (Prompt.ask("[bold yellow]是否添加消息推送？(y/n)[/bold yellow]", choices=["y", "n"]) == "y"):
                console.print("[bold yellow]请选择一个提供商：[/bold yellow]")
                console.print("[cyan]1.[/cyan] Server Chan Turbo")
                console.print("[cyan]2.[/cyan] todo")

                choice = Prompt.ask("[bold green]请输入选项编号 (1/2)[/bold green]", choices=["1", "2"])
                if choice == "1":
                    pushProvider = "server_chan_turbo"
                elif choice == "2":
                    pushProvider = ""
                else:
                    console.print("非法选项")
                    exit
                console.print("[bold yellow]请输入提供商提供的Token：[/bold yellow]")
                pushToken = input()
                configPush(pushProvider, pushToken)
                if (Prompt.ask("[bold yellow]是否继续添加消息推送？(y/n)[/bold yellow]", choices=["y", "n"]) == "n"):
                    break
        else:
            # 输出前置步骤说明
            steps = (
                "0. 请在 [bold yellow]config.json[/bold yellow] 内启用 [bold yellow]messagePush[/bold yellow]"
            )
            console.print(Panel(steps, title="未启用消息推送", expand=False, style="bold red"))
            exit

    elif choice == "4":
        print_github_action_config()

    elif choice == "5":
        print_github_action_push_config()

if __name__ == "__main__":
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="DouYin Spark Flow 工具")
    parser.add_argument(
        "--doTask",  # 参数名
        action="store_true",  # 如果提供该参数，则值为 True；否则为 False
        help="是否直接运行任务（默认为 False）",
    )
    args = parser.parse_args()

    if args.doTask:
        from core.tasks import runTasks
        asyncio.run(runTasks())
    else:
        main()
