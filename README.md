# D9 Streetball Stats

Stats fra vores pickup-kampe: box scores, en pivot til selv at vende og dreje tallene, rekorder og makkerpar.

**Live:** https://jacquesbie.github.io/d9-streetball/

Én selvstændig side (`index.html`) med data bagt ind. Bygges fra HoopStats-dashboardet med
`python3 ~/HoopStatsLocal/dashboard/build_site.py` og udgives med `./deploy.sh`.

**Highlights:** `highlights/make_highlights.py` klipper en video på højst 5 minutter ud af kampoptagelserne, med alle
spillere mindst én gang. Se [highlights/README.md](highlights/README.md).

Holdpoint, slutstillinger og minutter er sikre. Spillerpoint og rebounds er automatisk bedste bud fra én kameravinkel.
Steals, blocks og turnovers tælles ikke.
