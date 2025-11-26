import math

def stars1(n):
    for i in range(n):
        print("*")

def stars2(n):
    for i in range(n):
        print("*")
    for i in range(n):
        print("*")

def stars3(n):
    for i in range(n):
        print("*")
    for i in range(5):
        print("*")

def stars4(n):
    for i in range(n):
        for j in range(n):
            print("*")

def stars5(n) :
  i = 1
  s = 0
  while i*i < n :
    #print ("*",end="")
    s = s + 1
    i = i+1
  print(f"""{j}: s {s}, 
        A: {math.floor(math.sqrt(j-1))}, 
        B: {math.ceil(math.sqrt(j)-1)}, 
        C: {math.floor(math.sqrt(j)-1)}, 
        D: {math.floor(math.sqrt(j))-1}""")


for j in range(2,30):
    #print("n:", j)
    stars5(j)



def stars6 ( N ) :
  for i in range (N) :
    for j in range (N) :
      print ("*")
    print ("*")

def stars7(n):
    for i in range(1, n + 1):
        for j in range(i):
            print("*")

def stars8(n):
    print("*")
    if n > 1 :
        for j in range(n):
            print("*")

def stars9 ( n ) :
  while n > 1 :
    print ("*")
    n = n // 2

def stars10(n):
    if n < 2:
        print("*") 
        return
    stars10(n-1)
    stars10(n-1)
    stars10(n-1)

def stars11(n):
    if n % 2 == 0:
        for i in range(n // 2):
            print("*")
    else:
        for i in range(3 * n):
            print("*")

def stars12(n):
    s = 1
    for i in range(n):
        s *= 2
    for j in range(s):
        print("*")

def stars13(n):
    r = n % 5
    s = n + r * r
    for i in range(s):
        print("*")


    print(j)
    stars5(j)