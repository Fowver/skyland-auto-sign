import base64
import hashlib
import hmac
import logging
import os
import time
from datetime import date

import requests


def push_feishu(all_logs: list[str]):
    """通过飞书自定义机器人发送签到结果。"""
    webhook_url = os.getenv('FEISHU_WEBHOOK_URL', '').strip()
    if not webhook_url:
        return False

    title = f'森空岛自动签到结果 - {date.today():%Y-%m-%d}'
    content = '\n'.join(all_logs) if all_logs else '今日无可用账号或无输出'
    data = {
        'msg_type': 'interactive',
        'card': {
            'header': {'title': {'tag': 'plain_text', 'content': title}},
            'elements': [
                {'tag': 'div', 'text': {'tag': 'lark_md', 'content': content}}
            ],
        },
    }

    # 飞书机器人开启签名校验时才附加签名。
    if secret := os.getenv('FEISHU_SECRET', '').strip():
        timestamp = str(int(time.time()))
        digest = hmac.new(
            f'{timestamp}\n{secret}'.encode('utf-8'), digestmod=hashlib.sha256
        ).digest()
        data.update(timestamp=timestamp, sign=base64.b64encode(digest).decode('utf-8'))

    try:
        response = requests.post(webhook_url, json=data, timeout=10)
        response.raise_for_status()
        result = response.json()
        if result.get('code', result.get('StatusCode')) == 0:
            logging.info('飞书通知发送成功')
            return True
        error_message = result.get('msg') or result.get('StatusMessage') or '未知错误'
        logging.error(f'飞书通知发送失败：{error_message}')
    except Exception as e:
        logging.error('发送飞书通知时发生错误', exc_info=e)
    return False
