import datetime
import akshare as ak
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import json
import os
from dotenv import load_dotenv
load_dotenv()
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.agents.middleware import TodoListMiddleware
from cron_tools import (
    create_cron_job, list_cron_jobs, update_cron_job, delete_cron_job
)
from utils import parse_nl_to_cron
def get_current_time()-> str:
    '''获取当前时间'''
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return now  

def get_gold_price()-> str:
    '''获取当前黄金价格'''
    macro_china_au_report_df = ak.spot_quotations_sge()
    return macro_china_au_report_df.to_string()

def get_history_gold_price()-> str:
    '''获取历史黄金价格'''
    macro_china_au_report_df = ak.macro_china_au_report()
    au100g_df = macro_china_au_report_df[macro_china_au_report_df['商品'] == 'Au100g']
    # 转换日期格式
    au100g_df['日期'] = pd.to_datetime(au100g_df['日期'])

    # 按日期升序排序
    au100g_df_sorted = au100g_df.sort_values(by='日期', ascending=False)
    result_df = au100g_df_sorted[['日期','商品', '开盘价', '收盘价']].head(60)
    return result_df.to_string()

def send_email(subject: str, body: str)-> str:
    '''
    发送邮件到我的邮箱（目标邮箱地址已内置，无需提供）
    param subject: 邮件主题
    param body: 邮件内容
    返 回: 发送结果字符串
    '''
    # 邮箱配置
    smtp_server = 'smtp.qq.com'
    smtp_port = 465  # SSL端口
    username = os.environ["email_sender"]  # 发件人邮箱
    password = os.environ["email_key"]  # 邮箱密码或授权码

    # 邮件内容
    sender = username
    receiver = os.environ["email_to"]   # 收件人邮箱
    subject = "Finance AI: "+subject
    body = body

    # 构建邮件
    message = MIMEText(body, 'plain', 'utf-8')
    message['From'] = Header(sender)
    message['To'] = Header(receiver)
    message['Subject'] = Header(subject)

    try:
        # 连接SMTP服务器（SSL加密）
        smtp = smtplib.SMTP_SSL(smtp_server, smtp_port)
        smtp.login(username, password)
        smtp.sendmail(sender, [receiver], message.as_string())
        smtp.quit()
        return "邮件发送成功！"

    except Exception as e:
        return f"邮件发送失败：{e}"

def chat_stream(history_json):
    messages = history_json[-10:]

    model_instance = ChatOpenAI(
        base_url=os.environ["openai_base_url"],
        openai_api_key=os.environ["openai_api_key"],
        model=os.environ["model"]
    )
    agent = create_agent(
        model=model_instance,
        system_prompt=(
            "你是一个模拟人类大脑的Agent。你的任务是不断地思考、质疑、验证、提出新假设。深入思考用户真实需求，能转换为分步调用工具解决用户问题。每次得到工具的反馈后，你都要提出新的问题或反思，持续这个过程，直到得到满意的结果。"
        ),
        tools=[
            get_current_time, get_gold_price, get_history_gold_price, send_email,
            create_cron_job, list_cron_jobs, update_cron_job, delete_cron_job,
            parse_nl_to_cron
        ],
        #middleware=[TodoListMiddleware()],
    )
    full = ""
    for chunk,metadata in agent.stream(
        {"messages": messages},
        stream_mode="messages"
    ):
        if metadata["langgraph_node"]=="model":
            print(chunk.content, end='', flush=True)
            full += chunk.content
            yield chunk.content
    return full