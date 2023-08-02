import random as rd
from typing import List, Tuple


Poly = List[int]
Point = Tuple[int, int]


def miller_rabin(n: int, tol: int = 128) -> bool:
    """
    Miller-Rabin, primality test
    https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test

    test if n is definitely composite, or probably prime
    with certainty p <= 1 / 2**tol
    """

    # deal with simple cases
    if n in (2, 3):
        return True
    if (n == 1) or (n % 2 == 0):
        return False

    # find r & d s.t. n = 2**r * d + 1
    def get_dr(d, r):
        if d % 2:
            return d, r
        return get_dr(d // 2, r + 1)

    d, r = get_dr(n - 1, 0)

    def test(n, d, r):
        a = rd.randint(2, n - 2)
        x = pow(a, d, n)

        if x in (1, n - 1):
            return True
        for _ in range(r):
            x = (x * x) % n
            if x == n - 1:
                return True

        return False

    k = tol // 2 + 1
    answers = [test(n, d, r) for _ in range(k)]
    # if any of these answers is False, then it is False
    # otherwise return True
    return all(answers)


def find_prime(bits: int) -> int:
    """
    return a randomly generated prime of a given number of bits
    """
    lo = 2 ** bits
    hi = 2 ** (bits + 1)

    p = rd.randint(lo, hi)
    while not miller_rabin(p):
        p = rd.randint(lo, hi)

    return p


def create_polynomial(degree: int, p: int) -> Poly:
    """
    a polynomial is just a list of coefficients
    let's make them ints for ease
    all coefficients are less than a large prime, p
    """
    return [rd.randint(1, p) for _ in range(degree)]


def sample_polynomial(poly: Poly, n: int, prime: int) -> List[Point]:
    """
    return n pts on a polynomial (at x = 1, 2, 3...)
    mod the pts by our prime p
    """
    def f(x):
        return sum((c * (x ** i)) for i, c in enumerate(poly)) % prime

    return [(x, f(x)) for x in range(1, n + 1)]


def make_shares(secret: int, n: int) -> Tuple[List[Point], int]:
    """
    Take in a secret number, and return n Shamir shares of the encrypted number.
    k = (n // 2) + 1 shares will be required to recover the secret
    """
    # number of shares needed for reconstruction
    k = (n // 2) + 1

    bits = len(bin(secret)) - 2

    p = find_prime(bits)
    poly = [secret] + create_polynomial(k - 1, p)  # create a polynomial of degree k

    points = sample_polynomial(poly, n, p)

    return points, p


def reconstruct(pts: List[Point], p: int) -> int:
    """
    take a set of k shares (k > n / 2) and the prime p
    and use this to reconstruct the original secret
    we'll compute this using the optimised formula for the
    Lagrange polynomials
    """
    f0 = 0
    for xi, yi in pts:
        prod = 1
        for xm, _ in pts:
            if xi != xm:
                prod *= xm / (xm - xi)

        f0 += prod * yi

    return int(f0 % p)


if __name__ == "__main__":

    secret = 1234567890  # our super-secret number
    print(f"The secret is {secret}")

    # create 7 shares of the secret
    shares, prime = make_shares(secret, 7)

    # get 50% + 1 of our shares
    quorum = sorted(rd.sample(shares, 4), key=lambda x: x[0])

    # and unlock the secret
    unlocked = reconstruct(quorum, prime)

    print(f"The decrypted secret is {unlocked}")
