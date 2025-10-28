# Memory Benchmark

## Output Size (sys.getsizeof on Python str)

| Dataset | JSON | TOON | Diff | % |
|---|---:|---:|---:|---:|
| GitHub Repositories | 138.88 KB | 84.48 KB | 54.41 KB | 39.2% |
| Daily Analytics (180 days) | 19.84 KB | 6.71 KB | 13.13 KB | 66.2% |
| E-Commerce Orders | 20.76 KB | 17.25 KB | 3.50 KB | 16.9% |
| Employee Records | 15.04 KB | 6.41 KB | 8.64 KB | 57.4% |

## Encoding Peak Memory (tracemalloc)
| Dataset | JSON | TOON | Diff |
|---|---:|---:|---:|
| GitHub Repositories | 188.14 KB | 166.79 KB | 21.35 KB |
| Daily Analytics (180 days) | 21.58 KB | 72.54 KB | 50.96 KB |
| E-Commerce Orders | 22.45 KB | 119.34 KB | 96.89 KB |
| Employee Records | 17.79 KB | 46.13 KB | 28.33 KB |

## Decoding Peak Memory (tracemalloc)
| Dataset | JSON | TOON | Diff |
|---|---:|---:|---:|
| GitHub Repositories | 108.02 KB | 144.55 KB | 36.53 KB |
| Daily Analytics (180 days) | 75.47 KB | 91.87 KB | 16.40 KB |
| E-Commerce Orders | 86.11 KB | 162.27 KB | 76.16 KB |
| Employee Records | 48.46 KB | 60.72 KB | 12.26 KB |
