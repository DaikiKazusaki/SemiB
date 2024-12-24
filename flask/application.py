from flask import Flask, render_template, request, redirect, url_for, jsonify
from lib.Environment import SampleEnv, BOARD_SIZE   # TODO: 本実装では Environment

app = Flask(__name__)
env = SampleEnv()

@app.route('/')
def board():
    env.reset()
    return render_template('board.html')

@app.route('/move', methods=['GET', 'POST'])
def move():
    if request.method == 'POST':
        user_move = request.json
        [x, y, z] = user_move
        action = x + BOARD_SIZE * y + (BOARD_SIZE ** 2) * z
        # TODO: ここで「勝利判定・強化学習による次の一手・その後勝利判定」をする必要がある
        obs, reward, is_terminated, is_truncated, info = env.step(action)
        updatedBoard = obs.tolist()
        # TODO: ハードコーディングを直す
        if 'opponent' in info:
            opponent_move = info['opponent']
            print(f'player move: {user_move}')
            print(f'opponent move: {opponent_move}')
            return jsonify({
                'winner': reward,    # プレイヤーが勝ちなら1, 機械が勝ちなら-1, 決着がつかないなら0(enum作ったほうがいいかも？)
                'board' : updatedBoard,
                'opponent': info['opponent']
            })
        else:
            print(f'player move: {user_move}')
            return jsonify({
                'winner': reward,    # プレイヤーが勝ちなら1, 機械が勝ちなら-1, 決着がつかないなら0(enum作ったほうがいいかも？)
                'board' : updatedBoard
            })
    else:
        return redirect(url_for('board'))   # 「"/move"」に直接アクセスされた時は「"/"」 に飛ばす