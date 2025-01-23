import os
import datetime
from Environment import Environment
from Opponent.ModelOpponent import ModelOpponent
from Opponent.StrongOpponent import StrongOpponent
from stable_baselines3 import PPO

def self_play(model_file_name = "3d-tic-tac-toe.zip", total_timesteps = 100000, play_count = 10, verbose=1):
    current_time = datetime.datetime.now()
    ZIP_EXT = ".zip"
    MODEL_DIR = f'model_files/{current_time.strftime("%Y%m%d_%H%M%S")}'
    MODEL_FILE_NAME =  model_file_name if model_file_name.endswith(ZIP_EXT) else model_file_name + ZIP_EXT
    default_env = Environment(is_print_log=False)
    env = Environment(opponent=StrongOpponent())
    model1 = PPO("MlpPolicy", env, verbose=verbose)
    model2 = PPO("MlpPolicy", env, verbose=verbose)
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
    for count in range(play_count):
        env.reset()
        default_env.reset()
        # model2が学習
        model2.learn(total_timesteps=total_timesteps)
        # model1が学習
        env.reset()
        default_env.reset()
        env.set_opponent(ModelOpponent(model2))
        model1.learn(total_timesteps=total_timesteps)
        env.set_opponent(ModelOpponent(model1))
        if play_count < 10 or count % (play_count // 10) == 0: 
            model1.save(os.path.join(MODEL_DIR, f'{current_time.strftime("%Y%m%d_%H%M%S")}_{count + 1}_' + MODEL_FILE_NAME))
        print(f'play count: {count + 1}...')
    model1.save(os.path.join(MODEL_DIR, f'{current_time.strftime("%Y%m%d_%H%M%S")}_final_' + MODEL_FILE_NAME))

if __name__ == "__main__":
    self_play(total_timesteps=1000000, play_count=1)