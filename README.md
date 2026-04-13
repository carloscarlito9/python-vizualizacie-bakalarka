# Porovnanie vizualizačných nástrojov v Pythone

Projekt sa zameriava na praktické porovnanie knižníc Matplotlib, Seaborn, Plotly a GeoPandas pri riešení reálnych analytických úloh.

Tento repozitár obsahuje praktickú časť bakalárskej práce zameranej na porovnanie vybraných vizualizačných knižníc v jazyku Python pri práci s časovými radmi, korelačnými a geografickými dátami.

## Cieľ projektu

Cieľom práce je porovnať vybrané knižnice z hľadiska:
- zložitosti implementácie,
- rýchlosti vykonania,
- vizuálnej kvality výstupov,
- interaktivity,
- vhodnosti pre konkrétny typ dát.

## Použité knižnice

- Matplotlib
- Seaborn
- Plotly
- GeoPandas

## Použité dáta

Projekt pracuje s tromi hlavnými typmi dát:
- časové rady (GHCN),
- korelačné dáta (World Bank WDI),
- geografické dáta (OSM).

## Štruktúra projektu

- `notebooks/` – Jupyter notebooky s experimentmi a vizualizáciami
- `src/` – pomocné moduly na načítanie, spracovanie a vizualizáciu dát
- `configs/` – konfiguračné súbory experimentov
- `assets/` – doplnkové súbory a podklady
- `outputs/` – vybrané výstupy, metriky a výsledné súbory
- `_shared/` – zdieľané šablóny a pomocné notebooky

## Použitie projektu

Projekt je organizovaný vo forme Jupyter notebookov a pomocných Python modulov. Jednotlivé časti je možné spúšťať samostatne podľa typu dát:

- `01_time_series` – časové rady
- `02_correlations` – korelačné dáta
- `03_geo` – geografické dáta

## Poznámka k dátam

Veľké surové datasety nie sú súčasťou repozitára. Repo obsahuje najmä notebooky, zdrojové kódy, konfigurácie a vybrané výstupy potrebné na reprodukovanie experimentov.

## Hlavné časti analýzy

- porovnanie knižníc pri tvorbe vizualizácií časových radov,
- porovnanie knižníc pri korelačných a multivariačných dátach,
- porovnanie nástrojov pri geografických údajoch,
- zber metrík a vyhodnotenie silných a slabých stránok jednotlivých riešení.

## Výsledok

Výsledkom projektu je súbor odporúčaní, ktoré pomáhajú určiť, ktorá knižnica je vhodná pre konkrétny analytický problém a typ dát.

## Autor

Karol Antal
