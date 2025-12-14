# Assignment 1

## Prime Number Formulas: Willans' Formula & Linear Sieve Formula

This notebook explores two closed-form mathematical formulas for computing the n-th prime number.

### Overview

Both formulas prove that it's possible to express prime numbers using only basic arithmetic operations (addition, multiplication, division, floors, etc.) — no conditional logic required!

---

### Part 1: Willans' Formula

**Key Concepts:**
- **Wilson's Theorem**: $(p-1)! + 1$ is divisible by $p$ if and only if $p$ is prime
- **Prime-counting function** $\pi(n)$: counts primes ≤ n

**The Formula:**
```
p_n = 1 + Σ(i=1 to 2^n) ⌊(n / (1 + Σ(j=2 to i) ⌊cos²(((j-1)!+1)/j · π)⌋))^(1/n)⌋
```

**Complexity:** O(8^n) — exponential, impractical for large n

---

### Part 2: Linear Sieve Formula

**Key Concepts:**
- **Lowest Prime Factor (LPF)**: smallest prime that divides a number
- **Prime check**: x is prime ⟺ lpf(x) = x
- **Divides gadget**: D(d,n) = ⌊n/d⌋ - ⌊(n-1)/d⌋ (returns 1 if d|n, else 0)

**The Formula:**
```
p_n = 1 + Σ(m=1 to U) ⌊(n / (1 + Σ(x=2 to m) ⌊lpf(x)/x⌋))^(1/n)⌋

where lpf(x) = Σ(d=2 to x) [d · D(d,x) · Π(k=2 to d-1)(1-D(k,x))]
and U = max(13, ⌊n(ln n + ln ln n)⌋)
```

**Complexity:** O(n⁴ log⁴ n) — polynomial, much more efficient

---

### Files

- `Assignment_1.ipynb` — Main notebook with explanations and implementations

### How to Run

1. Open `Assignment_1.ipynb` in Jupyter Notebook or VS Code
2. Run cells sequentially to see:
   - Mathematical explanations
   - Python implementations
   - Complexity analysis
   - Timing comparisons

### Results

Both formulas correctly compute the prime sequence: 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31...

| Formula | Time Complexity | Practical for n=10? |
|---------|-----------------|---------------------|
| Willans' | O(8^n) | ~2.6M operations |
| Linear Sieve | O(n⁴ log⁴ n) | ~215K operations |

---

### Conclusion

These formulas are mathematical curiosities that prove closed-form prime expressions exist, but neither is practical compared to actual prime-finding algorithms like the Sieve of Eratosthenes.
