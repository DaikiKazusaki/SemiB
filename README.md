# SemiB

## セットアップ
1. 作業ディレクトリ作成
```
mkdir <dir>
```
2. プロジェクトのcloneをする
```
git clone https://github.com/DaikiKazusaki/SemiB
```

## 実行環境

### パッケージのインストール
```
pip install gymnasium stable-baselines3 "gymnasium[classic_control]" numpy
```

### ファイルの構成
#### trialフォルダ
| ファイル名 | 内容 |
| ---- | ---- |
| main.py | オセロの機械学習を行うファイル |
| ReversiEnv.py | オセロのゲーム進行を行うファイル |

#### Mainフォルダ
| ファイル名 | 内容 |
| ---- | ---- |
| main.py | 立体4目並べの機械学習を行うファイル |
| Environment.py | 立体4目並べのゲームの進行を行うファイル |
