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
2. Stažení integrace pomocí HACS
    1. Spustit HACS, případně [nainstalovat](https://hacs.xyz/), pokud ještě nemáte
    2. Vlastní repozitáře
    3. Přidat tento repozitář - https://github.com/jakubcermak/homeassistant-prazska-integrovana-doprava , kategorie Integrace
    4. Měl by se zobrazit tento nový repozitář v HACS, klikněte na něj a dejte "stáhnout"
3. Restart HA
4. V Nastavení - Integrace zvolte Přidat integraci a vyberte "Pražská  Integrovaná Doprava"
5. Do pole API klíč vložte API klíč z kroku 1 a potvrďte.
6. Integrace PID by se měla objevit v seznamu zařízení: 

    ![](img/pid_tile.png)
7. V nastavení integrace zadejte jednu až 10 zastávek, které chcete sledovat. POZOR - názvy zastávek je třeba zadat naprosto přesně, použijte např IDOS

    ![](img/options.png)
8. Potvrdit a pokud jste zadali všechny zastávky správně, po cca minutě by se měly entity naplnit údaji o odjezdech ze zvolené zastávky.

Užívejte s radostí.

## Troubleshooting
Pokud něco nefunguje, nejdříve se podívejte do logu HA. Zkontrolujte, jestli je API klíč zadán správně. Zkontrolujde, že máte připojení k internetu. Zkontrolujde přesné názvy zastávek. Pokud si ani tak nevíte rady, založte prosím issue na githubu, zkusím se tomu pověnovat.


Pomoc je vždy vítána, pokud chcete něco zlepšít nebo opravit, prosím založte pull request.

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
## Příklad nastavení Lovelace s vlastní grafikou
Další příklad nastavení karty Markdown, která  zobrazí a naformátuje všech 5 odjezdů, zbývající čas, linku a směr.
![](img/markdown.png)
```
type: markdown
content: >
  {% macro set_color(diff) %}
  {%- if diff > 360 -%}
  {{ '<font color=limegreen>' }}
  {%- elif diff > 180 -%}
  {{ '<font color=orange>' }}
  {%- elif diff > 0 -%}
  {{ '<font color=red>' }}
  {%- else -%}
  {{ '<font color=darkcyan>' }}
  {%- endif -%}
  {% endmacro %}

  {%- set c2 = "</font>" -%}
  ---
  {% for PIDodjezd in
  expand('sensor.pid_odjezd_1','sensor.pid_odjezd_2','sensor.pid_odjezd_3','sensor.pid_odjezd_4','sensor.pid_odjezd_5') | reverse | list %}

  {% set dt = PIDodjezd.state | as_datetime %}
  {% set diff = (dt - now()).total_seconds() %}
  {% set hod = diff | timestamp_custom('%H', false) | int %}
  {% set min = diff | timestamp_custom('%M', false) | int %}
  {% set c1 = set_color(diff) %}
  {% set lo = '' if hod > 0 else '<' %}

  {% if diff < 0 %}
  # Už asi {{c1}}odjel{{c2}}
  {% else %}
  # Za {% if hod > 0 %} {{c1}} {% if 2 > hod %} {{hod}}{{c2}} hodinu {% elif 5 >  hod > 1 %} {{hod}}{{c2}} hodiny{% else %} {{hod}}{{c2}} hodin{% endif %} {% endif %} {{c1}}{% if min < 1 and hod < 1  %} {{lo}} 1 {{c2}}minutu{% elif 2 > min > 0 %} {{min}}{{c2}} minutu {% elif 5 > min > 1 %} {{min}}{{c2}} minuty{% else %} {{min}}{{c2}} minut{% endif %}</font> {% endif %}

  ## {{ as_timestamp(state_attr(PIDodjezd.entity_id, 'predicted')) |
  timestamp_custom('%H:%M') }} - linka {{ state_attr(PIDodjezd.entity_id,
  'linenumber') }}

  ### Směr {{ state_attr(PIDodjezd.entity_id, 'stop_to') }}

  ---
  {% endfor %}
title: PID Odjezdy

```
