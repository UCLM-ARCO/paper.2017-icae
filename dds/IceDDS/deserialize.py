import struct


def deserialize(data, fmt):

    index = 0
    result = []

    for f in fmt:

        # string
        if f == 's':
            size = ord(data[index])
            index += 1
            result.append(data[index:index+size])

        # integer
        if f == 'i':
            result.append(struct.unpack("i", data[index:index+4])[0])
            size = 4

        # long
        if f == 'q':
            result.append(struct.unpack("q", data[index:index+8])[0])
            size = 8

        # float
        if f == 'f':
            result.append(struct.unpack("f", data[index:index+4])[0])
            size = 4

        # short
        if f == 'h':
            result.append(struct.unpack("h", data[index:index+2])[0])
            size = 2

        # double
        if f == 'd':
            result.append(struct.unpack("d", data[index:index+8])[0])
            size = 8

        # bool
        if f == '?':
            result.append(struct.unpack("?", data[index:index+1])[0])
            size = 1

        # byte
        if f == 'x':
            result.append(data[index:index+1])
            size = 1

        index += size

    return result
