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

# Validate the first two balls of the 10th frame; returns True if a bonus ball is earned.
def is_bonus_for_tenth_frame(first, second) -> bool:
    if first != 'X' and second == 'X':
        raise ValueError("Strike in second roll must follow a strike in the 10th frame")
    if first == 'X' and second == '/':
        raise ValueError("Spare notation invalid when pins were reset by a first-ball strike")
    if first != 'X' and second != '/' and int(first) + int(second) > 10:
        raise ValueError("Open frame total exceeds available pins")
    return first == 'X' or second == '/'

# Validate the bonus ball of the 10th frame given the second ball and rack context.
def validate_tenth_frame_bonus(second, third, shared_rack):
    if third == '/' and not shared_rack:
        raise ValueError("Spare requires pins remaining from the same rack")
    if third == 'X' and shared_rack:
        raise ValueError("Cannot strike with a partially depleted rack")
    if shared_rack and third != '/' and int(second) + int(third) > 10:
        raise ValueError("Third ball total exceeds 10 pins")

# Score the 10th frame, which awards a bonus roll after a strike or spare
def score_tenth_frame(rolls: list, roll_idx: int) -> int | None:
    first = rolls[roll_idx]

    if first == '/':
        raise ValueError("Spare cannot open the 10th frame")

    if roll_idx + 1 >= len(rolls):
        return None

    second = rolls[roll_idx + 1]
    earns_bonus = is_bonus_for_tenth_frame(first, second)

    if not earns_bonus:
        if roll_idx + 2 < len(rolls):
            raise ValueError("Extra rolls after a complete 10th frame with no bonus")
        return pin_value(rolls, roll_idx) + pin_value(rolls, roll_idx + 1)

    if roll_idx + 2 >= len(rolls):
        return None  # bonus ball not yet thrown

    third = rolls[roll_idx + 2]
    shared_rack = (first == 'X' and second not in ('X', '/'))
    validate_tenth_frame_bonus(second, third, shared_rack)

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
