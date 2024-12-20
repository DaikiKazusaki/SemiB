import gymnasium as gym
from gymnasium import spaces
import numpy as np

class Environment(gym.Env):
    # メタデータの定義
    ## Gymnasium環境に関する追加情報を格納するための辞書
    metadata = {"render_modes": ["human"]}

    # クラスのインスタンス化時に呼ばれるメソッド(=コンストラクタ)
    # 盤面の設定や黒が先手などの設定を行う
    def __init__(self, render_mode=None):
        super().__init__()
        self.board_size = 4
        # 4 x 4 x 4 のマス，各マスは {空=0, 黒=1, 白=-1} とする
        self.observation_space = spaces.Box(low=-1, high=1, shape=(self.board_size, self.board_size, self.board_size), dtype=int)
        # 行動空間: 64マスのいずれかに打つことを選択(0~63)
        self.action_space = spaces.Discrete(self.board_size * self.board_size * self.board_size)

        # 内部状態
        self.board = None
        self.current_player = 1  # 黒=1, 白=-1
        self.render_mode = render_mode

    # 環境の初期化
    ## 4 x 4 x 4 のマスを全て0にし，手番を黒にする
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        # 初期配置
        self.board = np.zeros((self.board_size, self.board_size, self.board_size), dtype=int)
        self.current_player = 1
        observation = self.board.copy()
        info = {}
        return observation, info
    
    # 行動の実行
    ## どこに置いたかの座標を戻り値にする
    def step(self, action):
        # actionは0~63の整数, これをボード上の(i,j,k)にマッピング
        i = action // (self.board_size * self.board_size)
        j = (action // self.board_size) % self.board_size
        k = action % self.board_size
        
        # 行動が有効か判定
        if not self.is_valid_move(i, j, k, self.current_player):
            # 無効手を打った場合は大きな負の報酬を与え、エピソード終了とするなどの処理を行う
            # ここでは簡易的に、報酬=-1でゲーム終了
            reward = -1
            terminated = True
            info = {"illegal_move": True}
            return self.board.copy(), reward, terminated, False, info
        
        # 石を置く
        self.place_disc(i, j, k, self.current_player)

        # 次のプレイヤーへ
        self.current_player *= -1

        # 相手の行動(ここではランダム)
        self.opponent_move()

        # 終了判定
        terminated = self.is_game_over()
        if terminated:
            reward = self.compute_final_reward()
        else:
            reward = 0.0

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
        
        # ひっくり返せる石があるか確認
        directions = [
            (di, dj, dk)
            for di in [-1, 0, 1]
            for dj in [-1, 0, 1]
            for dk in [-1, 0, 1]
            if not (di == 0 and dj == 0 and dk == 0)
        ]
        opponent = -player
        for di, dj, dk in directions:
            x, y, z = i + di, j + dj, k + dk
            found_opponent = False
            while 0 <= x < self.board_size and 0 <= y < self.board_size and 0 <= z < self.board_size:
                if self.board[x, y, z] == opponent:
                    found_opponent = True
                    x += di
                    y += dj
                    z += dk
                elif self.board[x, y, z] == player and found_opponent:
                    return True
                else:
                    break
        return False        

    # 指定された位置に石を置く
    ## i: x座標, j: y座標, k: z座標, player: 石の色(黒=1, 白=-1)
    def place_disc(self, i, j, k, player):
        pass


    ## 以下順也の担当
    # 石を置いた後の(AIの)相手の処理
    def opponent_move(self):
        pass

    # ゲームの終了判定
    ## return: True=ゲーム継続, False=ゲーム終了
    def is_game_over(self):
        pass
    
    # ゲーム終了時に報酬を計算する
    def compute_final_reward(self):
        pass

    # ボードの表示
    def render(self):
        if self.render_mode == "human":
            print(self.board)