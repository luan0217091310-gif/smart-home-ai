"""Dọn dữ liệu và sao lưu.

- Mỗi đêm (02:00): xóa ảnh trong data/snapshots cũ hơn 30 ngày, access_logs cũ hơn 90 ngày.
- Chủ nhật: sao lưu smarthome.db, zones.json, faces/ vào BACKUP_DIR (mặc định data/../backups).

  python scripts/maintenance.py --once     # chạy ngay một lần
  python scripts/maintenance.py            # chạy nền, tự lên lịch (dùng trong Docker)
"""
import _bootstrap  # noqa: F401
import argparse
import shutil
import sqlite3
import time
from datetime import timedelta
from pathlib import Path

from shared.config import ROOT, data_dir, env, now, settings, setup_logging
from shared.database import DB

log = setup_logging("maintenance")


def cleanup(cfg: dict) -> tuple[int, int]:
    cutoff = time.time() - cfg.get("snapshots_days", 30) * 86400
    n_files = 0
    snap = data_dir() / "snapshots"
    if snap.exists():
        for p in snap.rglob("*.jpg"):
            if p.stat().st_mtime < cutoff and not p.name.startswith("object_"):
                p.unlink(missing_ok=True)
                n_files += 1
    n_logs = DB().purge_access_logs(cfg.get("access_logs_days", 90))
    log.info("Đã xóa %d ảnh cũ, %d dòng access_logs cũ", n_files, n_logs)
    return n_files, n_logs


def backup(cfg: dict) -> Path:
    base = Path(env("BACKUP_DIR", str(ROOT / cfg.get("backup_dir", "backups"))))
    dest = base / f"{now():%Y%m%d_%H%M}"
    dest.mkdir(parents=True, exist_ok=True)
    db_path = data_dir() / "smarthome.db"
    if db_path.exists():  # sao lưu an toàn khi đang ghi (WAL)
        src, dst = sqlite3.connect(db_path), sqlite3.connect(dest / "smarthome.db")
        with dst:
            src.backup(dst)
        src.close(), dst.close()
    if (z := data_dir() / "zones.json").exists():
        shutil.copy2(z, dest / "zones.json")
    if (f := data_dir() / "faces").exists():
        shutil.copytree(f, dest / "faces", dirs_exist_ok=True)
    log.info("Đã sao lưu vào %s", dest)
    return dest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    args = ap.parse_args()
    cfg = settings().get("retention", {})
    if args.once:
        cleanup(cfg)
        backup(cfg)
        return
    done_clean, done_backup = None, None
    while True:
        n = now()
        if n.hour == 2 and done_clean != n.date():
            cleanup(cfg)
            done_clean = n.date()
            if n.weekday() == 6 and done_backup != n.date():
                backup(cfg)
                done_backup = n.date()
        time.sleep(300)


if __name__ == "__main__":
    main()
