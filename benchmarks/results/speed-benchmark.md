# Speed Benchmark

## Encoding

| Dataset | JSON | TOON | Speedup |
|---|---:|---:|---:|
| GitHub Repositories | 214.72 µs | 2.60 ms | 0.08x |
| Daily Analytics (180 days) | 224.00 µs | 1.31 ms | 0.17x |
| E-Commerce Orders | 214.35 µs | 2.17 ms | 0.10x |
| Employee Records | 112.67 µs | 1.03 ms | 0.11x |

Avg: 0.12x, Median: 0.10x, Min: 0.08x, Max: 0.17x

## Decoding

| Dataset | JSON | TOON | Speedup |
|---|---:|---:|---:|
| GitHub Repositories | 241.28 µs | 5.14 ms | 0.05x |
| Daily Analytics (180 days) | 199.07 µs | 1.53 ms | 0.13x |
| E-Commerce Orders | 153.08 µs | 3.26 ms | 0.05x |
| Employee Records | 117.36 µs | 712.61 µs | 0.16x |

Avg: 0.10x, Median: 0.09x, Min: 0.05x, Max: 0.16x

## Roundtrip

| Dataset | JSON | TOON | Speedup |
|---|---:|---:|---:|
| GitHub Repositories | 457.32 µs | 7.84 ms | 0.06x |
| Daily Analytics (180 days) | 475.67 µs | 2.86 ms | 0.17x |
| E-Commerce Orders | 380.17 µs | 5.59 ms | 0.07x |
| Employee Records | 200.09 µs | 1.66 ms | 0.12x |

Avg: 0.10x, Median: 0.09x, Min: 0.06x, Max: 0.17x
