#!/usr/bin/env python3
"""C12 maqayis isolation check.

Records a digest of tools/maqayis_ocr/ path/mtime state. Compare two
snapshots; if they differ, the tree is actively changing and the gate
should treat the run as environmentally contaminated.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MAQ = REPO / "tools" / "maqayis_ocr"


def snapshot() -> dict:
    if not MAQ.exists():
        return {"exists": False, "file_count": 0, "digest": "", "latest_mtime": 0.0}
    files = []
    total = 0
    latest_mtime = 0.0
    h = hashlib.sha256()
    for p in sorted(MAQ.rglob("*")):
        if p.is_file():
            try:
                st = p.stat()
            except OSError:
                continue
            rel = str(p.relative_to(MAQ))
            files.append({"path": rel, "size": st.st_size, "mtime": st.st_mtime})
            h.update(rel.encode())
            h.update(str(st.st_size).encode())
            h.update(str(int(st.st_mtime)).encode())
            total += 1
            latest_mtime = max(latest_mtime, st.st_mtime)
    return {
        "exists": True,
        "file_count": total,
        "digest": h.hexdigest(),
        "latest_mtime": latest_mtime,
    }


def main() -> int:
    action = sys.argv[1] if len(sys.argv) > 1 else "snapshot"
    if action == "snapshot":
        print(json.dumps(snapshot(), ensure_ascii=False, indent=2))
        return 0
    if action == "compare":
        if len(sys.argv) < 4:
            print("usage: c12_verify_maqayis_isolation.py compare <before.json> <after.json>",
                  file=sys.stderr)
            return 2
        before = json.loads(Path(sys.argv[2]).read_text())
        after = json.loads(Path(sys.argv[3]).read_text())
        same = (before.get("digest") == after.get("digest")
                and before.get("file_count") == after.get("file_count"))
        result = {
            "MAQAYIS_PRE_GATE_DIGEST": before.get("digest", ""),
            "MAQAYIS_POST_GATE_DIGEST": after.get("digest", ""),
            "MAQAYIS_CHANGED_DURING_GATE": not same,
            "ENVIRONMENT_STATUS": "QUIET" if same else "ENVIRONMENTALLY_CONTAMINATED",
            "file_count_before": before.get("file_count", 0),
            "file_count_after": after.get("file_count", 0),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if same else 6
    print(f"unknown action: {action}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
