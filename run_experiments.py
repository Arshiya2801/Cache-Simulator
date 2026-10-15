#!/usr/bin/env python3
"""
run_experiments.py
Cross-platform experiment runner for the cache simulator.
Iterates over multiple trace files, cache sizes, block sizes, associativities,
and eviction policies, and exports results to results.csv.
"""

import subprocess
import sys
import os

TRACE_FILES = [
    "sequential.trace",
    "loop.trace",
    "matrix_mul.trace",
    "stride.trace"
]

CACHE_SIZES = [8192, 16384, 32768] # 8KB, 16KB, 32KB
BLOCK_SIZES = [16, 32, 64]
ASSOCIATIVITIES = [1, 2, 4, 8] # 1 = Direct Mapped
EVICTION_POLICIES = ["lru", "fifo"]

def is_power_of_two(n):
    return n > 0 and (n & (n - 1)) == 0

def run_simulation(csim_bin, num_sets, assoc, block_size, wa, wb, evict, trace_path):
    cmd = [csim_bin, str(num_sets), str(assoc), str(block_size), wa, wb, evict]
    with open(trace_path, "r") as f:
        res = subprocess.run(cmd, stdin=f, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Error running command {' '.join(cmd)}: {res.stderr}")
    
    stats = {}
    for line in res.stdout.strip().split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            stats[key.strip()] = int(val.strip())
    return stats

def main():
    csim_bin = "./csim.exe" if os.name == "nt" else "./csim"
    if not os.path.exists(csim_bin) and not os.path.exists(csim_bin.lstrip("./")):
        print(f"Error: Executable {csim_bin} not found. Please compile csim first.", file=sys.stderr)
        sys.exit(1)

    print("Trace,TotalCacheSize,BlockSize,Associativity,NumSets,EvictionPolicy,Cycles,HitRate,MissRate,TotalLoads,TotalStores,LoadHits,LoadMisses,StoreHits,StoreMisses")

    for trace in TRACE_FILES:
        if not os.path.exists(trace):
            print(f"Skipping missing trace: {trace}", file=sys.stderr)
            continue

        print(f"Processing trace: {trace}...", file=sys.stderr)
        for cache_size in CACHE_SIZES:
            for block_size in BLOCK_SIZES:
                for assoc in ASSOCIATIVITIES:
                    num_sets = cache_size // (block_size * assoc)
                    if not is_power_of_two(num_sets):
                        continue

                    for evict in EVICTION_POLICIES:
                        try:
                            stats = run_simulation(
                                csim_bin, num_sets, assoc, block_size,
                                "write-allocate", "write-back", evict, trace
                            )
                        except Exception as e:
                            print(f"Failed configuration: {e}", file=sys.stderr)
                            continue

                        loads = stats.get("Total loads", 0)
                        stores = stats.get("Total stores", 0)
                        load_hits = stats.get("Load hits", 0)
                        load_misses = stats.get("Load misses", 0)
                        store_hits = stats.get("Store hits", 0)
                        store_misses = stats.get("Store misses", 0)
                        cycles = stats.get("Total cycles", 0)

                        total_hits = load_hits + store_hits
                        total_accesses = loads + stores
                        hit_rate = (total_hits / total_accesses) if total_accesses > 0 else 0.0
                        miss_rate = 1.0 - hit_rate

                        row = [
                            trace, cache_size, block_size, assoc, num_sets, evict,
                            cycles, f"{hit_rate:.6f}", f"{miss_rate:.6f}",
                            loads, stores, load_hits, load_misses, store_hits, store_misses
                        ]
                        print(",".join(map(str, row)))

    print("All experiments complete.", file=sys.stderr)

if __name__ == "__main__":
    main()
