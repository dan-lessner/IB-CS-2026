import random

list_range = int(input("Number of values in the list "))
array = random.sample(range(1, list_range), (list_range - 1))

def quicksort(array):
    if len(array) <= 1:
        return array
    left = []
    right =[]
    middle = []
    pivot = array[len(array) // 2] 
    for number in array:
        if number < pivot:
            left.append(number)
        elif number == pivot:
            middle.append(number)
        else:
            right.append(number)

    return quicksort(left) + middle + quicksort(right)

sorted_array = quicksort(array)
print(sorted_array)