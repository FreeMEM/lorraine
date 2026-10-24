#!/usr/bin/env python3
"""Lorraine test runner.

Compiles tests/test_*.dash with Dash ($DASH, default ~/Projects/FreeMEMLang/.worktrees/lorraine) for a 68020
with FPU and runs the ones with "# expect-out:" lines in FS-UAE (Dash's tools/emu_run.py), comparing what they
print, line by line. The programs (calc/calc.dash, write/write.dash) must compile too; they are not run.

    python3 tests/run.py               # all
    python3 tests/run.py zip           # only tests whose name contains "zip"
    python3 tests/run.py --no-emu      # compile only
    python3 tests/run.py --memcheck    # compile with ./dash --memcheck
    python3 tests/run.py -v            # show the output of failing tests in full

Lines a test can have:
    # expect-out: <line>        expected output, one per printed line, in order
    # memcheck                  always compiled with --memcheck (its summary line is in the expect-out)
    # autoclose: N              built in test mode: a MUI program ends by itself after N seconds
    # dash-flags: <flags>       extra ./dash options (e.g. --stack 65536)
    # cflags: <flags>           extra gcc options/objects (DASH_CFLAGS), paths relative to the repo
    # emu-config: key = value   extra FS-UAE option; tests with the same options share one boot
    # emu-needs: x.library      skip on the emulator when the system has no Libs/x.library;
                                muimaster.library: the system is $DASH_EMU_SYS_MUI (MUI 5)
    # screenshot: N file.png    save the front screen N seconds after boot to build/tests/file.png
                                (the test gets a boot of its own)

Environment: $DASH_KICKSTART (A1200 Kickstart 3.1; without it FS-UAE uses AROS and the results do not
count), $DASH_EMU_SYS (Workbench files) and $DASH_EMU_SYS_MUI (with MUI), as in Dash.
"""

import argparse
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DASH = Path(os.environ.get("DASH", Path.home() / "Projects" / "FreeMEMLang" / ".worktrees" / "lorraine"))
BUILD = ROOT / "build" / "tests"
EMU_BASE = "fpu = 68882\n"          # the tests are built with --fpu (68020 + 68881)
PROGRAMS = ["calc/calc.dash", "write/write.dash"]


def directives(src: Path, key: str):
    tag = f"# {key}:"
    return [l.split(tag, 1)[1].strip() for l in src.read_text().splitlines() if l.strip().startswith(tag)]


def compile_test(src: Path, memcheck: bool):
    exe = BUILD / src.stem
    cmd = [sys.executable, str(DASH / "dash"), "--fpu", str(src), "-o", str(exe)]
    if memcheck or any(l.strip() == "# memcheck" for l in src.read_text().splitlines()):
        cmd.append("--memcheck")
    for f in directives(src, "dash-flags"):
        cmd += shlex.split(f)
    # ./dash runs "python3 -m compiler.main" and writes build/ in the current directory:
    # the compiler comes from $DASH, build/ is ours (imports: relative to the test file)
    env = dict(os.environ, PYTHONPATH=str(DASH) + os.pathsep + os.environ.get("PYTHONPATH", ""))
    autoclose = directives(src, "autoclose")
    if autoclose:
        env["DASH_TEST_AUTOCLOSE"] = autoclose[0]
    extra = " ".join(directives(src, "cflags"))
    if extra:
        env["DASH_CFLAGS"] = (env.get("DASH_CFLAGS", "") + " " + extra).strip()
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, env=env)
    if r.returncode != 0 or not exe.exists():
        return None, (r.stdout + r.stderr).strip()
    return exe, None


