# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

HASH_SEED = 17

def hash_update(seed, value):
    return int(((seed << 5) + seed) ^ value)
