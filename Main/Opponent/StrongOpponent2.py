from .Opponent import OpponentBase
from Environment import Black, White, Empty
import numpy as np
import random

class StrongOpponent2(OpponentBase):
    def opponent_move(self, board):
        board_size = board.shape[0]
        valid_move = []
        for x in range(board_size):
            for y in range(board_size):
                for z in range(board_size):
                    if board[x, y, z] == Empty:
                        valid_move.append((x, y, z))
                        break
        def get_win_or_reach_moves(player):
            win_or_reach_moves = {
                "win": [],
                "reach": []
            }
            for x in range(board_size):
                # 上
                for y in range(board_size):
                    sum = board[x, y, :].sum()
                    if sum == player * 3:
                        # リーチ
                        for z in range(board_size):
                            if board[x, y, z] == Empty:
                                win_or_reach_moves["win"].append((x, y, z))
                                break
                    elif sum == player * 2:
                        # リーチ手前
                        for z in range(board_size):
                            if board[x, y, z] == Empty:
                                win_or_reach_moves["reach"].append((x, y, z))
                # 縦
                for z in range(board_size):
                    sum = board[x, :, z].sum()
                    if sum == player * 3:
                        # リーチ
                        for y in range(board_size):
                            if board[x, y, z] == Empty:
                                win_or_reach_moves["win"].append((x, y, z))
                                break
                    elif sum == player * 2:
                        # リーチ手前
                        for y in range(board_size):
                            if board[x, y, z] == Empty:
                                win_or_reach_moves["reach"].append((x, y, z))
                # 斜め1
                sum_cross_1 = np.diag(board[x]).sum()
                if sum_cross_1 == player * 3:
                    # リーチ
                    for i in range(board_size):
                        if board[x, i, i] == Empty:
                            win_or_reach_moves["win"].append((x, i, i))
                            break
                elif sum_cross_1 == player * 2:
                    # リーチ手前
                    for i in range(board_size):
                        if board[x, i, i] == Empty:
                            win_or_reach_moves["reach"].append((x, i, i))
                # 斜め2
                sum_cross_2 = np.diag(np.fliplr(board[x])).sum()
                if sum_cross_2 == player * 3:
                    # リーチ
                    for i in range(board_size):
                        if board[x, i, board_size - i - 1] == Empty:
                            win_or_reach_moves["win"].append((x, i, board_size - i - 1))
                            break
                elif sum_cross_2 == player * 2:
                    # リーチ手前
                    for i in range(board_size):
                        if board[x, i, board_size - i - 1] == Empty:
                            win_or_reach_moves["reach"].append((x, i, board_size - i - 1))
            for y in range(board_size):
                # 横
                for z in range(board_size):
                    sum = board[:, y, z].sum()
                    if sum == player * 3:
                        # リーチ
                        for x in range(board_size):
                            if board[x, y, z] == Empty:
                                win_or_reach_moves["win"].append((x, y, z))
                                break
                    elif sum == player * 2:
                        # リーチ手前
                        for x in range(board_size):
                            if board[x, y, z] == Empty:
                                win_or_reach_moves["reach"].append((x, y, z))
                # 斜め1
                sum_cross_1 = np.diag(board[:, y]).sum()
                if sum_cross_1 == player * 3:
                    # リーチ
                    for i in range(board_size):
                        if board[i, y, i] == Empty:
                            win_or_reach_moves["win"].append((i, y, i))
                            break
                elif sum_cross_1 == player * 2:
                    # リーチ手前
                    for i in range(board_size):
                        if board[i, y, i] == Empty:
                            win_or_reach_moves["reach"].append((i, y, i))
                # 斜め2
                sum_cross_2 = np.diag(np.fliplr(board[:, y])).sum()
                if sum_cross_2 == player * 3:
                    # リーチ
                    for i in range(board_size):
                        if board[i, y, board_size - i - 1] == Empty:
                            win_or_reach_moves["win"].append((i, y, board_size - i - 1))
                            break
                elif sum_cross_2 == player * 2:
                    # リーチ手前
                    for i in range(board_size):
                        if board[i, y, board_size - i - 1] == Empty:
                            win_or_reach_moves["reach"].append((i, y, board_size - i - 1))
            for z in range(board_size):
                # 斜め1
                sum_cross_1 = np.diag(board[:, :, z]).sum()
                if sum_cross_1 == player * 3:
                    # リーチ
                    for i in range(board_size):
                        if board[i, i, z] == Empty:
                            win_or_reach_moves["win"].append((i, i, z))
                            break
                elif sum_cross_1 == player * 2:
                    # リーチ手前
                    for i in range(board_size):
                        if board[i, i, z] == Empty:
                            win_or_reach_moves["reach"].append((i, i, z))
                # 斜め2
                sum_cross_2 = np.diag(np.fliplr(board[:, :, z])).sum()
                if sum_cross_2 == player * 3:
                    # リーチ
                    for i in range(board_size):
                        if board[i, board_size - i - 1, z] == Empty:
                            win_or_reach_moves["win"].append((i, board_size - i - 1, z))
                            break
                elif sum_cross_2 == player * 2:
                    # リーチ手前
                    for i in range(board_size):
                        if board[i, board_size - i - 1, z] == Empty:
                            win_or_reach_moves["reach"].append((i, board_size - i - 1, z))
            sum_cross_1 = np.array([board[i, i, i] for i in range(board_size)]).sum()
            if sum_cross_1 == player * 3:
                # リーチ
                for i in range(board_size):
                    if board[i, i, i] == Empty:
                        win_or_reach_moves["win"].append((i, i, i))
                        break
            elif sum_cross_1 == player * 2:
                # リーチ手前
                for i in range(board_size):
                    if board[i, i, i] == Empty:
                        win_or_reach_moves["reach"].append((i, i, i))
            sum_cross_2 = np.array([board[i, i, board_size - i - 1] for i in range(board_size)]).sum()
            if sum_cross_2 == player * 3:
                # リーチ
                for i in range(board_size):
                    if board[i, i, board_size - i - 1] == Empty:
                        win_or_reach_moves["win"].append((i, i, board_size - i - 1))
                        break
            elif sum_cross_2 == player * 2:
                # リーチ手前
                for i in range(board_size):
                    if board[i, i, board_size - i - 1] == Empty:
                        win_or_reach_moves["reach"].append((i, i, board_size - i - 1))
            sum_cross_3 = np.array([board[i, board_size - i - 1, i] for i in range(board_size)]).sum()
            if sum_cross_3 == player * 3:
                # リーチ
                for i in range(board_size):
                    if board[i, board_size - i - 1, i] == Empty:
                        win_or_reach_moves["win"].append((i, board_size - i - 1, i))
                        break
            elif sum_cross_3 == player * 2:
                # リーチ手前
                for i in range(board_size):
                    if board[i, board_size - i - 1, i] == Empty:
                        win_or_reach_moves["reach"].append((i, board_size - i - 1, i))
            sum_cross_4 = np.array([board[i, board_size - i - 1, board_size - i - 1] for i in range(board_size)]).sum()
            if sum_cross_4 == player * 3:
                # リーチ
                for i in range(board_size):
                    if board[i, board_size - i - 1, board_size - i - 1] == Empty:
                        win_or_reach_moves["win"].append((i, board_size - i - 1, board_size - i - 1))
                        break
            elif sum_cross_4 == player * 2:
                # リーチ手前
                for i in range(board_size):
                    if board[i, board_size - i - 1, board_size - i - 1] == Empty:
                        win_or_reach_moves["reach"].append((i, board_size - i - 1, board_size - i - 1))
            return win_or_reach_moves
        
        my_win_or_reach_moves = get_win_or_reach_moves(White)           # このクラスは敵だから、白色
        opponent_win_or_reach_moves = get_win_or_reach_moves(Black)     # このクラスにとっての敵は、黒色

        my_win_moves = [m for m in my_win_or_reach_moves["win"] if m in valid_move]
        opponent_win_moves = [m for m in opponent_win_or_reach_moves["win"] if m in valid_move]

        # 自分がリーチの場合、置く
        if len(my_win_moves) > 0:
            return random.choice(my_win_moves)
        # 相手がリーチの場合、防ぐ
        if len(opponent_win_moves) > 0:
            return random.choice(opponent_win_moves)
        
        my_reach_moves = [m for m in my_win_or_reach_moves["reach"] if m in valid_move]
        opponent_reach_moves = [m for m in opponent_win_or_reach_moves["reach"] if m in valid_move]

        # リーチになるかずが多いものを取得
        my_most_reach_moves = []
        most_reaches = 0
        for m in my_reach_moves:
            if m not in my_most_reach_moves:
                m_count = my_reach_moves.count(m)
                if m_count == most_reaches:
                    my_most_reach_moves.append(m)
                elif m_count > most_reaches:
                    my_most_reach_moves.clear()
                    my_most_reach_moves.append(m)
                    most_reaches = m_count
        if len(my_most_reach_moves) > 0:
            return random.choice(my_most_reach_moves)
        opponent_most_reach_moves = []
        most_reaches = 0
        for m in opponent_reach_moves:
            if m not in opponent_most_reach_moves:
                m_count = opponent_reach_moves.count(m)
                if m_count == most_reaches:
                    opponent_most_reach_moves.append(m)
                elif m_count > most_reaches:
                    opponent_most_reach_moves.clear()
                    opponent_most_reach_moves.append(m)
                    most_reaches = m_count
        if len(opponent_most_reach_moves) > 0:
            return random.choice(opponent_most_reach_moves)
        # 真ん中8つのマスが価値が高いらしいから優先的に置く
        valued_move = [
            m for m in [
                (1, 1, 1),
                (1, 1, 2),
                (1, 2, 1),
                (1, 2, 2),
                (2, 1, 1),
                (2, 1, 2),
                (2, 2, 1),
                (2, 2, 2)
            ] if m in valid_move
        ]
        if len(valued_move) > 0:
            return random.choice(valued_move)
        # フ型を作る
        hu_moves = []
        for x in range(board_size):
            if board[x, 0, 0] == White and board[x, 1, 1] == White:
                if board[x, 0, 2] == White:
                    hu_moves.append((x, 1, 2))
                elif board[x, 1, 2] == White:
                    hu_moves.append((x, 0, 2))
            if board[x, 0, 1] == White and board[x, 1, 2] == White:
                if board[x, 0, 3] == White:
                    hu_moves.append((x, 1, 3))
                elif board[x, 1, 3] == White:
                    hu_moves.append((x, 0, 3))
            if board[x, 3, 0] == White and board[x, 2, 1] == White:
                if board[x, 3, 2] == White:
                    hu_moves.append((x, 2, 2))
                elif board[x, 2, 2] == White:
                    hu_moves.append((x, 3, 2))
            if board[x, 3, 1] == White and board[x, 2, 2] == White:
                if board[x, 3, 3] == White:
                    hu_moves.append((x, 2, 3))
                elif board[x, 2, 3] == White:
                    hu_moves.append((x, 3, 3))
        for y in range(board_size):
            if board[0, y, 0] == White and board[1, y, 1] == White:
                if board[0, y, 2] == White:
                    hu_moves.append((1, y, 2))
                elif board[1, y, 2] == White:
                    hu_moves.append((0, y, 2))
            if board[0, y, 1] == White and board[1, y, 2] == White:
                if board[0, y, 3] == White:
                    hu_moves.append((1, y, 3))
                elif board[1, y, 3] == White:
                    hu_moves.append((0, y, 3))
            if board[3, y, 0] == White and board[2, y, 1] == White:
                if board[3, y, 2] == White:
                    hu_moves.append((2, y, 2))
                elif board[2, y, 2] == White:
                    hu_moves.append((3, y, 2))
            if board[3, y, 1] == White and board[2, y, 2] == White:
                if board[3, y, 3] == White:
                    hu_moves.append((2, y, 3))
                elif board[2, y, 3] == White:
                    hu_moves.append((3, y, 3))
        for z in range(board_size):
            if board[0, 0, z] == White and board[1, 1, z] == White:
                if board[2, 0, z] == White:
                    hu_moves.append((2, 1, z))
                elif board[2, 1, z] == White:
                    hu_moves.append((2, 0, z))
            if board[1, 0, z] == White and board[2, 1, z] == White:
                if board[3, 0, z] == White:
                    hu_moves.append((3, 1, z))
                elif board[3, 1, z] == White:
                    hu_moves.append((3, 0, z))
            if board[0, 3, z] == White and board[1, 2, z] == White:
                if board[2, 3, z] == White:
                    hu_moves.append((2, 2, z))
                elif board[2, 2, z] == White:
                    hu_moves.append((2, 3, z))
            if board[1, 3, z] == White and board[2, 2, z] == White:
                if board[3, 3, z] == White:
                    hu_moves.append((3, 2, z))
                elif board[3, 2, z] == White:
                    hu_moves.append((3, 3, z))
        hu_moves = [m for m in hu_moves if m in valid_move]
        if len(hu_moves) > 0:
            return random.choice(hu_moves)
        # どれも当てはまらないなら、置けるところにおく
        return random.choice(valid_move)