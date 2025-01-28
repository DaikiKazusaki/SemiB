import os
import datetime
from board_renderer import renderer
from Environment import Environment, GameResult, Black, White
from Opponent.ModelOpponent import ModelOpponent
from Opponent.StrongOpponent import StrongOpponent
from Opponent.StrongOpponent2 import StrongOpponent2
from Opponent.RandomOpponent import RandomOpponent
from stable_baselines3 import PPO

class Logger:

    def __init__(self, log_file_path, html_dir):
        self.log_file_path = log_file_path
        self.dir_name = os.path.dirname(log_file_path)
        self.log_file_name = os.path.basename(log_file_path)
        self.html_dir = html_dir
        self.f = None

    def game_detail_log(self, details):
        details_without_result_none = [d for d in details.values() if d[Environment.result_key] != None]
        total_game_count = len(details)
        first_details = [d for d in details_without_result_none if d[Environment.first_stone_key] == Black]   # 先手
        second_details = [d for d in details_without_result_none if d[Environment.first_stone_key] == White]  # 後手
        first_win  = len([d for d in first_details if d[Environment.result_key] == GameResult.Win])
        first_draw = len([d for d in first_details if d[Environment.result_key] == GameResult.Draw])
        first_lose = len([d for d in first_details if d[Environment.result_key] == GameResult.Lose])
        first_illegal = len([d for d in first_details if d[Environment.result_key] == GameResult.Illegal])
        first_opponent_illegal = sum([d[Environment.opponent_illegal_key] for d in first_details])
        second_win  = len([d for d in second_details if d[Environment.result_key] == GameResult.Win])
        second_draw = len([d for d in second_details if d[Environment.result_key] == GameResult.Draw])
        second_lose = len([d for d in second_details if d[Environment.result_key] == GameResult.Lose])
        second_illegal = len([d for d in second_details if d[Environment.result_key] == GameResult.Illegal])
        second_opponent_illegal = sum([d[Environment.opponent_illegal_key] for d in second_details])
        self.writeln(f'総試合数: {total_game_count}')
        self.writeln('先手：')
        self.writeln(f'\t試合数 {len(first_details)}回')
        self.writeln(f'\t勝ち  {first_win}回')
        self.writeln(f'\t負け  {first_lose}回')
        self.writeln(f'\t引分  {first_draw}回')
        self.writeln(f'\t無効手による負け {first_illegal}回')
        self.writeln(f'\t相手の不正回数 {first_opponent_illegal}回')
        self.writeln('後手：')
        self.writeln(f'\t試合数 {len(second_details)}回')
        self.writeln(f'\t勝ち {second_win}回')
        self.writeln(f'\t負け {second_lose}回')
        self.writeln(f'\t引分 {second_draw}回')
        self.writeln(f'\t無効手による負け {second_illegal}回')
        self.writeln(f'\t相手の不正回数 {second_opponent_illegal}回')
        if first_win > 0:
            first_win_last_detail = [d for d in first_details if d[Environment.result_key] == GameResult.Win][-1]
            first_last_move = [[i, j] for i, j, k in first_win_last_detail[Environment.moves_key]]
            renderer.render(first_last_move, browse=False, result_dir_name=os.path.join(self.dir_name, self.html_dir), html_file_name='first.html')
        if second_win > 0:
            second_win_last_detail = [d for d in second_details if d[Environment.result_key] == GameResult.Win][-1]
            second_last_move = [[i, j] for i, j, k in second_win_last_detail[Environment.moves_key]]
            renderer.render(second_last_move, browse=False, result_dir_name=os.path.join(self.dir_name, self.html_dir), html_file_name='second.html')
    
    def writeln(self, log):
        self.f.write(log)
        self.f.write('\n')      # 改行も出力

    def __enter__(self):
        if not os.path.exists(self.dir_name):
            os.makedirs(self.dir_name)
        if not os.path.exists(self.log_file_path):
            # これいるかわからん、下の self.f で mode='a' がファイルないときにどういう動きするかわからんから一応ここでファイル作る
            f = open(self.log_file_path, 'w', encoding='utf-8')
            f.close()
        self.f = open(self.log_file_path, 'a', encoding='utf-8')
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if self.f:
            self.f.close()
        pass