def compare(got, expected, out, memcheck, verbose):
    """(ok, message) for one program's output"""
    leak = None
    if memcheck and not any(e.startswith("memcheck:") for e in expected):
        # --memcheck adds a summary line: nothing alive and no errors, or it fails
        summary = [g for g in got if g.startswith("memcheck:")]
        got = [g for g in got if not g.startswith("memcheck:")]
        # (a program that allocates nothing has no memory runtime and prints none)
        if summary and ("vivos 0 objetos y 0 strings" not in summary[-1] or "errores 0" not in summary[-1]):
            leak = summary[-1]
    if leak:
        return False, "memcheck: " + leak
    if out.timed_out:
        return False, "TIMEOUT\n" + "\n".join(got)
    if got == expected and out.rc == 0:
        return True, "ok (emulator)"
    diff = [f"  line {i + 1}: expected {e!r}, got {g!r}"
            for i, (e, g) in enumerate(zip(expected + [None] * len(got), got + [None] * len(expected)))
            if e != g and not (e is None and g is None)]
    return False, f"RC={out.rc}\n" + "\n".join(diff[:10]) + ("\n--- output:\n" + "\n".join(got) if verbose else "")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("filter", nargs="?")
    ap.add_argument("--no-emu", action="store_true")
    ap.add_argument("--memcheck", action="store_true")
    # (the tests with the same emulator config run in one session: it gets this plus 20 s per test)
    ap.add_argument("--timeout", type=float, default=600)
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    if not (DASH / "dash").exists():
        print(f"Dash not found in {DASH} (set $DASH; see docs/LORRAINE_LOOP.md, rule 3)", file=sys.stderr)
        return 2
    sys.path.insert(0, str(DASH / "tools"))
    from emu_run import run_programs

    tests = sorted((ROOT / "tests").glob("test_*.dash"))
    if args.filter:
        tests = [t for t in tests if args.filter in t.stem]
    programas = [] if args.filter else [ROOT / p for p in PROGRAMS if (ROOT / p).exists()]
    BUILD.mkdir(parents=True, exist_ok=True)

    results = {}          # name -> (ok, message)
    to_run = {}           # (emu config, system, screenshot) -> [(src, exe, expected)]
    t0 = time.time()
    for prog in programas:
        exe, err = compile_test(prog, args.memcheck)
        results[str(prog.relative_to(ROOT))] = (False, "compile failed:\n" + err) if err else (True, "compiled")
    for src in tests:
        exe, err = compile_test(src, args.memcheck)
        if err:
            results[src.stem] = (False, "compile failed:\n" + err)
            continue
        expected = directives(src, "expect-out")
        needs = directives(src, "emu-needs")
        system = os.environ.get("DASH_EMU_SYS_MUI" if "muimaster.library" in needs else "DASH_EMU_SYS", "")
        missing = [lib for lib in needs if not any((Path(system) / d / lib).exists() for d in ("Libs", "MUI/Libs"))]
        if not expected or args.no_emu:
            results[src.stem] = (True, "compiled")
        elif missing:
            results[src.stem] = (True, f"compiled (emulator skipped: no {', '.join(missing)})")
        else:
            cfg = EMU_BASE + "".join(c + "\n" for c in directives(src, "emu-config"))
            # a test with a screenshot boots alone (the screen is its window's)
            shot = src.stem if directives(src, "screenshot") else None
            to_run.setdefault((cfg, system, shot), []).append((src, exe, expected))

    if to_run and not os.environ.get("DASH_KICKSTART"):
        print("warning: $DASH_KICKSTART not set, FS-UAE uses AROS: results do not count", file=sys.stderr)
    for (cfg, system, shot_of), group in to_run.items():
        screenshot = None
        if shot_of:
            seconds, name = directives(group[0][0], "screenshot")[0].split()
            screenshot = (float(seconds), str(BUILD / name))
        try:
            outs = run_programs([exe for _, exe, _ in group], timeout=args.timeout + 20 * len(group),
                                kickstart=os.environ.get("DASH_KICKSTART"), extra_config=cfg,
                                system=system or None, screenshot=screenshot)
        except RuntimeError as e:
            for src, _, _ in group:
                results[src.stem] = (False, f"emulator: {e}")
            continue
        for (src, _, expected), out in zip(group, outs):
            got = (out.output or "").replace("\r", "").splitlines()
            results[src.stem] = compare(got, expected, out, args.memcheck, args.verbose)

    failed = 0
    names = [str(p.relative_to(ROOT)) for p in programas] + [t.stem for t in tests]
    for name in names:
        ok, msg = results[name]
        failed += not ok
        first, _, rest = msg.partition("\n")
        print(f"{'PASS' if ok else 'FAIL'}  {name}: {first}")
        if not ok and rest:
            print("\n".join("      " + l for l in rest.splitlines()))
    print(f"\n{len(names) - failed}/{len(names)} passed ({time.time() - t0:.0f} s)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
