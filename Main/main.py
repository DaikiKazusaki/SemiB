import numpy as np
from Environment import Environment
from board_renderer import renderer
from stable_baselines3 import PPO
import gymnasium as gym
from Opponent.StrongOpponent import StrongOpponent

action_counts = [0] * 16

# ランダムな相手プレイヤーのインスタンスを作成
# opponent_instance = RandomOpponent()

# 強い相手プレイヤーのインスタンスを作成
opponent_instance = StrongOpponent()

# カスタム環境を登録するか、直接インスタンス化
env = Environment(opponent=opponent_instance)

model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=300000)  # 任意

# 学習後にテスト
obs, info = env.reset()
done = False
tmp = obs.copy()
# env.set_opponent(ModelOpponent(model2, Environment()))
move_list=[] #ここに履歴を保存
while not done:
    action, _ = model.predict(obs)

    # アクションを取得してリトライが必要か確認
    valid_action = False
    while not valid_action:
        action, _ = model.predict(obs)  # モデルからアクションを予測
        if action_counts[action] < 3:   # アクションが3回未満なら有効
            valid_action = True
            action_counts[action] += 1  # アクションのカウントを更新
        else:
            print(f"Action {action} has been selected 3 times. Retrying...")
    
    obs, reward, done, truncated, info = env.step(action)
    changed_indices = np.where(tmp != obs) #1step前との差分を取得
    change_list = []
    for idx in zip(*changed_indices):#差分すべてをチェック
        x, y, z = idx #x,y,z座標を取得
        value = obs[idx] #ぞの座標におかれたのがどちらの石かを取得
        if value == 1:#黒が先手なので先に格納
            change_list.insert(0, [x, y]) 
        elif value == -1:#白が後手なので後に格納
            change_list.append([x, y]) 
        tmp[idx] = value #ひとつ前の盤面を更新
    move_list += change_list #move_listに結合
print("Final reward:", reward)

renderer.render(move_list, interval=1000)