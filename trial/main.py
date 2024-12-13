from ReversiEnv import ReversiEnv
from stable_baselines3 import PPO
import gymnasium as gym

# カスタム環境を登録するか、直接インスタンス化
env = ReversiEnv()

model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=100000)  # 任意

# 学習後にテスト
obs, info = env.reset()
done = False
while not done:
    action, _ = model.predict(obs)
    obs, reward, done, truncated, info = env.step(action)

print("Final reward:", reward)

# 学習後の対戦表示例
# ※前回提示した環境定義および学習コードをすでに実行済みであることが前提

# 新たに環境をhumanモードで作り直す（表示用）
display_env = ReversiEnv(render_mode="human")
obs, info = display_env.reset()

done = False
truncated = False

print("Initial Board:")
display_env.render()
print()

while not done and not truncated:
    # エージェントの行動選択
    action, _ = model.predict(obs)
    obs, reward, done, truncated, info = display_env.step(action)
    
    # 環境表示
    print("Agent's move:")
    display_env.render()
    print()

    # ゲーム終了判定後
    if done or truncated:
        break

    # 相手（ランダムプレイヤー）の手は環境step内で実行済み
    print("Opponent's move:")
    display_env.render()
    print()

print("Game Over.")
print("Final reward:", reward)
print("Final Board:")
display_env.render()
