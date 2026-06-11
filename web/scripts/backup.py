#!/usr/bin/env python3
"""
BlueHarbor Backup Utility  v1.2.0
Maintainer : dev-team@bharbor.dl
Last update : 2024-01-10

Changelog:
  v1.2.0 - Added blueharbor_utils notifications
  v1.1.0 - Switched from rsync to shutil for portability
  v1.0.0 - Initial release

TODO (sprint #14):
  - Replace blueharbor_utils with stdlib logging
  - Add checksum verification after copy
  - Unit tests
"""

import os
import shutil
import datetime
import sys
import blueharbor_utils

BACKUP_SRC = "/var/www/html"
BACKUP_DST = "/tmp/blueharbor_backup_{}".format(
    datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
)

EXCLUDE_PATTERNS = ("*.pyc", "__pycache__", "*.log", ".git")

def run_backup() -> None:
    blueharbor_utils.log("Starting backup process...")
    blueharbor_utils.log(f"  Source : {BACKUP_SRC}")
    blueharbor_utils.log(f"  Dest   : {BACKUP_DST}")

    if not os.path.isdir(BACKUP_SRC):
        blueharbor_utils.log(f"Source directory not found: {BACKUP_SRC}", level="ERROR")
        sys.exit(1)

    if os.path.exists(BACKUP_DST):
        shutil.rmtree(BACKUP_DST)

    shutil.copytree(
        BACKUP_SRC,
        BACKUP_DST,
        ignore=shutil.ignore_patterns(*EXCLUDE_PATTERNS),
    )

    size_mb = _get_dir_size(BACKUP_DST) / (1024 * 1024)
    blueharbor_utils.log(f"Backup complete. Size: {size_mb:.2f} MB")
    blueharbor_utils.notify(
        recipient="admin@bharbor.dl",
        subject="Backup OK",
        body=f"Backup created at {BACKUP_DST} ({size_mb:.2f} MB)",
    )

def _get_dir_size(path: str) -> int:
    total = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total += os.path.getsize(fp)
    return total

if __name__ == "__main__":
    run_backup()
