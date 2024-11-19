import copy

def apply_move(state, move, direction, score):
    """
    Thực hiện nước đi cho người chơi.
    state: Trạng thái bàn cờ hiện tại.
    move: Ô được chọn để bắt đầu di chuyển (index trong danh sách state).
    direction: Hướng di chuyển, "right" (ccw) hoặc "left" (cw).
    """
    new_state = state[:]
    hand = len(new_state[move])  # Số quân từ ô được chọn
    new_state[move] = ""  # Làm rỗng ô đã chọn
    pos = move

    while hand > 0:  # Rải quân
        if direction == "right":
            pos = (pos - 1) % 12  # Vòng quanh bàn cờ về bên phải
        else:
            pos = (pos + 1) % 12  # Vòng quanh bàn cờ về bên trái

        new_state[pos] += "0"  # Thêm 1 quân vào ô
        hand -= 1
    # Tiếp tục nếu ô cuối cùng có quân
    while True:  # Không được lấy quân ở ô quan
        next_pos = (pos - 1) % 12 if direction == "right" else (pos + 1) % 12
        if new_state[next_pos] == "":
            # Nếu ô kế tiếp trống, kiểm tra ăn quân
            further_pos = (next_pos - 1) % 12 if direction == "right" else (next_pos + 1) % 12
            if new_state[further_pos] != "":
                # Ăn quân ở ô kế tiếp nữa
                current_player = "player1" if move >= 7 else "player2"
                score[current_player] += new_state[further_pos]
                new_state[further_pos] = ""  # Làm rỗng ô đã ăn
            break
        elif next_pos != 0 and next_pos != 6:
            # Lấy quân ở ô kế tiếp và tiếp tục rải
            hand = len(new_state[next_pos])
            new_state[next_pos] = ""
            pos = next_pos
            while hand > 0:
                if direction == "right":
                    pos = (pos - 1) % 12
                else:
                    pos = (pos + 1) % 12
                new_state[pos] += "0"
                hand -= 1

        if next_pos == 0 or next_pos == 6:
            break
        next_two_pos = (next_pos - 1) % 12 if direction == "right" else (next_pos + 1) % 12
        if new_state[next_pos] == "" and new_state[next_two_pos] == "":
            break
    #     print("score: ", score)
    #     print("new_state: ", new_state)
    #     print("next_pos: ", next_pos)
    #     print("next_two_pos: ", next_two_pos)
    #     print("move ", move)
    #     print("direction ", direction)
    # print("new state break: ", new_state)
    return new_state    

def is_empty(state, player):
    """
    Kiểm tra nếu bàn cờ của người chơi hiện tại trống.
    """
    if player == "player1":
        region = state[7:12]  # Vùng quân của Player 1
    else:
        region = state[1:6]  # Vùng quân của Player 2

    return all(cell == "" for cell in region)

def redistribute_from_score(state, player):
    """
    Rải tối đa 5 quân từ điểm số của người chơi vào các ô trống trên bàn cờ.
    state: Trạng thái bàn cờ hiện tại.
    player: Người chơi cần rải quân ("player1" hoặc "player2").
    """
    if player == "player1":
        region = range(7, 12)  # Các ô của Player 1
    else:
        region = range(1, 6)  # Các ô của Player 2

    # Rải quân vào các ô trống
    for i in region:
        if "0" in score[player]:  # Kiểm tra nếu còn quân trong score
            state[i] = "0"  # Rải 1 quân vào ô
            score[player] = score[player].replace("0", "", 1)  # Xóa 1 "0" đầu tiên trong score
        else:
            return False  # Nếu không còn quân nào, dừng lại
    return True


def evaluate(state, score):
    """
    Tính điểm dựa trên trạng thái bàn cờ, điểm số hiện tại và số quân còn lại.
    - Mỗi quân trên bàn cờ thuộc về player sẽ được tính điểm.
    - Quan được tính là 10 điểm cho mỗi quan đã bị ăn (trong score, ký tự "1" hoặc "2").
    """
    # Điểm từ số quân đã ăn
    player1_score = len(score["player1"])  # Số quân thường Player 1 đã ăn
    player2_score = len(score["player2"])  # Số quân thường Player 2 đã ăn

    # Cộng thêm 10 điểm cho mỗi quan ("1" hoặc "2") trong score
    player1_score += (score["player1"].count("1") + score["player1"].count("2")) * 10
    player2_score += (score["player2"].count("1") + score["player2"].count("2")) * 10

    # Điểm từ các quân trên bàn cờ
    player1_board_score = sum(len(cell) for cell in state[7:12])  # Các ô của Player 1
    player2_board_score = sum(len(cell) for cell in state[1:6])   # Các ô của Player 2

    # Tổng điểm
    total_player1_score = player1_score + player1_board_score
    total_player2_score = player2_score + player2_board_score

    # Điểm số AI (Player 2) trừ điểm Player 1
    return total_player2_score - total_player1_score


