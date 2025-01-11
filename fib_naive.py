def F(n):
    if n<=2:
        return 1
    else :
        print("we are calling F", n-1, n-2)
        return F(n-1)+F(n-2)

print(20, F(20))
#for i in range(100):
#    print(i, F(i))
#print("Done")