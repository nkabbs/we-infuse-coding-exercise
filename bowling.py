def calculate_frame_scores(rolls: list) -> list[int | None]:
    """
    Calculate per-frame bowling scores for a game in progress.

    Args:
        rolls: Roll values as int (0-9), 'X' (strike), or '/' (spare).

    Returns:
        Per-frame scores (int) or None for frames whose score can't be determined yet.
    """

    def pin_value(idx: int) -> int:
        roll = rolls[idx]
        if roll == 'X':
            return 10
        if roll == '/':
            prev = rolls[idx - 1]
            return 10 - (10 if prev == 'X' else int(prev))
        return int(roll)

    results = []
    roll_idx = 0

    for frame in range(10):
        if roll_idx >= len(rolls):
            break

        if frame < 9:
            first = rolls[roll_idx]

            if first == 'X':  # Strike: consumes 1 roll, needs 2 lookahead
                score = (
                    None if roll_idx + 2 >= len(rolls)
                    else 10 + pin_value(roll_idx + 1) + pin_value(roll_idx + 2)
                )
                results.append(score)
                roll_idx += 1

            elif roll_idx + 1 >= len(rolls):  # Only one roll so far in frame
                results.append(None)
                break

            elif rolls[roll_idx + 1] == '/':  # Spare: needs 1 lookahead
                score = (
                    None if roll_idx + 2 >= len(rolls)
                    else 10 + pin_value(roll_idx + 2)
                )
                results.append(score)
                roll_idx += 2

            else:  # Open frame
                results.append(pin_value(roll_idx) + pin_value(roll_idx + 1))
                roll_idx += 2

        else:  # 10th frame: strike or spare earns a bonus roll
            if roll_idx + 1 >= len(rolls):
                results.append(None)
                break

            first, second = rolls[roll_idx], rolls[roll_idx + 1]
            needs_bonus = first == 'X' or second == '/'

            if needs_bonus and roll_idx + 2 >= len(rolls):
                results.append(None)
            elif needs_bonus:
                results.append(
                    pin_value(roll_idx) + pin_value(roll_idx + 1) + pin_value(roll_idx + 2)
                )
            else:
                results.append(pin_value(roll_idx) + pin_value(roll_idx + 1))

    return results


if __name__ == "__main__":
    # --- Problem statement examples ---
    assert calculate_frame_scores([4, 5, "X", 8])    == [9, None, None], "strike missing both lookaheads"
    assert calculate_frame_scores([4, 5, "X", 8, 1]) == [9, 19, 9],     "strike with complete lookahead"

    # --- Strike lookahead ---
    assert calculate_frame_scores(["X"])             == [None],          "strike, no lookahead at all"
    assert calculate_frame_scores(["X", 3])          == [None, None],    "strike missing second lookahead"
    assert calculate_frame_scores(["X", 3, 4])       == [17, 7],         "strike fully resolved"
    assert calculate_frame_scores(["X", "X", 5])     == [25, None, None],"consecutive strikes partial"
    assert calculate_frame_scores(["X", "X", "X"])   == [30, None, None],"three strikes, only first resolved"

    # --- Spare lookahead ---
    assert calculate_frame_scores([5, "/"])           == [None],          "spare, no lookahead"
    assert calculate_frame_scores([5, "/", 3])        == [13, None],      "spare resolved, next frame open"
    assert calculate_frame_scores([5, "/", "X"])      == [20, None],      "spare + strike lookahead"
    assert calculate_frame_scores([5, "/", 3, 4])     == [13, 7],         "spare then open frame"

    # --- '/' pin value depends on prior roll ---
    assert calculate_frame_scores(["X", 7, "/"])      == [20, None],      "strike lookahead includes spare"
    assert calculate_frame_scores(["X", 7, "/", 5])  == [20, 15, None],  "spare resolves, next frame open"
    assert calculate_frame_scores(["X", 7, "/", 5, 2]) == [20, 15, 7],   "strike -> spare -> open, all resolved"

    # --- All gutter balls ---
    assert calculate_frame_scores([0] * 20)           == [0] * 10,        "gutter game"

    # --- Perfect game ---
    assert calculate_frame_scores(["X"] * 12)         == [30] * 10,       "perfect game"

    # --- 10th frame: strike earns two bonus rolls ---
    base = [4, 5] * 9  # 9 complete open frames (score 9 each)
    assert calculate_frame_scores(base + ["X"])           == [9]*9 + [None], "10th strike, no bonuses"
    assert calculate_frame_scores(base + ["X", 5])        == [9]*9 + [None], "10th strike, one bonus"
    assert calculate_frame_scores(base + ["X", 5, 3])     == [9]*9 + [18],   "10th strike, two bonuses"
    assert calculate_frame_scores(base + ["X", "X", "X"]) == [9]*9 + [30],   "10th frame three strikes"
    assert calculate_frame_scores(base + ["X", 7, "/"])   == [9]*9 + [20],   "10th strike then spare"

    # --- 10th frame: spare earns one bonus roll ---
    assert calculate_frame_scores(base + [5, "/"])        == [9]*9 + [None], "10th spare, no bonus"
    assert calculate_frame_scores(base + [5, "/", 7])     == [9]*9 + [17],   "10th spare with bonus"
    assert calculate_frame_scores(base + [5, "/", "X"])   == [9]*9 + [20],   "10th spare, bonus strike"

    # --- 10th frame: open (no bonus roll) ---
    assert calculate_frame_scores(base + [3, 5])          == [9]*9 + [8],    "10th open frame"
    assert calculate_frame_scores(base + [3])             == [9]*9 + [None], "10th frame, only one roll"

    print("All tests passed.")
