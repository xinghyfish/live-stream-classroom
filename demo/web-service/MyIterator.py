def MyIterator():
    for i, data in enumerate([1, 3, 9]):
        print("I'm in the idx:[0] call of next()".format(i))
        yield data


if __name__ == '__main__':
    for i in MyIterator():
        print(i)