from enum import IntEnum

class Game(IntEnum):
    Black = 0
    White = 1
    Black2 = 2
    White2 = 3

class Language(IntEnum):
    Japanese = 0
    Italian = 1
    German = 2
    French = 3
    Spanish = 4
    English = 5
    Korean = 6
    
class DSType(IntEnum):
    DS = 0
    DSi = 1
    DS3 = 2

class Buttons(IntEnum):
    NONE = 0

    R = 1 << 0 # -0x10000
    L = 1 << 1 # -0x20000

    X = 1 << 2 # -0x40000
    Y = 1 << 3 # -0x80000
    A = 1 << 4 # -0x1000000
    B = 1 << 5 # -0x2000000

    Select = 1 << 6 # -0x4000000
    Start  = 1 << 7 # -0x8000000

    Right = 1 << 8  # -0x10000000
    Left  = 1 << 9  # -0x20000000
    Up    = 1 << 10 # -0x40000000
    Down  = 1 << 11 # -0x80000000

    # Invalid keypresses
    SoftReset = L | R | Start | Select
    UpDown = Up | Down
    LeftRight = Left | Right

BUTTONS_VALUES = (
    0x10000, 0x20000, 
    0x40000, 0x80000, 
    0x1000000, 0x2000000, 
    0x4000000, 0x8000000, 
    0x10000000, 0x20000000, 
    0x40000000, 0x80000000
)

