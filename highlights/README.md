# D9 highlights

Laver en highlight-video på højst 5 minutter ud fra kampoptagelserne. Alle spillere fra stats-siden er med mindst én gang.
Videoen starter med et introkort og har et kort for hver session. Hvert klip har spillerens navn og kurven
(fx "2'er · 28. sep · Kamp 1"), og til sidst kommer en rulletekst med alle navnene.

Scriptet kører på din egen computer, hvor videoerne og `~/HoopStatsLocal` ligger.

## Det skal du bruge

- `ffmpeg` og `ffprobe`: `brew install ffmpeg`
- Python 3.9 eller nyere (den der følger med macOS, er fin). Ingen pakker kræves. Hvis din ffmpeg mangler
  `drawtext`-filteret, skriver scriptet navnene med Pillow i stedet: `python3 -m pip install --user pillow`

## Tre trin

Kør kommandoerne fra mappen `d9-streetball`.

```sh
# 1. Find kurvene (tidspunkt + spiller) i HoopStats-dataene og skriv dem til highlights/klip.csv
python3 highlights/make_highlights.py importer ~/HoopStatsLocal --videomappe /Volumes/GoPro

# 2. Se hvilke klip der bliver valgt, og tjek at alle 12 spillere er med
python3 highlights/make_highlights.py plan

# 3. Lav en hurtig prøve (960x540), og derefter den rigtige video
python3 highlights/make_highlights.py lav --hurtig
python3 highlights/make_highlights.py lav
```

Videoen havner i `highlights/ud/D9_highlights.mp4`. `ud/` og `klip.csv` er udelukket i `.gitignore`, så `./deploy.sh` ikke
lægger dem på GitHub.

`--videomappe` er kun nødvendig, hvis videoerne ikke ligger i `~/HoopStatsLocal`. Den kan gentages for flere mapper.

## Sådan vælges klippene

- Hver spiller får først sit bedste klip. Spillere med få kurve vælger først.
- Resten af tiden fyldes med de bedste klip. 2'ere og vinderholdets sidste kurv i en færdigspillet kamp tæller mest.
  Klippene spredes, så den samme spiller eller kamp ikke fylder det hele.
- Hvert klip er 5,5 sekunder før kurven og 2,5 sekunder efter (kan ændres med `--foer` og `--efter`).
- Samlet længde inklusive kort holdes under `--max` (standard 300 sekunder).
- `lav` stopper, hvis en spiller ikke har et brugbart klip. Brug `--tillad-mangler`, hvis du vil lave videoen alligevel.

## Hvad importen kan læse

`importer` gennemsøger JSON-, JSONL- og CSV-filer i mappen efter poster med et tidspunkt, en spiller og et tegn på,
at skuddet gik i (fx `made: true`, `result: ramt`, `type: shot_made`, eller kun et antal point). Bomskud sorteres fra.

- Tidspunktet må være sekunder, `m:ss` eller et billednummer. Er det et billednummer, bruges fps fra dataene eller videoen.
- Videoen hentes fra posten, fra en forælder- eller meta-blok, eller fra den eneste video i samme mappe.
  GoPro-kapitler (`GX010045.MP4`, `GX020045.MP4`, …) følges automatisk.
- Kampen genkendes ud fra `game_id`, eller ud fra dato og kampnummer i stien.
- Ligger samme kamp i flere filer, bruges den nyeste (fx den rettede version). Brug `--alle-filer` for at få alle med.
- Navnene `Bie` og `Jonas` oversættes til Jacob og Nicehair. Andre navne kan tilføjes med `--alias 'Player 3=Casper'`.

For hver kamp viser importen, hvor mange kurve den fandt, ved siden af antallet af ramte skud på stats-siden. Så kan du se,
om den har fat i de rigtige data. Mangler en kamp sin video, eller er tiderne målt fra kampstart i stedet for videostart,
kan du angive videoen sådan: `--video 2026-09-28-k1=/Volumes/GoPro/GX010045.MP4@-12.5`.
`@-12.5` lægges til alle tider i den kamp.

Finder importen ingenting, viser den et eksempel fra de filer, den ikke kunne forstå. Send en linje fra den fil, HoopStats
gemmer kurvene i, til Claude, så kan importen tilpasses.

## Ret eller skriv klip.csv selv

`klip.csv` kan åbnes i Numbers eller Excel. Både komma og semikolon virker som skilletegn.

| kolonne     | betydning                                                                    |
|-------------|------------------------------------------------------------------------------|
| `spiller`   | navnet som på stats-siden                                                    |
| `video`     | filnavn eller fuld sti; flere filer i træk som `a.mp4\|b.mp4`                |
| `tid`       | hvornår kurven går i, fx `12:34.5` (fra starten af videoen)                  |
| `kamp`      | kamp-id fra stats-siden, fx `2026-09-28-k1` (valgfri)                        |
| `type`      | fx `Blok` eller `Crossover` vises i stedet for "Kurv" og giver lidt ekstra vægt |
| `point`     | `2` for en 2'er                                                              |
| `prioritet` | et tal lægges til klippets vægt; `x` springer rækken over                    |

Rettelser bliver ved med at virke, når du kører `plan` og `lav` igen. `importer` overskriver kun filen med `--overskriv`.
Spillerpoint i HoopStats er et bedste bud, så tjek navnene i prøvevideoen og ret dem i `klip.csv`, hvis en kurv er givet
til den forkerte.
