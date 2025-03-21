import random
array = []
values_number = int(input("Number of values in the list "))
list_range = int(input("How many digits you want to create? (The number you put in will act as an exponential to number 10) "))

for i in range(0, values_number):
    n = random.randint(1, 10**list_range)
    array.append(n)

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