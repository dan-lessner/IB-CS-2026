# spec_auto.md - skriptovane ovladani aut (faze 2)

## Cil
- Kazde auto je ovladano bud mysi, nebo skriptem.
- Skriptovane auto se jmenuje podle hodnoty vracene metodou GetName().
- Defaultni beh bez parametru: pouzit vsechny skripty ve slozce Scripts (max 10).

## Slozka se skripty
- Slozka: `Scripts` v koreni repozitare.
- Nazev souboru: jmeno studenta, napr. `Adam.py`.
- Nacteni: vsechny soubory `*.py` v `Scripts`, serazene podle nazvu (krome template.py).
- V kazdem souboru musi byt trida `Auto`, ktera dedi z `AutoAuto`.

## Base class `AutoAuto`
- Umisteni: nova trida v simulaci.
- Metody:
  - `GetName(self) -> str`
    - Vraci jmeno programovaneho auta.
    - Pokud vrati prazdny retezec, pouzije se nazev souboru bez pripony.
  - `PickMove(self, world, targets, validity) -> Vertex`
    - `targets` je seznam vrcholu (po rade pro ax=-1..1, ay=-1..1). `validity` je 9-prvkovy seznam boolu, kde `True` znaci dostupny vertex. Pokud doslo ke kolizi, predava se jediny vertex (soucasna poloha) a je oznacen jako validni.
    - Metoda musi vratit jeden z prvku `allowed_moves`.
    - Pokud vrati `None`, pouzije se stredova volba (akcelerace 0,0) a tah pokracuje.
    - Pokud vrati jinou hodnotu, auto zvoli cekani na miste (zadna zmena rychlosti).
  - dosavadni ovladani mysi a souvisejici logika se presune do tridy ManualAuto, ktera taktez dedi od AutoAuto

## World state (objekt pro skripty)
- Objekt `WorldState` (jen data, bez logiky):
  - `road`: 2D pole bool (bitove pole trate).
  - `start_vertices`: seznam Vertex na startu.
  - `finish_vertices`: seznam Vertex na cilove care.
  - `cars`: seznam objektu `CarInfo`:
    - `id`, `name`, `position` (Vertex), `velocity` (Vector2i).
- WorldState se predava do `PickMove()` kazdy tick.

## Vyber ovladani
- GUI: u kazdeho hrace cyklovani typu (Mouse / Script) + vyber skriptu.
- Konzole: parametr `--controllers` s carkami oddelenym seznamem:
  - hodnoty: `mouse` nebo nazev skriptu (bez pripony)
  - priklad: `--controllers mouse,Adam,Bara`
  - pocet hracu = delka seznamu
- Pokud `--controllers` chybi a v `Scripts` existuji skripty:
  - pouziji se prvni 10 podle nazvu
  - pocet hracu = pocet pouzitych skriptu
- Pokud `--controllers` chybi a `Scripts` je prazdna:
  - pouzije se standardni pocet hracu z parametru hry
  - vsichni hraci jsou Mouse

## Volani skriptu
- Skript se vola kazdy tick pouze pro auto, ktere je na tahu.
- Seznam `allowed_moves` generuje hra (stejne jako pro klikaci ovladani).

## Merici rezim vykonu
- Zapinatelne z konzole i GUI.
- Po zapnuti se meri cas straveny ve volani `PickMove()` pro kazde auto.
- Na konci hry:
  - vypis do konzole (souhrn za kazde auto)
  - log do souboru v koreni: `performance_log.csv`
