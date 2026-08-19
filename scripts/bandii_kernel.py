#!/usr/bin/env python3
"""Band II image kernel: factorial table, r(p), survive-test.

Column k survives prime p iff exists b in [0, p-k-1] with
    F[k+b] ≡ r(p)·F[k]·F[b]  (mod p)
which is C(k+b, k) ≡ r(p) (mod p). b is the fat-image j.

Do not build Pascal rows. Do not cache F across primes.
int64 only: s·F[b] < p² < 2^63.
"""

from __future__ import annotations

import math

import numpy as np

N = 10_803_704
K = 4_126_647
D = 6_677_057
N2 = 5_401_852
KMAX = 5_182_637
KMIN = K + 2  # 4126649
NCOLS = KMAX - KMIN + 1  # 1055989
LOG10_M = 3120255.2212

PRIMES = [
    5_401_853,
    5_401_861,
    5_401_867,
    5_401_897,
    5_401_901,
    5_401_951,
    5_401_969,
    5_401_973,
    5_401_993,
    5_401_999,
    5_402_003,
    5_402_011,
    5_402_021,
    5_402_051,
    5_402_057,
    5_402_063,
]
CAP = 14
P1 = PRIMES[0]
P2 = PRIMES[1]
R_P1 = 1_275_205

STRAGGLERS = {
    4_126_624: 273_671,
    4_126_638: 268_500,
    4_126_642: 2_006,
    4_126_643: 554_555,
}


def delta(p: int) -> int:
    return 2 * p - N


def fact_table(p: int) -> np.ndarray:
    """F[i] = i! mod p, i = 0..p-1. Python loop, ~0.3 s at p1."""
    F = np.empty(p, dtype=np.int64)
    F[0] = 1
    acc = 1
    for i in range(1, p):
        acc = acc * i % p
        F[i] = acc
    return F


def r_from_F(F: np.ndarray, p: int) -> int:
    n0 = N - p
    return (
        int(F[n0])
        * pow(int(F[K]), -1, p)
        * pow(int(F[n0 - K]), -1, p)
        % p
    )


def r_falling(p: int) -> int:
    n0 = N - p
    kk = n0 - K
    num = 1
    for i in range(kk):
        num = num * (n0 - i) % p
    den = 1
    for i in range(1, kk + 1):
        den = den * i % p
    return num * pow(den, -1, p) % p


def r_closed(p: int) -> int:
    """(-1)^K C(K+δ-1, δ-1) mod p, δ = 2p-N. Lower index is δ-1."""
    dlt = delta(p)
    n = K + dlt - 1
    kk = dlt - 1
    c = 1
    for i in range(kk):
        c = c * (n - i) % p
        c = c * pow(i + 1, -1, p) % p
    if K % 2:
        c = (-c) % p
    return c


def r_checked(F: np.ndarray, p: int, falling: bool = False) -> int:
    ra = r_from_F(F, p)
    rc = r_closed(p)
    if ra != rc:
        raise RuntimeError(f"r(p) table {ra} != closed {rc} at p={p}")
    if falling:
        rb = r_falling(p)
        if ra != rb:
            raise RuntimeError(f"r(p) table {ra} != falling {rb} at p={p}")
    return ra


def scan_ks(F: np.ndarray, p: int, r: int, ks) -> list[dict]:
    """Survivors in ks. Reduces the equality mask immediately."""
    out: list[dict] = []
    p64 = np.int64(p)
    rp = int(r)
    for k in ks:
        k = int(k)
        s = rp * int(F[k]) % p
        n = p - k
        left = F[k:p]
        right = (np.int64(s) * F[:n]) % p64
        eq = left == right
        hit = bool(eq.any())
        if hit:
            b = int(eq.argmax())
            g = n
            out.append({"k": k, "g": g, "g_even": g % 2 == 0, "b": b})
        del eq
    return out


def scan_columns(p: int, ks, r_expected: int | None = None) -> tuple[int, list[dict]]:
    """Build F, check r, scan. Returns (r, survivors). Worker entry."""
    F = fact_table(p)
    r = r_checked(F, p, falling=False)
    if r_expected is not None and r != r_expected:
        raise RuntimeError(f"r(p) {r} != expected {r_expected} at p={p}")
    return r, scan_ks(F, p, r, ks)


def r_two_digit(F: np.ndarray, p: int) -> int:
    """C(N,K) mod p via two-digit Lucas from the factorial table.

    Works for every p > k_max of Band I leftover and for p > N/2.
    C(α,β) C(n0,k0); α = N//p < p on the two-digit range.
    """
    a, b = N // p, K // p
    n0, k0 = N - a * p, K - b * p
    if not (0 <= b <= a and 0 <= k0 <= n0):
        return 0
    cab = int(F[a]) * pow(int(F[b]), -1, p) * pow(int(F[a - b]), -1, p) % p
    c0 = int(F[n0]) * pow(int(F[k0]), -1, p) * pow(int(F[n0 - k0]), -1, p) % p
    return cab * c0 % p


def scan_columns_general(p: int, ks) -> tuple[int, list[dict]]:
    """Like scan_columns, but r(p) is two-digit Lucas, not the α=1 closed form."""
    F = fact_table(p)
    r = r_two_digit(F, p)
    if r == 0:
        raise RuntimeError(f"live prime {p} has r=0 (Z / digit-0); do not scan")
    return r, scan_ks(F, p, r, ks)


def cumulative_g(k_end: int, kmin: int, p: int) -> int:
    if k_end < kmin:
        return 0
    m = k_end - kmin + 1
    return m * (2 * p - kmin - k_end) // 2


def equal_g_chunks(kmin: int, kmax: int, p: int, n_chunks: int) -> list[tuple[int, int]]:
    """Contiguous [lo, hi] with equal Σ(p-k). Covers kmin..kmax exactly."""
    total = cumulative_g(kmax, kmin, p)
    edges = [kmin]
    for i in range(1, n_chunks):
        target = total * i // n_chunks
        lo, hi = kmin, kmax
        while lo < hi:
            mid = (lo + hi) // 2
            if cumulative_g(mid, kmin, p) < target:
                lo = mid + 1
            else:
                hi = mid
        if lo <= edges[-1]:
            lo = edges[-1] + 1
        if lo > kmax - (n_chunks - i) + 1:
            lo = kmax - (n_chunks - i) + 1
        edges.append(lo)
    edges.append(kmax + 1)
    chunks = []
    for i in range(n_chunks):
        lo = edges[i]
        hi = edges[i + 1] - 1
        if hi < lo:
            raise RuntimeError(f"empty chunk {i}: {lo}>{hi}")
        chunks.append((lo, hi))
    if chunks[0][0] != kmin or chunks[-1][1] != kmax:
        raise RuntimeError("chunk coverage failed")
    for i in range(1, n_chunks):
        if chunks[i][0] != chunks[i - 1][1] + 1:
            raise RuntimeError("chunk gap")
    return chunks


def log10_central(k: int) -> float:
    return (math.lgamma(2 * k + 1) - 2 * math.lgamma(k + 1)) / math.log(10)