# https://github.com/Admiral-Fish/PokeFinder/blob/46d382f322456aa7a40d4da3a6be08ed69a2a9c9/Core/Gen5/Nazos.cpp
NAZOS = (
    # Japanese
    (
        (0x105f2102, 0x0c602102, 0x0c602102, 0x58602102, 0x58602102), # Black
        (0x305f2102, 0x2c602102, 0x2c602102, 0x78602102, 0x78602102), # White
        (0x50117602, 0x4c127602, 0x4c127602, 0x98127602, 0x98127602), # Black DSi
        (0x50117602, 0x4c127602, 0x4c127602, 0x98127602, 0x98127602), # White DSi
        (0xdca80902, 0xc99a0302, 0xb0f91f02, 0x04fa1f02, 0x04fa1f02), # Black 2
        (0xfca80902, 0xf59a0302, 0xd0f91f02, 0x24fa1f02, 0x24fa1f02), # White 2
        (0xdca80902, 0xc99a0302, 0x30a77a02, 0x84a77a02, 0x84a77a02), # Black 2 DSi
        (0xfca80902, 0xf59a0302, 0xf0a57a02, 0x44a67a02, 0x44a67a02), # White 2 DSi
    ),
    # Italian
    (
        (0xb05f2102, 0xac602102, 0xac602102, 0xf8602102, 0xf8602102), # Black
        (0xd05f2102, 0xcc602102, 0xcc602102, 0x18612102, 0x18612102), # White
        (0xd0017602, 0xcc027602, 0xcc027602, 0x18037602, 0x18037602), # Black DSi
        (0xd0017602, 0xcc027602, 0xcc027602, 0x18037602, 0x18037602), # White DSi
        (0xe8ad0902, 0x699d0302, 0x10ff1f02, 0x64ff1f02, 0x64ff1f02), # Black 2
        (0x28ae0902, 0x959d0302, 0x50ff1f02, 0xa4ff1f02, 0xa4ff1f02), # White 2
        (0xe8ad0902, 0x699d0302, 0x705f7a02, 0xc45f7a02, 0xc45f7a02), # Black 2 DSi
        (0x28ae0902, 0x959d0302, 0xd05e7a02, 0x245f7a02, 0x245f7a02), # White 2 DSi
    ),
    # German
    (
        (0xf05f2102, 0xec602102, 0xec602102, 0x38612102, 0x38612102), # Black
        (0x10602102, 0x0c612102, 0x0c612102, 0x58612102, 0x58612102), # White
        (0xf0027602, 0xec037602, 0xec037602, 0x38047602, 0x38047602), # Black DSi
        (0xf0027602, 0xec037602, 0xec037602, 0x38047602, 0x38047602), # White DSi
        (0x28ae0902, 0x699d0302, 0x50ff1f02, 0xa4ff1f02, 0xa4ff1f02), # Black 2
        (0x48ae0902, 0x959d0302, 0x70ff1f02, 0xc4ff1f02, 0xc4ff1f02), # White 2
        (0x28ae0902, 0x699d0302, 0x10617a02, 0x64617a02, 0x64617a02), # Black 2 DSi
        (0x48ae0902, 0x959d0302, 0x10607a02, 0x64607a02, 0x64607a02), # White 2 DSi
    ),
    # French
    (
        (0x30602102, 0x2c612102, 0x2c612102, 0x78612102, 0x78612102), # Black
        (0x50602102, 0x4c612102, 0x4c612102, 0x98612102, 0x98612102), # White
        (0x30027602, 0x2c037602, 0x2c037602, 0x78037602, 0x78037602), # Black DSi
        (0x50027602, 0x4c037602, 0x4c037602, 0x98037602, 0x98037602), # White DSi
        (0x08af0902, 0xf99d0302, 0x30002002, 0x84002002, 0x84002002), # Black 2
        (0x28af0902, 0x259e0302, 0x50002002, 0xa4002002, 0xa4002002), # White 2
        (0x08af0902, 0xf99d0302, 0x905f7a02, 0xe45f7a02, 0xe45f7a02), # Black 2 DSi
        (0x28af0902, 0x259e0302, 0xf05e7a02, 0x445f7a02, 0x445f7a02), # White 2 DSi
    ),
    # Spanish
    (
        (0x70602102, 0x6c612102, 0x6c612102, 0xb8612102, 0xb8612102), # Black
        (0x70602102, 0x6c612102, 0x6c612102, 0xb8612102, 0xb8612102), # White
        (0xf0017602, 0xec027602, 0xec027602, 0x38037602, 0x38037602), # Black DSi
        (0xf0017602, 0xec027602, 0xec027602, 0x38037602, 0x38037602), # White DSi
        (0xa8ae0902, 0xb99d0302, 0xd0ff1f02, 0x24002002, 0x24002002), # Black 2
        (0xc8ae0902, 0xe59d0302, 0xf0ff1f02, 0x44002002, 0x44002002), # White 2
        (0xa8ae0902, 0xb99d0302, 0x70607a02, 0xc4607a02, 0xc4607a02), # Black 2 DSi
        (0xc8ae0902, 0xe59d0302, 0xb05f7a02, 0x04607a02, 0x04607a02), # White 2 DSi
    ),
    # English
    (
        (0xb0602102, 0xac612102, 0xac612102, 0xf8612102, 0xf8612102), # Black
        (0xd0602102, 0xcc612102, 0xcc612102, 0x18622102, 0x18622102), # White
        (0x90017602, 0x8c027602, 0x8c027602, 0xd8027602, 0xd8027602), # Black DSi
        (0xb0017602, 0xac027602, 0xac027602, 0xf8027602, 0xf8027602), # White DSi
        (0xe8ae0902, 0xe99d0302, 0x10002002, 0x64002002, 0x64002002), # Black 2
        (0x28af0902, 0x159e0302, 0x50002002, 0xa4002002, 0xa4002002), # White 2
        (0xe8ae0902, 0xe99d0302, 0x705f7a02, 0xc45f7a02, 0xc45f7a02), # Black 2 DSi
        (0x28af0902, 0x159e0302, 0x905e7a02, 0xe45e7a02, 0xe45e7a02), # White 2 DSi
    ),
    # Korean
    (
        (0xb0672102, 0xac682102, 0xac682102, 0xf8682102, 0xf8682102), # Black
        (0xb0672102, 0xac682102, 0xac682102, 0xf8682102, 0xf8682102), # White
        (0x50117602, 0x4c127602, 0x4c127602, 0x98127602, 0x98127602), # Black DSi
        (0x50117602, 0x4c127602, 0x4c127602, 0x98127602, 0x98127602), # White DSi
        (0x0cb60902, 0xd5a40302, 0x50072002, 0xa4072002, 0xa4072002), # Black 2
        (0x2cb60902, 0x01a50302, 0x70072002, 0xc4072002, 0xc4072002), # White 2
        (0x0cb60902, 0xd5a40302, 0x70072002, 0xc4072002, 0xc4072002), # Black 2 DSi
        (0x2cb60902, 0x01a50302, 0xb0577a02, 0x04587a02, 0x04587a02), # White 2 DSi
    )
)

