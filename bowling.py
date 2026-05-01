# Return the number of pins knocked down by the roll at rolls[idx].
def pin_value(rolls: list, idx: int) -> int:
    roll = rolls[idx]
    if roll == 'X':
        return 10
    if roll == '/':
        prev = rolls[idx - 1]
        return 10 - int(prev)
    return int(roll)

# Score a single regular frame (frames 1–9), returning (score, rolls_consumed)
def score_regular_frame(rolls: list, roll_idx: int) -> tuple[int | None, int | None]:
    first = rolls[roll_idx]
    if first == '/':
        raise ValueError("Spare cannot open a frame")
    if first == 'X':
        if roll_idx + 2 >= len(rolls):
            return None, 1
        score = 10 + pin_value(rolls, roll_idx + 1) + pin_value(rolls, roll_idx + 2)
        return score, 1
    if roll_idx + 1 >= len(rolls):
        return None, None  # second ball not thrown yet, caller should stop
    second = rolls[roll_idx + 1]
    if second == 'X':
        raise ValueError("Strike cannot be the second ball of a frame")
    if second == '/':
        if roll_idx + 2 >= len(rolls):
            return None, 2
        return 10 + pin_value(rolls, roll_idx + 2), 2
    if int(first) + int(second) > 10:
        raise ValueError("Frame total exceeds 10 pins")
    return pin_value(rolls, roll_idx) + pin_value(rolls, roll_idx + 1), 2

# Score the 10th frame, which awards a bonus roll after a strike or spare
def score_tenth_frame(rolls: list, roll_idx: int) -> int | None:
    first = rolls[roll_idx]
    
    if first == '/':
        raise ValueError("Spare cannot open the 10th frame")
    
    if roll_idx + 1 >= len(rolls):
        return None

    second = rolls[roll_idx + 1]

    if first != 'X' and second == 'X':
        raise ValueError("Strike in second roll must follow a strike in the 10th frame")
    if first == 'X' and second == '/':
        raise ValueError("Spare notation invalid when pins were reset by a first-ball strike")
    if first != 'X' and second != '/' and int(first) + int(second) > 10:
        raise ValueError("Open frame total exceeds available pins")

    earns_bonus = (first == 'X' or second == '/')
    if not earns_bonus:
        if roll_idx + 2 < len(rolls):
            raise ValueError("Extra rolls after a complete 10th frame with no bonus")
        return pin_value(rolls, roll_idx) + pin_value(rolls, roll_idx + 1)

    if roll_idx + 2 >= len(rolls):
        return None  # bonus ball not yet thrown

    third = rolls[roll_idx + 2]
    shared_rack = (first == 'X' and second not in ('X', '/'))
    if third == '/' and not shared_rack:
        raise ValueError("Spare requires pins remaining from the same rack")
    if third == 'X' and shared_rack:
        raise ValueError("Cannot strike with a partially depleted rack")
    if shared_rack and third != '/' and int(second) + int(third) > 10:
        raise ValueError("Third ball total exceeds 10 pins")
    if roll_idx + 3 < len(rolls):
        raise ValueError("More than 3 rolls after a complete 10th frame with bonus")

    return pin_value(rolls, roll_idx) + pin_value(rolls, roll_idx + 1) + pin_value(rolls, roll_idx + 2)


def is_invalid_value_in_rolls(rolls: list) -> bool:
    valid_values = set(range(10)) | {'X', '/'}
    if any(r not in valid_values for r in rolls):
        return True
    return False

# rolls: Roll values as int (0-9), 'X' (strike), or '/' (spare)
def calculate_frame_scores(rolls: list) -> list[int | None]:
    if is_invalid_value_in_rolls(rolls):
        raise ValueError(f"Invalid roll value: {rolls}")

    results = []
    roll_idx = 0

    for frame in range(10):
        if roll_idx >= len(rolls):
            break

        if frame < 9:
            score, rolls_consumed = score_regular_frame(rolls, roll_idx)
            results.append(score)
            if rolls_consumed is None:  # frame is mid-roll, no further frames to score
                break
            roll_idx += rolls_consumed
        else:
            results.append(score_tenth_frame(rolls, roll_idx))

    return results


if __name__ == "__main__":
    def assert_invalid(rolls, msg):
        try:
            calculate_frame_scores(rolls)
            raise AssertionError(f"Expected ValueError for: {msg}")
        except ValueError:
            pass

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

    # --- invalid inputs (now caught by scoring functions) ---
    assert_invalid(["/", 5],                      "spare opens a frame")
    assert_invalid([5, "X"],                      "strike as second ball")
    assert_invalid([5, 6],                        "open frame exceeds 10 pins")
    assert_invalid(base + ["/", 5],               "spare opens 10th frame")
    assert_invalid(base + [3, "X"],               "strike as second ball in 10th")
    assert_invalid(base + ["X", "/"],             "spare after first-ball strike in 10th")
    assert_invalid(base + ["X", "X", "/"],        "spare after two strikes in 10th")
    assert_invalid(base + ["X", 7, "X"],          "strike on depleted rack in 10th")
    assert_invalid(base + ["X", 7, 4],            "third ball exceeds remaining pins")
    assert_invalid(base + [3, 5, 7],              "extra ball after open 10th")
    assert_invalid(base + ["X", 5, 3, 1],         "extra ball after complete 10th")
    assert_invalid([11],                          "invalid roll value: 11")
    assert_invalid(["Y"],                         "invalid roll value: Y")

    print("All tests passed.")
