#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dispatch.py — H3完美动作迁移 派发器
RunningHub workflow 2105103613914865665《MiniMaxH3动作迁移 人物角色替换》(Leon)

用法:
  python3 dispatch.py --probe                       # 免费探针 (803=可派)
  python3 dispatch.py --upload <file>               # 上传图片/视频, 返回 openapi/... fileName
  python3 dispatch.py --card <fileName> --video <fileName> --prompt "..." --width 576 --height 1024
  python3 dispatch.py --query <taskId>              # 查任务状态/结果

只装五样: 8.image / 22.video / 28.prompt / 28.width+height / 26.width+height
实例固定 Standard (instanceType=default)。其余全用流内默认, 时长默认 10 秒。
"""
import sys, os, json, argparse, urllib.request, mimetypes
sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request

BASE = "https://www.runninghub.cn"
WF = "2105103613914865665"
CRED = "custom.runninghub"
UA = "h3-perfect-motion-transfer/1.0"

def post_json(path, payload, timeout=30):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json", "User-Agent": UA}, method="POST")
    add_surrogate_to_request(req, CRED, allowed_hosts=["www.runninghub.cn"])
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))

def probe():
    r = post_json(f"/openapi/v2/run/workflow/{WF}",
                  {"nodeInfoList": [{"nodeId": "999999", "fieldName": "nope", "fieldValue": "probe"}],
                   "instanceType": "default", "usePersonalQueue": False})
    ec, em = r.get("errorCode"), str(r.get("errorMessage"))
    print(f"probe: errorCode={ec} {em[:120]}")
    return 0 if ec == "803" else 1

def upload_media(path):
    path = os.path.expanduser(path)
    with open(path, "rb") as f:
        data = f.read()
    boundary = "----mt" + os.urandom(8).hex()
    fname = os.path.basename(path)
    ctype = mimetypes.guess_type(fname)[0] or "application/octet-stream"
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{fname}\"\r\n"
            f"Content-Type: {ctype}\r\n\r\n").encode() + data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(BASE + "/openapi/v2/media/upload/binary", data=body,
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}",
                                          "User-Agent": UA}, method="POST")
    add_surrogate_to_request(req, CRED, allowed_hosts=["www.runninghub.cn"])
    with urllib.request.urlopen(req, timeout=180) as resp:
        r = json.loads(resp.read().decode("utf-8"))
    fn = (r.get("data") or {}).get("fileName")
    if not fn:
        raise RuntimeError(f"upload failed: {json.dumps(r)[:300]}")
    print(f"[+] uploaded {path} -> {fn} ({len(data)//1024}KB)", flush=True)
    return fn

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--upload", metavar="FILE")
    ap.add_argument("--query", metavar="TASKID")
    ap.add_argument("--card", help="uploaded fileName -> 8.image")
    ap.add_argument("--video", help="uploaded fileName -> 22.video")
    ap.add_argument("--prompt", default="", help="-> 28.prompt (背景参考词, 见 SKILL.md 模板)")
    ap.add_argument("--width", type=int, default=0, help="-> 28/26.width (按比例, 9:16=576)")
    ap.add_argument("--height", type=int, default=0, help="-> 28/26.height (9:16=1024)")
    a = ap.parse_args()
    if a.probe:
        return probe()
    if a.upload:
        print(upload_media(a.upload))
        return 0
    if a.query:
        r = post_json("/openapi/v2/query", {"taskId": a.query}, timeout=20)
        print(json.dumps(r, ensure_ascii=False)[:1500])
        return 0
    nodes = []
    if a.card:
        nodes.append({"nodeId": "8", "fieldName": "image", "fieldValue": a.card})
    if a.video:
        nodes.append({"nodeId": "22", "fieldName": "video", "fieldValue": a.video})
    if a.prompt:
        nodes.append({"nodeId": "28", "fieldName": "prompt", "fieldValue": a.prompt})
    if a.width and a.height:
        for nid in ("28", "26"):
            nodes.append({"nodeId": nid, "fieldName": "width", "fieldValue": a.width})
            nodes.append({"nodeId": nid, "fieldName": "height", "fieldValue": a.height})
    if not nodes:
        print("nothing to dispatch")
        return 1
    print("nodeInfoList:", json.dumps(nodes, ensure_ascii=False))
    r = post_json(f"/openapi/v2/run/workflow/{WF}",
                  {"nodeInfoList": nodes, "instanceType": "default", "usePersonalQueue": False}, timeout=60)
    print(json.dumps(r, ensure_ascii=False)[:800])
    tid = r.get("taskId")
    if tid:
        print("TASKID:", tid)
    return 0

if __name__ == "__main__":
    sys.exit(main())
