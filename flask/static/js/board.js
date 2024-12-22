import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

window.onload = event => {
    // 初期化
    App.init();
    // アニメーションの表示開始
    App.animate();
};

const App = {
    camera: null,     // カメラ
    scene: null,      // シーン
    renderer: null,   // 描画処理
    controls: null,   // カメラ操作用コントロール
    rods: [],         // 棒の配列
    board: [],        // 現在の盤面 (4×4×4形式)
    clickLog: [],     // クリックした棒の記録
    turnCount: 0,     // ターン数（奇数・偶数を判定）
};

App.isMyTurn = function() {
    return App.turnCount % 2 == 0;
}

App.init = function() {
    const canvas = document.querySelector("#board");

    // カメラの設定
    App.camera = new THREE.PerspectiveCamera(75, canvas.width / canvas.height, 1, 10000);
    App.camera.position.set(7, 7, 15);
    App.scene = new THREE.Scene();

    // 背景色の設定
    App.renderer = new THREE.WebGLRenderer({ canvas: canvas });
    App.renderer.setClearColor(0xf0f8ff); // アリスブルー
    App.renderer.setSize(canvas.width, canvas.height);

    // カメラ操作のコントロール
    App.controls = new OrbitControls(App.camera, canvas);
    App.controls.enableDamping = true; // 慣性を有効にする
    App.controls.dampingFactor = 0.1;

    // 基板の追加（淡い緑色）
    const baseMaterial = new THREE.MeshLambertMaterial({ color: 0xadff2f });
    const baseGeometry = new THREE.BoxGeometry(8, 1, 8);
    const base = new THREE.Mesh(baseGeometry, baseMaterial);
    base.position.y = -2.5;
    App.scene.add(base);

    // 球体と棒を描画
    const gridSize = 4;
    const rodMaterialDefault = new THREE.MeshLambertMaterial({ color: 0x0000ff });
    const rodMaterialHighlight = new THREE.MeshLambertMaterial({ color: 0x00ffff });
    const sphereRadius = 0.55;
    const whiteMaterial = new THREE.MeshPhongMaterial({ color: 0xffffff });
    const blackMaterial = new THREE.MeshPhongMaterial({ color: 0x000000 });

    App.board = Array.from({ length: gridSize }, () =>
        Array.from({ length: gridSize }, () => Array(gridSize).fill(0))
    );

    for (let x = 0; x < gridSize; x++) {
        for (let z = 0; z < gridSize; z++) {
            // 棒の作成
            const rodHeight = gridSize + 1;
            const rodGeometry = new THREE.CylinderGeometry(0.2, 0.2, rodHeight, 16);
            const rod = new THREE.Mesh(rodGeometry, rodMaterialDefault);
            rod.position.set(2*x - 3, 0, 2*z - 3);
            rod.userData = { x, z, spheres: 0 }; // 棒の状態を追跡
            App.scene.add(rod);
            App.rods.push(rod);
        }
    }

    // 照明を追加（明るく設定）
    const ambientLight = new THREE.AmbientLight(0xaaaaaa, 1); // 環境光
    App.scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0xffffff, 2); // 点光源（強度を2倍）
    pointLight.position.set(10, 15, 10);
    App.scene.add(pointLight);

    // マウスイベントの設定
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    function onMouseMove(event) {
        // マウス位置を計算
        mouse.x = (event.clientX / canvas.width) * 2 - 1;
        mouse.y = -(event.clientY / canvas.height) * 2 + 1;

        // レイキャスト
        raycaster.setFromCamera(mouse, App.camera);
        const intersects = raycaster.intersectObjects(App.rods);

        // 棒の色をリセット
        App.rods.forEach(rod => rod.material = rodMaterialDefault);

        if (intersects.length > 0) {
            const intersectedRod = intersects[0].object;
            intersectedRod.material = rodMaterialHighlight; // 選択中の棒をハイライト
        }
    }

    function onMouseClick(event) {
        // マウス位置を計算
        mouse.x = (event.clientX / canvas.width) * 2 - 1;
        mouse.y = -(event.clientY / canvas.height) * 2 + 1;

        // レイキャスト
        raycaster.setFromCamera(mouse, App.camera);
        const intersects = raycaster.intersectObjects(App.rods);

        if (intersects.length > 0) {
            const intersectedRod = intersects[0].object;
            const { x, z } = intersectedRod.userData;
            const y = intersectedRod.userData.spheres;

            // 棒に球体を追加（最大4つまで）
            if (y < 4) {
                const sphereGeometry = new THREE.SphereGeometry(sphereRadius, 16, 16);
                const material = App.isMyTurn() ? blackMaterial : whiteMaterial;
                const sphere = new THREE.Mesh(sphereGeometry, material);
                sphere.position.set(
                    intersectedRod.position.x,
                    -1.5 + y,                   // 縦に積む
                    intersectedRod.position.z
                );
                App.scene.add(sphere);

                // 盤面情報を更新
                App.board[x][y][z] =
                    App.isMyTurn() ? 1 : -1;

                intersectedRod.userData.spheres++;
                App.turnCount++;
                App.clickLog.push(`棒(${x}, ${z})`);

                // ここから敵の動き
                fetch('/move', {
                    method: "POST",
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify([x, z, y])     // 注意!!js内ではy方向が縦になっているが、python内ではz方向が縦にする
                    }
                )
                .then(response => response.json())
                .then(data => {
                    // TODO: ここで相手の手を盤面に描画、勝敗がついたならそれっぽい画面に飛ばすかテキストを表示させる
                    // python内ではz方向が縦であるが、js内ではy方向が縦であるので、適切な変換が必要
                    console.log(data)
                })
                .catch(error => console.error('Error: ', error));

                // 現在の盤面を表示
                //console.log(document.getElementById("output").textContent =
                //`盤面:\n${formatBoard(App.board)}\n\nクリック履歴: ${App.clickLog.join(", ")}`);
            }
        }
    }
    
    // 盤面情報を整形して表示する関数
    function formatBoard(board) {
        return board.map(layer => layer.map(row => row.join(", ")).join("\n")).join("\n\n");
    }

    // イベントリスナーの登録
    canvas.addEventListener('mousemove', onMouseMove);
    canvas.addEventListener('click', onMouseClick);
};

// 表示の更新
App.animate = function() {
    requestAnimationFrame(App.animate);

    // カメラ操作を反映
    App.controls.update();

    // 再描画
    App.renderer.render(App.scene, App.camera);
};