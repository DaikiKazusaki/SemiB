import tempfile
import os
import http.server
import socketserver

PORT = 8000

# 全ての手をアニメーションで表示する
def render(moves, browse=False):
    if not browse:
        _create_page('.', moves)
    else:
        with tempfile.TemporaryDirectory() as dname:
            _create_page(dname, moves)
            # リクエストハンドラ
            class _Handler(http.server.SimpleHTTPRequestHandler):
                def translate_path(self, path):
                    path = super().translate_path(path)
                    return os.path.join(dname, os.path.relpath(path, start=os.getcwd()))
            with socketserver.TCPServer(("", PORT), _Handler) as httpd:
                print(f'Please Access localhost:{PORT}.')
                httpd.serve_forever()
                print('test')

# ブラウザに表示するためのhtml,jsファイルを生成する
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
                    "three": "https://cdn.jsdelivr.net/npm/three@0.171.0/build/three.module.js",
                    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.171.0/examples/jsm/"
                }}
            }}
        </script>
        <script type="module" src="{js_relpath}"></script>
    </head>
    <body>
        <canvas id="CANVAS1" width="800" height="800" style="border: 1px solid black;"></canvas>
    </body>
</html>
"""
        )
    # script.jsの作成
    with open(js_path, mode='w', encoding='utf-8') as f:
        f.write(
f"""\
import * as THREE from 'three';
import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';

window.onload = event => {{
    // 初期化
    App.init();
    // アニメーションの表示開始
    App.animate();
}};

const App = {{
    camera: null,     // カメラ
    scene: null,      // シーン
    renderer: null,   // 描画処理
    controls: null,   // カメラ操作用コントロール
    rods: [],         // 棒の配列
    board: [],        // 現在の盤面 (4×4×4形式)
    clickLog: [],     // クリックした棒の記録
    turnCount: 0,     // ターン数（奇数・偶数を判定）
}};

App.init = function() {{
    const canvas = document.querySelector('#CANVAS1');

    // カメラの設定
    App.camera = new THREE.PerspectiveCamera(75, canvas.width / canvas.height, 1, 10000);
    App.camera.position.set(7, 7, 15);
    App.scene = new THREE.Scene();

    // 背景色の設定
    App.renderer = new THREE.WebGLRenderer({{ canvas: canvas }});
    App.renderer.setClearColor(0xf0f8ff); // アリスブルー
    App.renderer.setSize(canvas.width, canvas.height);

    // カメラ操作のコントロール
    App.controls = new OrbitControls(App.camera, canvas);
    App.controls.enableDamping = true; // 慣性を有効にする
    App.controls.dampingFactor = 0.1;

    // 基板の追加（淡い緑色）
    const baseMaterial = new THREE.MeshLambertMaterial({{ color: 0xadff2f }});
    const baseGeometry = new THREE.BoxGeometry(8, 1, 8);
    const base = new THREE.Mesh(baseGeometry, baseMaterial);
    base.position.y = -2.5;
    App.scene.add(base);

    // 球体と棒を描画
    const gridSize = 4;
    const rodMaterialDefault = new THREE.MeshLambertMaterial({{ color: 0x0000ff }});
    const rodMaterialHighlight = new THREE.MeshLambertMaterial({{ color: 0x00ffff }});
    const sphereRadius = 0.55;
    const whiteMaterial = new THREE.MeshPhongMaterial({{ color: 0xffffff }});
    const blackMaterial = new THREE.MeshPhongMaterial({{ color: 0x000000 }});

    App.board = Array.from({{ length: gridSize }}, () =>
        Array.from({{ length: gridSize }}, () => Array(gridSize).fill(0))
    );

    for (let x = 0; x < gridSize; x++) {{
        for (let z = 0; z < gridSize; z++) {{
            // 棒の作成
            const rodHeight = gridSize + 1;
            const rodGeometry = new THREE.CylinderGeometry(0.2, 0.2, rodHeight, 16);
            const rod = new THREE.Mesh(rodGeometry, rodMaterialDefault);
            rod.position.set(2*x - 3, 0, 2*z - 3);
            rod.userData = {{ x, z, spheres: 0 }}; // 棒の状態を追跡
            App.scene.add(rod);
            App.rods.push(rod);
        }}
    }}

    // 照明を追加（明るく設定）
    const ambientLight = new THREE.AmbientLight(0xaaaaaa, 1); // 環境光
    App.scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0xffffff, 2); // 点光源（強度を2倍）
    pointLight.position.set(10, 15, 10);
    App.scene.add(pointLight);

}};

// 表示の更新
App.animate = function() {{
    requestAnimationFrame(App.animate);

    // カメラ操作を反映
    App.controls.update();

    // 再描画
    App.renderer.render(App.scene, App.camera);
}};
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