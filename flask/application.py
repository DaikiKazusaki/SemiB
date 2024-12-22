from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

@app.route('/')
def board():
    return render_template('board.html')

@app.route('/move', methods=['GET', 'POST'])
def move():
    if request.method == 'POST':
        data_from_js = request.json
        print(data_from_js)
        # TODO: ここで「勝利判定・強化学習による次の一手・その後勝利判定」をする必要がある
        next_move = [0, 0]  # 仮データ
        return jsonify({
            'winner': 0,    # プレイヤーが勝ちなら1, 機械が勝ちなら-1, 決着がつかないなら0(enum作ったほうがいいかも？)
            'move': next_move
        })
    else:
        return redirect(url_for('board'))