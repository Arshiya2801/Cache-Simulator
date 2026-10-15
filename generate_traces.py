#!/usr/bin/env python3
"""
generate_traces.py
Generates synthetic memory access traces for cache simulation experiments:
1. sequential.trace - High spatial locality (linear array scan)
2. loop.trace - High temporal locality (repeated loops over a small working set)
3. matrix_mul.trace - 2D matrix multiplication memory pattern (row-major vs column-major)
4. stride.trace - Strided memory access pattern (tests conflict misses & block size impact)
"""

import random

def generate_sequential_trace(filename="sequential.trace", count=5000):
    """Linear access over memory showing high spatial locality."""
    with open(filename, "w") as f:
        f.write("# Sequential Access Trace (High Spatial Locality)\n")
        addr = 0x10000000
        for i in range(count):
            access_type = 'l' if (i % 4 != 0) else 's'
            f.write(f"{access_type} 0x{addr:08x} 4\n")
            addr += 4

def generate_loop_trace(filename="loop.trace", loops=50, array_size=256):
    """Repeated access to a small buffer showing high temporal locality."""
    with open(filename, "w") as f:
        f.write("# Loop Trace (High Temporal Locality)\n")
        base = 0x20000000
        for _ in range(loops):
            for i in range(array_size):
                addr = base + (i * 4)
                f.write(f"l 0x{addr:08x} 4\n")
                if i % 2 == 0:
                    f.write(f"s 0x{addr:08x} 4\n")

def generate_matrix_trace(filename="matrix_mul.trace", n=32):
    """Simulates 32x32 matrix multiplication C[i][j] += A[i][k] * B[k][j]."""
    with open(filename, "w") as f:
        f.write(f"# Matrix Multiplication Trace ({n}x{n} float32)\n")
        base_A = 0x30000000
        base_B = 0x40000000
        base_C = 0x50000000
        
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    addr_a = base_A + (i * n + k) * 4
                    addr_b = base_B + (k * n + j) * 4
                    addr_c = base_C + (i * n + j) * 4
                    f.write(f"l 0x{addr_a:08x} 4\n")
                    f.write(f"l 0x{addr_b:08x} 4\n")
                    f.write(f"s 0x{addr_c:08x} 4\n")

def generate_stride_trace(filename="stride.trace", count=3000, stride=64):
    """Access memory with fixed byte stride to test conflict misses and block size impact."""
    with open(filename, "w") as f:
        f.write(f"# Strided Access Trace (Stride={stride} bytes)\n")
        addr = 0x60000000
        for i in range(count):
            f.write(f"l 0x{addr:08x} 4\n")
            addr = (addr + stride) % 0x60010000

if __name__ == "__main__":
    print("Generating synthetic traces...")
    generate_sequential_trace("sequential.trace")
    generate_loop_trace("loop.trace")
    generate_matrix_trace("matrix_mul.trace")
    generate_stride_trace("stride.trace")
    print("Done! Generated sequential.trace, loop.trace, matrix_mul.trace, stride.trace.")
