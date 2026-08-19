#!/usr/bin/env python3
"""Replay Band II + Z-jump on a Fibonacci family member. No giant m.

Default i=7. Exact i=7 already scanned k<=200; this job does
k=201..k_max except {K, K+1}.

Not a next-prime sweep from k through (k, N/2]. Cap 14 Band II,
cap 12 Z-jump live primes. Refuse if results/i{i}_sweep.json exists.
"""

from __future__ import annotations

import json
import math
import multiprocessing as mp
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import gmpy2

from bandii_kernel import (  # noqa: E402
    Fam,
    equal_g_chunks,
    fact_table,
    kmax_of,
    make_fam,
    r_checked,
    r_closed,
    r_from_F,
    r_two_digit,
    scan_columns,
    scan_columns_general,
    scan_ks,
)

CAP_BII = 14
CAP_Z = 12
N_CHUNKS = 32
DEFAULT_WORKERS = 8
K_EXACT = {2: 200, 3: 200, 4: 200, 5: 200, 6: 200, 7: 200, 9: 80}
# i=2..7: exact k_extra=200 in fibonacci_i1-7.json
# i=9: modular k<=80 all impossible. i=1 is 3003 (N=8), skip.
# i=8 closed by the dedicated pipeline.


def cells(fam: Fam) -> list[dict]:
    out = []
    p2 = fam.p_two
    amax = fam.N // p2 + 1
    for a in range(2, amax + 1):
        for b in range(1, a):
            plo = max(fam.N // (a + 1) + 1, fam.K // (b + 1) + 1)
            phi = min(fam.N // a, fam.K // b)
            if plo > phi or phi < p2 or plo > fam.K:
                continue
            s = a - b
            zlo = fam.D // s + 1
            if zlo <= plo:
                kind = "FULL"
            elif zlo <= phi:
                kind = "PART"
            else:
                kind = "NONE"
            z_first = max(plo, zlo) if kind != "NONE" else None
            z_last = phi if kind != "NONE" and z_first is not None else None
            if kind != "NONE" and z_first is not None and z_first > phi:
                kind = "NONE"
                z_first = z_last = None
            out.append(
                {
                    "a": a,
                    "b": b,
                    "plo": plo,
                    "phi": phi,
                    "kind": kind,
                    "zlo": zlo,
                    "z_first": z_first,
                    "z_last": z_last,
                }
            )
    out.sort(key=lambda w: w["plo"])
    return out


def live_intervals(fam: Fam, windows: list[dict]) -> list[tuple[int, int]]:
    ivs = []
    for w in windows:
        if w["kind"] == "NONE":
            ivs.append((w["plo"], w["phi"]))
        elif w["kind"] == "PART" and w["plo"] <= w["zlo"] - 1:
            ivs.append((w["plo"], w["zlo"] - 1))
    ivs.append((fam.N2 + 1, fam.D))
    ivs.sort()
    return ivs


def first_live_after(x: int, ivs: list[tuple[int, int]], d: int) -> int | None:
    p = int(gmpy2.next_prime(x))
    i = 0
    n = len(ivs)
    while p <= d and i < n:
        lo, hi = ivs[i]
        if p > hi:
            i += 1
            continue
        if p < lo:
            p = int(gmpy2.next_prime(lo - 1))
            continue
        return int(p)
    return None


def first_primes_above(n2: int, d: int, kmax: int, n: int = 16) -> list[int]:
    out = []
    p = int(gmpy2.next_prime(n2))
    while len(out) < n and p <= d:
        if p > kmax:
            out.append(int(p))
        p = int(gmpy2.next_prime(p))
    return out


def chunk_ks(ks: list[int], p: int, n_chunks: int) -> list[list[int]]:
    ks = sorted(ks)
    if not ks:
        return []
    if len(ks) < 2000 or n_chunks <= 1:
        return [ks]
    weights = [p - k for k in ks]
    total = sum(weights)
    if total <= 0:
        return [ks]
    chunks, acc, start, t = [], 0, 0, 1
    for i, w in enumerate(weights):
        acc += w
        if t < n_chunks and acc >= total * t / n_chunks:
            chunks.append(ks[start : i + 1])
            start = i + 1
            t += 1
    if start < len(ks):
        chunks.append(ks[start:])
    return [c for c in chunks if c]


def _job(payload: tuple) -> dict:
    kind, p, ks, N, K, r_expected = payload
    t0 = time.time()
    if kind == "bii":
        r, rows = scan_columns(p, ks, r_expected=r_expected, N=N, K=K)
    else:
        r, rows = scan_columns_general(p, ks, N=N, K=K)
    return {
        "p": p,
        "r": r,
        "k_lo": int(ks[0]),
        "k_hi": int(ks[-1]),
        "n_cols": len(ks),
        "n_survivors": len(rows),
        "survivors": rows,
        "seconds": round(time.time() - t0, 3),
    }


def paths(i: int) -> tuple[Path, Path]:
    return ROOT / "results" / f"i{i}_sweep.json", ROOT / "results" / f"i{i}_sweep.jsonl"


def load_done(chk: Path) -> list[dict]:
    if not chk.exists():
        return []
    out = []
    with chk.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def write_jsonl(chk: Path, rec: dict) -> None:
    with chk.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
        fh.flush()


def summarize(rows: list[dict]) -> dict:
    n = len(rows)
    if not n:
        return {"n": 0, "even": None, "mean_k": None}
    even = sum(1 for s in rows if s.get("g_even")) / n
    return {"n": n, "even": round(even, 4), "mean_k": round(sum(s["k"] for s in rows) / n)}


def run_jobs(jobs: list[tuple], workers: int, chk: Path, tag: str, done_keys: set) -> list[dict]:
    pending = []
    for job in jobs:
        _kind, p, ks, _N, _K, _r = job
        key = (tag, p, int(ks[0]), int(ks[-1]))
        if key not in done_keys:
            pending.append(job)
    surv = []
    for rec in load_done(chk):
        if rec.get("tag") == tag:
            surv.extend(rec.get("survivors") or [])
    if not pending:
        print(f"  {tag} all chunks done  alive={len(surv)}", flush=True)
        return surv
    print(f"  {tag} jobs={len(pending)} workers={workers}", flush=True)
    nprint = 0
    ctx = mp.get_context("spawn")
    with ctx.Pool(workers) as pool:
        for rec in pool.imap_unordered(_job, pending):
            rec["tag"] = tag
            write_jsonl(chk, rec)
            surv.extend(rec["survivors"])
            nprint += 1
            fat = rec["n_cols"] >= 500 or rec["seconds"] >= 1.0
            if fat or nprint % 50 == 0:
                print(
                    f"    p={rec['p']} cols={rec['n_cols']} surv={rec['n_survivors']} "
                    f"{rec['seconds']}s  alive={len(surv)}",
                    flush=True,
                )
    return surv


def preflight(fam: Fam, kmax: int, primes: list[int]) -> list[tuple[int, int]]:
    print(f"=== i={fam.i} pre-flight ===", flush=True)
    t0 = time.time()
    assert fam.K != int(gmpy2.fib(2 * fam.i + 2) * gmpy2.fib(2 * fam.i + 1)), "K is F_{2i} F_{2i+3}"
    assert fam.N == int(gmpy2.fib(2 * fam.i + 2) * gmpy2.fib(2 * fam.i + 3))
    assert fam.K == int(gmpy2.fib(2 * fam.i) * gmpy2.fib(2 * fam.i + 3))
    assert fam.K1 == fam.K + 1
    for p in primes:
        assert bool(gmpy2.is_prime(p))
        assert 2 * p > fam.N and p <= fam.D and p > kmax
    print(
        f"  N={fam.N} K={fam.K} d={fam.D} N/2={fam.N2} kmax={kmax} "
        f"p1={primes[0]} dlt={2*primes[0]-fam.N}",
        flush=True,
    )

    F = fact_table(primes[0])
    ra = r_from_F(F, primes[0], N=fam.N, K=fam.K)
    rc = r_closed(primes[0], N=fam.N, K=fam.K)
    rt = r_two_digit(F, primes[0], N=fam.N, K=fam.K)
    if not (ra == rc == rt):
        raise RuntimeError(f"r(p1) {ra} {rc} {rt}")
    if int(F[-1]) != primes[0] - 1:
        raise RuntimeError("Wilson")
    print(f"  r(p1)={ra} table=closed=two-digit  Wilson ok", flush=True)

    from singmaster_intersect import binom_mod_lucas

    if int(binom_mod_lucas(fam.N, fam.K, primes[0])) != ra:
        raise RuntimeError("lucas(p1) mismatch")

    import numpy as np

    rng = np.random.default_rng(1)
    bad = 0
    for p in (11, 29, 101, 211, 1009):
        Fp = fact_table(p)
        assert int(Fp[p - 1]) == p - 1
        for _ in range(100):
            k = int(rng.integers(1, p))
            rr = int(rng.integers(0, p))
            s = rr * int(Fp[k]) % p
            ker = bool(np.any(Fp[k:p] == (np.int64(s) * Fp[: p - k]) % np.int64(p)))
            brute = any(math.comb(n0, k) % p == rr for n0 in range(k, p))
            if ker != brute:
                bad += 1
    if bad:
        raise RuntimeError(f"kernel mismatches {bad}")
    print(f"  kernel 500 cases, 0 mismatches  {time.time()-t0:.1f}s", flush=True)

    windows = cells(fam)
    ivs = live_intervals(fam, windows)
    k0 = K_EXACT.get(fam.i, 2) + 1
    if k0 < fam.K:
        p0 = first_live_after(k0, ivs, fam.D)
        if p0 is None or p0 <= k0:
            raise RuntimeError(f"no live prime after {k0}")
        print(f"  live after k={k0}: {p0}  intervals={len(ivs)}", flush=True)
    else:
        print(f"  Band I extra already in exact k<= {k0-1}; Z-jump empty", flush=True)
    print("=== pre-flight passed ===", flush=True)
    return ivs


def main() -> int:
    i = 7
    if "--i" in sys.argv:
        i = int(sys.argv[sys.argv.index("--i") + 1])
    if i == 8:
        print("i=8 is already closed. Use the i=8 bats. Not rerunning.", flush=True)
        return 2

    out, chk = paths(i)
    if "--preflight" in sys.argv:
        fam = make_fam(i)
        kmax, _ = kmax_of(fam)
        primes = first_primes_above(fam.N2, fam.D, kmax)
        preflight(fam, kmax, primes)
        return 0

    if out.exists():
        print(f"{out} already exists. Not rerunning.", flush=True)
        return 2
    try:
        import numpy as np  # noqa: F401
    except ImportError:
        print("numpy is required.", flush=True)
        return 1

    workers = int(os.environ.get("I7_WORKERS", os.environ.get("FAMILY_WORKERS", DEFAULT_WORKERS)))
    workers = max(1, min(workers, 16))
    out.parent.mkdir(exist_ok=True)

    t0 = time.time()
    fam = make_fam(i)
    kmax, logm = kmax_of(fam)
    primes = first_primes_above(fam.N2, fam.D, kmax, n=max(CAP_BII, 16))
    if not primes:
        raise RuntimeError("no live Band II primes in (N/2, d]")
    ivs = preflight(fam, kmax, primes)
    k_lo_z = K_EXACT.get(i, 2) + 1
    n_z = max(0, fam.K - k_lo_z)  # k_lo_z .. K-1, or 0 if exact already covers
    n_bii = kmax - (fam.K + 2) + 1
    print(
        f"=== i={i} sweep  Z {k_lo_z}..{fam.K-1} ({n_z})  "
        f"BII {fam.K+2}..{kmax} ({n_bii})  workers={workers} ===",
        flush=True,
    )
    print(f"    log10 m={logm:.4f}  p1={primes[0]}", flush=True)

    done = load_done(chk)
    done_keys = {
        (r["tag"], r["p"], r["k_lo"], r["k_hi"])
        for r in done
        if "tag" in r and "p" in r and "k_lo" in r
    }
    complete = {r["phase"] for r in done if r.get("event") == "phase_complete"}

    phases = {}

    # --- Band II ---
    if "bandii" not in complete:
        alive = None
        for pi, p in enumerate(primes[:CAP_BII], start=1):
            tag = f"bii{pi}"
            if alive is None:
                if n_bii < 2000:
                    jobs = [
                        (
                            "bii",
                            p,
                            list(range(fam.K + 2, kmax + 1)),
                            fam.N,
                            fam.K,
                            r_closed(p, N=fam.N, K=fam.K),
                        )
                    ]
                else:
                    chunks = equal_g_chunks(fam.K + 2, kmax, p, N_CHUNKS)
                    jobs = [
                        ("bii", p, list(range(lo, hi + 1)), fam.N, fam.K, r_closed(p, N=fam.N, K=fam.K))
                        for lo, hi in chunks
                    ]
            else:
                if not alive:
                    break
                buckets: dict[int, list[int]] = defaultdict(list)
                for s in alive:
                    buckets[p].append(s["k"])
                jobs = []
                for pp, ks in buckets.items():
                    for ch in chunk_ks(ks, pp, N_CHUNKS if len(ks) >= 2000 else 1):
                        jobs.append(("bii", pp, ch, fam.N, fam.K, r_closed(pp, N=fam.N, K=fam.K)))
            surv = run_jobs(jobs, workers, chk, tag, done_keys)
            sm = summarize(surv)
            phases.setdefault("bandii", []).append({"prime_index": pi, "p": p, **sm})
            print(f"  BII pass {pi} p={p} alive={sm['n']} even={sm['even']} mean_k={sm['mean_k']}", flush=True)
            alive = surv
            write_jsonl(chk, {"event": "round_complete", "phase": "bandii", "pass": pi, "n_alive": sm["n"]})
            done_keys = {
                (r["tag"], r["p"], r["k_lo"], r["k_hi"])
                for r in load_done(chk)
                if "tag" in r and "p" in r and "k_lo" in r
            }
            if not alive:
                break
        write_jsonl(chk, {"event": "phase_complete", "phase": "bandii", "n_alive": 0 if not alive else len(alive)})
        bii_left = [] if not alive else alive
    else:
        print("  bandii phase already complete", flush=True)
        bii_left = []

    # --- Z-jump Band I remnant ---
    if "zjump" not in complete and n_z > 0:
        current: list = [{"k": k} for k in range(k_lo_z, fam.K)]
        zrounds = []
        for rnd in range(1, CAP_Z + 1):
            if not current:
                break
            buckets = defaultdict(list)
            none = []
            for it in current:
                if isinstance(it, dict) and "g" in it:
                    k, x = int(it["k"]), int(it["k"] + it["g"])
                else:
                    k = int(it["k"] if isinstance(it, dict) else it)
                    x = k
                p = first_live_after(x, ivs, fam.D)
                if p is None:
                    none.append(k)
                else:
                    buckets[p].append(k)
            if none:
                print(f"  Z round {rnd} no live prime: {len(none)} (anomaly)", flush=True)
            jobs = []
            for p, ks in sorted(buckets.items()):
                for ch in chunk_ks(ks, p, N_CHUNKS if len(ks) >= 2000 else 1):
                    jobs.append(("z", p, ch, fam.N, fam.K, None))
            surv = run_jobs(jobs, workers, chk, f"z{rnd}", done_keys)
            sm = summarize(surv)
            zrounds.append({"round": rnd, "n_primes": len(buckets), **sm, "n_nolive": len(none)})
            print(
                f"  Z round {rnd} alive={sm['n']} even={sm['even']} mean_k={sm['mean_k']}",
                flush=True,
            )
            current = surv
            write_jsonl(chk, {"event": "round_complete", "phase": "zjump", "round": rnd, "n_alive": sm["n"]})
            done_keys = {
                (r["tag"], r["p"], r["k_lo"], r["k_hi"])
                for r in load_done(chk)
                if "tag" in r and "p" in r and "k_lo" in r
            }
        write_jsonl(chk, {"event": "phase_complete", "phase": "zjump"})
        phases["zjump"] = zrounds
        z_left = current
        z_none = []
    elif "zjump" in complete:
        print("  zjump phase already complete", flush=True)
        z_left = []
    else:
        print("  zjump skipped (exact already covers Band I extra)", flush=True)
        z_left = []
        write_jsonl(chk, {"event": "phase_complete", "phase": "zjump", "skipped": True})

    n_bii_left = len(bii_left) if isinstance(bii_left, list) else 0
    n_z_left = len(z_left) if isinstance(z_left, list) else 0
    clean = n_bii_left == 0 and n_z_left == 0
    payload = {
        "search": f"i{i}_sweep",
        "i": i,
        "N": fam.N,
        "K": fam.K,
        "d": fam.D,
        "k_max": kmax,
        "log10_m": round(logm, 6),
        "k_z": [k_lo_z, fam.K - 1],
        "k_bii": [fam.K + 2, kmax],
        "n_z": n_z,
        "n_bii": n_bii,
        "primes_bii": primes[:CAP_BII],
        "workers": workers,
        "phases": phases,
        "n_bii_alive": n_bii_left,
        "n_z_alive": n_z_left,
        "bii_survivors": bii_left if n_bii_left and n_bii_left <= 100 else [],
        "z_survivors": z_left if n_z_left and n_z_left <= 100 else [],
        "clean": clean,
        "certificate": (
            f"Every extra k in [2, k_max] except {{K, K+1}} for i={i} "
            f"has r(p) notin I_{{p,k}}. Together with exact k<=200 and "
            f"two family columns, N(C(N,K))=6. Not Singmaster."
        )
        if clean
        else None,
        "seconds": round(time.time() - t0, 3),
    }
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(flush=True)
    print(
        f"wrote {out}  clean={clean}  bii_left={n_bii_left}  "
        f"z_left={n_z_left}  {payload['seconds']}s",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    mp.freeze_support()
    raise SystemExit(main())