def get_nazos(game: Game, language: Language, dstype: DSType) -> tuple[int, int, int, int, int]:
    idx = 0
    if game == Game.White or game == Game.White2:
        idx |= 1 
    if dstype != DSType.DS:
        idx |= 2
    if game == Game.Black2 or game == Game.White2:
        idx |= 4
    return NAZOS[language][idx]

def valid_keypresses(combo: int, defective_buttons: int) -> bool:
    if combo < 0 or combo >= 0x1000:
        return False

    if (combo & defective_buttons) != 0:
        return False

    # maximum 8 keypresses are processed
    if combo.bit_count() > 8:
        return False

    if (combo & Buttons.SoftReset) == Buttons.SoftReset:
        return False

    if (combo & Buttons.UpDown) == Buttons.UpDown:
        return False

    if (combo & Buttons.LeftRight) == Buttons.LeftRight:
        return False

    return True

def keypresses_to_str(combo: int) -> str:
    return " + ".join(
        Buttons(combo & (1 << i)).name 
        for i in range(combo.bit_length()) 
        if (combo >> i) & 1
    )   

def keypresses_to_value(combo: int) -> int:
    return sum(
        -BUTTONS_VALUES[i] 
        for i in range(combo.bit_length()) 
        if (combo >> i) & 1
    ) + 0xff2f0000

T = (0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4)

DAYS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

