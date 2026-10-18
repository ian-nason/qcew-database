# Required space preparation before another rebuild

The completed read-only audit peaked at 1,913,445,049 bytes under the 2 GiB isolated-repository cap. This checkout retains multiple audited candidates and extraction caches; another guarded build here may hit the cap.

Use a fresh isolated clone/worktree for a future pinned rebuild, with one ingestion worker and the same guard. Download or copy only the checksum-pinned inputs required for that build. Keep this release checkout and its evidence intact. If reuse is necessary, first inventory and hash individually named redundant source extractions or superseded local candidate databases, check ownership and retained originals, and record any removal; never blanket-delete release/evidence directories or touch FEC/shared checkouts. Do not raise the guard or assume ZIP size predicts peak disk/RAM.

This documents the final Claude review's operational note. The current artifact and completed validation are unaffected; no cleanup was performed by this freeze step.
