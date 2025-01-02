import tempfile
import os
import http.server
import socketserver
import threading
import time
import webbrowser

PORT = 8000

# 全ての手をアニメーションで表示する
#   moves: スタートからゲームオーバーまでの全手を二次元のリスト形式で持つ(縦・横で、高さは持たない)
#           eg. [[0, 0], [0, 1], [1, 0], ...]
#   interval: アニメーションの切り替わり間隔(msec)
#   browse: ローカルホストを立ち上げてブラウザで閲覧するかどうか
def render(moves, interval=1000, browse=False):
    if not browse:
        RESULT_DIR = 'result'
        os.makedirs(RESULT_DIR, exist_ok=True)
        _create_page(RESULT_DIR, moves, interval)
    else:
        with tempfile.TemporaryDirectory() as dname:
            _create_page(dname, moves, interval)
            # リクエストハンドラ
            class _Handler(http.server.SimpleHTTPRequestHandler):
                def translate_path(self, path):
                    path = super().translate_path(path)
                    return os.path.join(dname, os.path.relpath(path, start=os.getcwd()))
            # サーバーを開始する関数
            def start_server():
                with socketserver.TCPServer(("", PORT), _Handler) as httpd:
                    print(f'Please Access localhost:{PORT}.')
                    httpd.serve_forever()
            # サーバーをバックグラウンド実行
            def run_server_background():
                thread = threading.Thread(target=start_server)
                thread.daemon = True            # メインプログラム終了とともに終了
                thread.start()
            # ブラウザ表示
            def open_in_browser():
                time.sleep(1)                   # サーバー起動まで待機
                webbrowser.open(f'http://localhost:{PORT}')
            run_server_background()
            open_in_browser()
            input('Press Enter to quit...')     # サーバーを終了させないために

