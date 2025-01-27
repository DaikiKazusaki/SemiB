import numpy as np
from Environment import Environment, Black
from board_renderer import renderer
from stable_baselines3 import PPO
import gymnasium as gym
import os
from Opponent.StrongOpponent import StrongOpponent
from Opponent.RandomOpponent import RandomOpponent
from Opponent.ModelOpponent import ModelOpponent
from Opponent.StrongOpponent2 import StrongOpponent2


# ランダムな相手プレイヤーのインスタンスを作成
# opponent_instance = RandomOpponent()

# 強い相手プレイヤーのインスタンスを作成
opponent_instance = StrongOpponent()
random_opponent_instance = RandomOpponent()
opponent2_instance = StrongOpponent2()

# カスタム環境を登録するか、直接インスタンス化
env = Environment(opponent=opponent_instance)

model = PPO.load(os.path.join("model_files", "tmp", "1.zip"), env=env)

# 学習後にテスト
obs, info = env.reset()
done = False
tmp=obs.copy()
move_list=[] #ここに履歴を保存
while not done:
    action, _ = model.predict(obs)
    obs, reward, done, truncated, info = env.step(action)
    changed_indices=np.where(tmp != obs) #1step前との差分を取得
    change_list=[]
    for idx in zip(*changed_indices):#差分すべてをチェック
        x, y, z = idx #x,y,z座標を取得
        value = obs[idx] #ぞの座標におかれたのがどちらの石かを取得
        if value == 1:#黒が先手なので先に格納
            change_list.insert(0, [x, y]) 
        elif value == -1:#白が後手なので後に格納
            change_list.append([x, y]) 
        tmp[idx]=value #ひとつ前の盤面を更新
    move_list+=change_list #move_listに結合
print("Final reward:", reward)

game_detail = env.game_details.get(1)
move_list = [[m[0], m[1]] for m in game_detail[env.moves_key]]

print('先攻' if game_detail[env.first_stone_key] == Black else '後攻')

renderer.render(move_list, interval=1000)