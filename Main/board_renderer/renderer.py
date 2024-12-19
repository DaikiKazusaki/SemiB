import tempfile
import os
import http.server
import socketserver

PORT = 8000

def render(moves):
    with tempfile.TemporaryDirectory() as dname:
        _create_page(dname, moves)
        print(dname)
        # リクエストハンドラ
        class _Handler(http.server.SimpleHTTPRequestHandler):
            def translate_path(self, path):
                path = super().translate_path(path)
                return os.path.join(dname, os.path.relpath(path, start=os.getcwd()))
        with socketserver.TCPServer(("", PORT), _Handler) as httpd:
            print(f'Please Access localhost:{PORT}.')
            httpd.serve_forever()

def _create_page(dname, moves):
    if (not os.path.exists(dname)):
        raise FileNotFoundError(dname)
    INDEX_FILE = 'index.html'
    JS_FILE = 'script.js'
    JS_DIRECTORY = 'js'
    index_path = os.path.join(dname, INDEX_FILE)
    js_path = os.path.join(dname, JS_DIRECTORY, JS_FILE)
    js_relpath = os.path.join(JS_DIRECTORY, JS_FILE)
    os.makedirs(os.path.join(dname, JS_DIRECTORY), exist_ok=True)
    # index.htmlの作成
    with open(index_path, mode='w', encoding='utf-8') as f:
        f.write(
f"""\
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8"/>
        <script type="importmap">
            {{
                "imports": {{
                    "three": "https://cdn.jsdelivr.net/npm/three@0.171.0/build/three.module.js"
                }}
            }}
        </script>
        <script type="module" src="{js_relpath}"></script>
    </head>
    <body>
        <canvas id="myCanvas"></canvas>
    </body>
</html>
"""
        )
    # script.jsの作成
    with open(js_path, mode='w', encoding='utf-8') as f:
        f.write(
f"""\
console.log('test');
"""
        )

##### 以下は開発用に書いているだけで、本来は使用しない
if __name__ == "__main__":
    sample_move = [
        [0, 0, 0],
        [0, 0, 1],
        [0, 0, 2],
        [0, 0, 3]
    ]
    render(sample_move)