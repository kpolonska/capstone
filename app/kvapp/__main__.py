"""Entry point: `python3 -m kvapp` starts the role set in /etc/kv.env (ROLE=coordinator or shard)."""

import os
import sys

from . import coordinator, shard


def read_role():
    role = os.environ.get("ROLE")
    if role:
        return role
    try:
        with open("/etc/kv.env") as f:
            for line in f:
                if line.startswith("ROLE="):
                    return line.strip().split("=", 1)[1]
    except OSError:
        pass
    return ""


if __name__ == "__main__":
    role = read_role()
    if role == "coordinator":
        coordinator.serve()
    elif role == "shard":
        shard.serve()
    else:
        sys.exit(f"unknown or missing ROLE: {role!r}")
