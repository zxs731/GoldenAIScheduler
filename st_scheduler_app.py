# st_app_react.py
import streamlit as st
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


# 启动后台 scheduler 线程
from scheduler_runner import start_scheduler
import threading
from agen_chat import chat_stream

# 启动 apscheduler 后台线程（建议只启动一次）
if "scheduler_started" not in st.session_state:
    start_scheduler()
    st.session_state["scheduler_started"] = True


PRESET_QUESTIONS = [
    "当前黄金价格是多少？",
    "最近一周黄金价格走势如何？",
    "帮我分析下近期黄金投资策略。",
    "每天下午3点，发送最新黄金分析到我的邮箱。",
    "创建定时任务：每2分钟发送黄金价格到邮箱"
]


st.markdown("""
    <style>
        .stSidebar button {
            justify-content: flex-start !important;
            text-align: left !important;
        }
    </style>
""", unsafe_allow_html=True)
st.title("🚩主动AI黄金管家")

# ---- 新增侧边栏代码 ----
st.sidebar.header("常规任务")
for q in PRESET_QUESTIONS:
    if st.sidebar.button(q, key=q):
        st.session_state["preset_ask"] = q
        st.rerun()
        break

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "你好！我是你的黄金投资分析助手，有什么我可以帮你的吗？"}
    ]

prompt = None
if st.session_state.get("preset_ask"):
    prompt = st.session_state["preset_ask"]
    st.session_state["preset_ask"] = ""

input_prompt = st.chat_input(placeholder="请输入你的问题...")
prompt = prompt if prompt else input_prompt

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        slot = st.empty()
        slot.write("⏳...")
        def streamer():
            for chunk in chat_stream(st.session_state.messages):
                yield chunk
        full_response = slot.write_stream(streamer(), cursor="▍")
        st.session_state.messages.append({"role": "assistant", "content": full_response})