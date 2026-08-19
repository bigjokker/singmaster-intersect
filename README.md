# Singmaster intersect

Search past the Blokhuis–Brouwer–de Weger (2017) envelope for extra binomial representations of the Lind/Singmaster/Tovey \(N=6\) Fibonacci family, plus unsettled nearby-row and column-pair collisions.

This does **not** prove Singmaster’s conjecture. It does prove
\(N\bigl(C(F_{18}F_{19},F_{16}F_{19})\bigr)=6\) exactly: every extra
left-half column \(2\le k\le k_{\max}\), \(k\notin\{K,K+1\}\), has a
modular kill certificate.

## Engine

`singmaster_intersect.py` (needs `gmpy2`):

| Command | Question |
|---|---|
| `intersect` | Exact extra-rep on a Fibonacci member (builds \(m\)) |
| `modular` | Lucas / image obstruction: prove a column cannot represent \(m_i\) **without** building \(m\) |
| `nearby` | Sampled \(C(n,k)=C(n-d,k+e)\) for unsettled \((d,e)\) |
| `collide` | Finite \(m\)-slice of \(C(n,k)=C(m,l)\) |
| `sanity` | Catalog, classifier, Lucas, image, 3003 tripwire |

```text
python singmaster_intersect.py sanity
python singmaster_intersect.py modular --imin 9 --imax 9 --kextra 80
```

`impossible` + a witness prime is a column-level proof. `possible` only means the prime list did not kill it. Nearby nulls are **sampled**, not exhaustive.

## Results worth keeping

| File | Claim |
|---|---|
| `results/fibonacci_i8_k300.json` | Exact: i=8 has no extra left-half with \(2\le k\le 300\), no central. \(N=6\). ~16.3 h |
| `results/modular_i8_k400.json` | Modular: i=8, \(k=2..400\) all impossible |
| `results/modular_i9_k80.json` | Modular: i=9, \(k=2..80\) all impossible |
| `results/modular_i10_k20.json` | Modular: i=10, \(k=2..20\) all impossible |
| `results/nearby_k2M-8M_de8.json` | Sampled nearby, \(k=2\text{M}..8\text{M}\), \(d,e\le 8\), `new_hits=0` |
| `results/nextprime_i8_k100001-1000000_summary.json` | Stage 3 census summary (i=8, \(k=10^5..10^6\)). Not a theorem |
| `results/stragglers_nearK.json` | 25 near-\(K\) Band I \(k\) all killed at \(p>N/2\) |
| `results/triple_hunt_p1e6-K.json` | NONE-window image runs, \(P_\mathrm{hi}>10^6\): max run 2, 0 triples (fat cells not exhaustive) |
| `results/fat_image_hunt.json` | Fat NONE+PART-lower, first 3 primes: 369 triples, hunt cap max run 3 |
| `results/walk_369.json` | Those 369 walked past prime 3: max run 6, counts match size law |
| `results/bandii_sweep.json` | Band II \(p>N/2\): 1,055,989 columns, all killed by prime 8 |
| `results/zjump.json` | Band I remnant Z-jump: 3,215,816 columns, 0 anomalies, tail = walk-369 |

Do not build \(m_{10}\) (~147 million digits) to answer small-\(k\) extra-rep. Modular already killed those columns.

## i=8 extra columns

Every extra \(k\in[2,k_{\max}]\setminus\{K,K+1\}\) has an unconditional
modular certificate. \(N(C(F_{18}F_{19},F_{16}F_{19}))=6\). Not Singmaster.

- [`docs/i8-N6.md`](docs/i8-N6.md) — the \(N=6\) theorem, as a note
- [`docs/band-I.md`](docs/band-I.md) — lemmas and census behind it
- [`docs/bandii-spec.md`](docs/bandii-spec.md) — Band II \(p>N/2\) sweep
- [`docs/zjump-spec.md`](docs/zjump-spec.md) — Band I Z-jump remnant
- [`docs/zeromap-p1e5-1e6.md`](docs/zeromap-p1e5-1e6.md) — 136 digit-windows, 38 NONE

## Notes

- [`docs/modular-spec.txt`](docs/modular-spec.txt) — Lucas/modular layer: what a certificate is, how to run scans, what not to rebuild
- [`docs/campaign-log.txt`](docs/campaign-log.txt) — original search campaign (exact i=8 \(k\le 300\), nearby, collide)
- [`scripts/run-i8-k300.bat`](scripts/run-i8-k300.bat) — historical wrapper for the exact i=8 \(k\le 300\) job (already finished)
- Settled theorem pairs \((k,l)\) and nearby \((1,1),(1,2),(2,1)\) are not re-sieved
- Classifier uses `is_fibonacci_pair`, not “rows differ by 1”
- Lucas digits use `_binom_mod_prime`, not `math.comb`. Large-\(p\) column tests scan and do not cache residue images

