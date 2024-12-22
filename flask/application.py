from flask import Flask, render_template, request, redirect, url_for, jsonify
from lib.model import sample_model  # TODO: 本実装では model を import

app = Flask(__name__)
current_board = [[[0] * 4 for i in range(4)] for j in range(4)] # 4*4*4盤面

@app.route('/')
def board():
    return render_template('board.html')

@app.route('/move', methods=['GET', 'POST'])
def move():
    if request.method == 'POST':
        user_move = request.json
        [x, y, z] = user_move
        current_board[x][y][z] = 1      # TODO: 先攻・後攻によって1とか-1とかを変える必要がありそう
        # TODO: ここで「勝利判定・強化学習による次の一手・その後勝利判定」をする必要がある
        next_move = sample_model.predict(current_board)
        return jsonify({
            'winner': 0,    # プレイヤーが勝ちなら1, 機械が勝ちなら-1, 決着がつかないなら0(enum作ったほうがいいかも？)
            'move': next_move
        })
    else:
        return redirect(url_for('board'))   # 「"/move"」に直接アクセスされた時は「"/"」 に飛ばす