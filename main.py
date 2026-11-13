import os, json, urllib.request

E = os.environ
URL = E.get('MAKEFUN_ENV_URL', 'http://127.0.0.1:8080')

KN = (-21, -19, -12, -8, 8, 12, 19, 21)
KG = (-11, -10, -9, -1, 1, 9, 10, 11)
BS = (-11, -9, 9, 11)
RS = (-10, -1, 1, 10)
IX = [i for i in range(21, 99) if i % 10 not in (0, 9)]
D = {'n': KN, 'k': KG, 'b': BS, 'r': RS, 'q': BS + RS}
PW = ' pnbrqk'
piece_values = {'p': 100 + 6 * 5 + (10 if 3 <= 5 <= 4 else 0),
                 'n': 300 + 6 * 4,
                 'b': 322 + 4 * 4,
                 'r': 500 + 2 * 5,
                 'q': 894 + 2 * 4,
                 'k': -20 * 5}
T = {}
for t in 'pnbrqk':
    a = [0] * 120
    d = [0] * 120
    for r in range(8):
        for f in range(8):
            a[21 + r * 10 + f] = piece_values[t] + 6 * r + (10 if f in (3, 4) and r > 2 else 0)
            d[21 + r * 10 + f] = piece_values[t] + 6 * (7 - r) + (10 if f in (3, 4) and 7 - r > 2 else 0)
    T[t] = [-v for v in d]; T[t.upper()] = a

def pa(s):
    b = ['#'] * 120
    for i in IX:
        b[i] = '.'
    b[0] = s.split()[1]; r = 7
    for w in s.split()[0].split('/'):
        f = 0
        for c in w:
            if c.isdigit(): f += int(c)
            else: b[21 + r * 10 + f] = c; f += 1
        r -= 1
    return b

def ak(b, s, by):
    if by == 'w':
        if b[s - 9] == 'P' or b[s - 11] == 'P': return 1
    elif b[s + 9] == 'p' or b[s + 11] == 'p': return 1
    n = 'N' if by == 'w' else 'n'
    for d in KN:
        if b[s + d] == n: return 1
    k = 'K' if by == 'w' else 'k'
    for d in KG:
        if b[s + d] == k: return 1
    for d in BS:
        j = s + d
        while b[j] == '.': j += d
        if b[j] in ('BQ' if by == 'w' else 'bq'): return 1
    for d in RS:
        j = s + d
        while b[j] == '.': j += d
        if b[j] in ('RQ' if by == 'w' else 'rq'): return 1
    return 0

U = []
def um(b):
    f, t, cp, pr, pc = U.pop()
    b[f] = pc; b[t] = cp
    b[0] = 'b' if b[0] == 'w' else 'w'

def mk(b, m):
    us = b[0]; f = m % 16384 >> 7; t = m & 127; pr = m >> 14; pc = b[f]; cp = b[t]
    U.append((f, t, cp, pr, pc))
    b[f] = '.'
    b[t] = ('nbrq'[pr - 1] if us == 'b' else 'NBRQ'[pr - 1]) if pr else pc
    b[0] = 'b' if us == 'w' else 'w'
    if ak(b, b.index('K' if us == 'w' else 'k'), b[0]): um(b); return 0
    return 1

def ge(b):
    us = b[0]; o = []
    for i in IX:
        c = b[i]
        if c == '.' or c.isupper() != (us == 'w'): continue
        l = c.lower()
        if l == 'p':
            d = 10 if us == 'w' else -10
            t = i + d
            if b[t] == '.':
                if t // 10 in (2, 9): o.append(i * 128 + t + 65536)
                else:
                    o.append(i * 128 + t)
                    if i // 10 in (3, 8) and b[t + d] == '.': o.append(i * 128 + t + d)
            for x in (d - 1, d + 1):
                t = i + x
                if b[t] not in '.#' and b[t].isupper() != (us == 'w'): o.append(i * 128 + t + (65536 if t // 10 in (2, 9) else 0))
            continue
        st = l in 'nk'
        for d in D[l]:
            t = i + d
            while b[t] == '.':
                o.append(i * 128 + t)
                if st: break
                t += d
            else:
                if b[t] not in '.#' and b[t].isupper() != (us == 'w'): o.append(i * 128 + t)
    return o

def ev(b):
    s = 0
    for i in IX:
        c = b[i]
        if c != '.': s += T[c][i]
    return s if b[0] == 'w' else -s

N = 0; AB = 0; LIM = 16000
def qs(b, a, bt):
    global N, AB
    N += 1
    if N > LIM: AB = 1; return 0
    s = ev(b)
    if s >= bt: return s
    if s > a: a = s
    for m in ge(b):
        if b[m & 127] == '.' and m < 16384: continue
        if not mk(b, m): continue
        v = -qs(b, -bt, -a)
        um(b)
        if AB: return 0
        if v > a:
            a = v
            if a >= bt: break
    return a

def ab(b, d, a, bt, p):
    global N, AB
    if AB: return 0
    N += 1
    if N > LIM: AB = 1; return 0
    if d < 1: return qs(b, a, bt)
    ms = ge(b)
    ms.sort(key=lambda m: PW.find(b[m & 127].lower()), reverse=True)
    best = -30000; lg = 0
    f