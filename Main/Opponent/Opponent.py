# 抽象クラスの作成に必要なimport文
from abc import ABCMeta, abstractmethod

# 抽象クラスの作成
class OpponentBase(metaclass = ABCMeta):
    @abstractmethod
    def opponent_move(self, board):
        pass