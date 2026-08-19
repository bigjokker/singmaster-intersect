# Band I next-prime (i=8)

This is a census plus a few lemmas. It does **not** prove Singmaster’s conjecture
and it does **not** prove that every Band I column dies.

Fixed objects (do not use \(K=F_{18}F_{17}\); that is \(K+1\)):

\[
N=F_{18}F_{19}=10803704,\quad
K=F_{16}F_{19}=4126647,\quad
d=N-K=6677057,\quad
N/2=5401852.
\]

Band I is \(2\le k<K\). Two-digit primes: \(3287\le p\le K\).
Write \(\alpha=\lfloor N/p\rfloor\), \(\beta=\lfloor K/p\rfloor\),
\(n_0=N-\alpha p\), \(k_0=K-\beta p\), \(g=p-k\).

## Theorems

**Digit-0.** For two-digit \(p\), \(C(N,K)\equiv 0\pmod p\) iff \(p(\alpha-\beta)>d\).

**NONE nonvanishing.** If \(p(\alpha-\beta)\le d\) then
\(C(N,K)\equiv C(\alpha,\beta)C(n_0,k_0)\not\equiv 0\pmod p\).
Every NONE survivor is an image match, never a zero.

**Kill test (no giant \(m\)).** With
\(I_g=\{(-1)^j\binom{g-1}{j}\bmod p:0\le j<g\}\)
(equivalently \(\binom{k+j}{j}\), **not** \(\binom{k}{j}\)),
a NONE prime kills iff \(r(p)\notin I_g\).

**Z-slab.** If no prime lies in \((k,t]\) for threshold \(t=d/(\alpha-\beta)\),
then \(q(k)\) is at least the first prime after the slab top \(u\).

**Z-width (closed).** Cell
\(P_\mathrm{lo}=\max(\lfloor N/(\alpha+1)\rfloor+1,\lfloor K/(\beta+1)\rfloor+1)\),
\(P_\mathrm{hi}=\min(\lfloor N/\alpha\rfloor,\lfloor K/\beta\rfloor)\),
\(z_\mathrm{lo}=\lfloor d/(\alpha-\beta)\rfloor+1\),
\(\mathrm{Zw}=P_\mathrm{hi}-\max(P_\mathrm{lo},z_\mathrm{lo})\) (or 0).
FULL / PART / NONE from where \(z_\mathrm{lo}\) sits in the cell.
Six Stage-3 fat slabs recover (prime-rounding only).

**Band II zero block.** \(K<p\le N/2\Rightarrow p\mid m\). Those primes cannot kill.
Out of scope for next-prime-below-\(K\).

## Census

**3(b) / image runs**, all 38 NONE windows on \(10^5\le p\le 10^6\),
every \(k\) from the preceding Z through first-NONE\(-1\):
no whole-window image-run; longest consecutive NONE-prime image-run is 2;
zero triples (expected \(\sim 0.04\) under independence — a sample, not a cutoff).
Table: [`zeromap-p1e5-1e6.md`](zeromap-p1e5-1e6.md).

Known doubles, each killed at the next NONE prime:

| \(k\) | window | matches \((p,j)\) | kill |
|---:|---:|---|---:|
| 268733 | (39,15) | 270097 / 589, 270121 / 196 | 270131 |
| 761274 | (13,5) | 771697 / 3436, 771703 / 4909 | 771739 |
| 961361 | (10,4) | 982171 / 11442, 982183 / 5741 | 982187 |
| 1335751 | (7,3) | 1350467 / 833, 1350469 / 3128 | 1350473 |

**Stage 3**, \(k=100001..1000000\), until-kill, hang-guard \(p-k>20000\)
(that is a **gap** cap, not 20,000 surviving primes):
900000 columns, 31420 s; 810805 killed; 89195 hang-guard;
\(r=0\) on 452944 columns (50.3%).
Every killed row with \(r\ge 50\) (306189/306189) has \(q\) immediately after a \(Z_\mathrm{last}\).
All hang-guard \(k\) sit in six fat Z slabs (seven runs). Summary:
[`../results/nextprime_i8_k100001-1000000_summary.json`](../results/nextprime_i8_k100001-1000000_summary.json).
The 81 MB row dump stays local.

**Near-\(K\) stragglers**, \(k=4126622..4126646\): no prime in \((k,K]\).
All 25 killed by the first primes \(>N/2\): 21 at 5401853, four image-survive
that prime (explicit \(j\)) and die at 5401861.
[`../results/stragglers_nearK.json`](../results/stragglers_nearK.json).
Not a theorem that the first \(p>N/2\) always kills.

**Triple hunt** on NONE cells with \(P_\mathrm{hi}>10^6\): 0 triples, max run 2
(the (7,3) double above). Fat cells (5,2) and (2,1) were three canonical \(k\)
only (`g_max>25000`). [`../results/triple_hunt_p1e6-K.json`](../results/triple_hunt_p1e6-K.json).

## Heuristic / open

Long \(q(k)-k\) is Z-slab geometry. A single numerical \(G(k)\) (including
\(\lceil(\ln k)^2\rceil\)) hides that. Image persistence is rare.

\(\rho=\mathrm{Zw}/P_\mathrm{hi}\) (that is \(g/p\) at the first NONE prime for
an under-Z \(k\)) is \(\le 0.039\) on the Stage-3 map. Globally among two-digit
cells it reaches **0.176** at \((\alpha,\beta)=(4,1)\), then 0.109 at (7,2).
So \(g/p\le 1/20\) is not a Band I bound. A hang-guard that walked (4,1)
would need \(>475240\). Do not run that.

**Open.** No proof that a NONE image-run of length 3 is impossible.
Frozen \((\alpha,\beta)\) writes \(r(p)\) but does not correlate \(m\bmod p_1\)
with \(m\bmod p_2\) (CRT). Two-to-three is parked. Part 3(a) is open at the
correlation layer.

This line does not start Stage 4 / \(k=10^6..K\) until-kill, Band II next-prime,
exact \(i=10\), or nearby \(10^9..2\cdot 10^9\).
