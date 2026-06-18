# Mersenne Twister

from typing import Sequence

class MT:    
    def __init__(self, init: int | Sequence[int]):
        self.state = [0] * 624
        if isinstance(init, int):
            self.reseed(init)
        else:
            self.restate(init)

    def reseed(self, seed: int):
        self.state[0] = seed & 0xffffffff
        for i in range(1, 624):
            seed = (0x6C078965 * (seed ^ (seed >> 30)) + i) & 0xffffffff
            self.state[i] = seed
        
        self.twist()
        self.index = 0
    
    def restate(self, state: Sequence[int]):        
        for i in range(624): 
            self.state[i] = state[i] & 0xffffffff
        
        self.index = 0

    def twist(self):
        for i in range(624):
            x = (self.state[i] & 0x80000000) | (self.state[(i + 1) % 624] & 0x7fffffff)            
            self.state[i] = self.state[(i + 397) % 624] ^ (x >> 1)
            if x & 1: 
                self.state[i] ^= 0x9908B0DF

    def untwist(self):
        for i in reversed(range(624)):
            x = self.state[i] ^ self.state[(i + 397) % 624]
            if x >> 31:
                x ^= 0x9908B0DF

            self.state[i] = (x << 1) & 0x80000000

            x = self.state[(i - 1) % 624] ^ self.state[(i + 396) % 624]
            if x >> 31:
                x ^= 0x9908B0DF
                self.state[i] |= 1

            self.state[i] |= (x << 1) & 0x7fffffff

    def next_u32(self) -> int:        
        if self.index == 624:
            self.twist()
            self.index = 0

        # temper
        t = self.state[self.index]
        t ^= t >> 11
        t ^= (t << 7) & 0x9D2C5680
        t ^= (t << 15) & 0xEFC60000
        t ^= t >> 18

        self.index += 1

        return t

    def next_u16(self) -> int:
        return self.next_u32() >> 16
              
    def rand(self, maximum: int) -> int:       
        return (self.next_u32() * maximum) >> 32

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