import pytest
from bowling import calculate_frame_scores

base = [4, 5] * 9  # 9 complete open frames, each scoring 9


# ════════════════════════════════════════════════════════════════
# INVALID INPUTS
# ════════════════════════════════════════════════════════════════

def test_invalid_roll_value_int():
    with pytest.raises(ValueError):
        calculate_frame_scores([11])

def test_invalid_roll_value_negative():
    with pytest.raises(ValueError):
        calculate_frame_scores([-1])

def test_invalid_roll_value_str():
    with pytest.raises(ValueError):
        calculate_frame_scores(["Y"])

# ── Spare cannot open a regular frame ──────────────

@pytest.mark.parametrize("rolls", [
    ["/"],
    ["/", 5],
    [4, 3, "/"],            # spare opens frame 2 after open frame
    ["X", "/"],             # spare opens frame 2 after strike
    [5, "/", "/"],          # spare opens frame 2 after spare
    [4, 3, 4, 3, "/"],      # spare opens frame 3
    ["X", 3, 4, "/"],       # spare opens frame 3 (frame 1 was a strike)
    [4, 3] * 4 + ["/"],     # spare opens frame 5
])
def test_spare_opens_regular_frame(rolls):
    with pytest.raises(ValueError):
        calculate_frame_scores(rolls)


# ── Strike cannot be the second ball ───────────────

@pytest.mark.parametrize("rolls", [
    [5, "X"],
    [0, "X"],
    [9, "X"],
    [1, "X"],
    ["X", 5, "X"],          # frame 2: strike as second ball (after first-frame strike)
    [4, 3, 5, "X"],         # frame 2: strike as second ball (after open frame)
    [5, "/", 5, "X"],       # frame 2: strike as second ball (after spare)
])
def test_strike_as_second_ball_regular_frame(rolls):
    with pytest.raises(ValueError):
        calculate_frame_scores(rolls)


# ── Open frame total exceeds 10 pins ───────────────

@pytest.mark.parametrize("rolls", [
    [6, 5],
    [9, 2],
    [8, 3],
    [7, 4],
    [5, 6],
    ["X", 6, 5],            # frame 2 totals 11 (after strike)
    [4, "/", 6, 5],         # frame 2 totals 11 (after spare)
    [4, 3, 8, 3],           # frame 2 totals 11
    [4, 3] * 3 + [7, 4],    # frame 4 totals 11
])
def test_open_frame_exceeds_10_regular(rolls):
    with pytest.raises(ValueError):
        calculate_frame_scores(rolls)


# ── 10th frame: spare cannot open ───────────────────────────────

@pytest.mark.parametrize("rolls", [
    base + ["/"],
    base + ["/", 3],
    base + ["/", "X"],
])
def test_10th_spare_opens_frame(rolls):
    with pytest.raises(ValueError):
        calculate_frame_scores(rolls)


# ── 10th frame: strike as second ball without first-ball strike ──

@pytest.mark.parametrize("rolls", [
    base + [3, "X"],
    base + [0, "X"],
    base + [9, "X"],
    [5, "/"] * 9 + [5, "X"],    # spare-based game, invalid 10th
])
def test_10th_strike_as_second_ball(rolls):
    with pytest.raises(ValueError):
        calculate_frame_scores(rolls)


# ── 10th frame: spare notation invalid after first-ball strike ──

@pytest.mark.parametrize("rolls", [
    base + ["X", "/"],
    base + ["X", "/", 5],
    ["X"] * 9 + ["X", "/", 5],  # all-strikes game with invalid 10th
])
def test_10th_spare_after_first_ball_strike(rolls):
    with pytest.raises(ValueError):
        calculate_frame_scores(rolls)


# ── 10th frame: open frame total exceeds 10 ─────────────────────

@pytest.mark.parametrize("rolls", [
    base + [6, 5],
    base + [9, 8],
    base + [8, 5],
])
def test_10th_open_frame_exceeds_10(rolls):
    with pytest.raises(ValueError):
        calculate_frame_scores(rolls)


# ── 10th frame: bonus ball violations ───────────────────────────

@pytest.mark.parametrize("rolls", [
    base + ["X", "X", "/"],     # spare after two strikes (pins were reset; no shared rack)
    base + ["X", 7, "X"],       # strike on a partially depleted rack
    base + ["X", 0, "X"],       # strike after gutter ball (rack still shared, pins remain)
    base + ["X", "/"],          # spare after strike
    base + ["X", 6, 5],         # 6+5=11 exceeds remaining pins on shared rack
    base + [9, "X", 3],         # strike on second roll after no strike
    base + [5, "/", "/"],       # spare as bonus ball after spare (pins were reset)
])
def test_10th_frame_bonus_ball_invalid(rolls):
    with pytest.raises(ValueError):
        calculate_frame_scores(rolls)


# ── Too many rolls (game is complete, extra balls provided) ──────

@pytest.mark.parametrize("rolls", [
    [0] * 21,                       # extra ball after gutter game
    ["X"] * 13,                     # extra strike after perfect game
    [3, 4] * 10 + [1],              # extra ball after all-open game
    base + [3, 5, 7],               # extra ball after open 10th frame
    base + ["X", 5, 3, 1],          # extra ball after bonus 10th (strike)
    base + [5, "/", 3, 1],          # extra ball after bonus 10th (spare)
])
def test_too_many_rolls(rolls):
    with pytest.raises(ValueError):
        calculate_frame_scores(rolls)
