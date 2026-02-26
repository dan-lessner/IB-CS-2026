# SPECIFIKACE: Generování ideální trasy na čtvercové síti pro závodní auta

## Shrnutí

Cíl:
Z binární mřížky (trať / mimo trať)
→ najít platnou cestu
→ iterativně ji „napnout“ (zkrátit)
→ převést ji na sekvenci uzlů
→ generovat z ní pokyny pro `PickMove`

---

# 2. FÁZE A – NALEZENÍ PRIMÁRNÍ CESTY

Cíl: získat libovolnou validní cestu mezi `start` a `goal`.
použij BFS (algoritmus vlny)
  * každý bod je sousední (8-směrná sousednost povolena)
  * všechny body jsou na trati
výstup: seznam vertexů, kudy je potřeba projít; optimalita zde není nutná.

---

# 3. FÁZE B – ITERATIVNÍ NAPÍNÁNÍ NITKY

Cíl: zkrátit cestu, se zachováním průchodnosti.

## 3.1 Princip

Pro danou cestu:

Pro každý bod `i`:

* hledáme nejvzdálenější bod `j > i`,
* takový, že úsečka mezi `Pi` a `Pj`:
  * vede pouze po trati
  * je validní podle existující herní rutiny (potřebná rutina již existuje někde v codebase, můžeš ji zkusit použít)
* kontroluje, zda auto nevyjede mimo trať
* používá diskretizaci po mřížce

---

## 3.2 Algoritmus napínání

Iterativní průchod:

```
i = 0
while i < len(path) - 1:
    najdi největší j > i takové, že segment(Pi, Pj) je validní
    přidej Pj do nové cesty
    i = j
```

Vlastnosti:

* greedy strategie
* každý bod zpracován omezeně krát
* časová složitost v praxi ~ O(n)

Výstup:

```
tight_path = [Q0, Q1, ..., Qm]
```

Toto je lomená čára (uzly pouze v síti).

---

# 4. DISKRETIZACE ÚSEČKY

Použije se Bresenhamův algoritmus:

* generuje celočíselné body
* aproximuje úsečku mezi dvěma uzly
* výstupem je sekvence mřížkových bodů

Používá se:

* při validaci segmentu
* při generování konkrétních průjezdních bodů

---

# 5. FÁZE C – GENEROVÁNÍ PRŮJEZDNÝCH BODŮ

Vstup:

```
tight_path
```

Výstup:

```
waypoints = [W0, W1, ..., Wk]
```

Pro každý segment:

```
Qi → Qi+1
```

* aplikuj Bresenham
* přidej mezibody
* spoj segmenty do jedné sekvence

Poznámka:

* duplicitní body odstranit

---

# 6. DVĚ VARIANTY POHYBU

## Varianta 1 – Rychlost max 1

* Δx ∈ {-1,0,1}
* Δy ∈ {-1,0,1}
* |Δx| ≤ 1
* |Δy| ≤ 1

Každý krok je jeden uzel sousední.

Používá se přímo sekvence z Bresenham.

---

## Varianta 2 – Akcelerace

Auto má:

```
velocity = (vx, vy)
```

Omezení:

* změna rychlosti po složkách:

  * Δvx ∈ {-1,0,1}
  * Δvy ∈ {-1,0,1}

Algoritmus:

* cílový bod = další waypoint
* vyber takovou akceleraci,
  aby nová pozice byla co nejblíže cílovému waypointu
* respektuj omezení herního API

---

# 7. INTEGRACE S PickMove

API:

```
PickMove(possible_moves)
```

Kde:

* `possible_moves` = seznam až 9 cílových pozic
  (dáno aktuální rychlostí a akcelerací)

Algoritmus:

1. vezmi první bod z `waypoints`
2. z `possible_moves` vyber ten,
   který odpovídá cílovému waypointu
3. pokud není přesná shoda:

   * vyber ten, který minimalizuje vzdálenost
4. po dosažení waypointu:

   * odeber jej ze seznamu

---

# 8. VÝSTUP CELÉHO PLÁNOVAČE

Finální výstup plánování:

Používá se opakovaně v `PickMove`.

---

# 9. VLASTNOSTI SYSTÉMU

* pracuje výhradně s celočíselnou mřížkou
* respektuje fyziku hry
* využívá existující validaci segmentu
* odděluje:

  * nalezení cesty
  * její optimalizaci
  * převod na řízení auta
