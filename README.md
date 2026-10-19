# D9 Streetball Stats

Stats fra vores pickup-kampe: box scores, en pivot til selv at vende og dreje tallene, rekorder og makkerpar.

**Live:** https://jacquesbie.github.io/d9-streetball/

Én selvstændig side (`index.html`) med data bagt ind. Bygges fra HoopStats-dashboardet med
`python3 ~/HoopStatsLocal/dashboard/build_site.py` og udgives med `./deploy.sh`.

**Forsiden** har en knap til fantasy-spillet øverst og **PER, AST/TO og TS%** sidst i box score og i pivotens "Tal".
Det ligger i `forside.js`, fordi `build_site.py` skriver `index.html` forfra; `./deploy.sh` sætter linket til `forside.js`
ind igen, hvis det mangler. PER er Hollingers model tilpasset
jeres kampe (15 er snittet i hver kamp), TS% regnes på NBA-skalaen ud fra 2'ere og skud indenfor, og AST/TO vises, når
turnovers registreres (feltet `TOV`).

**Fantasy:** https://jacquesbie.github.io/d9-streetball/fantasy/ har roto 8-cat (FG%, 2'ere, PTS, REB, AST, STL, BLK og TO,
hvor færrest turnovers vinder) og en player rater med z-score pr. kategori og samlet. Der draftes ikke, så hver spiller er
sit eget hold. Fra start vises 3v3 og 4v4 med tal pr. kamp. Perioden kan justeres, og visningen kan deles som link. Siden henter tallene fra `index.html`, hver gang den
åbnes, så den følger med efter `./deploy.sh`. Steals, blocks og turnovers kommer med af sig selv, når `player_games` får
felterne `STL`, `BLK` og `TOV`.

**Highlights:** `highlights/make_highlights.py` klipper en video på højst 5 minutter ud af kampoptagelserne, med alle
spillere mindst én gang. Se [highlights/README.md](highlights/README.md).

Holdpoint, slutstillinger og minutter er sikre. Spillerpoint og rebounds er automatisk bedste bud fra én kameravinkel.
Steals, blocks og turnovers tælles ikke.
