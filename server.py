#!/usr/bin/env python3
"""
Arui Portfolio Server — serves static files + JSON data persistence API + image upload.
Usage: python3 server.py [--port 8765]
"""
import json
import os
import sys
import time
import uuid
import cgi
import base64
import argparse
import urllib.request
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')

DEFAULT_DATA = {
    "works": [
        {"id":1,"title":"JunyStar-Web Design","category":"网页设计","link":"https://www.zcool.com.cn/work/ZNzMzNzE1NTI=.html","thumb":"https://img.zcool.cn/community/69ca0ca586e7bp8sef9087620.png?k=a71d328954003528b94c7a151fb81da8&t=6a302180"},
        {"id":2,"title":"2024季度部分作品整理","category":"APP设计","link":"https://www.zcool.com.cn/work/ZNzAyMjkyNDA=.html","thumb":"https://img.zcool.cn/community/66bf132e37386x3wd6phr45216.png?k=873b75c118beaf868940798f10836de5&t=6a302180"},
        {"id":3,"title":"数藏交流平台-Digital Link","category":"APP设计","link":"https://www.zcool.com.cn/work/ZNjc2MTM5NDQ=.html","thumb":"https://img.zcool.cn/community/031fovecdy8oufiyrwdhlbc3231.png?k=5365554b27b1effa70918cc12512219f&t=6a302180"},
        {"id":4,"title":"It's Me APP","category":"APP设计","link":"https://www.zcool.com.cn/work/ZNjc1NjA4MDA=.html","thumb":"https://img.zcool.cn/community/031j5civkdef3ol4oro08tq3536.png?k=8dd84fc1f8b7569eea99661472399bdb&t=6a302180"},
        {"id":5,"title":"HMI Concept Design-2023","category":"HMI设计","link":"https://www.zcool.com.cn/work/ZNjczMjEzMjg=.html","thumb":"https://img.zcool.cn/community/031ntfqe48b0q6namycrn1n3334.png?k=ddcf0b582fde83d942c42447c9d8d4b7&t=6a302180"},
        {"id":6,"title":"2022 设计作品合集","category":"综合设计","link":"https://www.zcool.com.cn/work/ZNjQ0Mjk2MDA=.html","thumb":"https://img.zcool.cn/community/0311esuwxi9z9bpryney0e93332.png?k=73fb426fff3073b0eaf604d25f5139c5&t=6a302180"},
        {"id":7,"title":"MOTA 饮水智能面板方案设计","category":"智能硬件","link":"https://www.zcool.com.cn/work/ZNjQzMDY4NzI=.html","thumb":"https://img.zcool.cn/community/031cdn8ibxxarryydglvhjj3938.png?k=5f416a89e08d93a87ea3a2af37b25b3f&t=6a302180"},
        {"id":8,"title":"About-网页设计集","category":"网页设计","link":"https://www.zcool.com.cn/work/ZNjIwNTE1NjA=.html","thumb":"https://img.zcool.cn/community/031ny6e4t6jigh0odporbn43838.png?k=d4a376d217ac455cead631d682a9bd99&t=6a302180"},
        {"id":9,"title":"About-B端项目合集","category":"B端设计","link":"https://www.zcool.com.cn/work/ZNjE4NDE1NzY=.html","thumb":"https://img.zcool.cn/community/031mdeexjvid9j6ii6kavth3230.png?k=82917779d7da8dd8533a75833daeb7ba&t=6a302180"},
        {"id":10,"title":"一些杂货整理","category":"综合设计","link":"https://www.zcool.com.cn/work/ZNjA3NDAwNDg=.html","thumb":"https://img.zcool.cn/community/031g8zjyiw4onwbnumex2wb3939.png?k=013f30592b993180235b7c5d84c2de3c&t=6a302180"},
        {"id":11,"title":"比亚迪车机主题设计-蓝色星河","category":"HMI设计","link":"https://www.zcool.com.cn/work/ZNjAyNTk1ODQ=.html","thumb":"https://img.zcool.cn/community/031regd3ttcu1qvpi9ceegd3035.png?k=f010d9fdfc87f509a8f3a2734e943c9b&t=6a302180"},
        {"id":12,"title":"空状态插画设计-飞书","category":"插画设计","link":"https://www.zcool.com.cn/work/ZNTk3MTE5OTI=.html","thumb":"https://img.zcool.cn/community/031pcs7wn8lrh4kckxo68qm3833.png?k=7757215993bd12ef5019ee6920f14a11&t=6a302180"},
        {"id":13,"title":"智选小程序-教学管理工具","category":"APP设计","link":"https://www.zcool.com.cn/work/ZNTYwMDc3NzY=.html","thumb":"https://img.zcool.cn/community/031i0eo3n0f4nlnexmpvfrj3235.png?k=ca2dae58484bed3aa561796439ce5338&t=6a302180"},
        {"id":14,"title":"云及数据大屏编辑平台","category":"B端设计","link":"https://www.zcool.com.cn/work/ZNTQ2MzgyOTI=.html","thumb":"https://img.zcool.cn/community/011fa96119e95f11013eaf70f2d098.jpg?k=db128bd155f61acf242f18d70fd38e1b&t=6a302180"},
        {"id":15,"title":"甲状腺健康管家APP","category":"APP设计","link":"https://www.zcool.com.cn/work/ZNTE2MTYxNDA=.html","thumb":"https://img.zcool.cn/community/01ea37605c549411013e87f41d5189.jpg?k=8e475df194293813e17109006a49923a&t=6a302180"}
    ],
    "profile": {
        "name": "阿睿",
        "title": "UI/UX Designer",
        "gender": "男",
        "age": 28,
        "email": "arui@example.com",
        "phone": "+86 138-0013-8000",
        "direction": "UI/UX设计师 · 产品设计师",
        "experience": "5年",
        "location": "北京",
        "bio": "专注APP、网页、车机及多领域数字体验设计,擅长将创意与用户需求结合,打造直观、美观且易用的产品界面。具备丰富的B端和C端项目经验,致力于通过设计提升产品价值和用户体验。",
        "avatar": None,
        "heroBadge": "UI/UX Designer",
        "heroNameLeft": "阿睿",
        "heroNameRight": "ARUI",
        "heroTagline": "专注APP、网页、车机及多领域数字体验设计，用创意连接用户与产品。",
        "brandLeft": "阿睿",
        "brandRight": "ARUI",
        "sectionLabel": "Selected Works",
        "sectionTitle": "作品集"
    },
    "categories": ["APP设计", "网页设计", "HMI设计", "B端设计", "智能硬件", "插画设计", "综合设计"]
}


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return json.loads(json.dumps(DEFAULT_DATA))


