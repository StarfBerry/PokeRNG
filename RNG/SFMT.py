# SIMD-oriented Fast Mersenne Twister

from typing import Sequence

class SFMT:
    def __init__(self, init: int | Sequence[int]):
        self.state = [0] * 624
        if isinstance(init, int):
            self.reseed(init)
        else:
            self.restate(init)

    def period_certification(self):
        inner = (self.state[0] & 1) ^ (self.state[3] & 0x13C9E684)
        inner ^= inner >> 16
        inner ^= inner >> 8
        inner ^= inner >> 4
        inner ^= inner >> 2
        inner ^= inner >> 1

        if (inner & 1) == 0:
            self.state[0] ^= 1

    def reseed(self, seed: int):
        self.state[0] = seed & 0xffffffff
        for i in range(1, 624):
            seed = (0x6C078965 * (seed ^ (seed >> 30)) + i) & 0xffffffff
            self.state[i] = seed

        self.period_certification()
        self.twist()
        self.index = 0

    def restate(self, seq: Sequence[int]):
        assert len(seq) == 624, "The length of the sequence must be 624."

        for i in range(624): 
            self.state[i] = seq[i] & 0xffffffff

        self.period_certification()
        self.index = 0

    def twist(self):
        b, c, d = 488, 616, 620
        state = self.state

        for a in range(0, 624, 4):
            state[a + 3] ^= (state[a + 3] << 8) ^ (state[a + 2] >> 24) ^ ((state[b + 3] >> 11) & 0xBFFFFFF6)
            state[a + 3] ^= (state[c + 3] >> 8) ^ (state[d + 3] << 18) 
            state[a + 3] &= 0xffffffff

            state[a + 2] ^= (state[a + 2] << 8) ^ (state[a + 1] >> 24) ^ ((state[b + 2] >> 11) & 0xBFFAFFFF)
            state[a + 2] ^= (state[c + 2] >> 8) ^ (state[c + 3] << 24) ^ (state[d + 2] << 18)
            state[a + 2] &= 0xffffffff

            state[a + 1] ^= (state[a + 1] << 8) ^ (state[a] >> 24) ^ ((state[b + 1] >> 11) & 0xDDFECB7F)
            state[a + 1] ^= (state[c + 1] >> 8) ^ (state[c + 2] << 24) ^ (state[d + 1] << 18)
            state[a + 1] &= 0xffffffff

            state[a] ^= (state[a] << 8) ^ ((state[b] >> 11) & 0xDFFFFFEF)
            state[a] ^= (state[c] >> 8) ^ (state[c + 1] << 24) ^ (state[d] << 18)
            state[a] &= 0xffffffff

            b, c, d = (b + 4) % 624, d, a

    def untwist(self):
        b, c, d = 488, 616, 620
        state = self.state

        for a in reversed(range(0, 624, 4)):
            b, c, d = (b - 4) % 624, (c - 4) % 624, c

            state[a] ^= (state[c] >> 8) ^ (state[c + 1] << 24) ^ (state[d] << 18) ^ ((state[b] >> 11) & 0xDFFFFFEF)
            state[a] ^= state[a] << 8 
            state[a] ^= state[a] << 16
            state[a] &= 0xffffffff         

            state[a + 1] ^= (state[c + 1] >> 8) ^ (state[c + 2] << 24) ^ (state[d + 1] << 18)
            state[a + 1] ^= (state[a] >> 24) ^ ((state[b + 1] >> 11) & 0xDDFECB7F)
            state[a + 1] ^= state[a + 1] << 8
            state[a + 1] ^= state[a + 1] << 16
            state[a + 1] &= 0xffffffff

            state[a + 2] ^= (state[c + 2] >> 8) ^ (state[c + 3] << 24) ^ (state[d + 2] << 18)
            state[a + 2] ^= (state[a + 1] >> 24) ^ ((state[b + 2] >> 11) & 0xBFFAFFFF)
            state[a + 2] ^= state[a + 2] << 8
            state[a + 2] ^= state[a + 2] << 16
            state[a + 2] &= 0xffffffff

            state[a + 3] ^= (state[c + 3] >> 8) ^ (state[d + 3] << 18)
            state[a + 3] ^= (state[a + 2] >> 24) ^ ((state[b + 3] >> 11) & 0xBFFFFFF6)
            state[a + 3] ^= state[a + 3] << 8
            state[a + 3] ^= state[a + 3] << 16
            state[a + 3] &= 0xffffffff

    def next_u64(self) -> int:
        if self.index == 624:
            self.twist()
            self.index = 0

        lo = self.state[self.index]
        hi = self.state[self.index + 1]
        self.index += 2

        return (hi << 32) | lo

    def rand(self, maximum: int) -> int:
        return self.next_u64() % maximum

    def advance(self, n: int):
        self.index += n
        while self.index > 624:
            self.twist()
            self.index -= 624

    def reverse(self, n: int):
        self.index -= n
        while self.index < 0:
            self.untwist()
            self.index += 624