# ブラウザに表示するためのhtml,jsファイルを生成する
def _create_page(dname, moves, interval):
    if (not os.path.exists(dname)):
        raise FileNotFoundError(dname)
    INDEX_FILE = 'index.html'
    index_path = os.path.join(dname, INDEX_FILE)
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
    </head>
    <body>
        <canvas id="board" width="800" height="800" style="border: 1px solid black;"></canvas>
        <script type="module">
            import * as THREE from 'three';
            import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';
            import {{ TextGeometry }} from 'three/addons/geometries/TextGeometry.js';
            import {{ FontLoader }} from 'three/addons/loaders/FontLoader.js';

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
                isGameOver: false,// ゲームが終わったか
            }};

            App.isMyTurn = function() {{
                return App.turnCount % 2 == 0;
            }}

            App.init = function() {{
                const canvas = document.querySelector("#board");

                // カメラの設定
                App.camera = new THREE.PerspectiveCamera(75, canvas.width / canvas.height, 1, 10000);
                App.camera.position.set(7, 7, 10);
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
                const gridSize = 4;
                const leftBound = -5.0;
                const rightBound = -leftBound;
                const gap = (rightBound - leftBound) / (gridSize - 1);
                const baseMaterial = new THREE.MeshLambertMaterial({{ color: 0xadff2f }});
                const baseGeometry = new THREE.BoxGeometry(rightBound - leftBound + 2, 1, rightBound - leftBound + 2);
                const base = new THREE.Mesh(baseGeometry, baseMaterial);
                base.position.y = -2.5;
                App.scene.add(base);

                // 球体と棒を描画
                const rodMaterialDefault = new THREE.MeshLambertMaterial({{ color: 0x0000ff }});
                const rodMaterialHighlight = new THREE.MeshLambertMaterial({{ color: 0x00ffff }});
                const sphereRadius = 0.55;
                const whiteMaterial = new THREE.MeshPhongMaterial({{ color: 0xffffff }});
                const blackMaterial = new THREE.MeshPhongMaterial({{ color: 0x000000 }});
                const setRodsDefaultColor = function() {{
                    App.rods.forEach(rod => rod.material = rodMaterialDefault);
                }};
                const setRodHighLight = function(x, z) {{
                    setRodsDefaultColor();  // 一旦デフォルト色
                    App.rods.filter(
                        function(rod) {{
                            return rod.userData.x == x && rod.userData.z == z;
                        }}
                    ).forEach(selectedRod => selectedRod.material = rodMaterialHighlight);
                }};


                App.board = Array.from({{ length: gridSize }}, () =>
                    Array.from({{ length: gridSize }}, () => Array(gridSize).fill(0))
                );

                for (let x = 0; x < gridSize; x++) {{
                    for (let z = 0; z < gridSize; z++) {{
                        // 棒の作成
                        const rodHeight = gridSize + 1;
                        const rodGeometry = new THREE.CylinderGeometry(0.2, 0.2, rodHeight, 16);
                        const rod = new THREE.Mesh(rodGeometry, rodMaterialDefault);
                        rod.position.set(leftBound + gap * x, 0, leftBound + gap * z);
                        rod.userData = {{ x, z, spheres: 0 }}; // 棒の状態を追跡
                        App.scene.add(rod);
                        App.rods.push(rod);
                    }}
                }}

                // // X軸, Y軸, Z軸の描画
                // const axisMaterial = new THREE.LineBasicMaterial({{ color: 0x000000 }});
                // const xPoints = [];
                // xPoints.push( new THREE.Vector3(leftBound - 3, -3, leftBound - 3) );
                // xPoints.push( new THREE.Vector3(rightBound + 3, -3, leftBound - 3) );
                // const xGeometry = new THREE.BufferGeometry().setFromPoints(xPoints);
                // const xLine = new THREE.Line(xGeometry, axisMaterial);
                // App.scene.add(xLine);
                // const yPoints = [];
                // yPoints.push( new THREE.Vector3(leftBound - 3, -3, leftBound - 3) );
                // yPoints.push( new THREE.Vector3(leftBound - 3, 7, leftBound - 3) );
                // const yGeometry = new THREE.BufferGeometry().setFromPoints(yPoints);
                // const yLine = new THREE.Line(yGeometry, axisMaterial);
                // App.scene.add(yLine);
                // const zPoints = [];
                // zPoints.push( new THREE.Vector3(leftBound - 3, -3, leftBound - 3) );
                // zPoints.push( new THREE.Vector3(leftBound - 3, -3, rightBound + 3) );
                // const zGeometry = new THREE.BufferGeometry().setFromPoints(zPoints);
                // const zLine = new THREE.Line(zGeometry, axisMaterial);
                // App.scene.add(zLine);
                // // X, Y, Zの文字
                // const loader = new FontLoader();
                // const labelMaterial = new THREE.MeshNormalMaterial();

                // loader.load('fonts/Roboto_Regular.json', function ( font ) {{
                    // const xLabelGeometry = new TextGeometry( 'X', {{
                        // font: font,
                        // size: 1,
                        // depth: 0.25,
                    // }} );
                    // xLabelGeometry.center();
                    // const xLabel = new THREE.Mesh(xLabelGeometry, labelMaterial);
                    // xLabel.position.set(rightBound + 4, -3, leftBound - 3);
                    // App.scene.add(xLabel);
                    // const yLabelGeometry = new TextGeometry( 'Y', {{
                        // font: font,
                        // size: 1,
                        // depth: 0.25,
                    // }} );
                    // yLabelGeometry.center();
                    // const yLabel = new THREE.Mesh(yLabelGeometry, labelMaterial);
                    // yLabel.position.set(leftBound - 3, 8, leftBound - 3);
                    // App.scene.add(yLabel);
                    // const zLabelGeometry = new TextGeometry( 'Z', {{
                        // font: font,
                        // size: 1,
                        // depth: 0.25,
                    // }} );
                    // zLabelGeometry.center();
                    // const zLabel = new THREE.Mesh(zLabelGeometry, labelMaterial);
                    // zLabel.position.set(leftBound - 3, -3, rightBound + 4);
                    // App.scene.add(zLabel);
                // }} );

                // 照明を追加（明るく設定）
                const ambientLight = new THREE.AmbientLight(0xaaaaaa, 1); // 環境光
                App.scene.add(ambientLight);

                // const pointLight = new THREE.PointLight(0xffffff, 2); // 点光源（強度を2倍）
                // pointLight.position.set(10, 15, 10);
                // App.scene.add(pointLight);

                const dirLight = new THREE.DirectionalLight(0xffffff, 1);
                App.scene.add(dirLight);
            }};

            // 表示の更新
            App.animate = function() {{
                requestAnimationFrame(App.animate);

                // カメラ操作を反映
                App.controls.update();

                // 再描画
                App.renderer.render(App.scene, App.camera);
            }};

        </script>
    </body>
</html>
"""
        )

##### 以下は開発用に書いているだけで、本来は使用しない
if __name__ == "__main__":
    sample_move = [
        [0, 1],
        [3, 2],
        [1, 3],
        [2, 0]
    ]
    render(sample_move, interval=20000)