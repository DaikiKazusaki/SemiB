# 抽象クラスの作成に必要なimport文
from abc import ABC, abstractmethod

class Opponent():
    @abstractmethod
    def opponent_move(self):
        pass