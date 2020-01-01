def grep(key, s):
    ret = ""
    for r in s.split("\n"):
        if key in r:
            ret += r + "\n"
    return ret