#!/usr/bin/env python3
"""Local tests for news-image-20261124-v4 main.py (stdlib only)."""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import main as M  # noqa: E402


def test_atlas():
    a = M.load_atlas()
    assert len(a.glyphs) > 1500, len(a.glyphs)
    for fid, size in [(1, 66), (1, 22), (0, 13), (4, 11), (3, 10)]:
        w = a.text_width(fid, size, "Tuesday 24 November 2026")
        assert w > 100, (fid, size, w)
    # every char used in the copy must have a glyph in every used face
    faces = [(0, 12), (0, 13), (0, 15), (1, 14), (1, 18), (1, 22),
             (1, 28), (1, 30), (1, 66), (2, 15), (3, 10), (3, 12),
             (4, 9), (4, 10), (4, 11), (4, 12), (4, 13), (4, 16)]
    texts = ["Tuesday 24 November 2026"]
    for _n, _r, _p, h, b, _s, _t in M.HEROES + M.MEDIUM:
        texts.append(h)
        texts.append(b)
    for _n, _r, h, _s in M.ALSO:
        texts.append(h)
    for fid, size in faces:
        for t in texts:
            for ch in t:
                assert (fid, size, ord(ch)) in a.glyphs, (fid, size, ch)
    print("atlas ok:", len(a.glyphs), "glyphs")


def test_wrap_fit():
    lines = M.wrap_text("Russian drone enters Polish airspace",
                        M.SERIFB, 18, 196)
    assert len(lines) == 2, lines
    assert M.text_width(M.SERIFB, 14, "x" * 200) > 300
    short = M.fit_text("A very long headline that must be cut", M.SERIFB, 14,
                       120)
    assert short.endswith("..."), short
    assert M.text_width(M.SERIFB, 14, short) <= 120
    print("wrap/fit ok")


def test_build():
    png = M.build()
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert len(png) < 1048576, len(png)
    import struct
    w, h = struct.unpack_from(">II", png, 16)
    assert (w, h) == (1024, 1024), (w, h)
    print("build ok: %d bytes, %dx%d" % (len(png), w, h))
    return png


def test_determinism(png):
    png2 = M.build()
    assert png == png2, "non-deterministic output"
    print("determinism ok: sha256",
          hashlib.sha256(png).hexdigest()[:16])


def test_clean_dir(png):
    """Run main.py from a fresh dir, another CWD, MAKEFUN_OUTPUT_DIR set."""
    tmp = tempfile.mkdtemp(prefix="v4-clean-")
    try:
        for name in ("main.py", "atlas.bin"):
            shutil.copy(os.path.join(HERE, name), os.path.join(tmp, name))
        out = os.path.join(tmp, "out")
        env = dict(os.environ, MAKEFUN_OUTPUT_DIR=out)
        r = subprocess.run([sys.executable, os.path.join(tmp, "main.py")],
                           cwd="/", env=env, capture_output=True, text=True,
                           timeout=120)
        assert r.returncode == 0, r.stderr[-2000:]
        got = os.path.join(out, "entry.png")
        assert os.path.exists(got), "no entry.png in MAKEFUN_OUTPUT_DIR"
        with open(got, "rb") as f:
            data = f.read()
        assert data == png, "clean-dir bytes differ from local render"
        print("clean-dir ok: exit 0, entry.png %d bytes, identical" %
              len(data))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_no_output_dir_env():
    """Without MAKEFUN_OUTPUT_DIR, /output may not exist: must not crash."""
    tmp = tempfile.mkdtemp(prefix="v4-noenv-")
    try:
        for name in ("main.py", "atlas.bin"):
            shutil.copy(os.path.join(HERE, name), os.path.join(tmp, name))
        env = dict(os.environ)
        env.pop("MAKEFUN_OUTPUT_DIR", None)
        r = subprocess.run([sys.executable, os.path.join(tmp, "main.py")],
                           cwd=tmp, env=env, capture_output=True, text=True,
                           timeout=120)
        assert r.returncode == 0, r.stderr[-2000:]
        assert os.path.exists(os.path.join(tmp, "entry-v4.png"))
        print("no-env ok: exit 0, local copy written")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    test_atlas()
    test_wrap_fit()
    png = test_build()
    test_determinism(png)
    test_clean_dir(png)
    test_no_output_dir_env()
    print("ALL TESTS PASSED")
