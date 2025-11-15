# scheduler_runner.py
from apscheduler.schedulers.background import BackgroundScheduler
from cron_tools import load_cron_jobs
import threading
import time
from agen_chat import chat_stream

def parse_cron_args(cron_expr):
    '''
    "0 15 * * *" => {"minute": 0, "hour": 15, ...}
    '''
    parts = cron_expr.split()
    return {
        "minute": parts[0],
        "hour": parts[1],
        "day": parts[2],
        "month": parts[3],
        "day_of_week": parts[4]
    }

def agent_runner(task_desc):
    # 你的 Agent 任务逻辑，例如发送黄金价格到邮箱等
    print(f"[定时任务触发] 执行任务: {task_desc}")

    history = [{"role": "user", "content": task_desc}]
    result = ""
    for chunk in chat_stream(history):
        result += chunk
    
    print(f"[任务完成，结果已处理]\n{result}")

def schedule_all_jobs(scheduler):
    scheduler.remove_all_jobs()
    all_jobs = load_cron_jobs()
    for job in all_jobs:
        if job.get("enabled", True):
            scheduler.add_job(
                agent_runner,
                "cron",
                args=[job["desc"]],
                id=job["id"],
                **parse_cron_args(job["cron"])
            )

def scheduler_thread():
    scheduler = BackgroundScheduler()
    schedule_all_jobs(scheduler)
    scheduler.start()
    print("定时任务后台线程 running...")
    while True:
        # 可定时 reload 任务池
        schedule_all_jobs(scheduler)
        time.sleep(30)

# 建议在 __main__ 入口启动：
def start_scheduler():
    threading.Thread(target=scheduler_thread, daemon=True).start()