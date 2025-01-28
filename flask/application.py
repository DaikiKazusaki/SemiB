from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
from lib.BattleEnvironment import BattleEnvironment, BOARD_SIZE

app = Flask(__name__)
is_player_first = True
env = BattleEnvironment()

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/move_order/<int:move_order>')
def define_move_order(move_order):
    global is_player_first
    if move_order == 1:
        is_player_first = True
    elif move_order == 2:
        is_player_first = False
    else:
        raise Exception('move order is invalid.')
    return redirect(url_for('board'))

@app.route('/board', methods=['GET', 'POST'])
def board():
    if request.method == 'POST':
        global is_player_first
        # board.htmlが先攻・後攻を取得するためにPOSTで要求してくる
        if is_player_first:
            env.reset(True)
            return jsonify({
                'player_first': True
            })
        else:
            _, info = env.reset(False)
            return jsonify({
                'player_first': False,
                'opponent': [int(i) for i in info['opponent']]
            })
    else:
        return render_template('board.html')

@app.route('/board/back')
def back():
    return redirect(url_for('index'))


@app.route('/board/move', methods=['GET', 'POST'])
def move():
    if request.method == 'POST':
        user_move = request.json
        [x, y, z] = user_move
        action = x + BOARD_SIZE * y
        # TODO: ここで「勝利判定・強化学習による次の一手・その後勝利判定」をする必要がある
        obs, reward, is_terminated, is_truncated, info = env.step(action)
        updatedBoard = obs.tolist()
        # TODO: ハードコーディングを直す
        if 'opponent_move' in info:
            opponent_move = info['opponent_move']
            print(info)
            print(f'player move: {user_move}')
            print(f'opponent move: {opponent_move}')
            # どうやらint64->intの変換が必要らしい
            opponent_move_int32 = [int(i) for i in opponent_move]
            return jsonify({
                'winner': reward,    # プレイヤーが勝ちなら1, 機械が勝ちなら-1, 決着がつかないなら0(enum作ったほうがいいかも？)
                'board' : updatedBoard,
                'opponent': opponent_move_int32
            })
        else:
            print(f'player move: {user_move}')
            return jsonify({
                'winner': reward,    # プレイヤーが勝ちなら1, 機械が勝ちなら-1, 決着がつかないなら0(enum作ったほうがいいかも？)
                'board' : updatedBoard
            })
    else:
        return redirect(url_for('index'))   # 「"/move"」に直接アクセスされた時は「"/"」 に飛ばす

# フォント置いてる場所を返すだけ
@app.route('/fonts/<path:font>')
def send_font(font):
    return send_from_directory('static', 'fonts/' + font)