"""Minimal reader for Tibia 15.x appearances.dat (protobuf) -> item flags we need for map building.
No protobuf library needed. Only object (item) entries are read."""
from __future__ import annotations


def _varint(b, i):
    r = s = 0
    while True:
        c = b[i]; i += 1
        r |= (c & 0x7F) << s
        if c < 0x80:
            return r, i
        s += 7


def _fields(b):
    i = 0
    while i < len(b):
        key, i = _varint(b, i)
        f, wt = key >> 3, key & 7
        if wt == 0:
            v, i = _varint(b, i)
        elif wt == 2:
            n, i = _varint(b, i); v = b[i:i + n]; i += n
        elif wt == 5:
            v = b[i:i + 4]; i += 4
        elif wt == 1:
            v = b[i:i + 8]; i += 8
        else:
            raise ValueError(f"wire type {wt}")
        yield f, wt, v


FLAG_FIELDS = {1: "bank", 2: "clip", 3: "bottom", 4: "top", 5: "container", 13: "unpass", 14: "unmove",
               15: "unsight", 16: "avoid", 18: "take", 30: "automap"}


def load(path):
    data = open(path, "rb").read()
    items = {}
    for f, wt, v in _fields(data):
        if f != 1:  # 1 = objects
            continue
        iid, flags, name = None, {}, ""
        for f2, wt2, v2 in _fields(v):
            if f2 == 1:
                iid = v2
            elif f2 == 3:
                for f3, wt3, v3 in _fields(v2):
                    if f3 in FLAG_FIELDS:
                        if f3 == 1:  # bank: waypoints (speed)
                            sp = 0
                            for f4, _w, v4 in _fields(v3):
                                if f4 == 1:
                                    sp = v4
                            flags["bank"] = sp or 1
                        elif f3 == 30:
                            col = 0
                            for f4, _w, v4 in _fields(v3):
                                if f4 == 1:
                                    col = v4
                            flags["automap"] = col
                        else:
                            flags[FLAG_FIELDS[f3]] = True
            elif f2 == 4:
                name = v2.decode("utf-8", "ignore")
        if iid is not None:
            items[iid] = (flags, name)
    return items
