class HashTable:
    def __init__(self, size=41):
        self.size = size
        self.hash_table = self.create_buckets()

    def create_buckets(self):
        return [[] for _ in range(self.size)]

    def set_val(self, key, val):
        hashed_key = hash(key) % self.size
        bucket = self.hash_table[hashed_key]

        found_key = False
        for index, record in enumerate(bucket):
            record_key, _ = record
            if record_key == key:
                found_key = True
                break

        if found_key:
            bucket[index] = (key, val)
        else:
            bucket.append((key, val))

    def get_val(self, key):
        hashed_key = hash(key) % self.size
        bucket = self.hash_table[hashed_key]

        for record_key, record_val in bucket:
            if record_key == key:
                return record_val
        return "No record found"

    def delete_val(self, key):
        hashed_key = hash(key) % self.size
        bucket = self.hash_table[hashed_key]

        for index, (record_key, _) in enumerate(bucket):
            if record_key == key:
                bucket.pop(index)
                return

    def __str__(self):
        return "".join(str(item) for item in self.hash_table)
