# Systém na grafickú vizualizáciu optimalizačných algoritmov inšpirovaných prírodou pri riešení problému obchodného cestujúceho

## Popis projektu
Tento projekt implementuje systém na vizualizáciu metaheuristickych algoritmov pri riešení problému obchodného cestujuceho (TSP - Travelling Salesman Problem). Systém je navrhnutý na experimentálne porovnávanie algoritmov a didaktické využitie pri výučbe umelej inteligencie, evolučných algoritmov a rojovej inteligencie.

Aplikácia umožnuje nastavovať vstupné parametre algoritmov, definovať rozloženie vrcholov problému obchodného cestujúceho, spúštať simulácie a vizualizovať riešenia a priebeh algoritmov. Cieľom projektu je analyzovať kvalitu nájdených riešení, konvergenciu a výpočtové charakteristiky jednotlivých metaheuristických prístupov za rovnakých experimentálnych podmienok..

V projekte sú implementované naledujúce algoritmy:

- Genetic Algorithm (GA)

- Ant Colony Optimizer (ACO)

- Artificial Bee Colony (ABC)

- Particle Swarm Optimization (PSO)

Každý algoritmus je implementovaný ako samostatný modul, čo umožnuje jeho samostatné testovanie a pracovanie s ním v rámci jedného experimentálneho prostredia.

## Štruktúra projektu

Projekt pozostáva z nasledujúcich hlavných súborov:

- BP2_TSP.py – hlavný riadiaci modul zabezpečujúci konfiguráciu parametrov, riadenie simulácie a vizualizáciu výsledkov

- BP2_GA.py – implementácia Genetic algorithm

- BP2_ACO.py – implementácia Ant Colony Optimizer

- BP2_ABC.py – implementácia Artificial Bee Colony

- BP2_PSO.py – implementácia Particle Swarom Optimization

Súbor BP2_TSP.py integruje všetky algoritmické moduly do jedného uceleného systému a predstavuje centrálnu riadiacu jednotku aplikácie.

## Technické požiadavky

Aplikácia je programovaná v jazyku Python 3.13.

Na spustenie aplikácie je potrebné mať nainštalované nasledujúce knižnice:

- random
- math
- time
- matplotlib
- tkinter
- customtkinter
- pillow (PIL)

Externé knižnice je možné nainštalovať pomocou správcu balíkov pip.

## Spustenie aplikácie 

Aplikáciu je možné spustiť hlavným súborom:

```
python BP2_TSP.py
```

Grafické používatelské rozhranie umožnuje nastavovanie paramtrov pre jednotlivé algoritmy, definovanie problému obchodného cestujúceho, spúštanie simulácií a vizualizáciu výsledkov simulácií.

## Konfigurácia 

Každý algoritmus umožnuje nastavenie vlastných hyperparametrov, ako sú počet iterácií, velkosť populácie a riadiace parametre špecifické pre každú metódu. Všetky algoritmy pracujú s rovnakým vstupným problémom a definíciou fitness funkcie, čím je zabezpečené objektívne porovnávanie metód.

## Výstupy experimentov

Počas behu simulácie systém zaznamenáva:

- vývoj hodnoty fitness v priebehu iterácií 

- najlepšie nájdené fitness

- itaráciu, v ktorej bolo dosiahnuté najlepšie riešenie pre jednotlivé algoritmy

Tieto parametre zabezpečujú kompletnú alnalýzu konvergencie a porovnanie výkonnosti jednotlivých algoritmov.

## Didaktické využitie

Modulárna architektúra projektu umožnuje jeho využitie pri výučbe evolučných algoritmov, umelej inteligencii a rojovej inteligencie. Študenti môžu sledovať implementáciu algoritmov a správanie algoritmov pri zmene vstupných parametrov, čím dosiahnu znalosť o jednotlových hyperparamtroch vstupujúcich do algorimov.
