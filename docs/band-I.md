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
PART-lower (\(p<z_\mathrm{lo}\)) is the same image clause (digit-0 silent).

**Kill test (no giant \(m\)).** With
\(I_g=\{(-1)^j\binom{g-1}{j}\bmod p:0\le j<g\}\)
(equivalently \(\binom{k+j}{j}\), **not** \(\binom{k}{j}\)),
a NONE / PART-lower prime kills iff \(r(p)\notin I_g\).

**Z-slab.** If no prime lies in \((k,t]\) for threshold \(t=d/(\alpha-\beta)\),
then \(q(k)\) is at least the first prime after the slab top \(u\).

**Z-width (closed).** Cell
\(P_\mathrm{lo}=\max(\lfloor N/(\alpha+1)\rfloor+1,\lfloor K/(\beta+1)\rfloor+1)\),
\(P_\mathrm{hi}=\min(\lfloor N/\alpha\rfloor,\lfloor K/\beta\rfloor)\),
\(z_\mathrm{lo}=\lfloor d/(\alpha-\beta)\rfloor+1\),
\(\mathrm{Zw}=P_\mathrm{hi}-\max(P_\mathrm{lo},z_\mathrm{lo})\) (or 0).
FULL / PART / NONE from where \(z_\mathrm{lo}\) sits in the cell.
Six Stage-3 fat slabs recover (prime-rounding only).

**Pascal size of \(I_g\).** \(I_g\) is the coefficient set of \((1-X)^{g-1}\)
over \(\mathbf{F}_p\). For \(g-1<p\) no coefficient vanishes. The only
systematic collision is the reflection \(j\leftrightarrow n-j\) with \(n=g-1\):

- \(g\) odd (\(n\) even): fold, \(\lvert I_g\rvert\approx(g+1)/2\)
- \(g\) even (\(n\) odd): sends \(v\mapsto -v\), no fold, \(\lvert I_g\rvert\approx g\)

Remaining collisions match the birthday count
\(p\bigl(1-(1-1/p)^M\bigr)\) with \(M=g\) or \((g+1)/2\), to \(0.1\%\)
on the fat cells. Prime gaps are even, so the parity of \(g\) is frozen
along a chain: even-\(g\) columns stay about twice as easy.

**Band II zero block.** \(K<p\le N/2\Rightarrow p\mid m\). Those primes cannot kill.
Out of scope for next-prime-below-\(K\).

## Census

**3(b) / image runs**, all 38 NONE windows on \(10^5\le p\le 10^6\),
every \(k\) from the preceding Z through first-NONE\(-1\):
no whole-window image-run; longest consecutive NONE-prime image-run is 2;
zero triples (low-\(\rho\) sample; independence guessed \(\sim 0.04\)).
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

**Fat-image hunt**, first three primes of every NONE + PART-lower cell with
\(P_\mathrm{hi}>10^6\) and \(g_\max>25000\) (8/8, 6.82 h):
[`../results/fat_image_hunt.json`](../results/fat_image_hunt.json).
Two-to-three is false as a lemma: 369 first-3-prime image triples
(324 in (3,1) PART-lower, 20 on genuine NONE). Hunt cap `max_run=3`
(only three primes tested). Low-\(\rho\) cells (9,3) and (10,4) still
max run 2; (10,4) recovered \(k=961361\).

Independence-after-size (Pascal + birthday, no fitted parameters) predicts
the (3,1)/(2,1)/(5,2) counts \(n_1/n_2/n_3\) to \(+1.4\sigma\) on pooled
triples (344 observed vs 319). The old \(n_1/g_\max=0.0626\Rightarrow
\lvert I_g\rvert/g\approx 0.355\) step was a slip: that ratio averages
over \(g=1..g_\max\). Even-\(g\) fraction of the 369: \(332/369=0.900\)
(predicted \(0.878\)).

**Walk-369**, those 369 \(k\) past prime 3, image clause only, until kill
or cell end (174 s):
[`../results/walk_369.json`](../results/walk_369.json).
Pre-registered vs measured: survive-4 \(42\) (pred \(\sim 44\), band \(32\)–\(58\));
survive-5 \(4\) (\(\sim 6\)); survive-6 \(1\) (\(\sim 0.8\)); survive-7 \(0\) (\(\sim 0.1\)).
`max_run=6`. All 369 killed; no cell-end, no digit-0.
Record: \((3,1)\) \(k=2227205\), \(g=473762\) even, dies at \(2701099\) after
six image matches. NONE cells (2,1) and (5,2) all died at run 3.

## Heuristic / open

Long \(q(k)-k\) is Z-slab geometry plus a short image tail. A single
numerical \(G(k)\) (including \(\lceil(\ln k)^2\rceil\)) hides that.
The tail is length \(\le 2\) at Stage-3 \(\rho\le 0.039\), and length
\(6\) at the global max \(\rho=0.176\). Whole-window image-run on a fat
cell is \(10^{-\mathrm{many}}\) under the size law; the walk is the
registered check.

\(\rho=\mathrm{Zw}/P_\mathrm{hi}\) (that is \(g/p\) at the first NONE prime for
an under-Z \(k\)) is \(\le 0.039\) on the Stage-3 map. Globally among two-digit
cells it reaches **0.176** at \((\alpha,\beta)=(4,1)\), then 0.109 at (7,2).
Same geometry as the fat-image prize: under-Z \(k\) of (4,1), first NONE
primes of (3,1), \(g_\max=475282\). So \(g/p\le 1/20\) is not a Band I bound.
A hang-guard that walked (4,1) would need \(>475240\). Do not run that.

Frozen \((\alpha,\beta)\) writes \(r(p)\) but the falling-factorial identity
relating \(r(p)\) and \(r(p+h)\) lives in \(\mathbf{Z}\) and does not
descend \(\mathbf{F}_p\to\mathbf{F}_{p+h}\) (CRT). Independence is the
right model for consecutive NONE primes; the character-sum shape for a
correlation bound is the wrong shape (completion loses Pascal folding;
Weil is vacuous for \(j>\sqrt{p}\)).

This line does not start Stage 4 / \(k=10^6..K\) until-kill, Band II next-prime,
exact \(i=10\), or nearby \(10^9..2\cdot 10^9\).
