import json
import threading
import unittest
import urllib.error
import urllib.request

from quotaborrow import Allocator
from server import serve

class TestAllocator(unittest.TestCase):
    def test_first_request(self):
        self.assertTrue(Allocator().request("a", 10)["granted"])

    def test_over_base_rejected(self):
        allocator = Allocator(100, 20)
        allocator.request("a", 20)
        self.assertFalse(allocator.request("a", 10)["granted"])

    def test_release_frees(self):
        allocator = Allocator(100, 20)
        allocator.request("a", 20)
        self.assertEqual(allocator.release("a", 20)["used"], 0)

    def test_stats_shape(self):
        self.assertIn("pool", Allocator().stats())

    def test_http_request(self):
        server = serve(0)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = "http://127.0.0.1:%d" % server.server_port
        with urllib.request.urlopen(base + "/request", data=b'{"tenant": "a", "amount": 10}',
                                    timeout=5) as response:
            self.assertTrue(json.loads(response.read())["granted"])
        server.shutdown()
