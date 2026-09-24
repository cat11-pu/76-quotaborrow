"""check_http.py：起服务、按脚本走一圈，打印验收面。"""
import json
import sys
import threading
import urllib.error
import urllib.request

from server import serve


def call(method, url, body=None):
    request = urllib.request.Request(url, data=body, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode()


def parse(text):
    try:
        return json.loads(text)
    except Exception:
        return {"_raw": (text or "")[:60]}


def main() -> int:
    spec = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "sample/requests.json", encoding="utf-8"))
    server = serve(0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d" % server.server_port
    grants = []
    for step in spec["ops"]:
        route = step["op"]
        result = parse(call("POST", base + "/" + route, json.dumps(step).encode())[1])
        if route == "request":
            grants.append((step["tenant"], result.get("granted"), result.get("used")))
    stats = parse(call("GET", base + "/")[1])
    recovered = parse(call("POST", base + "/recover", b"{}")[1])
    print("请求判定 =", grants)
    print("各租户用量 =", stats.get("used"))
    print("借出的量 =", stats.get("borrowed"))
    print("被拒绝的请求数 =", stats.get("rejected"))
    print("抢占归还次数 =", stats.get("preemptions"))
    print("池总配额 =", stats.get("pool"))
    print("恢复后的用量 =", recovered.get("used"))
    print("恢复后的借用量 =", recovered.get("borrowed"))
    print("不变量（总用量不超过池配额） =", spec["pool_invariant"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
