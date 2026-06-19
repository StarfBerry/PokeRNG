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
        for i in range(624): 
            self.state[i] = seq[i] & 0xffffffff
        
        #self.period_certification()
        self.index = 0

    def twist(self):
        b, c, d = 488, 616, 620

        for a in range(0, 624, 4):
            self.state[a + 3] ^= self.state[a + 3] << 8
            self.state[a + 3] ^= (self.state[a + 2] >> 24) ^ ((self.state[b + 3] >> 11) & 0xBFFFFFF6)
            self.state[a + 3] ^= (self.state[c + 3] >> 8) ^ (self.state[d + 3] << 18) 
            self.state[a + 3] &= 0xffffffff

            self.state[a + 2] ^= self.state[a + 2] << 8
            self.state[a + 2] ^= (self.state[a + 1] >> 24) ^ ((self.state[b + 2] >> 11) & 0xBFFAFFFF)
            self.state[a + 2] ^= (self.state[c + 2] >> 8) ^ (self.state[c + 3] << 24) ^ (self.state[d + 2] << 18)
            self.state[a + 2] &= 0xffffffff

            self.state[a + 1] ^= self.state[a + 1] << 8
            self.state[a + 1] ^= (self.state[a] >> 24) ^ ((self.state[b + 1] >> 11) & 0xDDFECB7F)
            self.state[a + 1] ^= (self.state[c + 1] >> 8) ^ (self.state[c + 2] << 24) ^ (self.state[d + 1] << 18)
            self.state[a + 1] &= 0xffffffff

            self.state[a] ^= self.state[a] << 8
            self.state[a] ^= ((self.state[b] >> 11) & 0xDFFFFFEF) ^ (self.state[c] >> 8)
            self.state[a] ^= (self.state[c + 1] << 24) ^ (self.state[d] << 18)
            self.state[a] &= 0xffffffff

            b, c, d = (b + 4) % 624, d, a

    def untwist(self):
        b, c, d = 488, 616, 620

        for a in reversed(range(0, 624, 4)):
            b, c, d = (b - 4) % 624, (c - 4) % 624, c

            self.state[a] ^= (self.state[c + 1] << 24) ^ (self.state[d] << 18)
            self.state[a] ^= ((self.state[b] >> 11) & 0xDFFFFFEF) ^ (self.state[c] >> 8)
            self.state[a] ^= self.state[a] << 8
            self.state[a] ^= self.state[a] << 16
            self.state[a] &= 0xffffffff            
            
            self.state[a + 1] ^= (self.state[c + 1] >> 8) ^ (self.state[c + 2] << 24) ^ (self.state[d + 1] << 18)
            self.state[a + 1] ^= (self.state[a] >> 24) ^ ((self.state[b + 1] >> 11) & 0xDDFECB7F)
            self.state[a + 1] ^= self.state[a + 1] << 8
            self.state[a + 1] ^= self.state[a + 1] << 16
            self.state[a + 1] &= 0xffffffff

            self.state[a + 2] ^= (self.state[c + 2] >> 8) ^ (self.state[c + 3] << 24) ^ (self.state[d + 2] << 18)
            self.state[a + 2] ^= (self.state[a + 1] >> 24) ^ ((self.state[b + 2] >> 11) & 0xBFFAFFFF)
            self.state[a + 2] ^= self.state[a + 2] << 8
            self.state[a + 2] ^= self.state[a + 2] << 16
            self.state[a + 2] &= 0xffffffff

            self.state[a + 3] ^= (self.state[c + 3] >> 8) ^ (self.state[d + 3] << 18)
            self.state[a + 3] ^= (self.state[a + 2] >> 24) ^ ((self.state[b + 3] >> 11) & 0xBFFFFFF6)
            self.state[a + 3] ^= self.state[a + 3] << 8
            self.state[a + 3] ^= self.state[a + 3] << 16
            self.state[a + 3] &= 0xffffffff

    def next_u32(self) -> int:
        if self.index == 624:
            self.twist()
            self.index = 0

        out = self.state[self.index]
        self.index += 1

        return out

    def next_u64(self) -> int:
        lo = self.next_u32()
        hi = self.next_u32()
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