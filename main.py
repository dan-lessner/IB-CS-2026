def F(n):
    if n<=2:
        return 1
    else :
        return F(n-1)+F(n-2)
    
for i in range(100):
    print(i, F(i))
print("Done")