class HashTable:

    # Create empty bucket list
    def __init__(self, size=41):
        self.size = size
        self.hash_table = self.create_buckets()

    def create_buckets(self):
        return [[] for _ in range(self.size)]

    # Insert values into hash map
    def set_val(self, key, val):
        hashed_key = hash(key) % self.size

        bucket = self.hash_table[hashed_key]

        found_key = False
        for index, record in enumerate(bucket):
            record_key, record_val = record

            if record_key == key:
                found_key = True
                break
        
        if found_key:
            bucket[index] = (key, val)
        else:
            bucket.append((key, val))
    
    # Return searched value with key
    def get_val(self, key):
        hashed_key = hash(key) % self.size

        bucket = self.hash_table[hashed_key]

        found_key = False
        for index, record in enumerate(bucket):
            record_key, record_val = record

            if record_key == key:
                found_key = True
                break
        
        if found_key:
            return record_val
        else:
            return "No record found"
    
    def delete_val(self, key):
        hashed_key = hash(key) % self.size

        bucket = self.hash_table[hashed_key]

        found_key = False
        for index, record in enumerate(bucket):
            record_key, record_val = record

            if record_key == key:
                found_key = True
                break
        
        if found_key:
            bucket.pop(index)
        return

    # Print values in hash map
    def __str__(self):
        return "".join(str(item) for item in self.hash_table)
