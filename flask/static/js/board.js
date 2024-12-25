import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';
import { FontLoader } from 'three/addons/loaders/FontLoader.js';

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
    isGameOver: false,// ゲームが終わったか
};

App.isMyTurn = function() {
    return App.turnCount % 2 == 0;
}

App.init = function() {
    const canvas = document.querySelector("#board");

    // カメラの設定
    App.camera = new THREE.PerspectiveCamera(75, canvas.width / canvas.height, 1, 10000);
    App.camera.position.set(7, 7, 10);
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
    const setRodsDefaultColor = function() {
        App.rods.forEach(rod => rod.material = rodMaterialDefault);
    };
    const setRodHighLight = function(x, z) {
        setRodsDefaultColor();  // 一旦デフォルト色
        App.rods.filter(
            function(rod) {
                return rod.userData.x == x && rod.userData.z == z;
            }
        ).forEach(selectedRod => selectedRod.material = rodMaterialHighlight);
    };


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

    // X軸, Y軸, Z軸の描画
    const axisMaterial = new THREE.LineBasicMaterial({ color: 0x000000 });
    const xPoints = [];
    xPoints.push( new THREE.Vector3(-7, -3, -7) );
    xPoints.push( new THREE.Vector3(7, -3, -7) );
    const xGeometry = new THREE.BufferGeometry().setFromPoints(xPoints);
    const xLine = new THREE.Line(xGeometry, axisMaterial);
    App.scene.add(xLine);
    const yPoints = [];
    yPoints.push( new THREE.Vector3(-7, -3, -7) );
    yPoints.push( new THREE.Vector3(-7, 7, -7) );
    const yGeometry = new THREE.BufferGeometry().setFromPoints(yPoints);
    const yLine = new THREE.Line(yGeometry, axisMaterial);
    App.scene.add(yLine);
    const zPoints = [];
    zPoints.push( new THREE.Vector3(-7, -3, -7) );
    zPoints.push( new THREE.Vector3(-7, -3, 7) );
    const zGeometry = new THREE.BufferGeometry().setFromPoints(zPoints);
    const zLine = new THREE.Line(zGeometry, axisMaterial);
    App.scene.add(zLine);
    // X, Y, Zの文字
    const loader = new FontLoader();
    const labelMaterial = new THREE.MeshNormalMaterial();

    loader.load('fonts/Roboto_Regular.json', function ( font ) {
        const xLabelGeometry = new TextGeometry( 'X', {
            font: font,
            size: 1,
            depth: 0.25,
        } );
        xLabelGeometry.center();
        const xLabel = new THREE.Mesh(xLabelGeometry, labelMaterial);
        xLabel.position.set(8, -3, -7);
        App.scene.add(xLabel);
        const yLabelGeometry = new TextGeometry( 'Y', {
            font: font,
            size: 1,
            depth: 0.25,
        } );
        yLabelGeometry.center();
        const yLabel = new THREE.Mesh(yLabelGeometry, labelMaterial);
        yLabel.position.set(-7, 8, -7);
        App.scene.add(yLabel);
        const zLabelGeometry = new TextGeometry( 'Z', {
            font: font,
            size: 1,
            depth: 0.25,
        } );
        zLabelGeometry.center();
        const zLabel = new THREE.Mesh(zLabelGeometry, labelMaterial);
        zLabel.position.set(-7, -3, 8);
        App.scene.add(zLabel);
    } );

    // 照明を追加（明るく設定）
    const ambientLight = new THREE.AmbientLight(0xaaaaaa, 1); // 環境光
    App.scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0xffffff, 2); // 点光源（強度を2倍）
    pointLight.position.set(10, 15, 10);
    App.scene.add(pointLight);

    // マウスイベントの設定
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    const updateBoardWithLog = function(x, y, z) {
        let isMyTurn = App.isMyTurn();
        App.board[x][y][z] = isMyTurn ? 1 : -1;       // 盤面配列に配置
        let log = isMyTurn ?
        `you: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(${x}, ${y}, ${z})` :   // TODO: めんどいからtableにしてないけど、tableにすべき
        `opponent: (${x}, ${y}, ${z})`;
        App.clickLog.push(log);
        const logContentElement = document.getElementById('log-content');
        logContentElement.innerHTML = App.clickLog.join('<br>\n');
    };
    const placeIfPossible = function(x, z) {
        if (App.isGameOver || !App.isMyTurn()) { return; }  // ゲームオーバーか、自分のターンでない場合は抜ける
        const rods = App.rods.filter(
            function(rod) {
                return rod.userData.x == x && rod.userData.z == z;
            }
        );
        if (rods.length > 0) {      // 対応する棒が存在する場合
            const rod = rods[0];
            const y = rod.userData.spheres;
            if (y < 4) {            // まだ置けるなら
                const sphereGeometry = new THREE.SphereGeometry(sphereRadius, 16, 16);
                const material = App.isMyTurn() ? blackMaterial : whiteMaterial;
                const sphere = new THREE.Mesh(sphereGeometry, material);
                sphere.position.set(
                    rod.position.x,
                    -1.5 + y,                   // 縦に積む
                    rod.position.z
                );
                App.scene.add(sphere);

                // 盤面情報を更新
                updateBoardWithLog(x, y, z);

                rod.userData.spheres++;
                App.turnCount++;

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
                    if ('opponent' in data) {
                        const [ opponentX, opponentZ, opponentY ] = data['opponent'];
                        const opponentRod = App.rods.find(function (rod) {
                            const { x, z } = rod.userData;
                            return x == opponentX && z == opponentZ;
                        });
                        const sphereGeometry = new THREE.SphereGeometry(sphereRadius, 16, 16);
                        const material = App.isMyTurn() ? blackMaterial : whiteMaterial;
                        const sphere = new THREE.Mesh(sphereGeometry, material);
                        sphere.position.set(
                            opponentRod.position.x,
                            -1.5 + opponentY,    // 縦に積む
                            opponentRod.position.z
                        );
                        App.scene.add(sphere);

                        // 盤面情報を更新
                        updateBoardWithLog(opponentX, opponentY, opponentZ);

                        opponentRod.userData.spheres++;
                        App.turnCount++;
                    }
                    if (data['winner'] != 0) {
                        App.isGameOver = true;
                        let message = '';
                        if (data['winner'] == 1) {
                            message = 'player win!!';
                        }
                        else {
                            message = 'player lose...';
                        }
                        // htmlに書き込む
                        document.getElementById('result').textContent = message;
                    }
                })
                .catch(error => console.error('Error: ', error));
            }
        }
    };

    function onMouseMove(event) {
        // マウス位置を計算
        mouse.x = (event.clientX / canvas.width) * 2 - 1;
        mouse.y = -(event.clientY / canvas.height) * 2 + 1;

        // レイキャスト
        raycaster.setFromCamera(mouse, App.camera);
        const intersects = raycaster.intersectObjects(App.rods);

        // 選択された棒をハイライト
        if (intersects.length > 0) {
            const { x, z } = intersects[0].object.userData;
            setRodHighLight(x, z);
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
            placeIfPossible(x, z);
        }
    }

    // ボタンのホバー設定
    const rodButtons = document.getElementsByTagName('custom-rod-button');
    let rodButtonArray = [...rodButtons];    // foreachをするために配列に変換する必要があるらしい
    rodButtonArray.forEach(rodButton => {
        const x = parseInt(rodButton.getAttribute('x'));
        const z = parseInt(rodButton.getAttribute('z'));
        if (isNaN(x) || isNaN(z)) { return; }   // 数値に変換できない場合はここで抜ける
        rodButton.addEventListener('mouseover', function() {
            App.rods.forEach(rod => rod.material = rodMaterialDefault);
            App.rods.filter(function(value) {
                 return value.userData.x == x && value.userData.z == z
            }).forEach(rod => rod.material = rodMaterialHighlight);     // ホバーした座標の棒をハイライト
        });
        rodButton.addEventListener('mouseleave', function() {
            setRodsDefaultColor();
        });
        rodButton.addEventListener('click', function() {
            placeIfPossible(x, z);
        });
    });
    
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
