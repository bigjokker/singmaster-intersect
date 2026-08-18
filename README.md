# Singmaster intersect

Search past the Blokhuis–Brouwer–de Weger (2017) envelope for extra binomial representations of the Lind/Singmaster/Tovey \(N=6\) Fibonacci family, plus unsettled nearby-row and column-pair collisions.

This does **not** prove Singmaster’s conjecture.

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

Do not build \(m_{10}\) (~147 million digits) to answer small-\(k\) extra-rep. Modular already killed those columns.

## Notes

- `CLI-Commands.txt` — run log and gates (D/E order is historical)
- `AFTER-D.txt` — modular spec and post-D procedure
- Settled theorem pairs \((k,l)\) and nearby \((1,1),(1,2),(2,1)\) are not re-sieved
- Classifier uses `is_fibonacci_pair`, not “rows differ by 1”
