import pytest
from bowling import calculate_frame_scores

base = [4, 5] * 9  # 9 complete open frames (score 9 each)


# --- Problem statement examples ---

def test_strike_missing_both_lookaheads():
    assert calculate_frame_scores([4, 5, "X", 8]) == [9, None, None]

def test_strike_with_complete_lookahead():
    assert calculate_frame_scores([4, 5, "X", 8, 1]) == [9, 19, 9]


# --- Strike lookahead ---

def test_strike_no_lookahead():
    assert calculate_frame_scores(["X"]) == [None]

def test_strike_missing_second_lookahead():
    assert calculate_frame_scores(["X", 3]) == [None, None]

def test_strike_fully_resolved():
    assert calculate_frame_scores(["X", 3, 4]) == [17, 7]

def test_consecutive_strikes_partial():
    assert calculate_frame_scores(["X", "X", 5]) == [25, None, None]

def test_three_strikes_only_first_resolved():
    assert calculate_frame_scores(["X", "X", "X"]) == [30, None, None]


# --- Spare lookahead ---

def test_spare_no_lookahead():
    assert calculate_frame_scores([5, "/"]) == [None]

def test_spare_resolved_next_frame_open():
    assert calculate_frame_scores([5, "/", 3]) == [13, None]

def test_spare_plus_strike_lookahead():
    assert calculate_frame_scores([5, "/", "X"]) == [20, None]

def test_spare_then_open_frame():
    assert calculate_frame_scores([5, "/", 3, 4]) == [13, 7]


# --- '/' pin value depends on prior roll ---

def test_strike_lookahead_includes_spare():
    assert calculate_frame_scores(["X", 7, "/"]) == [20, None]

def test_spare_resolves_next_frame_open():
    assert calculate_frame_scores(["X", 7, "/", 5]) == [20, 15, None]

def test_strike_spare_open_all_resolved():
    assert calculate_frame_scores(["X", 7, "/", 5, 2]) == [20, 15, 7]


# --- Full games ---

def test_gutter_game():
    assert calculate_frame_scores([0] * 20) == [0] * 10

def test_perfect_game():
    assert calculate_frame_scores(["X"] * 12) == [30] * 10


# --- 10th frame: strike earns two bonus rolls ---

def test_10th_strike_no_bonuses():
    assert calculate_frame_scores(base + ["X"]) == [9]*9 + [None]

def test_10th_strike_one_bonus():
    assert calculate_frame_scores(base + ["X", 5]) == [9]*9 + [None]

def test_10th_strike_two_bonuses():
    assert calculate_frame_scores(base + ["X", 5, 3]) == [9]*9 + [18]

def test_10th_three_strikes():
    assert calculate_frame_scores(base + ["X", "X", "X"]) == [9]*9 + [30]

def test_10th_strike_then_spare():
    assert calculate_frame_scores(base + ["X", 7, "/"]) == [9]*9 + [20]


# --- 10th frame: spare earns one bonus roll ---

def test_10th_spare_no_bonus():
    assert calculate_frame_scores(base + [5, "/"]) == [9]*9 + [None]

def test_10th_spare_with_bonus():
    assert calculate_frame_scores(base + [5, "/", 7]) == [9]*9 + [17]

def test_10th_spare_bonus_strike():
    assert calculate_frame_scores(base + [5, "/", "X"]) == [9]*9 + [20]


# --- 10th frame: open ---

def test_10th_open_frame():
    assert calculate_frame_scores(base + [3, 5]) == [9]*9 + [8]

def test_10th_only_one_roll():
    assert calculate_frame_scores(base + [3]) == [9]*9 + [None]


# --- Invalid inputs ---

def test_invalid_spare_opens_frame():
    with pytest.raises(ValueError):
        calculate_frame_scores(["/", 5])

def test_invalid_strike_as_second_ball():
    with pytest.raises(ValueError):
        calculate_frame_scores([5, "X"])

def test_invalid_open_frame_exceeds_10():
    with pytest.raises(ValueError):
        calculate_frame_scores([5, 6])

def test_invalid_spare_opens_10th():
    with pytest.raises(ValueError):
        calculate_frame_scores(base + ["/", 5])

def test_invalid_strike_as_second_ball_in_10th():
    with pytest.raises(ValueError):
        calculate_frame_scores(base + [3, "X"])

def test_invalid_spare_after_strike_in_10th():
    with pytest.raises(ValueError):
        calculate_frame_scores(base + ["X", "/"])

def test_invalid_spare_after_two_strikes_in_10th():
    with pytest.raises(ValueError):
        calculate_frame_scores(base + ["X", "X", "/"])

def test_invalid_strike_on_depleted_rack_in_10th():
    with pytest.raises(ValueError):
        calculate_frame_scores(base + ["X", 7, "X"])

def test_invalid_third_ball_exceeds_remaining_pins_in_10th():
    with pytest.raises(ValueError):
        calculate_frame_scores(base + ["X", 7, 4])

def test_invalid_extra_ball_after_open_10th():
    with pytest.raises(ValueError):
        calculate_frame_scores(base + [3, 5, 7])

def test_invalid_extra_ball_after_complete_10th():
    with pytest.raises(ValueError):
        calculate_frame_scores(base + ["X", 5, 3, 1])

def test_invalid_roll_value_int():
    with pytest.raises(ValueError):
        calculate_frame_scores([11])

def test_invalid_roll_value_negative():
    with pytest.raises(ValueError):
        calculate_frame_scores([-1])

def test_invalid_roll_value_str():
    with pytest.raises(ValueError):
        calculate_frame_scores(["Y"])
