# cron_tools.py
import uuid
import json
import os

CRON_FILE = "cron_jobs.json"

def load_cron_jobs():
    if not os.path.exists(CRON_FILE):
        return []
    with open(CRON_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_cron_jobs(cron_jobs):
    with open(CRON_FILE, "w", encoding="utf-8") as f:
        json.dump(cron_jobs, f, ensure_ascii=False, indent=2)

def create_cron_job(cron_expr,plan_desc, task_desc):
    '''
    创建新的定时任务
    param cron_expr: cron表达式，如 "0 15 * * *"
    param plan_desc: 任务的时间计划描述
    param task_desc: 任务描述（除去定时信息之外）
    返 回: 成功消息
    '''
    jobs = load_cron_jobs()
    job = {
        "id": str(uuid.uuid4()),
        "cron": cron_expr,
        "desc": task_desc,
        "plan": plan_desc,
        "enabled": True,
    }
    jobs.append(job)
    save_cron_jobs(jobs)
    return f"定时任务创建成功: {job['desc']} | 表达式: {cron_expr} | ID: {job['id']}"

def list_cron_jobs():
    '''
    列出所有定时任务
    返 回: 任务列表字符串
    '''
    jobs = load_cron_jobs()
    return "\n".join([f"ID:{j['id']}, 时程:{j['cron']}, 描述:{j['desc']}, 状态:{'启用' if j['enabled'] else '禁用'}" for j in jobs]) or "暂无定时任务"

def update_cron_job(job_id, **kwargs):
    '''
    更新定时任务
    param job_id: 任务ID
    param kwargs: 可更新的字段，如 cron, desc, enabled
    返 回: 成功消息
    '''
    jobs = load_cron_jobs()
    for job in jobs:
        if job['id'] == job_id:
            job.update(kwargs)
            save_cron_jobs(jobs)
            return f"任务 {job_id} 已更新！"
    return f"未找到任务 ID: {job_id}"

def delete_cron_job(job_id):
    '''
    删除定时任务
    param job_id: 任务ID
    返 回: 成功消息'''
    jobs = load_cron_jobs()
    jobs = [j for j in jobs if j['id'] != job_id]
    save_cron_jobs(jobs)
    return f"任务已删除(ID:{job_id})"