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

    if first == 'X':
        if roll_idx + 2 >= len(rolls):
            return None, 1
        score = 10 + pin_value(rolls, roll_idx + 1) + pin_value(rolls, roll_idx + 2)
        return score, 1

    if roll_idx + 1 >= len(rolls):
        return None, None  # second ball not thrown yet, caller should stop

    if rolls[roll_idx + 1] == '/':
        if roll_idx + 2 >= len(rolls):
            return None, 2
        return 10 + pin_value(rolls, roll_idx + 2), 2

    return pin_value(rolls, roll_idx) + pin_value(rolls, roll_idx + 1), 2

# Score the 10th frame, which awards a bonus roll after a strike or spare.
def score_tenth_frame(rolls: list, roll_idx: int) -> int | None:
    if roll_idx + 1 >= len(rolls):
        return None

    first, second = rolls[roll_idx], rolls[roll_idx + 1]
    earns_bonus = first == 'X' or second == '/'

    if earns_bonus:
        if roll_idx + 2 >= len(rolls):
            return None
        return pin_value(rolls, roll_idx) + pin_value(rolls, roll_idx + 1) + pin_value(rolls, roll_idx + 2)

    return pin_value(rolls, roll_idx) + pin_value(rolls, roll_idx + 1)

# rolls: Roll values as int (0-9), 'X' (strike), or '/' (spare).
def calculate_frame_scores(rolls: list) -> list[int | None]:
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

# Validate the rolls array to ensure it is a valid bowling game (possibly in progress).
def validate_rolls(rolls: list) -> bool:
    valid_values = set(range(10)) | {'X', '/'}
    if any(r not in valid_values for r in rolls):
        raise ValueError(f"Invalid roll value")

    roll_idx = 0

    for frame in range(10):
        if roll_idx >= len(rolls):
            return True  # game still in progress

        first = rolls[roll_idx]
        if first == '/':
            raise ValueError("Spare cannot open a frame")

        if first == 'X':
            if frame < 9:
                roll_idx += 1
                continue
            # 10th frame strike: check second ball under reset-rack rules
            if roll_idx + 1 >= len(rolls):
                return True
            second = rolls[roll_idx + 1]
            if second == '/':
                raise ValueError("Spare notation invalid when pins were reset by a first-ball strike")
        else:
            # Non-strike: validate the second ball (shared rules for all frames)
            if roll_idx + 1 >= len(rolls):
                return True  # mid-frame, game still in progress
            second = rolls[roll_idx + 1]
            if second == 'X':
                raise ValueError("Strike cannot be the second ball of a frame")
            if second != '/' and int(first) + int(second) > 10:
                raise ValueError("Open frame total exceeds available pins")
            if frame < 9:
                roll_idx += 2
                continue

        # Only the 10th frame reaches here
        earns_bonus = (first == 'X' or second == '/')
        if not earns_bonus:
            if roll_idx + 2 < len(rolls):
                raise ValueError("Extra rolls after a complete open 10th frame")
            return True
        if roll_idx + 2 >= len(rolls):
            return True  # bonus ball not yet thrown
        third = rolls[roll_idx + 2]
        shared_rack = (first == 'X' and second not in ('X', '/'))
        if third == '/' and not shared_rack:
            raise ValueError("Spare requires pins remaining from the same rack")
        if third == 'X' and shared_rack:
            raise ValueError("Cannot strike with a partially depleted rack")
        if shared_rack and third != '/' and int(second) + int(third) > 10:
            raise ValueError("Third ball exceeds remaining pins")
        if roll_idx + 3 < len(rolls):
            raise ValueError("Game is complete, no further rolls allowed")

    return True

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

    def assert_invalid(rolls, msg):
        try:
            validate_rolls(rolls)
            raise AssertionError(f"Expected ValueError for: {msg}")
        except ValueError:
            pass

    # --- validate_rolls: valid inputs ---
    assert validate_rolls([]) == True,                              "empty list"
    assert validate_rolls(["X"]) == True,                          "single strike"
    assert validate_rolls([5, "/"]) == True,                       "spare in progress"
    assert validate_rolls([4, 5, "X", 8, 1]) == True,             "mixed frames"
    assert validate_rolls(["X"] * 12) == True,                     "perfect game"
    assert validate_rolls([0] * 20) == True,                       "gutter game"
    assert validate_rolls(base + ["X", 5, 3]) == True,             "10th strike with bonuses"
    assert validate_rolls(base + ["X", 7, "/"]) == True,           "10th strike then spare"
    assert validate_rolls(base + [5, "/", "X"]) == True,           "10th spare, bonus strike"
    assert validate_rolls(base + [3, 5]) == True,                  "open 10th frame"

    # --- validate_rolls: invalid inputs ---
    assert_invalid([11],                          "invalid roll value")
    assert_invalid(["Y"],                         "invalid roll value")
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

    print("All tests passed.")
