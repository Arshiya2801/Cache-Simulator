# Configurable C++ Cache Architecture & Memory Hierarchy Simulator

## Overview
This repository contains a configurable, trace-driven L1 cache simulator implemented in C++20. The project models realistic memory subsystems to evaluate the performance impact of different set-associativity levels, block sizes, write strategies, and eviction policies across real-world and synthetic program workloads.

It processes memory access traces (loads and stores with 32-bit hex addresses) to calculate hit/miss rates, memory latency penalties, and total processor execution cycles, demonstrating quantitative computer architecture principles.

---

## Architecture & Cache Design

The simulator engine is configurable to model various memory subsystem architectures:
* **Simulator Core (`csim.cpp`):** Contains the state machine for parsing memory access traces, tag matching, hit/miss resolution, and latency accounting.
* **Associativity & Cache Structures:** Models direct-mapped ($1$-way), $N$-way set-associative ($2, 4, 8$-way), and fully associative configurations.
* **Write Policies:** 
  - Miss Handling: `write-allocate` (fetch block on write miss) vs. `no-write-allocate` (write directly to memory).
  - Memory Update: `write-back` (with dirty-bit tracking per cache line) vs. `write-through` (simultaneous write to cache and main memory).
* **Eviction Policies:** 
  - **LRU (Least-Recently-Used):** Dynamic recency tracking on each hit and block allocation.
  - **FIFO (First-In, First-Out):** Age tracking based on block insertion timestamp.
* **Cycle-Accurate Latency Model:**
  - Cache access check: $1\text{ cycle}$
  - Memory block transfer: $100 \times (\text{block\_size} / 4)\text{ cycles}$
  - Direct 4-byte memory write: $100\text{ cycles}$

---

## Architectural Trade-Offs & Findings

Through systematic design space exploration (DSE) across multiple workloads, key empirical trade-offs were identified:

1. **Associativity vs. Hardware Complexity:**
   - Transitioning from direct-mapped to 2-way and 4-way set-associative caches drastically reduced conflict misses.
   - Increasing associativity from 4-way to 8-way yielded less than 1% additional hit rate improvement while requiring double the physical tag-matching comparators and wider multiplexer trees.
   - **Conclusion:** 4-way associativity achieved the optimal balance of hit rate vs. silicon area/timing overhead.

2. **Block Size vs. Miss Penalty:**
   - Larger block sizes (e.g., 64 bytes) exploited spatial locality, pushing raw hit rates higher.
   - However, the heavy memory latency penalty ($100 \times (B/4)$ cycles) of transferring large blocks from main memory on a miss outweighed hit rate gains for irregular workloads.
   - **Conclusion:** A 16-byte to 32-byte block size consistently minimized total processor execution cycles.

3. **Write Policy Impact:**
   - `write-back` with `write-allocate` substantially outperformed `write-through` by absorbing repeated writes locally in the L1 cache, eliminating redundant memory bus transactions.

---

## Repository Structure

```
├── csim.cpp              # Core C++ cache simulator source code
├── Makefile              # Build configuration for GCC / Clang
├── generate_traces.py    # Python benchmark workload generator
├── run_experiments.py    # Automated parameter sweep test harness
├── run_experiments.sh    # Bash automated sweep script
├── results.csv           # Empirical simulation results across configurations
├── example.trace         # Annotated trace illustrating spatial & temporal locality
├── sequential.trace      # Benchmark: high spatial locality
├── loop.trace            # Benchmark: high temporal locality
├── matrix_mul.trace      # Benchmark: 32x32 matrix multiplication access pattern
├── stride.trace          # Benchmark: strided memory access pattern
└── .gitignore            # Git exclusion rules for compiled binaries
```

---

## Build & Usage Instructions

### 1. Compilation
Compile using any modern C++ compiler supporting C++20 (GCC, Clang, or MinGW):

- **Linux / macOS:**
  ```bash
  make
  # or directly:
  g++ -O3 -Wall -std=c++20 csim.cpp -o csim
  ```

- **Windows (PowerShell / MinGW):**
  ```powershell
  g++ -O3 -Wall -std=c++20 csim.cpp -o csim.exe
  ```

### 2. Command-Line Syntax
```bash
./csim <num_sets> <blocks_per_set> <bytes_per_block> <write-allocate|no-write-allocate> <write-back|write-through> <lru|fifo>
```

#### Parameters:
- `num_sets`: Number of sets (positive power of 2)
- `blocks_per_set`: Number of lines per set / associativity (power of 2)
- `bytes_per_block`: Block size in bytes (power of 2, minimum 4)
- `write-allocate`: `write-allocate` or `no-write-allocate`
- `write-back`: `write-back` or `write-through`
- `eviction`: `lru` or `fifo`

### 3. Running Simulations

#### Run an Individual Trace:
- **Windows PowerShell:**
  ```powershell
  Get-Content example.trace | .\csim.exe 256 4 16 write-allocate write-back lru
  Get-Content matrix_mul.trace | .\csim.exe 256 4 16 write-allocate write-back lru
  ```

- **Linux / macOS:**
  ```bash
  ./csim 256 4 16 write-allocate write-back lru < example.trace
  ```

#### Example Output:
```text
Total loads: 65536
Total stores: 32768
Load hits: 65024
Load misses: 512
Store hits: 32512
Store misses: 256
Total cycles: 405504
```

### 4. Running the Automated Parameter Sweep
To run all permutations across cache sizes (8KB–32KB), block sizes (16B–64B), associativities (1–8 way), and eviction policies:

```bash
python run_experiments.py > results.csv
```

---

## Author
**Arshiya Singh**  
GitHub: [@Arshiya2801](https://github.com/Arshiya2801)
