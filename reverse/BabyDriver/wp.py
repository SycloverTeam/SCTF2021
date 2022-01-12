def ReadMM(name, n, w):
    mm = [[0 for j in range(w)] for i in range(n)]
    with open('{}_{}_{}.txt'.format(name, n, w), 'r') as f:
        lines = f.readlines()
        i = 0
        for line in lines:
            j = 0
            for w in line.split():
                mm[i][j] = int(w)
                j += 1
            i += 1
                
    return mm


def msOrd2wsOrd(ms_ord):

    a = ms[ms_ord][0]*3+ms[ms_ord][1]
    b = ms[ms_ord][2]*4+ms[ms_ord][3]
    return a * 60 + b


def dp3(ii, ww):

    if ww < 0:
        return 0

    ans = 0

    if mm3[ii][ww] != -1:
        return mm3[ii][ww]

    # take ws[n]
    if ii == 59:
        for n in range(ii*60, (ii+1)*60):
            print(n)
            new_w = ww - ws[n]
            ans += dp3(ii-1, new_w)
    else:
        for n in range(ii*60, (ii+1)*60):
            new_w = ww - ws[n]
            ans += dp3(ii-1, new_w)

    mm3[ii][ww] = ans
    return ans


opos = [0]*60
cur_ans = []
def findPath(ii, ww):

    total_ans = []

    if ii == 0:
        for oo in range(60):
            if ws[oo] == ww:
                total_ans = [cur_ans[:] + [oo]]
                break
        return total_ans

    n = ii*60
    for oo in range(60):
        if opos[oo]:
            n += 1
            continue

        new_w = ww - ws[n]
        if new_w >= 0 and mm3[ii-1][new_w] > 0:
            opos[oo] = 1
            cur_ans.append(n)

            new_ans = findPath(ii-1, new_w)

            total_ans += new_ans

            del cur_ans[-1]
            opos[oo] = 0

        # continue
        n += 1
    
    return total_ans


w = 3100
ms = ReadMM('ms', 3600, 5)

wsOrd2msOrd = [0]*3600
ws = [0]*3600
for msOrd in range(3600):
    wsOrd = msOrd2wsOrd(msOrd)
    wsOrd2msOrd[wsOrd] = msOrd
    ws[wsOrd] = ms[msOrd][4]

# step 1 dp

mm3 = [[-1 for i in range(w+1)] for j in range(60)]
for ww in range(w+1):
    mm3[0][ww] = 0
for oo in range(60):
    mm3[0][ws[oo]] = 1
dp3(59, w)
print(mm3[59][w])

# step 2 dfs

ansWsOrds = findPath(59, w)[0]
ansMsOrds = [wsOrd2msOrd[ord] for ord in ansWsOrds]
print(ansMsOrds)

# step 3 key

ans = [0]*3600
for ord in ansMsOrds:
    ans[ord] = 1

s = ''
for x in ans:
    s += str(x)

with open('./key.bin', 'wb') as f:
    for i in range(0, 3600, 8):
        f.write(int(s[i:i+8][::-1], 2).to_bytes(1, 'little'))
