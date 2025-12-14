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

---
---

# Assignment 2: Extracting Elliptic Curve Parameters from an EC-DSA Certificate

## Description

This assignment investigates the Elliptic Curve Digital Signature Algorithm (EC-DSA) as used in TLS/HTTPS website authentication. The objective is to analyze a real TLS certificate, extract elliptic curve information, and determine what cryptographic parameters can be derived directly from the certificate versus those that must be obtained from external standards.

EC-DSA is widely deployed in modern web security due to its efficiency: it provides equivalent security to RSA with significantly smaller key sizes, resulting in faster computations and reduced bandwidth overhead.

---

## Problem Statement

**Key Question:** Given a TLS certificate that uses EC-DSA for its public key, can we extract the elliptic curve equation and the characteristic of the finite field?

This question is fundamental to understanding how elliptic curve cryptography is deployed in practice. The answer reveals important design decisions in cryptographic standards regarding:
- How curve parameters are communicated between parties
- The role of standardization in ensuring interoperability
- The separation between key material and mathematical specifications

---

## Key Insight

**TLS certificates do NOT store elliptic curve equations.**

This is a common misconception. In practice:

1. Certificates store only a **named elliptic curve identifier** (e.g., `secp256r1`)
2. The identifier is an Object Identifier (OID) that references a specific curve
3. The actual curve equation, field characteristic, and other parameters are defined in **publicly available cryptographic standards**
4. All implementations must use the same standards to correctly interpret the curve identifier

This design ensures:
- Compact certificate representation
- Consistent mathematical definitions across all parties
- Use of well-analyzed, secure curves only

---

## Approach and Methodology

The analysis follows these steps:

1. **Certificate Export**: The TLS certificate was exported from `_.bits-pilani.ac.in` in PEM format using a web browser.

2. **Certificate Parsing**: Python's `cryptography` library was used to load and parse the X.509 certificate structure.

3. **Public Key Extraction**: The EC public key was extracted, and its type was verified as `EllipticCurvePublicKey`.

4. **Curve Identification**: The named curve identifier was extracted from the public key object.

5. **Field Type Determination**: Based on the curve name prefix (`secp` for prime fields, `sect` for binary fields), the finite field type was identified.

6. **Parameter Lookup**: The named curve was mapped to its mathematical parameters using NIST FIPS 186-4 and SEC 2 specifications.

7. **Verification**: The public key point was verified to satisfy the curve equation, confirming the correctness of the looked-up parameters.

---

## Tools and Technologies Used

| Category | Tool/Standard |
|----------|---------------|
| Programming Language | Python 3.x |
| Certificate Parsing | `cryptography` library |
| Mathematical Standards | NIST FIPS 186-4 |
| Curve Parameters | SEC 2: Recommended Elliptic Curve Domain Parameters |

---

## Repository Structure

```
Cryptography/
├── Assignment_2.ipynb      # Main Jupyter Notebook with analysis
├── _.bits-pilani.ac.in.crt # Exported TLS certificate (PEM format)
└── README.md               # This documentation file
```

| File | Purpose |
|------|---------|
| `Assignment_2.ipynb` | Contains theoretical explanations, Python code, and analysis results |
| `_.bits-pilani.ac.in.crt` | The TLS certificate under analysis |
| `README.md` | Project documentation and instructions |

---

## How to Run the Code

### Prerequisites

- Python 3.8 or higher
- Jupyter Notebook or VS Code with Jupyter extension

### Installation

```bash
# Install required library
pip install cryptography
```

### Execution

1. Ensure `_.bits-pilani.ac.in.crt` is in the same directory as the notebook
2. Open `Assignment_2.ipynb` in Jupyter Notebook or VS Code
3. Run all cells sequentially (Kernel → Run All)

---

## Sample Output

```
ELLIPTIC CURVE PARAMETERS (FROM STANDARDS)
======================================================================

Curve: secp256r1
   Aliases: prime256v1, P-256
   Field Type: Prime Field

Prime p (Field Characteristic):
   p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
   Bit length: 256 bits

Curve Coefficients:
   a = 0xffffffff00000001000000000000000000000000fffffffffffffffffffffffc
   b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b

Elliptic Curve Equation:
   y^2 = x^3 + ax + b (mod p)

[VERIFIED] The public key point lies on the curve.
```

---

## Conclusion

### What Was Successfully Extracted from the Certificate

- Public key type (Elliptic Curve)
- Named curve identifier (`secp256r1`)
- Public key point coordinates $(Q_x, Q_y)$
- Key size (256 bits)

### What Required Standards-Based Lookup

- Prime $p$ (field characteristic)
- Curve coefficients $a$ and $b$
- Generator point $G$
- Curve order $n$

### Final Answer

**No, the elliptic curve equation cannot be extracted directly from a TLS certificate.**

The certificate contains only a curve identifier. The mathematical parameters defining the curve equation must be obtained from published cryptographic standards (NIST FIPS 186-4 or SEC 2). This is an intentional design choice that promotes standardization, security, and interoperability.

---

## References

1. **NIST FIPS 186-4**: Digital Signature Standard (DSS)  
   https://csrc.nist.gov/publications/detail/fips/186/4/final

2. **SEC 2**: Recommended Elliptic Curve Domain Parameters  
   https://www.secg.org/sec2-v2.pdf

3. **RFC 5480**: Elliptic Curve Cryptography Subject Public Key Information  
   https://tools.ietf.org/html/rfc5480

4. **Python `cryptography` Library**  
   https://cryptography.io/en/latest/

---

*Cryptography Programming Assignment 2*  
*Elliptic Curve Digital Signature Algorithm (EC-DSA) Analysis*
