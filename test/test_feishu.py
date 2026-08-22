import base64
import hashlib
import hmac
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from push.feishu import push_feishu


class FeishuNotificationTest(unittest.TestCase):
    @patch.dict(os.environ, {'FEISHU_WEBHOOK_URL': 'https://example.com/hook', 'FEISHU_SECRET': 'test-secret'})
    @patch('push.feishu.time.time', return_value=1700000000)
    @patch('push.feishu.requests.post')
    def test_send_signed_card(self, post, _time):
        post.return_value.json.return_value = {'code': 0}

        self.assertTrue(push_feishu(['签到成功']))

        payload = post.call_args.kwargs['json']
        expected_sign = base64.b64encode(
            hmac.new(b'1700000000\ntest-secret', digestmod=hashlib.sha256).digest()
        ).decode('utf-8')
        self.assertEqual(payload['sign'], expected_sign)
        self.assertEqual(payload['card']['elements'][0]['text']['content'], '签到成功')
        post.assert_called_once_with('https://example.com/hook', json=payload, timeout=10)


if __name__ == '__main__':
    unittest.main()
