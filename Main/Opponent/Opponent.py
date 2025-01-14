# 抽象クラスの作成に必要なimport文
from abc import ABCMeta, abstractmethod

class Opponent(metaclass = ABCMeta):
    @abstractmethod
    def opponent_move(self):
        pass