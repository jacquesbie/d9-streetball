# D9 Streetball Stats

Stats fra vores pickup-kampe: box scores, Nemesis-tabellen, en pivot til selv at vende og dreje tallene, rekorder og makkerpar.

**Live:** https://jacquesbie.github.io/d9-streetball/

Én selvstændig side (`index.html`) med data bagt ind. Bygges fra HoopStats-dashboardet med
`python3 ~/HoopStatsLocal/dashboard/build_site.py` og udgives med `./deploy.sh`.

**Forsiden** har knapper til holdgeneratoren og fantasy-spillet øverst. Den ligger i `forside.js`, fordi `build_site.py` skriver `index.html` forfra; `./deploy.sh` sætter linket til `forside.js?v=...` ind igen, hvis det mangler (ret `?v=`, når filen ændres). **PER, AST/TO og TS%** (sidst i box score og i pivotens "Tal") er siden 6. nov. en del af forsiden selv, så artifacten også har dem. PER er Hollingers model tilpasset D9 (15 er snittet i hver kamp), TS% regnes på NBA-skalaen ud fra 2'ere og skud indenfor, og AST/TO vises, når turnovers registreres (feltet `TOV`).

**Nemesis-tabellen:** hvem dækker hvem. Den, der står over for en spiller ved check ball (i midten lige uden for toppen af
den sorte bue), er hans direkte modstander resten af sekvensen, til bolden er død igen. Tabellen viser hver spillers
nemesis og yndlingsmodstander og pr. modstander point, skud og point pr. 10 min i angreb og forsvar, sammenlignet med
modstanderens snit mod andre. Data er `matchups` i `index.html` (én række pr. kamp, angriber og forsvarer), lavet af
`~/HoopStatsLocal/review/matchups.py`. Parrene er tjekket på video for 12. okt. og 17. okt.; 28. sep. er ikke med
(ens sorte T-shirts, og checket sker i billedets kant).

**Fantasy:** https://jacquesbie.github.io/d9-streetball/fantasy/ har roto 8-cat (FG%, 2'ere, PTS, REB, AST, STL, BLK og TO,
hvor færrest turnovers vinder) og en player rater med z-score pr. kategori og samlet. Der draftes ikke, så hver spiller er
sit eget hold. Fra start vises 3v3 og 4v4 med tal pr. kamp. Perioden kan justeres, og visningen kan deles som link. Siden henter tallene fra `index.html`, hver gang den
åbnes, så den følger med efter `./deploy.sh`. Steals, blocks og turnovers kommer med af sig selv, når `player_games` får
felterne `STL`, `BLK` og `TOV`.

**Holdgenerator:** https://jacquesbie.github.io/d9-streetball/hold/ laver to hold af dem, der er mødt op: tilfældigt eller
så lige som muligt efter Elo pr. kamp. Man trykker på spillerne eller skriver navne (nye spillere regnes som 1500; Bie,
Schjødt og Jonas finder Jacob, Thomas og Nicehair). Lige hold prøver alle delinger (op til 20 spillere, ellers søgning) og
trækker lod mellem dem, hvis vinderchance højst er 2 procentpoint fra den mest lige; tryk igen for et nyt bud. Hvert bud viser
vinderchancen (win probability) for begge hold: Elo-formlen med forskellen i holdenes snit ganget med β, som siden selv
fitter på de spillede kampe (hver spilledag forudsagt ud fra de andre; 12. nov.: β = 2,75, favoritten vandt 12 af 18).
Siden henter tallene fra `index.html`, hver gang den åbnes, ligesom fantasy. `eloPerGame()` i `hold/index.html` er en tvilling
af `eloRun()` i dashboardets `index.html`, så ret begge, hvis Elo-reglen ændres. Valget huskes i browseren (localStorage).

**Elo pr. kamp** (fra 12. nov.): hver kamp giver det sædvanlige Elo-skridt, 32 × M × (resultat − forventet) × andel af
spilletiden, og ratingen er 1500 + 10 × gennemsnittet af skridtene pr. kamp (mindst 3 i nævneren). Antallet af kampe trækker
derfor ikke op. Forventet regnes ud fra holdenes Elo pr. kamp før kampen.

**Highlights:** `highlights/make_highlights.py` klipper en video på højst 5 minutter ud af kampoptagelserne, med alle
spillere mindst én gang. Se [highlights/README.md](highlights/README.md).

Slutstillinger og minutter er sikre. Fra 28. sep. er hver assist tjekket i videoen, og det samme gælder hver kurv (undtagen
28. sep. kamp 3, hvor kun assists er tjekket); 1 eller 2 er målt mod den sorte 2'er-linje. Assist (fra 22. okt.): en holdkammerats aflevering, hvorefter scoreren skyder inden for ca. 4½ s; drib og
drive er tilladt, og en aflevering lige efter check ball tæller også (før: ca. 3 s og et par drib). Rebounds og bom er automatisk bedste bud fra én kameravinkel. Steals, blocks, turnovers og screen-assists
(`STL`, `BLK`, `TOV`, `SAST`) er talt i videoen for 28. sep. kamp 1–2, 12. okt. og 17. okt.; andre kampe har `null`.