def self_play(model_file_name = "3d-tic-tac-toe.zip", total_timesteps = 1000000, play_count = 10, verbose=1, init_model1_path=None, init_model2_path=None):
    log_interval = 1000000
    current_time = datetime.datetime.now()
    ZIP_EXT = ".zip"
    time = f'{current_time.strftime("%Y%m%d_%H%M%S")}'
    MODEL_DIR = f'model_files/{time}'
    MODEL_FILE_NAME =  model_file_name if model_file_name.endswith(ZIP_EXT) else model_file_name + ZIP_EXT
    env = Environment(opponent=StrongOpponent())
    model1 = PPO("MlpPolicy", env=env, verbose=verbose)
    if init_model1_path:
        model1 = PPO.load(init_model1_path, env=env)
        env.set_opponent(ModelOpponent(model1))
    model2 = PPO("MlpPolicy", env, verbose=verbose)
    if init_model2_path:
        model2 = PPO.load(init_model2_path, env=env)
    for count in range(play_count):
        env.reset()
        # model2が学習
        print(f'model2 learn(total timesteps: {total_timesteps})')
        timestep = 0
        i = 0
        while timestep < total_timesteps:
            if total_timesteps - timestep < log_interval:
                model2.learn(total_timesteps=total_timesteps-timestep)
            else:
                model2.learn(total_timesteps=log_interval)
            details = env.game_details
            model_dir = os.path.join(MODEL_DIR, f'{count}', 'model2')
            if not os.path.exists(model_dir):
                os.makedirs(model_dir)
            model2.save(os.path.join(model_dir, f'{i}.zip'))
            with Logger(os.path.join('log', f'{time}', 'model2', f'{count}', f'log_{i}'), f'result/{i}') as l:
                l.game_detail_log(details)
            timestep += log_interval
            env.clear_game_details()
            i += 1
            print(f'\tcurrent timestep: {timestep}')
            total_game_count = len(details)
            win_count = len([d for d in details.values() if d[Environment.result_key] == GameResult.Win])
            if (float(win_count) / total_game_count) >= 0.95:
                print('勝率が良すぎるためbreak.')
                break
        env.set_opponent(ModelOpponent(model2))
        env.reset()
        # model1が学習
        print(f'model1 learn(total timesteps: {total_timesteps})')
        timestep = 0
        i = 0
        while timestep < total_timesteps:
            if total_timesteps - timestep < log_interval:
                model1.learn(total_timesteps=total_timesteps-timestep)
            else:
                model1.learn(total_timesteps=log_interval)
            details = env.game_details
            model_dir = os.path.join(MODEL_DIR, f'{count}', 'model1')
            if not os.path.exists(model_dir):
                os.makedirs(model_dir)
            model2.save(os.path.join(model_dir, f'{i}.zip'))
            with Logger(os.path.join('log', f'{time}', 'model1', f'{count}', f'log_{i}'), f'result{i}') as l:
                l.game_detail_log(details)
            timestep += log_interval
            env.clear_game_details()
            i += 1
            print(f'\tcurrent timestep: {timestep}')
            total_game_count = len(details)
            win_count = len([d for d in details.values() if d[Environment.result_key] == GameResult.Win])
            if (float(win_count) / total_game_count) >= 0.95:
                print('勝率が良すぎるためbreak.')
                break
        env.set_opponent(ModelOpponent(model1))
        print(f'play count: {count + 1}...')
    model1.save(os.path.join(MODEL_DIR, f'{time}_final_' + MODEL_FILE_NAME))

if __name__ == "__main__":
    self_play(total_timesteps=40000000, play_count=5, init_model1_path=None, init_model2_path='model_files/20250128_005609/4/model1/0.zip')