def minimax(state, depth, maximizing_player, alpha, beta, score):
    """
    Thuật toán Minimax với cắt tỉa Alpha-Beta.
    state: Trạng thái bàn cờ hiện tại.
    depth: Độ sâu tối đa để tìm kiếm.
    maximizing_player: True nếu AI đang chơi, False nếu đối thủ đang chơi.
    alpha: Giá trị alpha để cắt tỉa.
    beta: Giá trị beta để cắt tỉa.
    """
    if depth == 0 or (state[0] == "" and state[6] == ""):  # Trò chơi kết thúc hoặc đạt độ sâu tối đa
        return evaluate(state, score), None

    if maximizing_player:
        max_eval = float("-inf")
        best_move = None
        for move in range(1, 6):  # Player 2 (AI) chơi từ ô 1 -> 5
            if state[move] != "":  # Bỏ qua các ô trống
                for direction in ["left", "right"]:  # Thử cả hai hướng
                    temp_score = copy.deepcopy(score)
                    temp_state = copy.deepcopy(state)
                    new_state = apply_move(temp_state, move, direction, temp_score)
                    eval, _ = minimax(new_state, depth - 1, False, alpha, beta, temp_score)
                    if eval > max_eval:
                        max_eval = eval
                        best_move = (move, direction)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break  # Cắt tỉa
        return max_eval, best_move
    else:
        min_eval = float("inf")
        best_move = None
        for move in range(7, 12):  # Player 1 chơi từ ô 7 -> 11
            if state[move] != "":  # Bỏ qua các ô trống
                for direction in ["left", "right"]:  # Thử cả hai hướng
                    temp_score = copy.deepcopy(score)
                    temp_state = copy.deepcopy(state)
                    new_state = apply_move(temp_state, move, direction, temp_score)
                    eval, _ = minimax(new_state, depth - 1, True, alpha, beta, temp_score)
                    if eval < min_eval:
                        min_eval = eval
                        if direction == "right":
                            best_move = (move, "ccw")
                        else:
                            best_move = (move, "cw")
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break  # Cắt tỉa
        return min_eval, best_move


# Trạng thái ban đầu của bàn cờ
state = ["1", "00000", "00000", "00000", "00000", "00000", "2", "00000", "00000", "00000", "00000", "00000"]

print("Initial state:")
print(state)
depth = 5
score = {"player1": "", "player2": ""}  # Khởi tạo điểm số
# Chơi 2 người
while True:
    # Người chơi 1 chọn nước đi
    if is_empty(state, "player1"):
        print("Player 1's board is empty! Redistributing pieces from score...")
        is_can_redistribute = redistribute_from_score(state, "player1")
        if is_can_redistribute is False:
            print("Player 1 can't redistribute any more pieces! Player 2 wins!")
            break
        print("State after redistribution (Player 1):")
        print(state)
    # Người chơi 1 thực hiện nước đi
    move = int(input("Player 1: Choose a hole (7-11): "))
    direction = input("Player 1: Choose direction (ccw/cw): ").strip()
    if direction == "ccw":
        direction = "right"
    else:
        direction = "left"
    state = apply_move(state, move, direction, score)
    print("After Player 1's move:")
    print("Score: ", score)
    print(state)

    # Kiểm tra kết thúc
    if state[0] == "" and state[6] == "":
        print("Game over!")
        print("Final state:")
        print(state)
        print("Final scores:")
        print("Player 1:", score["player1"])
        print("Player 2:", score["player2"])
        break

    # Player 2 (AI) chọn nước đi
    if is_empty(state, "player2"):
        print("Player 2's board is empty! Redistributing pieces from score...")
        is_can_redistribute = redistribute_from_score(state, "player2")
        if is_can_redistribute is False:
            print("Player 2 can't redistribute any more pieces! Player 1 wins!")
            break
        print("State after redistribution (Player 2):")
        print(state)

    # AI thực hiện Minimax để chọn nước đi tốt nhất
    print("Player 2 (AI) is thinking...")
    temp_score = copy.deepcopy(score)
    temp_state = copy.deepcopy(state)
    _, best_move = minimax(temp_state, depth, True, float("-inf"), float("inf"), temp_score)
    if best_move is not None:
        move, direction = best_move
        print(f"Player 2 (AI) chooses hole {move} and direction {direction}")
        state = apply_move(state, move, direction, score)
        print("After Player 2's move:")
        print("Score: ", score)
        print(state)
    else:
        print("No valid moves for Player 2!")
        break

    # Kiểm tra kết thúc
    if state[0] == "" and state[6] == "":
        print("Game over!")
        print("Final state:")
        print(state)
        print("Final scores:")
        print("Player 1:", score["player1"])
        print("Player 2:", score["player2"])
        break