def calc_week_day(year: int, month: int, day: int) -> int:
    year -= month < 3
    return (year + (year >> 2) - (year // 100) + (year // 400) + T[month - 1] + day) % 7

def calc_bcd(val: int) -> int:
    val &= 0xff
    return ((val // 10) << 4) + (val % 10)

def rotl(x: int, n: int) -> int:
    return ((x << n) | (x >> (32 - n))) & 0xffff_ffff

def byteswap(x: int) -> int:
    return (((x >> 24) & 0x00_00_00_ff) |
            ((x >>  8) & 0x00_00_ff_00) |
            ((x <<  8) & 0x00_ff_00_00) |
            ((x << 24) & 0xff_00_00_00))

class SHA1:
    def __init__(self, game: Game, language: Language, dstype: DSType, mac: int, vframe: int, gxstat: int, defective_buttons: int = 0):
        assert 0 <= defective_buttons < 0x1000, "invalid defective buttons"

        mac &= 0xffff_ffff_ffff_ffff
        vframe &= 0xff
        gxstat &= 0xff

        self.dstype = dstype
        self.defective_buttons = defective_buttons

        self.w = [0] * 80

        nazos = get_nazos(game, language, dstype)
        self.w[:5] = nazos

        self.w[6] = mac & 0xffff
        self.w[7] = ((mac >> 16) ^ (vframe << 24) ^ gxstat) & 0xffff_ffff

        self.w[10] = 0
        self.w[11] = 0
        self.w[13] = 0x80000000
        self.w[14] = 0
        self.w[15] = 0x1a0

    def set_timer0(self, timer0: int, vcount: int):
        timer0 &= 0xffff_ffff
        vcount &= 0xff

        val = ((vcount << 16) | timer0) & 0xffff_ffff

        self.w[5] = byteswap(val)

    def set_date(self, year: int, month: int, day: int):
        assert 2000 <= year <= 2099, "invalid year"
        assert 1 <= month <= 12, "invalid month"
        assert 1 <= day <= (DAYS[month - 1] + (month == 2 and (year % 4) == 0)), "invalid day"

        val  = calc_bcd(year - 2000) << 24 
        val |= calc_bcd(month) << 16 
        val |= calc_bcd(day) << 8
        val |= calc_week_day(year, month, day)

        self.w[8] = val

    def set_time(self, hour: int, minute: int, second: int):
        assert 0 <= hour <= 23, "invalid hour"
        assert 0 <= minute <= 59, "invalid minute"
        assert 0 <= second <= 59, "invalid second"

        val  = calc_bcd(hour) << 24 
        val |= calc_bcd(minute) << 16 
        val |= calc_bcd(second) << 8

        if hour >= 12 and self.dstype != DSType.DS3:
            val |= 0x40000000

        self.w[9] = val

    def set_keypresses(self, combo: int):
        assert valid_keypresses(combo, self.defective_buttons), "invalid keypresses"
        self.w[12] = keypresses_to_value(combo)

    def hash_seed(self) -> int:
        a = 0x67452301
        b = 0xefcdab89
        c = 0x98badcfe
        d = 0x10325476
        e = 0xc3d2e1f0
        w = self.w

        for i in range(80):
            if i <= 19:
                f = (b & c) | (~b & d)
                k = 0x5a827999
            elif i <= 39:
                f = b ^ c ^ d
                k = 0x6ed9eba1
            elif i <= 59:
                f = (b & c) | (b | c) & d
                k = 0x8f1bbcdc
            else:
                f = b ^ c ^ d
                k = 0xca62c1d6

            if i >= 16:
                w[i] = rotl(w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16], 1)

            t = (rotl(a, 5) + f + e + k + w[i]) & 0xffff_ffff
            a, b, c, d, e = t, a, rotl(b, 30), c, d

        lo = byteswap((a + 0x67452301) & 0xffff_ffff)
        hi = byteswap((b + 0xefcdab89) & 0xffff_ffff)
        seed = (hi << 32) | lo
        
        return (seed * 0x5D588B656C078965 + 0x269EC3) & 0xffff_ffff_ffff_ffff

if __name__ == "__main__":
    def test_sha1(
        game: Game, 
        language: Language, 
        dstype: DSType, 
        mac: int, 
        vcount: int, 
        timer0: int, 
        gxstat: int, 
        vframe: int, 
        date: tuple[int, int, int],
        time: tuple[int, int, int],
        keypresses: int,
        expected_seed: int
    ):
        sha = SHA1(game, language, dstype, mac, vframe, gxstat)
        sha.set_timer0(timer0, vcount)
        sha.set_date(*date)
        sha.set_time(*time)
        sha.set_keypresses(keypresses)

        seed = sha.hash_seed()
        assert seed == expected_seed, f"{seed = :016X}, {expected_seed = :016X}" 

    '''test_sha1(
        game = Game.Black, 
        language = Language.French, 
        dstype = DSType.DS, 
        mac = 0x9bf123456, 
        vcount = 0x1d, 
        timer0 = 0x3e3, 
        gxstat = 6, 
        vframe = 4, 
        date = (2011, 10, 22),
        time = (15, 34, 24),
        keypresses = 0, 
        expected_seed = 0xEA6F9D59361640E1
    )'''

    '''test_sha1(
        game = Game.White, 
        language = Language.English, 
        dstype = DSType.DSi, 
        mac = 0x9bf123456, 
        vcount = 0x1d, 
        timer0 = 0x3e3, 
        gxstat = 6, 
        vframe = 4, 
        date = (2048, 8, 16),
        time = (11, 9, 14),
        keypresses = Buttons.Start | Buttons.Select, 
        expected_seed = 0xB6F99B9972097637
    )'''

    '''test_sha1(
        game = Game.White2, 
        language = Language.Japanese, 
        dstype = DSType.DS3, 
        mac = 0x9bf123456, 
        vcount = 0x3e, 
        timer0 = 0x812, 
        gxstat = 6, 
        vframe = 4, 
        date = (2022, 2, 22),
        time = (1, 49, 57),
        keypresses = Buttons.R | Buttons.L | Buttons.X | Buttons.Y, 
        expected_seed = 0xD24722861E6DBB7F
    )'''