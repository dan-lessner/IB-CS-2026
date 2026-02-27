# vstupy
nosnost_batohu = 50
pocet_predmetu = 10
hmotnosti = [5, 8, 12, 25, 45, 10, 13, 32, 4, 7]
ceny =      [1, 3, 6,   3,  20, 9, 20, 15, 6, 2]

#nastaveni
velikost_populace = 32
pocet_generaci = 20
delka_DNA = pocet_predmetu
pst_mutace = 1.0/delka_DNA ############ jak to bude zrat float? ocisti deleni

import random, copy
random.seed(0)

### pomocne funkce
def ss( v1, v2 ):
  return sum(a*b for a,b in zip(v1,v2))

def fitness( jedinec ):
  return ss(jedinec, ceny) if ss(jedinec, hmotnosti) <= nosnost_batohu else 0

def zkriz( tata, mama ):
    pozice = random.randrange(delka_DNA)
    return [ tata[:pozice] + mama[pozice:],
             mama[:pozice] + tata[pozice:] ]
    
def mutuj( mutant ):
    mutant = [ kodon if random.random() <= pst_mutace else (kodon+1)%2 
      for kodon in mutant ] 
    
	
    
### inicializace populace
populace = [ [ random.randrange(2) for _ in range(delka_DNA) ] for _ in range(velikost_populace) ]

### evoluce
for plonkova_promenna in range(pocet_generaci) :
    # selekce - "turnajova"
    random.shuffle(populace)
    prezivsi = [ (j0 if fitness(j0) >= fitness(j1) else j1)
	for j0, j1 in zip(populace[::2], populace[1::2]) ]
    # krizeni
    krizenci = sum( [ zkriz(r0, r1) for r0, r1 in zip(prezivsi[::2], prezivsi[1::2]) ], [])
    # slozeni dalsi generace        
    populace = prezivsi + krizenci
    # mutace
    list(map(mutuj, populace))
    
### vypis vysledku
vitez = max (populace, fitness) 
print ("vitez: ", vitez)
print ("fitness: ", fitness(vitez), ", cena: ", ss(vitez, ceny), ", hmotnost: ", ss(vitez, hmotnosti))
