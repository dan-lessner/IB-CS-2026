#Boxes = [145, 687, 58, 68, 278, 149, 296, 382, 398, 426, 827, 654, 257, 12, 16, 8, 147, 1028, 283, 647, 2, 48, 12]

def SearchOO (Co, Kde) :
    Count = 0
    R = len(Kde) - 1
    L = 0
    while R != L: 
        Count += 1
        M = (R + L) / 2
        Pokus = Kde[int(M)]
        if Pokus == Co:
            break
        elif Pokus > Co:
            R = M
        else:
            L = M
    return Count


def SearchO (Co, Kde) :
    Count = 0
    L = 0
    R = len(Kde) - 1
    while L <= R: 
        M = (R + L) // 2
        Pokus = Kde[M]
        #print (Co, Pokus, L, M, R)
        if Co == Pokus:
            Count += 1
            break
        elif Co > Pokus:
            Count += 2
            L = M+1
        else:
            Count += 2
            R = M-1
    return Count

def SearchS(Co, Kde):
    Count = 0
    L = 0
    R = len(Kde)-1
    while L != R:
        M = (L + R) // 2
        Count += 1
        print (Co, Kde[M], L, M, R)
        if Kde[M] < Co:
            L = M + 1
        else:
            R = M
    Count += 1
    return Count

MaxSize = 10000000
Boxes = list(range(MaxSize))
for Size in range(MaxSize-1,MaxSize) :
    Total = 0
    print(f"Size: {Size}")
    for Trial in Boxes[:Size] :
        Total += SearchS(Trial,Boxes[:Size])
    print(f"Items: {str(Size).zfill(2)}, operations: {Total/Size:.2f}")

