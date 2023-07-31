# Integrace jízdních řádů Pražské integrované dopravy (PID)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

(English translation below)

Cílem této integrace je možnost zobrazení jízdních řádů PID ve vašem Home Assistantovi - ať už pro zobrazení na dashboardu, na nějakém externím displeji nebo případně k vytvoření automatizací.

Doplněk pracuje velmi jednoduše - v nastavení si zadáte, které zastávky chcete sledovat, načež integrace periodicky stahuje data z rozhraní PIDu a vytvoří 5 entit, které odpovídají příštím pěti spojům z daných zastávek. 

Příkladem budiž:

![lovelace ukázka](img/lovelace.png)

## Postup instalace 
1. Je třeba si vygenerovat vlastní API klíč z webu Golemio provozovaného Prahou.
    * Nejdřív se zaregistrujte na https://api.golemio.cz/api-keys/auth/sign-in
    * Následně na stránce https://api.golemio.cz/api-keys/dashboard klikněte na VYGENEROVAT NOVÝ a vygenerovaný klíč si někam zkopírujte, bude se hodit vzápětí.
2. 

## Vzorový příklad nastavení Lovelace
Tento vzorový příklad nastavení karty Entity zobrazí všech 5 odjezdů a u každého detail a plánovaný čas příjezdu.
```
type: entities
entities:
  - sensor.pid_odjezd_1
  - type: attribute
    entity: sensor.pid_odjezd_1
    name: Z
    attribute: details
  - type: attribute
    entity: sensor.pid_odjezd_1
    name: Jízdní řád
    attribute: scheduled
  - type: attribute
    entity: sensor.pid_odjezd_1
    name: Odhad
    attribute: predicted
  - sensor.pid_odjezd_2
  - type: attribute
    entity: sensor.pid_odjezd_2
    name: Z
    attribute: details
  - type: attribute
    entity: sensor.pid_odjezd_2
    name: Jízdní řád
    attribute: scheduled
  - sensor.pid_odjezd_3
  - type: attribute
    entity: sensor.pid_odjezd_3
    name: Z
    attribute: details
  - type: attribute
    entity: sensor.pid_odjezd_3
    name: Jízdní řád
    attribute: scheduled
  - sensor.pid_odjezd_4
  - type: attribute
    entity: sensor.pid_odjezd_4
    name: Z
    attribute: details
  - type: attribute
    entity: sensor.pid_odjezd_4
    name: Jízdní řád
    attribute: scheduled
  - sensor.pid_odjezd_5
  - type: attribute
    entity: sensor.pid_odjezd_5
    name: Z
    attribute: details
  - type: attribute
    entity: sensor.pid_odjezd_5
    name: Jízdní řád
    attribute: scheduled
title: PID Odjezdy

```