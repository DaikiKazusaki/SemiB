# SemiB

## セットアップ
1. 作業ディレクトリ作成
```
mkdir <dir>
```
2. cloneする
```
git clone https://github.com/DaikiKazusaki/SemiB
```
## Gitにcommit，pushする流れ
1. ステージングしたいファイルを選択する．
``` 
git add <file>
```

2. コミットする．コミットする際にはコミットメッセージが必要になるので，``` -m ```オプションを用いる．
```
git commit -m <message>
```

3. mainとの照合を行う．
```
git switch main
git pull origin main
```

4. remote branchにpush
```
git push origin <branch>
```

5. GitHub上でPull Requestを作成する
6. Pull Requestが通ればmainにmerge
```
git merge <branch>
```

## 開発中に使用頻度の高いコマンド

### Git管理しないファイルのメモ : .gitignore
ディレクトリ内に置いておきたいものの，Git管理したくないファイルは``` .gitignore ```に記載しておく．

なお，``` .gitignore ```ファイル自体はGit管理するファイルなので，作成後は
``` 
git add .gitignore
git commit -m <message>
```
としてコミットしておく必要がある．

### インデックスにステージング : add
必要に応じて以下のオプションの利用も可能である．特に``` -A ```オプションは使用頻度が高いものである．
| オプション | 内容 | 
| :-: | --- |
| ``` -A ``` | 作業フォルダ全ての変更をステージングする |

### ブランチを確認する : branch
現在のブランチを確認するコマンドは以下のとおりである．
```
git branch
```
必要に応じて以下のオプションの利用も可能である．
| オプション | 内容 | 
| :-: | --- |
| ``` -d ``` | ブランチの削除 |
| ``` -D ``` | 強制的にブランチを削除する |

### ブランチを移動 : switch
ブランチを移動するコマンドは以下の通りである．
``` 
git switch <branch> 
```
必要に応じて以下のオプションの利用も可能である．

| オプション | 内容 | 
| :-: | --- |
| ``` -c  ``` | 新しくブランチを作成し，そのブランチに移動する |

### ファイルの状態を確認 : status
``` 
git status 
```
| オプション | 内容 | 
| :-: | --- |
| ``` -s  ``` |  |

### 過去の履歴を確認する : log
```
git log
```
必要に応じて以下のオプションを用いることがある．
| オプション | 内容 | 
| :-: | --- |
| ``` --online ``` | 短縮表示される |
| ``` --graph ``` | グラフ表示する |

### コミットメッセージの修正
コミットメッセージにタイプミスがあった場合，以下のコマンドを用いることで修正することができる．
```
git commit --amend -m "message"
```

## 付録：GitHubを使用する上での注意点

### branch名について
remote branchの名前は，"誰が，何を"実装しているのかを分かりやすく命名する．
- 命名規則 : feature/{名前}/{実装内容}
- (ex) feature/Daiki-Kazusaki/計算機能のバグ修正

### remote branchの削除
remote branchの削除のコマンドは``` git branch -d <branch> ```であるが，これを行う際には以下の点に注意する必要がある．
- 削除対象のbranchがremote branchにpushまたはmergeされている場合にのみ行われる．
- pushやmergeされていないブランチを削除したい場合は``` -D ```オプションを用いる．

### 名称の変更
GitHubでは名称の変更が行われていたり，非推奨のコマンドがあったりします．以下はその一部である．
| 旧名称 | 新名称 |
| :-: | :-: |
| masterブランチ | mainブランチ |
| checkoutコマンド | switchコマンド |
| resetコマンド| restoreコマンド |
