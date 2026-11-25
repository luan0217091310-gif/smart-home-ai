"""GĐ 4: chuỗi trạng thái té ngã với chuỗi điểm khớp giả (COCO-17)."""
import numpy as np

from services.worker_fall.logic import CONFIRMED, FallDetector, FallParams, torso_tilt_deg

H, X, FLOOR, FPS = 300.0, 400.0, 600.0, 15
WH = (800, 640)


def standing(top=FLOOR - H, x=X):
    k = np.zeros((17, 3), np.float32)
    k[:, 2] = 0.9
    k[:, 0] = x
    k[5, :2], k[6, :2] = (x - 30, top + 0.2 * H), (x + 30, top + 0.2 * H)
    k[11, :2], k[12, :2] = (x - 20, top + 0.5 * H), (x + 20, top + 0.5 * H)
    k[0, 1] = top + 0.05 * H
    return (x - 0.15 * H, top, x + 0.15 * H, top + H), k


def lying(x=X, jitter=0.0, rng=np.random.default_rng(1)):
    k = np.zeros((17, 3), np.float32)
    k[:, 2] = 0.9
    y = FLOOR - 0.15 * H
    k[:, 1] = y
    k[:, 0] = x
    k[5, 0], k[6, 0] = x - 0.3 * H, x - 0.3 * H
    k[11, 0], k[12, 0] = x, x
    k[0, 0] = x - 0.45 * H
    k[:, :2] += rng.normal(0, jitter, size=(17, 2)) if jitter else 0
    return (x - 0.5 * H, FLOOR - 0.3 * H, x + 0.5 * H, FLOOR), k


def interp(a, b, t):
    (ba, ka), (bb, kb) = a, b
    return tuple(np.add(np.multiply(ba, 1 - t), np.multiply(bb, t))), ka * (1 - t) + kb * t


def run(det, seq, t0=0.0):
    events, t = [], t0
    for bbox, k in seq:
        if det.update(1, t, bbox, k, WH) == CONFIRMED:
            events.append(t)
        t += 1 / FPS
    return events


def frames(state, seconds):
    return [state] * int(seconds * FPS)


def transition(a, b, seconds):
    n = max(1, int(seconds * FPS))
    return [interp(a, b, (i + 1) / n) for i in range(n)]


def make(zone=None):
    return FallDetector(FallParams(), zone)


def test_tilt():
    assert torso_tilt_deg(standing()[1], 0.5) < 10
    assert torso_tilt_deg(lying()[1], 0.5) > 80


def test_real_fall_confirmed_once():
    seq = frames(standing(), 1) + transition(standing(), lying(), 0.5) + frames(lying(), 6)
    ev = run(make(), seq)
    assert len(ev) == 1
    assert 1.5 + 3.9 <= ev[0] <= 1.5 + 4.5  # ~4 giây sau khi nằm yên


def test_slow_lie_down_no_alarm():
    seq = frames(standing(), 1) + transition(standing(), lying(), 4.0) + frames(lying(), 8)
    assert run(make(), seq) == []


def test_fall_then_get_up_quickly():
    seq = (frames(standing(), 1) + transition(standing(), lying(), 0.5) + frames(lying(), 1.5)
           + transition(lying(), standing(), 0.5) + frames(standing(), 5))
    assert run(make(), seq) == []


def test_fall_onto_sofa_is_safe():
    sofa = lambda x, y: "safe_rest"  # noqa: E731
    seq = frames(standing(), 1) + transition(standing(), lying(), 0.5) + frames(lying(), 6)
    assert run(make(sofa), seq) == []


def test_sitting_down_no_alarm():
    _, k = standing()
    sit_top = FLOOR - 0.7 * H
    sit = ((X - 0.2 * H, sit_top, X + 0.2 * H, FLOOR), standing(top=sit_top)[1])
    seq = frames(standing(), 1) + transition(standing(), sit, 0.5) + frames(sit, 6)
    assert run(make(), seq) == []


def test_moving_on_floor_delays_confirmation():
    moving = [lying(x=X + 50 * np.sin(i), jitter=0) for i in range(int(3 * FPS))]
    seq = frames(standing(), 1) + transition(standing(), lying(), 0.5) + moving + frames(lying(), 6)
    ev = run(make(), seq)
    assert len(ev) == 1 and ev[0] >= 1.5 + 3 + 3.9


def test_uses_real_timestamps_with_dropped_frames():
    """Bỏ sót khung (khoảng cách ts không đều) vẫn tính đúng vận tốc."""
    det, t = make(), 0.0
    for bbox, k in frames(standing(), 1):
        det.update(1, t, bbox, k, WH)
        t += 1 / FPS
    t += 0.4  # mất khung trong lúc ngã
    ev = []
    for bbox, k in frames(lying(), 6):
        if det.update(1, t, bbox, k, WH):
            ev.append(t)
        t += 1 / FPS
    assert len(ev) == 1


def test_occluded_person_behind_sofa_no_alarm():
    """Ca báo nhầm thật (quán cà phê 25/11): chỉ thấy đầu–vai sau lưng ghế. Hông lúc mất lúc thấy làm
    trung điểm vai–hông 'nhảy xuống', sau đó khung bao bè ngang và người ngồi yên. Không được báo."""
    top = FLOOR - H
    def frame(hips_visible, wide):
        _, k = standing(top=top)
        k[13:17, 2] = 0.1                                   # thân dưới bị che
        k[11:13, 2] = 0.9 if hips_visible else 0.1
        bbox = ((X - 0.35 * H, top, X + 0.35 * H, top + 0.35 * H) if wide
                else (X - 0.12 * H, top, X + 0.12 * H, top + 0.4 * H))
        return bbox, k
    seq = ([frame(False, False)] * int(2 * FPS) + [frame(True, False)] * 3
           + [frame(True, True)] * int(8 * FPS))
    assert run(make(), seq) == []
