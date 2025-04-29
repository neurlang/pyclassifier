"""
Efficient dictionary for storing boolean values (like a boolean hashmap)

See blog post and Go package
    https://blog.hashtron.cloud/post/2025-02-20-quaternary-filter
    https://github.com/neurlang/quaternary
"""

from typing import Dict
from hashtron.hash.hash import Hash

def hash64(n: int, s: int, m: int) -> int:
    if m < 1<<32:
        # Use 32-bit hash
        return Hash.hash(n, s, m)
    # dumb extension to 64bit modulo to enable massive tables
    h = ((s<<32 | n) % m)
    # Return 32-bit result
    return h & 0xFFFFFFFF

def byte_size(n: int) -> int:
    """
    Bytes size for N cells
    """
    return (3 + n) // 4

def cell_size(n: int) -> int:
    """
    Cell size in bits from n bytes
    """
    return n * 4

def grow(n: int) -> int:
    """
    Increase n by ~50%
    """
    return (3 * n + 1) // 2

def rotate(n: int) -> int:
    """
    Rotate the bits of a 32-bit integer to the right by 1 position
    Example: 0b(1)010 -> 0b010(1)
    """
    # Apply 0xFFFFFFFF mask to ensure the result fits within 32 bits
    return ((n >> 1) | ((n & 1) << 31)) & 0xFFFFFFFF

class Quatenary:
    def __init__(self, data: Dict[object, bool]):
        self.attemps = 64
        self._create(data)
        
    
    def _create(self, data: Dict[object, bool]):
        if len(data) == 0:
            return
        current_bytes_size = byte_size(grow(len(data)))
        self.filter = bytearray(current_bytes_size)
        max_load = len(data)

        while True:
            is_mutated = True
            load = 0
            while is_mutated and load < max_load:
                new_inserted = 0
                for k, v in data.items():
                    new_inserted += self._set(k, v)
                    if load + new_inserted >= max_load:
                        break
                is_mutated = is_mutated and new_inserted > 0
                # ^ Is mutated if still have collisions
                load += new_inserted
            if is_mutated:
                # Increate size
                current_bytes_size = byte_size(grow(cell_size(len(self.filter))))
                self.filter = bytearray(current_bytes_size)
                max_load = grow(max_load)
            else:
                # Ready
                break


    def _set(self, key: object, answer: bool):
        if not self.filter:
            return 1
        
        answer = int(answer)
        
        inserted = 0
        current_cells_size = cell_size(len(self.filter))
        x = key
        high = key >> 32
        for i in range(self.attemps):
            h = hash64(x, high ^ i, current_cells_size)
            idx = h >> 2
            shift = (h & 3) * 2
            val = (self.filter[idx] >> shift) & 0b11

            if val == 0:
                # ^ empty cell
                if answer == (x & 1) == 1:
                    # ^ We can get answer using math and keep cell usable
                    return inserted
                # No math answer. Store answer in cell
                self.filter[idx] |= ((int(answer) & 1) + 1) << shift
                inserted += 1
                return inserted
            elif val == 1 and answer == 0:
                # ^ We use cell one as False
                # Same value from some other key in the cell. let's use it for this key as well!
                return inserted
            elif val == 2 and answer == 1:
                # Again. same value from previous key. Use it for this one as well for saving space.
                return inserted
            elif val == 3:
                # ^ Trash cell
                pass # Try again

            # Mark collision if not already
            self.filter[idx] |= 0b11 << shift
            x = rotate(x)  # rotate x right
            inserted += 1

        # All failed, return count
        return inserted + 1


    def get(self, key: object) -> bool:
        if len(self.filter) == 0:
            return key&1 == 1
        current_cells_size = cell_size(len(self.filter))
        x = key
        high = key >> 32
        for i in range(self.attemps):
            h = hash64(x, high ^ i, current_cells_size)
            idx = h >> 2
            shift = (h & 3) * 2
            val = (self.filter[idx] >> shift) & 0b11
            if val == 0:
                return x&1 == 1
                # ^ Math answer
            elif val == 1:
                return False
            elif val == 2:
                return True
            elif val == 3:
                # ^ Trash cell, rotate the key for new cell position
                x = rotate(x)
        # Default
        return False



if __name__ == '__main__':
    quatenary = Quatenary({5: True, 55: False})
    print(quatenary.get(5))
    print(quatenary.get(55))
    print(quatenary.filter.hex()) # 000040