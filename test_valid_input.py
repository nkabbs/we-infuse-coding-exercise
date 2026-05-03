import pytest
from bowling import calculate_frame_scores

base = [4, 5] * 9  # 9 complete open frames (score 9 each)

def test_gutter_game():
    assert calculate_frame_scores([0] * 20) == [0] * 10

def test_perfect_game():
    assert calculate_frame_scores(["X"] * 12) == [30] * 10


def test_10th_open_frame():
    assert calculate_frame_scores(base + [3, 5]) == [9]*9 + [8]

def test_10th_only_one_roll():
    assert calculate_frame_scores(base + [3]) == [9]*9 + [None]


# ════════════════════════════════════════════════════════════════
# VALID GAMES IN PROGRESS
# ════════════════════════════════════════════════════════════════

def test_empty_game():
    assert calculate_frame_scores([]) == []


@pytest.mark.parametrize("rolls, expected", [
    ([5],          [None]),         # first ball only, frame 1
    (["X"],        [None]),         # strike, both lookaheads missing
    ([5, "/"],     [None]),         # spare, lookahead missing
    (["X", 3],     [None, None]),   # strike has one lookahead; frame 2 is also partial
    (["X", "X"],   [None, None]),   # two strikes, frame 1 still unresolvable
])
def test_in_progress_frame_1(rolls, expected):
    assert calculate_frame_scores(rolls) == expected


@pytest.mark.parametrize("rolls, expected", [
    ([3, 4],                [7]),                       # frame 1 done, frame 2 not started
    ([3, 4, 5],             [7, None]),                 # frame 2: one ball thrown
    ([3, 4, 5, "/"],        [7, None]),                 # frame 2: spare, lookahead missing
    ([3, 4, 5, "/", 2],     [7, 12, None]),             # frame 2 resolved, frame 3 partial
    (["X", 3, 4],           [17, 7]),                   # frames 1 and 2 complete
    (["X", 3, 4, 5],        [17, 7, None]),             # frame 3 partial
    (["X", "X", 5],         [25, None, None]),          # frame 1 resolved, 2 and 3 not
    (["X", "X", "X"],       [30, None, None]),          # frame 1 resolved, 2 and 3 not
    (["X", "X", "X", 4],    [30, 24, None, None]),      # frames 1 and 2 resolved
    ([5, "/", "X"],         [20, None]),                # spare + strike lookahead
    ([5, "/", 3],           [13, None]),                # spare resolved, frame 2 partial
    ([5, "/", 3, 4],        [13, 7]),                   # frames 1 and 2 complete
])
def test_in_progress_various(rolls, expected):
    assert calculate_frame_scores(rolls) == expected


@pytest.mark.parametrize("rolls, expected", [
    (base + ["X"],      [9]*9 + [None]),    # 10th: strike, two bonus balls still needed
    (base + ["X", 5],   [9]*9 + [None]),    # 10th: strike + one bonus thrown
    (base + [5, "/"],   [9]*9 + [None]),    # 10th: spare, bonus ball not yet thrown
    (base + [3],        [9]*9 + [None]),    # 10th: only first ball thrown
])
def test_in_progress_10th_frame(rolls, expected):
    assert calculate_frame_scores(rolls) == expected


# ════════════════════════════════════════════════════════════════
# VALID COMPLETE GAMES
# ════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("rolls, expected", [
    ([1, 1] * 10,   [2] * 10),
    ([3, 3] * 10,   [6] * 10),
    ([4, 5] * 10,   [9] * 10),
])
def test_all_open_complete_games(rolls, expected):
    assert calculate_frame_scores(rolls) == expected


@pytest.mark.parametrize("rolls, expected", [
    ([5, "/"] * 10 + [5],   [15] * 10),     # all 5-spares
    ([9, "/"] * 10 + [9],   [19] * 10),     # all 9-spares
    ([4, "/"] * 10 + [4],   [14] * 10),     # all 4-spares
    ([8, "/"] * 10 + [8],   [18] * 10),     # all 8-spares
    ([0, "/"] * 10 + [0],   [10] * 10),     # all 0-spares (gutter + spare)
])
def test_all_strike_or_spare_complete_games(rolls, expected):
    assert calculate_frame_scores(rolls) == expected


@pytest.mark.parametrize("rolls, expected", [
    # one strike at frame 1, rest open 3+4
    (["X", 3, 4] + [3, 4] * 8,
     [17, 7, 7, 7, 7, 7, 7, 7, 7, 7]),

    # one spare at frame 1, rest open 3+4
    ([5, "/"] + [3, 4] * 9,
     [13, 7, 7, 7, 7, 7, 7, 7, 7, 7]),

    # three consecutive strikes then open
    (["X", "X", "X"] + [3, 4] * 7,
     [30, 23, 17, 7, 7, 7, 7, 7, 7, 7]),

    # nine strikes then open 10th frame
    (["X"] * 9 + [3, 4],
     [30, 30, 30, 30, 30, 30, 30, 23, 17, 7]),

    # spare then strike then open
    ([5, "/", "X"] + [3, 4] * 8,
     [20, 17, 7, 7, 7, 7, 7, 7, 7, 7]),

    # strike then spare then open
    (["X", 5, "/"] + [3, 4] * 8,
     [20, 13, 7, 7, 7, 7, 7, 7, 7, 7]),

    # 10th frame: three strikes (bonus two strikes)
    (base + ["X", "X", "X"],
     [9]*9 + [30]),

    # 10th frame: strike then open bonus balls
    (base + ["X", 5, 3],
     [9]*9 + [18]),

    # 10th frame: strike then spare bonus
    (base + ["X", 7, "/"],
     [9]*9 + [20]),

    # 10th frame: spare with bonus strike
    (base + [5, "/", "X"],
     [9]*9 + [20]),

    # 10th frame: spare with numeric bonus
    (base + [5, "/", 7],
     [9]*9 + [17]),

    # 10th frame: open (no bonus)
    (base + [3, 5],
     [9]*9 + [8]),

    # 10th frame: open all zeros
    (base + [0, 0],
     [9]*9 + [0]),
])
def test_mixed_complete_games(rolls, expected):
    assert calculate_frame_scores(rolls) == expected
