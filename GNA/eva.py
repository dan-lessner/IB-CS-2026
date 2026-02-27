# I do not know anymore what this is

import random, copy
from functools import reduce

sample_chrm = list(range(1,10)) # a feasible solution
init_population = [ ] # an empty list
population_size = 5

for i in range( population_size ):
    new_chrm = copy.copy( sample_chrm )
    random.shuffle( new_chrm)
    init_population.append( new_chrm)


chrm = [4, 1, 5, 6, 9, 2, 3, 7, 8]
import operator
fitness_list = [6.0, 9.0, 4.0, 3.0, 5.0, 8.0, 3.0, 6.0, 3.0,3.0]
fitness_sum = reduce( operator.add, fitness_list)

prob_list = map((lambda x: x/fitness_sum),fitness_list)

cum_value = 0
cum_prob_list = []
for prob in prob_list:
    cum_prob_list.append( cum_value + prob )
    cum_value += prob

cum_prob_list[-1] = 1.0

import random
selected = []
size = 100
for i in range(size):
    rn = random.random()
    for j, cum_prob in enumerate(cum_prob_list):
        if rn<= cum_prob:
            selected.append( j)
            break


