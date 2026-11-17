#!/usr/bin/env python3
"""Fjerner spilledage fra dataene i index.html (window.D9_DATA).

6. jul. og 10. aug. er taget ud, fordi tallene derfra er for usikre og trak de samlede stats skævt.
deploy.sh kører scriptet før hver udgivelse, så dagene ikke kommer tilbage, når build_site.py skriver index.html forfra.
Kører man det igen, sker der ikke noget.
"""
import json
import pathlib
import sys

FJERN_DATOER = {"2026-07-06", "2026-08-10"}
START = "<script>window.D9_DATA = "
SLUT = ";</script>"


def main():
    sti = pathlib.Path(__file__).with_name("index.html")
    linjer = sti.read_text(encoding="utf-8").split("\n")
    nr = [i for i, l in enumerate(linjer) if l.startswith(START) and l.endswith(SLUT)]
    if len(nr) != 1:
        sys.exit("fjern-kampe.py: fandt ikke linjen med window.D9_DATA i index.html")
    data = json.loads(linjer[nr[0]][len(START):-len(SLUT)])
    ids = {g["game_id"] for g in data["games"] if g["date"] in FJERN_DATOER}
    etiketter = {g["game"] for g in data["games"] if g["date"] in FJERN_DATOER}
    if not ids:
        return
    fjernet = 0
    for navn, raekker in data.items():
        if not isinstance(raekker, list):
            continue
        behold = [r for r in raekker
                  if not (isinstance(r, dict) and (r.get("game_id") in ids or r.get("game") in etiketter))]
        fjernet += len(raekker) - len(behold)
        data[navn] = behold
    linjer[nr[0]] = START + json.dumps(data, ensure_ascii=False) + SLUT
    sti.write_text("\n".join(linjer), encoding="utf-8")
    print(f"Fjernet {len(ids)} kampe ({fjernet} rækker) fra {', '.join(sorted(FJERN_DATOER))}.")


if __name__ == "__main__":
    main()
