import hashlib

def md5(text):
    m = hashlib.md5()
    m.update(text.encode('utf-8'))
    return m.hexdigest()


if __name__ == '__main__':
    text = "123"
    v = md5(text)
    print(v)
