import _sha3


def hashing_password(password, phone):
    hash_ = _sha3.sha3_256((str(password) + str(phone)).encode("utf-8")).hexdigest()
    return hash_

if __name__ == "__main__":
    print(hashing_password("qwe123", "333"))