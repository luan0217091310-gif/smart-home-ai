"""GĐ 2: logic quyết định mặt bằng vector giả."""
import numpy as np

from services.worker_face.logic import FaceDecider, best_match, face_big_enough, iou, l2_normalize, mean_embedding

rng = np.random.default_rng(0)


def _vec():
    return l2_normalize(rng.normal(size=512))


def test_mean_embedding_normalized():
    m = mean_embedding([_vec(), _vec(), _vec()])
    assert abs(np.linalg.norm(m) - 1) < 1e-5


def test_best_match():
    a, b = _vec(), _vec()
    gallery = np.stack([a, b])
    noisy = l2_normalize(b + 0.1 * rng.normal(size=512) / np.sqrt(512))
    idx, score = best_match(noisy, gallery, ["a", "b"])
    assert idx == 1 and score > 0.9
    assert best_match(a, np.zeros((0, 512)), []) == (-1, 0.0)


def test_iou():
    assert iou((0, 0, 10, 10), (0, 0, 10, 10)) == 1
    assert iou((0, 0, 10, 10), (20, 20, 30, 30)) == 0
    assert abs(iou((0, 0, 10, 10), (5, 0, 15, 10)) - 1 / 3) < 1e-6


def test_member_recognized_immediately():
    d = FaceDecider(threshold=0.55)
    out = d.update([((0, 0, 100, 100), 0, 0.7)])
    assert out[0].kind == "member"


def test_stranger_after_3_consecutive_frames_once():
    d = FaceDecider(threshold=0.55, stranger_frames=3)
    box = (0, 0, 100, 100)
    kinds = [d.update([(box, 0, 0.2)])[0].kind for _ in range(6)]
    assert kinds == ["undecided", "undecided", "stranger", "undecided", "undecided", "undecided"]


def test_single_high_frame_resets_stranger_count():
    d = FaceDecider(threshold=0.55, stranger_frames=3)
    box = (0, 0, 100, 100)
    seq = [0.2, 0.2, 0.8, 0.2, 0.2]
    kinds = [d.update([(box, 0, s)])[0].kind for s in seq]
    assert "stranger" not in kinds


def test_two_people_tracked_separately():
    d = FaceDecider(threshold=0.55, stranger_frames=3)
    member_box, stranger_box = (0, 0, 100, 100), (300, 0, 400, 100)
    for i in range(3):
        out = d.update([(member_box, 0, 0.8), (stranger_box, 0, 0.1)])
    assert out[0].kind == "member" and out[1].kind == "stranger"
    assert out[0].track_id != out[1].track_id


def test_track_expires_after_missed_frames():
    d = FaceDecider(max_missed=2)
    d.update([((0, 0, 100, 100), 0, 0.1)])
    for _ in range(3):
        d.update([])
    assert d.tracks == {}


def test_face_size():
    assert face_big_enough((0, 0, 60, 80), 60) and not face_big_enough((0, 0, 59, 80), 60)


def test_middle_band_is_undecided_not_stranger():
    """Chủ nhà quay đầu: điểm 0,26–0,38 nhiều khung liền → không được báo người lạ."""
    d = FaceDecider(threshold=0.45, stranger_threshold=0.25, stranger_frames=3)
    kinds = [d.update([((0, 0, 100, 100), 0, s)])[0].kind for s in [0.33, 0.30, 0.28, 0.26, 0.35, 0.38]]
    assert "stranger" not in kinds
    kinds = [d.update([((0, 0, 100, 100), 0, s)])[0].kind for s in [0.1, 0.12, 0.08]]
    assert kinds[-1] == "stranger"
