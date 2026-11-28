# Weekrapport (VOORBEELD) — vrijdag 27 november 2026

> Dit is een proefrun op echte data van vandaag, om te laten zien hoe het zondagrapport eruitziet.
> Beide kanalen zijn net begonnen, dus de cijfers zijn nog heel klein. Kosten: 5 vidIQ-credits
> (saldo 712 → 707), Hermoso en TubeAlfred gratis.

## 1. Samenvatting
- **Precinct Archive:** 10 openbare video's, samen een handvol views. De eerste 9 waren korte
  delen van ~3 minuten ("Part 1 of 3"); vandaag kwam de eerste lange video (16:20) online, met 3 views
  in 6 uur.
- **The Defector Files:** 1 video, 1 uur oud. Nog geen data te beoordelen.
- **Belangrijkste inzicht:** er is nog te weinig data om iets over onderwerpen of hooks te
  concluderen. Wel valt aan de verpakking iets te verbeteren: de titels missen de **namen waarop
  mensen zoeken** (Crippen, Pitchfork).
- **Belangrijkste actie:** de bekende naam van de zaak in elke titel zetten (zie experiment A1).

## 2. Cijfers

### Precinct Archive (vidIQ, 30 okt – 27 nov; openbare telling via TubeAlfred op 27 nov)

| Video | Lengte | Openbare views | Engaged views | Gem. kijkduur | % bekeken |
|---|---|---|---|---|---|
| The 1910 Murder Case That Used New Technology to Catch a Killer | 16:20 | 3 | nog niet in Analytics | – | – |
| …Thumbprint Evidence…At The Old Bailey \| Part 3 of 3 | 3:35 | 1 | 1 | 28 s | 13,3% |
| …First DNA Fingerprint…Narborough Murders \| Part 2 of 3 | 2:39 | 1 | 1 | 4 s | 2,65% |
| 7 andere "Part x of 3"-video's | 2:20–3:37 | 0 | geen data | – | – |

Abonnees: 56 (openbaar). Nieuwe abonnees in de periode: 0.

### The Defector Files (Hermoso, 30 okt – 27 nov)

| Video | Lengte | Openbare views |
|---|---|---|
| 8 Nazi Saboteurs Landed in America. One Called the FBI. | 20:19 | 0 (1 uur oud) |

Verkeersbronnen zoals YouTube ze teruggeeft:

| Bron | Views | Kijkminuten |
|---|---|---|
| YT_SEARCH | 10 | 42 |
| YT_OTHER_PAGE | 1 | 0 |
| NO_LINK_OTHER | 0 | 0 |

YouTube gaf geen rijen terug voor topVideos en voor de zoektermen (trafficSourceDetail). Dat
betekent: ontbrekende data, niet nul views.

## 3. Wat werkte / wat niet

| Bevinding | Bewijs | Zekerheid |
|---|---|---|
| De oude reeks van 3-minuten-delen trok vrijwel niemand | 9 video's, samen 2 views in 9–11 dagen | middel |
| Wie op een deel klikte, haakte snel af | 4 s en 28 s gemiddelde kijkduur (1 kijker per video) | **laag** (n=1) |
| De oude titelformule is te lang en te gelijkvormig | alle 9 titels: "Why The … Became A Turning Point In The … \| Part N of 3", 75–95 tekens, afgekapt op mobiel | hoog (verpakking, geen prestatie) |
| De nieuwe lange titel noemt de zaak niet | "The 1910 Murder Case…" zonder "Crippen" | hoog (verpakking) |
| De Defector-titel is sterk: concreet getal plus een twist | "8 Nazi Saboteurs… One Called the FBI." | middel (nog geen data) |

## 4. Uitgebreid advies

**Precinct Archive**
- **Titels:** begin met de naam die mensen in de zoekbalk typen: *"Dr Crippen: The Murderer Caught
  by Wireless Telegraph (1910)"* in plaats van *"The 1910 Murder Case That Used New Technology…"*.
  Nieuwe kanalen krijgen bijna al hun views via zoeken, en "Dr Crippen" wordt veel gezocht,
  "1910 murder case" nauwelijks.
- **Oude delen:** de 9 korte video's trekken het kanaalgemiddelde omlaag en passen niet meer bij het
  20-minutenformaat. Ze in een afspeellijst zetten of verbergen kan alleen jij beslissen (zie 7).
- **Lengte:** de eerste lange video duurt 16:20; het doel is ~20 min. Prima voor nu, maar houd het
  dagelijkse script op ~3.000 woorden.
- **Thumbnail:** één gezicht of object, maximaal 3 woorden, en geen tekst die de titel herhaalt
  (`/yt-package` controleert dat).

**The Defector Files**
- Titelformule "getal + onderwerp + twist" vasthouden; volgende week beoordelen op CTR zodra
  Studio-cijfers binnen zijn.
- Op Hermoso-data mag ik geen eigen afgeleide cijfers maken (percentages, gemiddelden, rangorde);
  dat zijn de gebruiksvoorwaarden van de YouTube-API. Voor dit kanaal laat ik de cijfers daarom
  zien zoals YouTube ze geeft, en baseer ik advies vooral op de inhoud: titels, scripts en reacties.

**Beide kanalen, komende 30 dagen**
- Elke dag een video, dus over 4 weken zijn er ~28 lange video's per kanaal. Pas dan zijn
  patronen in onderwerpen en hooks echt te zien. Tot die tijd stuur ik vooral op **verpakking
  (titels, thumbnails) en vindbaarheid**, niet op inhoudelijke koerswijzigingen.
- Maak van elke zaak een afspeellijst per thema ("Forensic firsts", "WWII spies"): dat helpt bij
  doorkijken en sessieduur.

## 5. Wat ik zelf heb aangepast
In deze proefrun heb ik twee dingen in het draaiboek `channel/weekly-review.md` gezet:
1. **Minimale data-regel:** zolang een video minder dan ~100 views heeft, past de weekreview geen
   inhoudelijke regels aan op basis van prestaties, alleen verpakking en productieproblemen.
2. **Hermoso-cijfers** worden getoond zoals YouTube ze geeft, zonder eigen percentages of
   rangordes (API-voorwaarden).

In een echte zondagrun zou ik ook dit doen (nu niet uitgevoerd, het is een voorbeeld):
- in `channel/daily-run.md` stap 7: "de titel bevat de naam waarop de zaak bekendstaat
  (persoon of plaats)";
- `channel/playbook.md` aanmaken met de regel "geen 'Part x of 3'-titels; namen voorop".

## 6. Experimenten volgende week
- **A1 (Precinct):** alle 7 titels beginnen met de bekende naam van de zaak. Meten: impressies en
  views uit zoeken t.o.v. de Crippen-video.
- **A2 (Precinct):** de eerste 30 seconden openen met de ontdekking of het misdrijf zelf, niet met
  de context. Meten: % bekeken na 30 s.
- **D1 (Defector):** 4 van de 7 titels met getal + twist, 3 met naam + vraag. Meten: CTR per groep.

## 7. Jouw akkoord nodig
1. Mogen de 9 korte "Part x of 3"-video's van Precinct Archive in een afspeellijst, of wil je ze
   verbergen (privé)? Ik raad een afspeellijst aan en ze laten staan.
2. Mag ik de titel van de Crippen-video veranderen in *"Dr Crippen: The Murderer Caught by
   Wireless Telegraph (1910)"*? (Een wijziging aan een live video, dus jouw beslissing.)

## 8. Kosten
vidIQ: 5 credits (1 analyse-oproep), saldo nu 707; reset 16 december. Hermoso en TubeAlfred:
gratis.
