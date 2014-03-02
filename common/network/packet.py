__author__ = 'alan.lee'


class Packet:
    def __init__(self, raw):
        self.fin = raw[0] >> 7
        self.op = raw[0] & 15
        self.seq = raw[1]
        self.len = raw[2] + raw[3]
        self.data = raw[4:]

    def to_bytes(self):
        raw = bytearray('')
        raw.append((self.fin >> 7) + self.op)
        raw.append(self.seq)
        raw.append(self.len >> 8)
        raw.append(self.len & 255)
        raw.extend(self.data)
