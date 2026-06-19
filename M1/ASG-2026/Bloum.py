import hashlib

class BloomFilter:
    def __init__(self, size=1000, hash_count=3):
        self.size = size
        self.hash_count = hash_count
        self.bits = [0] * size

    def get_hashes(self, item):
        hashes = []
        for i in range(self.hash_count):
            data = str(i) + item
            h = hashlib.sha256(data.encode()).hexdigest()
            index = int(h, 16) % self.size
            hashes.append(index)
        return hashes

    def add(self, item):
        indexes = self.get_hashes(item)
        for idx in indexes:
            self.bits[idx] = 1


    def contains(self, item):
        indexes = self.get_hashes(item)
        for idx in indexes:
            if self.bits[idx] == 0:
                return False
        return True