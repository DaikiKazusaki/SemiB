import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random
from enum import Enum

# 石を表す
# 黒 ->  1 (プレイヤーの石の色)
# 白 -> -1 (敵の石の色)
# 空 ->  0 (置かれてない)
White = -1
Empty = 0
Black = 1
class GameResult(Enum):
    Illegal = -2
    Lose = -1
    Draw = 0
    Win = 1

class Environment(gym.Env):
    # メタデータの定義
    ## Gymnasium環境に関する追加情報を格納するための辞書
    metadata = {"render_modes": ["human"]}

    result_key = "result"                          # リザルトを表すキー
    moves_key = "moves"                            # 打った手を表すキー
    first_stone_key = "first_stone"                # 先手を表すキー
    opponent_illegal_key = "opponent_illegal"      # 敵の無効手の回数を表すキー

    # クラスのインスタンス化時に呼ばれるメソッド(=コンストラクタ)
    # 盤面の設定や黒が先手などの設定を行う
    def __init__(self, render_mode=None, opponent=None):
        super().__init__()
        self.board_size = 4
        # 4 x 4 x 4 のマス，各マスは {空=0, 黒=1, 白=-1} とする
        self.observation_space = spaces.Box(low=-1, high=1, shape=(self.board_size, self.board_size, self.board_size), dtype=np.int64)
        # 行動空間: 16マスのいずれかに打つことを選択(0~15)
        self.action_space = spaces.Discrete(self.board_size * self.board_size)

        # 内部状態
        self.board = None
        self.opponent = opponent                            # 敵を設定
        self.render_mode = render_mode                      # 表示モード（現在未使用）
        self.current_player = None                          # プレイヤーに設定
        self.game_count = 0                                 # 実行した試合回数（学習の際のログ出力用）
        self.game_details = {}                              # ゲームの詳細
        self.penalty_illegal = -10.0                        # 無効な手を打った際のペナルティ
        self.value_lose      =  -1.0                        # 負けた時の報酬
        self.value_win       =   1.0                        # 勝った時の報酬
        self.value_draw      =   0.0                        # 引き分けの時の報酬

    # 環境の初期化
    ## 4 x 4 x 4 のマスを全て0にし，手番を黒にする
    ## first_stone: 先手を取る石（Noneでランダムになる）
    def reset(self, seed=None, first_stone=None, options=None):
        super().reset(seed=seed)
        self.board = np.array([[[Empty] * self.board_size] * self.board_size] * self.board_size)
        self.game_count += 1                                                            # ゲームカウントを1増やす
        self.game_details[self.game_count] = {
            Environment.result_key: None,
            Environment.first_stone_key: None,
            Environment.moves_key: [],
            Environment.opponent_illegal_key: 0
        }                                                                               # ゲームの詳細を入れる用
        if not first_stone:                                                             # 先手が指定されていない場合
            self.current_player = random.choice([Black, White])             # ランダムに先手を決定
        self.game_details[self.game_count][Environment.first_stone_key] = self.current_player  # 先手を保存
        if self.current_player == White:                                                # 敵が先手の場合
            x, y, z = self.opponent_move()                                              # 敵の手を取得
            self.place_disc(x, y, z, self.current_player)                               # 石を置く
            self.switch_player()                                                        # プレイヤーを切り替える
        info = { "first": self.current_player }                                         # 先手の情報は返す
        observation = self.board.copy()                                                 # 初期の盤面
        return observation, info
    
    # 行動の実行
    ## どこに置いたかの座標を戻り値にする
    def step(self, action):
        # actionは0~15の整数, これをボード上の(i,j,k)にマッピング
        i = action % self.board_size
        j = action // self.board_size
        k = 0
        while k < self.board_size:
            if self.is_valid_move(i, j, k, self.current_player):        # 適切なkならこれにする
                break
            k += 1
        
        # 行動が有効か判定
        if not self.is_valid_move(i, j, k, self.current_player):        # 無効な手の場合
            # 無効手を打った場合は大きな負の報酬を与え、エピソード終了とするなどの処理を行う
            reward = self.penalty_illegal                               # 無効な手を打ったことによるペナルティ
            terminated = True                                           # 終了
            info = {"illegal_move": True}                               # 無効な手という情報を加える
            self.game_details[self.game_count][Environment.result_key] = GameResult.Illegal    # 反則負けとする
            return self.board.copy(), reward, terminated, False, info
        
        # 石を置く
        self.place_disc(i, j, k, self.current_player)

        terminated = self.is_game_over()
        if terminated:
            reward = self.compute_final_reward()
            return self.board.copy(), reward, terminated, False, {}

        # 次のプレイヤーへ
        self.switch_player()

        # 相手の行動
        i, j, k = self.opponent_move()

        self.place_disc(i, j, k, self.current_player)

        # 終了判定
        terminated = self.is_game_over()
        if terminated:
            reward = self.compute_final_reward()
        else:
            reward = 0.0    # 勝敗がついていない時は0を返す

        # プレイヤーを切り替える
        self.switch_player()

        info = {}
        return self.board.copy(), reward, terminated, False, info

    # 指定された位置に石を置けるかどうか
    ## i: x座標, j: y座標, k: z座標, player: 石の色(黒=1, 白=-1)
    def is_valid_move(self, i, j, k, player):
        # ボード外、既に埋まっているマスは×
        if i < 0 or i >= self.board_size or j < 0 or j >= self.board_size or k < 0 or k >= self.board_size:
            return False
        if self.board[i, j, k] != 0:
            return False
        
        # zが0～k-1の範囲で空いているマスがないかを判定
        for z in range(k):
            if self.board[i, j, z] == 0:
                return False
        
        return True  

    # 指定された位置に石を置く
    # 立体四目並べでは石を反転する必要がないため，石を置くだけでよい
    ## i: x座標, j: y座標, k: z座標, player: 石の色(黒=1, 白=-1)
    def place_disc(self, i, j, k, player):
        self.game_details[self.game_count][Environment.moves_key].append((i, j, k))    # 手を追加
        self.board[i, j, k] = player      

    # 石を置いた後の(AIの)相手の処理
    def opponent_move(self):
        if self.opponent:                                       # 敵がいる場合
            move = self.opponent.opponent_move(self.board)      # 次の手を選択させる
            if move:
                return move
            else:
                self.game_details[self.game_count][Environment.opponent_illegal_key] += 1  # 無効な手の回数を増やす

        # 以下、ランダムに打つ
        valid_moves = []
        # 有効な手を収集
        for x in range(self.board_size):
            for y in range(self.board_size):
                for z in range(self.board_size):
                    if self.board[x, y, z] == 0:                    # 空いているマスを探す
                        if z == 0 or self.board[x, y, z - 1] != 0:  # 真下に駒があるか確認
                            valid_moves.append((x, y, z))           # 適切なマスに加える
                            break                                   # この(x,y)の組ではもう他は置けない
        
        return valid_moves[np.random.choice(len(valid_moves))]      # ランダムに選択する


    # ゲームの終了判定
    ## return: True=ゲーム終了, False=ゲーム継続
    def is_game_over(self):
        directions = [
        (1, 0, 0),  # x方向
        (0, 1, 0),  # y方向
        (0, 0, 1),  # z方向
        (1, 1, 0),  # x-y平面の対角線
        (1, -1, 0),
        (1, 0, 1),  # x-z平面の対角線
        (1, 0,-1),
        (0, 1, 1),  # y-z平面の対角線
        (0, 1,-1),
        (1, 1, 1),  # 立体対角線
        (1, 1,-1),
        (1, -1, 1),  # 逆立体対角線
        (1, -1, -1)
        ]

        def check_line(x, y, z, dx, dy, dz):
            """指定された方向(dx, dy, dz)に4つ並んでいるか確認する"""
            player = self.board[x, y, z]
            if player == Empty:
                return False
            for step in range(1, 4):
                nx, ny, nz = x + step * dx, y + step * dy, z + step * dz
                if not (0 <= nx < self.board_size and 0 <= ny < self.board_size and 0 <= nz < self.board_size):
                    return False
                if self.board[nx, ny, nz] != player:
                    return False
            return True

        # 盤面全体を走査して勝利条件を確認
        for x in range(self.board_size):
            for y in range(self.board_size):
                for z in range(self.board_size):
                    for dx, dy, dz in directions:
                        if check_line(x, y, z, dx, dy, dz):
                            return True  # 勝利条件を満たすラインがあればゲーム終了

        # 盤面が全て埋まっている場合もゲーム終了
        if np.all(self.board != Empty):
            return True

        return False
    
    # ゲーム終了時に報酬を計算する
    def compute_final_reward(self):
        ##ゲーム終了時最後の手番の人が勝利する
        if np.all(self.board != Empty):
            self.game_details[self.game_count][Environment.result_key] = GameResult.Draw
            return self.value_draw
        elif self.current_player == Black:
            self.game_details[self.game_count][Environment.result_key] = GameResult.Win
            return self.value_win
        elif self.current_player == White:
            self.game_details[self.game_count][Environment.result_key] = GameResult.Lose
            return self.value_lose
        else:
            raise Exception(f'Undefined player: {self.current_player}')
    
    def clear_game_details(self):
        self.game_count = 0
        self.game_details = {}

    def switch_player(self):
        if self.current_player == Black:
            self.current_player = White
        elif self.current_player == White:
            self.current_player = Black
        else:
            raise Exception(f'Undefined player: {self.current_player}')
    
    def set_opponent(self, opponent):
        self.opponent = opponent

    # ボードの表示
    def render(self):
        if self.render_mode == "human":
            print(self.board)