def save_data(data):
    # Merge-based save: load existing data, then overlay incoming data
    # This prevents partial saves from wiping other sections
    existing = load_data()
    merged = dict(existing)

    if 'works' in data:
        merged['works'] = data['works']
    if 'categories' in data:
        merged['categories'] = data['categories']
    if 'profile' in data:
        # Deep merge profile: keep existing fields if incoming ones are empty/missing
        existing_profile = merged.get('profile', {})
        incoming_profile = data['profile']
        merged_profile = dict(existing_profile)
        for key, value in incoming_profile.items():
            # Always update if value is non-empty/non-null, or if it's explicitly set
            if value is not None and value != '':
                merged_profile[key] = value
            elif key not in merged_profile:
                merged_profile[key] = value
        merged['profile'] = merged_profile

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/data':
            data = load_data()
            body = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def do_POST(self):
        if self.path == '/api/upload':
            # Handle multipart image upload — proxy to freeimage.host cloud
            try:
                content_type = self.headers.get('Content-Type', '')
                if 'multipart/form-data' not in content_type:
                    raise ValueError('Expected multipart/form-data')

                # Parse multipart form data
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={
                        'REQUEST_METHOD': 'POST',
                        'CONTENT_TYPE': content_type,
                    }
                )

                file_item = None
                if form.keys() and 'file' in form.keys():
                    file_item = form['file']
                if file_item is None or not file_item.filename:
                    raise ValueError('No file field found')

                # Read file data
                file_data = file_item.file.read()

                # Upload to freeimage.host cloud
                b64_data = base64.b64encode(file_data).decode('utf-8')
                cloud_params = urllib.parse.urlencode({
                    'source': b64_data,
                    'key': '6d207e02198a847aa98d0a2a901485a5',
                    'format': 'json'
                }).encode('utf-8')

                cloud_req = urllib.request.Request(
                    'https://freeimage.host/api/1/upload',
                    data=cloud_params,
                    method='POST'
                )
                cloud_resp = urllib.request.urlopen(cloud_req, timeout=30)
                cloud_result = json.loads(cloud_resp.read().decode('utf-8'))

                if cloud_result.get('status_code') == 200 and cloud_result.get('image', {}).get('url'):
                    url = cloud_result['image']['url']
                else:
                    raise ValueError(cloud_result.get('error', {}).get('message', 'Cloud upload failed'))

                resp = json.dumps({"ok": True, "url": url}).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(resp)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(resp)
            except Exception as e:
                err = json.dumps({"ok": False, "error": str(e)}).encode('utf-8')
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(err)))
                self.end_headers()
                self.wfile.write(err)
            return

        if self.path == '/api/data':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                save_data(data)
                resp = json.dumps({"ok": True}).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(resp)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(resp)
            except Exception as e:
                err = json.dumps({"ok": False, "error": str(e)}).encode('utf-8')
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(err)))
                self.end_headers()
                self.wfile.write(err)
            return
        super().do_POST()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        # Quieter logging
        if '/api/' in str(args[0]):
            sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), format % args))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    server = HTTPServer(('127.0.0.1', args.port), Handler)
    print(f'Server running at http://127.0.0.1:{args.port}')
    print(f'Data file: {DATA_FILE}')
    print(f'Upload dir: {UPLOAD_DIR}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down.')
        server.server_close()
