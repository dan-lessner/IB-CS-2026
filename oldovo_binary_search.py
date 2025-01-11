boxes = [1,2,3,4,5,6,7]
#boxes = list(range(7))

total = 0
for pokus in boxes :
    count = 0
    indexhigh = (len(boxes))
    print(indexhigh)
    indexlow = (0)
    while indexhigh != indexlow: 
        count += 1
        index = indexhigh//2
        hledam = boxes[index]
        #print(hledam)
        if hledam >= pokus:
            
            indexhigh = index
            
        else:
            indexlow = index
            
    total += count
print(len(boxes), total/len(boxes))
