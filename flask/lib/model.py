# 立体4目並べのモデル
from stable_baselines3 import PPO   # PPOである必要？調べてないからわかんない

# 以下はサンプルモデルで、本番では使わない
class SampleModel():
    # board: 4*4*4の盤面
    # 戻り値は、一つ目が次の置く場所、二つ目が次の状態？(サンプルのため常にNoneを返す)
    def predict(self, board):
        # サンプルのためランダムに置く
        import random
        _BOARD_SIZE = 4
        placeable_location = []
        for x in range(_BOARD_SIZE):
            for y in range(_BOARD_SIZE):
                placeable_z = 0
                for z in range(_BOARD_SIZE):
                    if board[x][y][z] == 0: # おける場所なら
                        break
                    placeable_z += 1
                if placeable_z == _BOARD_SIZE:
                    continue
                placeable_location.append([x, y, placeable_z])
        return random.choice(placeable_location)

sample_model = SampleModel()