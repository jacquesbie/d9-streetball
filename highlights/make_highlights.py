#!/usr/bin/env python3
"""D9 highlights: klip en highlight-video (max 5 min) ud af kampoptagelserne, med hver spiller
fra stats-siden mindst én gang.

    python3 highlights/make_highlights.py importer ~/HoopStatsLocal   # kurve (tid + spiller) -> highlights/klip.csv
    python3 highlights/make_highlights.py plan                        # vis udvalget uden at lave video
    python3 highlights/make_highlights.py lav                         # -> highlights/ud/D9_highlights.mp4

Kræver ffmpeg og ffprobe. Kun Pythons standardbibliotek; Pillow bruges til teksten, hvis ffmpeg
er bygget uden drawtext-filteret. Se highlights/README.md.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = HERE.parent / "index.html"
KLIP = HERE / "klip.csv"
UD = HERE / "ud"
HOOPSTATS = Path("~/HoopStatsLocal").expanduser()

# HoopStats-rådata bruger nogle steder andre navne end stats-siden
# (box scoren fra 10. aug skriver Bie og Jonas, hvor siden viser Jacob og Nicehair).
ALIASES = {"Bie": "Jacob", "Jonas": "Nicehair"}

VIDEO_EXT = {".mp4", ".mov", ".m4v", ".mkv", ".avi"}
SKIP_DIRS = {"node_modules", "site-packages", "__pycache__", "venv", "Library"}
MONTHS = ["januar", "februar", "marts", "april", "maj", "juni", "juli", "august",
          "september", "oktober", "november", "december"]
DATE_RE = re.compile(r"(20\d\d)[-_.]?(0[1-9]|1[0-2])[-_.]?(0[1-9]|[12]\d|3[01])")

FPS = 30
FADE = 0.2
INTRO, SESSION, OUTRO = 4.0, 2.5, 5.0
BG, WHITE, LIGHT, GREY, ORANGE, ACCENT = "#10151b", "#ffffff", "#e6ebf1", "#98a4b3", "#f0894a", "#c95b1e"


def die(msg: str, code: int = 1):
    print(f"\n{msg}", file=sys.stderr)
    sys.exit(code)


def rel(p) -> str:
    p = Path(p)
    try:
        return str(p.resolve().relative_to(Path.cwd()))
    except ValueError:
        return str(p).replace(str(Path.home()), "~", 1)


def norm(s) -> str:
    """Sammenligningsnøgle for navne: små bogstaver, uden æøå-varianter og tegn."""
    s = str(s).strip().lower()
    for a, b in (("æ", "ae"), ("ø", "o"), ("å", "aa"), ("é", "e"), ("ö", "o"), ("ä", "ae"), ("ü", "u")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]", "", s)


def parse_time(v):
    """Sekunder fra 75.5, '75,5', '1:15.5' eller '0:01:15'."""
    if v is None or isinstance(v, (bool, dict, list)):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(",", ".")
    try:
        parts = [float(p) for p in s.split(":")] if s else []
    except ValueError:
        return None
    if not 1 <= len(parts) <= 3:
        return None
    t = 0.0
    for p in parts:
        t = t * 60 + p
    return t


def fmt_time(t: float) -> str:
    t = round(max(0.0, t), 1)
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:04.1f}" if h else f"{int(m)}:{s:04.1f}"


def read_table(path: Path) -> list:
    """CSV med komma, semikolon (dansk Excel) eller tab; linjer der starter med # springes over."""
    lines = [ln for ln in path.read_text(encoding="utf-8-sig").splitlines()
             if ln.strip() and not ln.lstrip().startswith("#")]
    if not lines:
        return []
    delim = max(",;\t", key=lines[0].count)
    rows = []
    for row in csv.DictReader(lines, delimiter=delim):
        rows.append({k.strip().lower(): (v or "").strip() for k, v in row.items() if isinstance(k, str)})
    return rows


def walk(root: Path, exts):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in SKIP_DIRS]
        for f in filenames:
            if Path(f).suffix.lower() in exts and not f.startswith("._"):
                yield Path(dirpath) / f


# --- Stats-siden: spillere og kampe ---------------------------------------------------------

@dataclass
class Game:
    gid: str
    date: str
    session: str      # "28. sep"
    label: str        # "Kamp 1"
    no: int
    setup: str        # "4 mod 4 · 1 GoPro"
    winner: str
    complete: bool
    fgm: int = 0
    teams: dict = field(default_factory=dict)


def load_site(path: Path):
    """Spillerne og kampene fra stats-sidens indbagte D9_DATA."""
    if not path.exists():
        return [], {}
    m = re.search(r"window\.D9_DATA\s*=\s*(\{.*?\});\s*</script>", path.read_text(encoding="utf-8"), re.S)
    if not m:
        return [], {}
    data = json.loads(m.group(1))
    games = {}
    for g in data.get("games", []):
        games[g["game_id"]] = Game(g["game_id"], g["date"], g.get("session", ""),
                                   g.get("game", g["game_id"]).split("·")[-1].strip(), int(g.get("game_no") or 0),
                                   g.get("setup", ""), g.get("winner") or "", g.get("complete") == "Ja")
    players = set()
    for r in data.get("player_games", []):
        players.add(r["player"])
        g = games.get(r["game_id"])
        if g:
            g.teams[r["player"]] = r.get("team")
            g.fgm += int(r.get("FGM") or 0)
    return sorted(players, key=norm), games


class Roster:
    def __init__(self, names, aliases):
        self.names = list(names)
        self.keys = {norm(n): n for n in self.names}
        self.alias = {norm(k): v.strip() for k, v in aliases.items()}

    def canon(self, raw):
        """Stats-sidens navn for et rånavn, eller None hvis det ikke er en kendt spiller."""
        k = norm(raw) if raw is not None else ""
        if not k:
            return None
        target = self.alias.get(k)
        if not self.names:
            return target or str(raw).strip()
        return self.keys.get(norm(target) if target else k)


def parse_aliases(pairs) -> dict:
    out = dict(ALIASES)
    for p in pairs:
        if "=" not in p:
            die(f"--alias skal skrives NAVN=SPILLER, fx --alias 'Player 3=Casper' (fik {p!r})")
        k, v = p.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def match_game(cands, games):
    """(kamp, dato) ud fra et kamp-id, en dato eller en sti som '.../2026-09-28/k1/...'."""
    cands = [str(c) for c in cands if c]
    for c in cands:
        if c.strip() in games:
            g = games[c.strip()]
            return g, g.date
    for c in cands:
        for g in games.values():
            if norm(c) == norm(g.gid):
                return g, g.date
    for c in cands:
        m = DATE_RE.search(c)
        if not m:
            continue
        date = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        same = [g for g in games.values() if g.date == date]
        if len(same) == 1:
            return same[0], date
        rest = c[m.end():]
        for g in same:
            suffix = g.gid[len(date):].strip("-_ ")
            if suffix and re.match(rf"[\W_]*{re.escape(suffix)}(?![A-Za-z0-9])", rest, re.I):
                return g, date
        nm = re.match(r"[\W_]*(?:kamp|game|k|g)?[\W_]*0*(\d{1,2})(?!\d)", rest, re.I)
        for g in same:
            if nm and g.no == int(nm.group(1)):
                return g, date
        return None, date
    return None, ""


def session_title(date: str) -> str:
    y, mo, d = date.split("-")
    return f"{int(d)}. {MONTHS[int(mo) - 1]}"


def session_short(date: str, games) -> str:
    for g in games.values():
        if g.date == date and g.session:
            return g.session
    y, mo, d = date.split("-")
    return f"{int(d)}. {MONTHS[int(mo) - 1][:3]}"


# --- Videoer --------------------------------------------------------------------------------

GOPRO_NEW = re.compile(r"^(G[HX])(\d\d)(\d{4})(\.\w+)$", re.I)        # GX010045.MP4, GX020045.MP4, ...
GOPRO_OLD = re.compile(r"^(GOPR|GP(\d\d))(\d{4})(\.\w+)$", re.I)      # GOPR0045.MP4, GP010045.MP4, ...


def sibling(d: Path, name: str):
    q = d / name
    if q.exists():
        return q
    low = name.lower()
    return next((c for c in d.iterdir() if c.name.lower() == low), None)


def next_chapter(p: Path):
    """Næste GoPro-kapitel (kameraet deler lange optagelser op i filer på ca. 4 GB)."""
    m = GOPRO_NEW.match(p.name)
    if m:
        return sibling(p.parent, f"{m.group(1)}{int(m.group(2)) + 1:02d}{m.group(3)}{m.group(4)}")
    m = GOPRO_OLD.match(p.name)
    if m:
        ch = int(m.group(2)) if m.group(2) else 0
        return sibling(p.parent, f"GP{ch + 1:02d}{m.group(3)}{m.group(4)}")
    return None


def first_chapter(p: Path) -> bool:
    m = GOPRO_NEW.match(p.name)
    if m:
        return int(m.group(2)) <= 1
    m = GOPRO_OLD.match(p.name)
    return not m or not m.group(2)


@dataclass
class Probe:
    duration: float
    audio: bool
    fps: float
    date: str


class Media:
    def __init__(self, dirs):
        self.dirs = []
        for d in dirs:
            d = Path(d).expanduser()
            if d.is_dir() and d not in self.dirs:
                self.dirs.append(d)
        self._index = None
        self._probes = {}

    def _by_name(self):
        if self._index is None:
            self._index = defaultdict(list)
            for d in self.dirs:
                for p in walk(d, VIDEO_EXT):
                    self._index[p.name.lower()].append(p)
        return self._index

    def find(self, name, near=(), date=""):
        p = Path(str(name).strip()).expanduser()
        if p.is_absolute() and p.exists():
            return p
        if not p.is_absolute():
            for base in near:
                q = Path(base) / p
                if q.exists():
                    return q.resolve()
        hits = list(dict.fromkeys(self._by_name().get(p.name.lower(), [])))
        if len(hits) > 1 and date:
            dated = [h for h in hits if date in str(h) or date.replace("-", "") in str(h)
                     or self.probe(h).date == date]
            hits = dated or hits
        if len(hits) > 1:
            raise LookupError(f"flere videoer hedder {p.name} ({', '.join(rel(h) for h in hits[:3])}); "
                              "skriv hele stien i video-kolonnen")
        return hits[0] if hits else None

    def probe(self, p: Path) -> Probe:
        key = str(p)
        if key not in self._probes:
            r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                "format=duration:format_tags=creation_time:stream=codec_type,avg_frame_rate",
                                "-of", "json", str(p)], capture_output=True, text=True)
            if r.returncode != 0:
                raise LookupError(f"ffprobe kan ikke læse {p.name}: {r.stderr.strip()[:200]}")
            info = json.loads(r.stdout or "{}")
            fmt, streams = info.get("format", {}), info.get("streams", [])
            fps = 30.0
            for s in streams:
                if s.get("codec_type") == "video":
                    num, _, den = (s.get("avg_frame_rate") or "30/1").partition("/")
                    try:
                        fps = float(num) / float(den or 1) or 30.0
                    except (ValueError, ZeroDivisionError):
                        pass
                    break
            self._probes[key] = Probe(float(fmt.get("duration") or 0),
                                      any(s.get("codec_type") == "audio" for s in streams), fps,
                                      (fmt.get("tags", {}).get("creation_time") or "")[:10])
        return self._probes[key]

    def locate(self, video, t, near=(), date=""):
        """(fil, tid i filen, filens længde, optagelsens første fil) for tid t i en optagelse.

        GoPro-kapitler følges automatisk; flere filer kan også angives som 'a.mp4|b.mp4'."""
        names = [v.strip() for v in str(video).split("|") if v.strip()]
        if not names:
            raise LookupError("ingen video angivet")
        files = []
        for n in names:
            p = self.find(n, near, date)
            if p is None:
                raise LookupError(f"finder ikke videoen {n}")
            files.append(p)
        if t < 0:
            raise LookupError(f"negativ tid ({t})")
        p, i, local = files[0], 0, t
        while True:
            dur = self.probe(p).duration
            if local < dur:
                return p, local, dur, files[0]
            i += 1
            nxt = (files[i] if i < len(files) else None) if len(files) > 1 else next_chapter(p)
            if nxt is None:
                raise LookupError(f"tid {fmt_time(t)} ligger efter slutningen af {p.name} ({fmt_time(dur)}); "
                                  "er tiden i sekunder fra videoens start?")
            local -= dur
            p = nxt


# --- Import fra HoopStats -------------------------------------------------------------------

def nk(k) -> str:
    return re.sub(r"[\s\-]+", "_", str(k).strip().lower())


TIME_KEYS = [nk(k) for k in ("video_t", "video_time", "video_sec", "video_s", "t_video", "time_s", "time_sec",
                             "t_sec", "t_s", "sec", "secs", "seconds", "t", "time", "timestamp", "ts", "clock",
                             "start", "start_s", "start_sec", "t_start", "tid")]
FRAME_KEYS = ["frame", "frame_idx", "frame_index", "frame_no", "frame_num"]
FPS_KEYS = ["fps", "frame_rate", "framerate"]
PLAYER_KEYS = ["player", "shooter", "scorer", "spiller", "player_name", "shooter_name", "scorer_name", "skytte",
               "name", "who"]
MADE_KEYS = ["made", "make", "is_make", "is_made", "scored", "success", "hit", "ramt", "result", "outcome"]
TYPE_KEYS = ["type", "event", "event_type", "kind", "action", "label", "category"]
POINT_KEYS = ["points", "pts", "point", "point_value", "shot_value", "value"]
VIDEO_KEYS = ["video", "video_path", "video_file", "videofile", "file", "filename", "source", "src", "path",
              "clip", "camera_file"]
GAME_KEYS = ["game_id", "game", "kamp", "kamp_id", "match", "match_id"]
YES = {"1", "true", "yes", "ja", "y", "j", "make", "made", "in", "ramt", "scored", "score", "hit", "good", "kurv",
       "success", "x"}
NO = {"0", "false", "no", "nej", "n", "miss", "missed", "bom", "out", "airball", "blocked", "none"}


def keyed(d) -> dict:
    return {nk(k): v for k, v in d.items()} if isinstance(d, dict) else {}


def pick(low: dict, keys):
    for k in keys:
        v = low.get(k)
        if v is not None and v != "":
            return v
    return None


def truth(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v > 0
    s = nk(v)
    return True if s in YES else False if s in NO else None


def is_make(low: dict):
    v = pick(low, MADE_KEYS)
    if v is not None and not isinstance(v, (dict, list)):
        r = truth(v)
        if r is not None:
            return r
    t = pick(low, TYPE_KEYS)
    if t is not None and not isinstance(t, (dict, list)):
        s = str(t).lower()
        if re.search(r"miss|bom|airball|brick", s):
            return False
        if re.search(r"make|made|basket|score|kurv|fgm|bucket", s):
            return True
    return None


def as_points(v):
    if v is None or isinstance(v, (bool, dict, list)):
        return None
    try:
        p = int(float(str(v).replace(",", ".")))
    except ValueError:
        return None
    return p if p in (1, 2, 3) else None


def video_of(low: dict):
    for k in VIDEO_KEYS:
        v = low.get(k)
        if isinstance(v, str) and (Path(v.strip()).suffix.lower() in VIDEO_EXT or "|" in v):
            return v.strip()
    return None


def walk_json(obj, ctx, depth=0):
    """Alle dicts i en JSON-struktur, hver med forældrenes simple felter (fx video, fps, game_id)."""
    if depth > 20:
        return
    if isinstance(obj, dict):
        yield obj, ctx
        inner = dict(ctx)
        inner.update((k, v) for k, v in obj.items() if isinstance(v, (str, int, float)) and not isinstance(v, bool))
        for v in obj.values():   # også søskende som {"meta": {"video": ..., "fps": ...}, "events": [...]}
            if isinstance(v, dict):
                for k2, v2 in v.items():
                    if isinstance(v2, (str, int, float)) and not isinstance(v2, bool):
                        inner.setdefault(k2, v2)
        for v in obj.values():
            if isinstance(v, (dict, list)):
                yield from walk_json(v, inner, depth + 1)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk_json(v, ctx, depth + 1)


def records(path: Path):
    try:
        if path.suffix.lower() == ".csv":
            for row in read_table(path):
                yield row, {}
        elif path.suffix.lower() == ".jsonl":
            with path.open(encoding="utf-8") as fh:
                for line in fh:
                    if line.strip():
                        yield from walk_json(json.loads(line), {})
        else:
            yield from walk_json(json.loads(path.read_text(encoding="utf-8")), {})
    except (ValueError, UnicodeDecodeError, OSError):
        return


def to_event(rec, ctx):
    """('kurv', data), ('bom', None), ('uklar', None) eller None hvis posten ikke er et skud."""
    low = keyed(rec)
    who = pick(low, PLAYER_KEYS)
    if isinstance(who, dict):
        who = pick(keyed(who), ["name", "navn", "player", "spiller"])
    if who is None or isinstance(who, (list, dict, bool)):
        return None
    c = None
    t, frame = parse_time(pick(low, TIME_KEYS)), None
    if t is None:
        try:
            frame = int(float(pick(low, FRAME_KEYS)))
        except (TypeError, ValueError):
            return None
        c = keyed(ctx)
        try:
            fps = float(pick(low, FPS_KEYS) or pick(c, FPS_KEYS) or 0)
            t = frame / fps if fps else None
        except (TypeError, ValueError):
            t = None
    if t is not None and not 0 <= t <= 6 * 3600:
        return None
    pts = as_points(pick(low, POINT_KEYS))
    made = is_make(low)
    if made is None and pts:
        made = True
    if made is None:
        return "uklar", None
    if not made:
        return "bom", None
    c = c if c is not None else keyed(ctx)
    return "kurv", {"who": str(who).strip(), "t": t, "frame": frame, "pts": pts,
                    "video": video_of(low) or video_of(c), "game": pick(low, GAME_KEYS) or pick(c, GAME_KEYS)}


def nearest_recording(d: Path, root: Path, cache: dict):
    """Den eneste optagelse i datafilens mappe (eller nærmeste forældremappe), hvis der kun er én."""
    while True:
        if d not in cache:
            vids = [p for p in d.iterdir() if p.is_file() and p.suffix.lower() in VIDEO_EXT
                    and not p.name.startswith("._")] if d.is_dir() else []
            cache[d] = [p for p in vids if first_chapter(p)]
        if len(cache[d]) == 1:
            return cache[d][0]
        if cache[d] or d == root or d.parent == d:
            return None
        d = d.parent


def cmd_importer(args):
    names, games = load_site(Path(args.site).expanduser())
    roster = Roster(names, parse_aliases(args.alias))
    root = Path(args.mappe).expanduser().resolve()
    if not root.is_dir():
        die(f"Finder ikke mappen {root}. Angiv HoopStats-mappen: importer /sti/til/HoopStatsLocal")
    out = Path(args.ud).expanduser()
    if out.exists() and not args.overskriv:
        die(f"{rel(out)} findes allerede (måske med dine rettelser). Brug --overskriv for at erstatte den.")
    media = Media([root] + args.videomappe)

    def short(f):
        return str(f.relative_to(root))

    overrides = {}
    for spec in args.video:
        m = re.match(r"^([^=]+)=(.+?)(?:@(-?[\d.,:]+))?$", spec)
        g = m and match_game([m.group(1).strip()], games)[0]
        if not g:
            die(f"--video skal skrives KAMP=FIL eller KAMP=FIL@SEKUNDER med et kamp-id fra stats-siden, "
                f"fx 2026-09-28-k1=GX010045.MP4 (fik {spec!r})")
        overrides[g.gid] = (m.group(2).strip(), parse_time(m.group(3)) or 0.0)

    events, files, scanned, too_big = [], Counter(), 0, []
    misses, unclear, unknown = 0, {}, Counter()
    rec_cache = {}
    for f in walk(root, {".json", ".jsonl", ".csv"}):
        if f.resolve() == out.resolve():
            continue
        if f.stat().st_size > args.max_mb * 1e6:
            too_big.append(f)
            continue
        scanned += 1
        for rec, ctx in records(f):
            res = to_event(rec, ctx)
            if res is None:
                continue
            status, ev = res
            if status == "bom":
                misses += 1
                continue
            if status == "uklar":
                unclear.setdefault(f, rec)
                continue
            player = roster.canon(ev["who"])
            if player is None:
                unknown[ev["who"]] += 1
                continue
            g, date = match_game([ev["game"], ev["video"], str(f.relative_to(root))], games)
            video = ""
            if g and g.gid in overrides:
                video, off = overrides[g.gid]
                ev["t"] = None if ev["t"] is None else ev["t"] + off
            elif ev["video"]:
                try:
                    found = media.find(ev["video"], [f.parent] + list(f.parents), date)
                except LookupError:
                    found = None
                video = str(found) if found else ev["video"]
            else:
                found = nearest_recording(f.parent, root, rec_cache)
                video = str(found) if found else ""
            events.append({"spiller": player, "video": video, "t": ev["t"], "frame": ev["frame"],
                           "kamp": g.gid if g else date, "point": ev["pts"], "src": f})
            files[f] += 1

    # Samme kamp og video i flere filer er typisk ældre og nyere versioner af samme analyse: brug den nyeste.
    skipped = set()
    if not args.alle_filer:
        by_key = defaultdict(set)
        for e in events:
            if e["kamp"] in games:
                by_key[(e["kamp"], e["video"])].add(e["src"])
        for srcs in by_key.values():
            if len(srcs) > 1:
                newest = max(srcs, key=lambda s: s.stat().st_mtime)
                skipped |= srcs - {newest}
        events = [e for e in events if e["src"] not in skipped]

    # Samme kurv registreret to gange (fx både som skud og som point) tælles én gang.
    events.sort(key=lambda e: (e["kamp"], e["video"], e["spiller"], e["t"] if e["t"] is not None else e["frame"]))
    kept = []
    for e in events:
        last = kept[-1] if kept else None
        if (last and (last["kamp"], last["video"], last["spiller"]) == (e["kamp"], e["video"], e["spiller"])
                and e["t"] is not None and last["t"] is not None and e["t"] - last["t"] < 2.5):
            continue
        kept.append(e)
    events = kept

    print(f"Gennemsøgte {scanned} datafiler i {rel(root)}.")
    if too_big:
        print(f"  Sprang {len(too_big)} filer over {args.max_mb:g} MB over (fx {short(too_big[0])}); brug --max-mb.")
    if not events:
        print("\nFandt ingen kurve med både tid og en kendt spiller.")
        if unknown:
            print("Ukendte spillernavne (tilføj med --alias 'NAVN=Spiller'): "
                  + ", ".join(f"{n!r} ×{c}" for n, c in unknown.most_common(8)))
        for f, rec in list(unclear.items())[:5]:
            sample = json.dumps(rec, ensure_ascii=False)[:300]
            print(f"  {short(f)} har tid + spiller, men intet ramt/bom-felt. Eksempel: {sample}")
        die("Send en linje fra den fil HoopStats gemmer kurvene i til Claude, så kan importen tilpasses "
            "(eller skriv klip.csv selv, se highlights/README.md).")

    for f in sorted(files, key=short):
        if f not in skipped:
            print(f"  {short(f)}: {files[f]} kurve")
    for f in sorted(skipped, key=short):
        print(f"  {short(f)}: sprunget over (nyere fil for samme kamp; brug --alle-filer for at tage alle med)")
    print(f"\nFandt {len(events)} kurve ({misses} bomskud sorteret fra).")
    per_game = Counter(e["kamp"] for e in events)
    for gid in sorted(per_game, key=lambda k: (games[k].date, games[k].no) if k in games else (k or "~", 0)):
        g = games.get(gid)
        vids = sorted({Path(e["video"]).name or "MANGLER" for e in events if e["kamp"] == gid})
        label = f"{g.session} · {g.label}" if g else (gid or "ukendt kamp")
        facit = f"  (stats-siden: {g.fgm} ramte)" if g else ""
        print(f"  {label:<22}{per_game[gid]:>4} kurve{facit:<26} video: {', '.join(vids)[:70]}")
    per_player = Counter(e["spiller"] for e in events)
    print("Spillere: " + " · ".join(f"{p} {per_player[p]}" for p in sorted(per_player, key=norm)))
    missing = [p for p in roster.names if p not in per_player]
    if missing:
        print(f"MANGLER kurve for: {', '.join(missing)}. Tilføj dem selv i klip.csv (se README).")
    if unknown:
        print("Ukendte navne sprunget over (tilføj med --alias 'NAVN=Spiller'): "
              + ", ".join(f"{n!r} ×{c}" for n, c in unknown.most_common(8)))
    no_video = sum(1 for e in events if not e["video"])
    if no_video:
        print(f"{no_video} kurve mangler video. Angiv den per kamp med --video KAMP=FIL, fx "
              "--video 2026-09-28-k1=/Volumes/GoPro/GX010045.MP4")
    no_time = sum(1 for e in events if e["t"] is None)
    if no_time:
        print(f"{no_time} kurve har kun billednummer; fps læses fra videoen, når du kører plan.")

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["spiller", "video", "tid", "frame", "kamp", "type", "point", "prioritet", "note"])
        for e in events:
            w.writerow([e["spiller"], e["video"], fmt_time(e["t"]) if e["t"] is not None else "",
                        e["frame"] if e["t"] is None else "", e["kamp"], "", e["point"] or "", "",
                        short(e["src"])])
    print(f"\nSkrev {rel(out)}. Næste skridt:  python3 {rel(__file__)} plan")


# --- Udvælgelse -----------------------------------------------------------------------------

COLS = {"spiller": "spiller", "player": "spiller", "navn": "spiller", "video": "video", "fil": "video",
        "tid": "tid", "time": "tid", "t": "tid", "frame": "frame", "kamp": "kamp", "game": "kamp",
        "game_id": "kamp", "type": "type", "point": "point", "points": "point", "pts": "point",
        "prioritet": "prioritet", "priority": "prioritet", "foer": "foer", "før": "foer", "efter": "efter",
        "note": "note"}
GENERIC_KINDS = {"", "make", "made", "kurv", "basket", "score", "fgm", "shot", "skud", "2er", "1er"}
SKIP_PRIORITY = {"x", "nej", "skip", "fjern", "ud"}


@dataclass
class Moment:
    row: int
    player: str
    video: str
    t: float
    game: Game | None
    date: str
    kind: str = ""
    points: int | None = None
    priority: float = 0.0
    before: float = 5.5
    after: float = 2.5
    path: Path | None = None
    rec: str = ""
    start: float = 0.0
    dur: float = 0.0
    audio: bool = True
    winner: bool = False
    score: float = 0.0

    @property
    def gkey(self) -> str:
        return self.game.gid if self.game else self.date or self.rec

    def overlaps(self, o: Moment) -> bool:
        return (self.rec == o.rec and self.t - self.before < o.t + o.after
                and o.t - o.before < self.t + self.after)


def load_moments(args, roster, games):
    path = Path(args.klip).expanduser()
    if not path.exists():
        die(f"Finder ikke {rel(path)}. Kør først:  python3 {rel(__file__)} importer ~/HoopStatsLocal\n"
            "(eller skriv klippene selv, se highlights/README.md)")
    media = Media([path.parent, HOOPSTATS] + args.videomappe)
    sessions = {g.date for g in games.values()}
    moments, problems, unknown = [], [], Counter()
    for i, raw in enumerate(read_table(path), start=1):
        r = {COLS.get(k, k): v for k, v in raw.items()}
        who = r.get("spiller", "")
        if not who or norm(r.get("prioritet", "")) in SKIP_PRIORITY:
            continue
        player = roster.canon(who)
        if player is None:
            unknown[who] += 1
            continue
        video = r.get("video", "")
        game, date = match_game([r.get("kamp", ""), video], games)
        where = f"række {i} ({player} {r.get('tid') or r.get('frame') or '?'})"
        try:
            t = parse_time(r.get("tid"))
            if t is None and r.get("frame"):
                first = media.find(video.split("|")[0], [path.parent], date)
                if first is None:
                    raise LookupError(f"finder ikke videoen {video}")
                t = float(r["frame"]) / media.probe(first).fps
            if t is None:
                raise LookupError("mangler tid")
            p, local, length, first = media.locate(video, t, [path.parent], date)
        except (LookupError, ValueError) as e:
            problems.append(f"{where}: {e}")
            continue
        probe = media.probe(p)
        if not date and probe.date in sessions:
            date = probe.date
            same = [g for g in games.values() if g.date == date]
            game = same[0] if len(same) == 1 else None
        try:
            priority = float((r.get("prioritet") or "0").replace(",", "."))
        except ValueError:
            priority = 0.0
        m = Moment(i, player, video, t, game, date, r.get("type", ""), as_points(r.get("point")), priority,
                   parse_time(r.get("foer")) or args.foer, parse_time(r.get("efter")) or args.efter)
        span = m.before + m.after
        m.path, m.rec, m.audio = p, str(first), probe.audio
        m.start = max(0.0, min(local - m.before, length - span))
        m.dur = round(min(span, length - m.start) * FPS) / FPS
        if m.dur < 1.0:
            problems.append(f"{where}: videoen er for kort til et klip")
            continue
        moments.append(m)
    # Rækker uden kamp arver dato og kamp fra andre rækker i samme optagelse.
    known = defaultdict(set)
    for m in moments:
        if m.date:
            known[m.rec].add((m.date, m.game.gid if m.game else ""))
    for m in moments:
        if not m.date and len(known[m.rec]) == 1:
            m.date, gid = next(iter(known[m.rec]))
            m.game = games.get(gid)
    return moments, problems, unknown


def mark_winners(moments, games):
    """Vinderholdets sidste kurv i hver færdigspillet kamp."""
    by_game = defaultdict(list)
    for m in moments:
        if m.game:
            by_game[m.game.gid].append(m)
    for gid, ms in by_game.items():
        g = games[gid]
        if not g.complete or not g.winner:
            continue
        rec = Counter(m.rec for m in ms).most_common(1)[0][0]
        last = [m for m in ms if m.rec == rec and g.teams.get(m.player) == g.winner
                and norm(m.kind) in GENERIC_KINDS]   # kun kurve, ikke fx en blok
        if last:
            max(last, key=lambda m: m.t).winner = True


def score(m: Moment) -> float:
    s = 1.0 + m.priority
    if m.points == 2:
        s += 1.5
    if m.winner:
        s += 2.0
    if norm(m.kind) not in GENERIC_KINDS:
        s += 0.5
    return s


def select(moments, players, budget):
    """Hver spiller får sit bedste klip; resten af tiden fyldes med de bedste klip, spredt ud over
    spillere og kampe."""
    for m in moments:
        m.score = score(m)
    order = {id(m): n for n, m in enumerate(moments)}
    by_player = defaultdict(list)
    for m in moments:
        by_player[m.player].append(m)
    for lst in by_player.values():
        lst.sort(key=lambda m: (-m.score, order[id(m)]))

    chosen, sessions = [], set()

    def cost(m):
        return m.dur + (SESSION if m.date and m.date not in sessions else 0.0)

    used = INTRO + OUTRO
    for p in sorted(by_player, key=lambda p: (len(by_player[p]), norm(p))):   # sjældne spillere vælger først
        if players and p not in players:
            continue
        cands = by_player[p]
        m = next((c for c in cands if not any(c.overlaps(o) for o in chosen)), cands[0])
        used += cost(m)
        chosen.append(m)
        sessions.add(m.date)
    if used > budget:
        die(f"Ét klip per spiller fylder allerede {fmt_time(used)}; gør klippene kortere med --foer/--efter.")

    per_player, per_game = Counter(m.player for m in chosen), Counter(m.gkey for m in chosen)
    rest = [m for m in moments if all(m is not c for c in chosen)]
    while True:
        best, best_val = None, None
        for m in rest:
            if used + cost(m) > budget or any(m.overlaps(c) for c in chosen):
                continue
            val = m.score - 0.7 * per_player[m.player] - 0.25 * per_game[m.gkey]
            if best is None or val > best_val:
                best, best_val = m, val
        if best is None:
            break
        used += cost(best)
        chosen.append(best)
        sessions.add(best.date)
        rest.remove(best)
        per_player[best.player] += 1
        per_game[best.gkey] += 1

    def when(m):
        return (m.date or "9999", m.game.no if m.game else 99, m.gkey, m.rec, m.t)
    return sorted(chosen, key=when), used


def subtitle(m: Moment, games) -> str:
    parts = []
    if m.winner:
        parts.append("Vinderkurven")
    if norm(m.kind) not in GENERIC_KINDS:
        parts.append(m.kind[0].upper() + m.kind[1:])
    elif m.points == 2:
        parts.append("2'er")
    elif not parts:
        parts.append("Kurv")
    if m.date:
        parts.append(session_short(m.date, games))
    if m.game:
        parts.append(m.game.label)
    return " · ".join(parts)


def build_plan(args):
    names, games = load_site(Path(args.site).expanduser())
    if not names:
        print(f"OBS: fandt ingen spillere i {rel(args.site)}; bruger navnene fra klip.csv.")
    roster = Roster(names, parse_aliases(args.alias))
    moments, problems, unknown = load_moments(args, roster, games)
    for p in problems[:15]:
        print(f"  Springer over {p}")
    if len(problems) > 15:
        print(f"  ... og {len(problems) - 15} rækker mere med problemer")
    if unknown:
        print("  Ukendte spillere i klip.csv (ret navnet eller brug --alias): "
              + ", ".join(f"{n!r} ×{c}" for n, c in unknown.most_common(8)))
    if not moments:
        die("Ingen brugbare klip i klip.csv.")
    mark_winners(moments, games)
    players = set(roster.names)
    chosen, used = select(moments, players, args.max - 2.0)   # 2 s luft til afrunding ved encoding
    have = {m.player for m in chosen}
    missing = [p for p in roster.names if p not in have]
    return chosen, used, missing, roster, games


def print_plan(chosen, used, missing, roster, games, max_len):
    print(f"\nHighlights: {len(chosen)} klip, {fmt_time(used)} af max {fmt_time(max_len)}\n")
    pos, date = INTRO, None
    for m in chosen:
        if m.date != date:
            date = m.date
            if date:
                pos += SESSION
                print(f"  {session_title(date).upper()}")
        src = f"{m.path.name} {fmt_time(m.start)}"
        print(f"    {fmt_time(pos):>7}  {m.player:<10} {subtitle(m, games):<38} {src}")
        pos += m.dur
    counts = Counter(m.player for m in chosen)
    total = len(roster.names) or len(counts)
    print(f"\nSpillere med: {len(counts)}/{total}  "
          + " · ".join(f"{p} {counts[p]}" for p in sorted(counts, key=norm)))
    if missing:
        print(f"MANGLER: {', '.join(missing)} har ingen brugbare klip i klip.csv. "
              "Tilføj en række for hver (spiller, video, tid), se highlights/README.md.")


def cmd_plan(args):
    need_ffmpeg()
    chosen, used, missing, roster, games = build_plan(args)
    print_plan(chosen, used, missing, roster, games, args.max)


# --- Video ----------------------------------------------------------------------------------

@dataclass
class Txt:
    text: str
    size: int
    x: float | None     # None = centreret
    y: float
    color: str
    bold: bool = True
    box: bool = False


@dataclass
class Rect:
    x: float
    y: float
    w: float
    h: float
    color: str


# Layouts i 1080p-koordinater; skaleres ved --hurtig.
def lower_third(name, sub):
    return [Rect(60, 828, 12, 196, ACCENT),
            Txt(name.upper(), 76, 100, 836, WHITE, True, True),
            Txt(sub, 38, 100, 960, LIGHT, False, True)]


def intro_card(span, stats):
    return [Txt("D9 STREETBALL", 132, None, 360, WHITE), Rect(860, 536, 200, 8, ACCENT),
            Txt("Highlights", 64, None, 580, ORANGE, False),
            Txt(span, 40, None, 690, GREY, False), Txt(stats, 40, None, 746, GREY, False)]


def session_card(title, sub):
    return [Txt(title.upper(), 116, None, 400, WHITE), Rect(860, 560, 200, 8, ACCENT),
            Txt(sub, 46, None, 604, GREY, False)]


def outro_card(names):
    half = (len(names) + 1) // 2
    lines = [" · ".join(names[:half]), " · ".join(names[half:])]
    return [Txt("Tak for kampene", 96, None, 300, WHITE), Rect(860, 450, 200, 8, ACCENT),
            Txt(lines[0], 44, None, 500, LIGHT, False), Txt(lines[1], 44, None, 566, LIGHT, False),
            Txt("Alle stats: jacquesbie.github.io/d9-streetball", 36, None, 720, ORANGE, False)]


def ffc(color: str) -> str:
    return "0x" + color.lstrip("#")


def rgb(color: str):
    c = color.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


FONTS_BOLD = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial Bold.ttf",
              "/System/Library/Fonts/Supplemental/Verdana Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "C:/Windows/Fonts/arialbd.ttf",
              "/System/Library/Fonts/Helvetica.ttc"]
FONTS_REGULAR = ["/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf",
                 "/System/Library/Fonts/Supplemental/Verdana.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans.ttf",
                 "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", "C:/Windows/Fonts/arial.ttf",
                 "/System/Library/Fonts/Helvetica.ttc"]


def find_fonts(override):
    if override:
        if not Path(override).expanduser().exists():
            die(f"Finder ikke skrifttypen {override}")
        return str(Path(override).expanduser()), str(Path(override).expanduser())
    bold = next((f for f in FONTS_BOLD if Path(f).exists()), None)
    regular = next((f for f in FONTS_REGULAR if Path(f).exists()), None)
    return bold or regular, regular or bold


class Drawtext:
    """Tekst med ffmpegs drawtext. Tekst og skrifttyper ligger som filer i arbejdsmappen, så
    filtergrafen ikke skal escape stier, mellemrum eller æøå."""

    def __init__(self, work: Path, fonts, s: float):
        self.work, self.s, self.n, self.font = work, s, 0, {}
        for key, src in zip(("b", "r"), fonts):
            self.font[key] = f"font_{key}{Path(src).suffix.lower()}"
            shutil.copyfile(src, work / self.font[key])

    def filters(self, items):
        s, out = self.s, []
        for it in items:
            if isinstance(it, Rect):
                out.append(f"drawbox=x={round(it.x * s)}:y={round(it.y * s)}:w={round(it.w * s)}:h={round(it.h * s)}"
                           f":color={ffc(it.color)}:t=fill")
                continue
            self.n += 1
            name = f"tekst{self.n:03d}.txt"
            (self.work / name).write_text(it.text, encoding="utf-8")
            x = "(w-text_w)/2" if it.x is None else str(round(it.x * s))
            f = (f"drawtext=fontfile={self.font['b' if it.bold else 'r']}:textfile={name}:expansion=none"
                 f":fontsize={round(it.size * s)}:fontcolor={ffc(it.color)}:x={x}:y={round(it.y * s)}")
            if it.box:
                f += f":box=1:boxcolor=black@0.6:boxborderw={round(14 * s)}"
            out.append(f)
        return out


class Pillow:
    """Tekst tegnet som PNG med Pillow og lagt oven på videoen; bruges når ffmpeg mangler drawtext."""

    def __init__(self, work: Path, fonts, W: int, H: int):
        from PIL import Image, ImageDraw, ImageFont
        self.Image, self.ImageDraw, self.ImageFont = Image, ImageDraw, ImageFont
        self.work, self.W, self.H, self.s, self.fonts, self.n, self.cache = work, W, H, H / 1080, fonts, 0, {}

    def font(self, size, bold):
        if (size, bold) not in self.cache:
            path = self.fonts[0 if bold else 1]
            self.cache[(size, bold)] = (self.ImageFont.truetype(path, size) if path
                                        else self.ImageFont.load_default(size))
        return self.cache[(size, bold)]

    def png(self, items, bg=None) -> str:
        s = self.s
        img = self.Image.new("RGBA", (self.W, self.H), rgb(bg) + (255,) if bg else (0, 0, 0, 0))
        d = self.ImageDraw.Draw(img)
        for it in items:
            if isinstance(it, Rect):
                d.rectangle([round(it.x * s), round(it.y * s), round((it.x + it.w) * s) - 1,
                             round((it.y + it.h) * s) - 1], fill=rgb(it.color) + (255,))
                continue
            f = self.font(round(it.size * s), it.bold)
            xy, anchor = ((self.W / 2, it.y * s), "mt") if it.x is None else ((it.x * s, it.y * s), "lt")
            if it.box:
                b = round(14 * s)
                x0, y0, x1, y1 = d.textbbox(xy, it.text, font=f, anchor=anchor)
                d.rectangle([x0 - b, y0 - b, x1 + b, y1 + b], fill=(0, 0, 0, 153))
            d.text(xy, it.text, font=f, fill=rgb(it.color) + (255,), anchor=anchor)
        self.n += 1
        name = f"tekst{self.n:03d}.png"
        img.save(self.work / name)
        return name


def has_drawtext() -> bool:
    out = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    return re.search(r"\sdrawtext\s", out) is not None


def pick_renderer(args, work, W, H):
    fonts = find_fonts(args.font)
    if args.tekst in ("auto", "drawtext") and fonts[0] and has_drawtext():
        return Drawtext(work, fonts, H / 1080)
    if args.tekst == "drawtext":
        die("ffmpeg mangler drawtext-filteret, eller der er ingen skrifttype (angiv en med --font).")
    if args.tekst in ("auto", "pillow"):
        try:
            import PIL  # noqa: F401
            return Pillow(work, fonts, W, H)
        except ImportError:
            pass
    if args.tekst == "ingen":
        return None
    die("Kan ikke skrive navne på videoen: ffmpeg mangler drawtext-filteret, og Pillow er ikke installeret.\n"
        "Løs det med:  python3 -m pip install --user pillow     (eller kør med --tekst ingen)")


def need_ffmpeg():
    missing = [t for t in ("ffmpeg", "ffprobe") if not shutil.which(t)]
    if missing:
        die(f"Mangler {' og '.join(missing)}. Installér med:  brew install ffmpeg")


def encode_args(fast: bool):
    return ["-c:v", "libx264", "-preset", "ultrafast" if fast else "medium", "-crf", "28" if fast else "20",
            "-pix_fmt", "yuv420p", "-r", str(FPS), "-video_track_timescale", "15360",
            "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2"]


def ffmpeg(cmd, cwd: Path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y"] + cmd,
                       cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        die("ffmpeg fejlede:\n" + r.stderr.strip()[-1500:])


def fades(d: float, audio=False) -> str:
    f = "afade" if audio else "fade"
    return f"{f}=t=in:st=0:d={FADE},{f}=t=out:st={d - FADE:.3f}:d={FADE}"


def render_card(items, d, out, R, W, H, fast, work):
    silence = ["-f", "lavfi", "-t", f"{d:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
    if isinstance(R, Pillow):
        src = ["-loop", "1", "-framerate", str(FPS), "-t", f"{d:.3f}", "-i", R.png(items, bg=BG)]
        chain = f"[0:v]scale={W}:{H},setsar=1,format=yuv420p,{fades(d)}[v]"
    else:
        src = ["-f", "lavfi", "-i", f"color=c={ffc(BG)}:s={W}x{H}:r={FPS}:d={d:.3f}"]
        chain = "[0:v]" + ",".join((R.filters(items) if R else []) + ["setsar=1", "format=yuv420p", fades(d)]) + "[v]"
    ffmpeg(src + silence + ["-filter_complex", chain, "-map", "[v]", "-map", "1:a", "-t", f"{d:.3f}"]
           + encode_args(fast) + [out], work)


def render_clip(m: Moment, sub, out, R, W, H, fast, work):
    d = m.dur
    cmd = ["-ss", f"{m.start:.3f}", "-t", f"{d:.3f}", "-i", str(m.path)]
    n, a = 1, "[0:a:0]"
    if not m.audio:
        cmd += ["-f", "lavfi", "-t", f"{d:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
        n, a = 2, "[1:a]"
    base = (f"[0:v:0]scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,"
            f"setsar=1,fps={FPS},format=yuv420p")
    items = lower_third(m.player, sub)
    if isinstance(R, Pillow):
        cmd += ["-i", R.png(items)]
        v = f"{base}[b];[{n}:v]format=rgba[o];[b][o]overlay=0:0,format=yuv420p,{fades(d)}[v]"
    else:
        v = ",".join([base] + (R.filters(items) if R else []) + [fades(d)]) + "[v]"
    aud = f"{a}aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,{fades(d, audio=True)}[a]"
    ffmpeg(cmd + ["-filter_complex", f"{v};{aud}", "-map", "[v]", "-map", "[a]", "-t", f"{d:.3f}"]
           + encode_args(fast) + [out], work)


def cmd_lav(args):
    need_ffmpeg()
    chosen, used, missing, roster, games = build_plan(args)
    print_plan(chosen, used, missing, roster, games, args.max)
    if missing and not args.tillad_mangler:
        die("Stopper, fordi ikke alle spillere er med. Tilføj klip for dem, eller kør med --tillad-mangler.", 2)

    out = Path(args.ud).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    W, H = (960, 540) if args.hurtig else (1920, 1080)
    work = Path(tempfile.mkdtemp(prefix="d9_highlights_", dir=out.parent))
    try:
        R = pick_renderer(args, work, W, H)
        dates = [m.date for m in chosen if m.date]
        first, last = min(dates, default=""), max(dates, default="")
        span = (f"{session_title(first)} – {session_title(last)} {last[:4]}" if first and first != last
                else f"{session_title(first)} {first[:4]}" if first else "")
        n_games = len({m.gkey for m in chosen})
        stats = f"{len(games) or n_games} kampe · {len(roster.names) or len({m.player for m in chosen})} spillere"
        steps = [("intro", intro_card(span, stats), INTRO)]
        date = None
        for m in chosen:
            if m.date != date:
                date = m.date
                if date:
                    gs = [g for g in games.values() if g.date == date]
                    sub = " · ".join(x for x in [gs[0].setup.split("·")[0].strip() if gs else "",
                                                 f"{len(gs)} kamp{'e' if len(gs) != 1 else ''}" if gs else ""] if x)
                    steps.append(("kort", session_card(session_title(date), sub), SESSION))
            steps.append(("klip", m, m.dur))
        names = sorted({m.player for m in chosen}, key=norm)
        steps.append(("outro", outro_card(names), OUTRO))

        parts = []
        print(f"\nLaver {len(steps)} dele i {W}x{H} ({'hurtig prøve' if args.hurtig else 'fuld kvalitet'}); "
              f"tekst: {type(R).__name__.lower() if R else 'ingen'}")
        for i, (kind, what, d) in enumerate(steps, start=1):
            name = f"del{i:03d}.mp4"
            if kind == "klip":
                print(f"  [{i:>2}/{len(steps)}] {what.player:<10} {what.path.name} {fmt_time(what.start)}", flush=True)
                render_clip(what, subtitle(what, games), name, R, W, H, args.hurtig, work)
            else:
                print(f"  [{i:>2}/{len(steps)}] {kind}", flush=True)
                render_card(what, d, name, R, W, H, args.hurtig, work)
            parts.append(name)
        (work / "liste.txt").write_text("".join(f"file '{p}'\n" for p in parts), encoding="utf-8")
        ffmpeg(["-f", "concat", "-safe", "0", "-i", "liste.txt", "-c", "copy", "-movflags", "+faststart", str(out)], work)
    finally:
        if args.behold_tmp:
            print(f"Mellemfiler ligger i {rel(work)}")
        else:
            shutil.rmtree(work, ignore_errors=True)

    length = Media([]).probe(out).duration
    size = out.stat().st_size / 1e6
    print(f"\nFærdig: {rel(out)}  ({fmt_time(length)}, {size:.0f} MB, "
          f"{len({m.player for m in chosen})} spillere)")
    if length > args.max:
        print(f"ADVARSEL: videoen er {fmt_time(length)}, over max {fmt_time(args.max)}.")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--site", default=str(SITE), help="stats-siden med spillere og kampe (index.html)")
    common.add_argument("--alias", action="append", default=[], metavar="NAVN=SPILLER",
                        help="rånavn i dataene der svarer til en spiller på stats-siden (kan gentages)")
    common.add_argument("--videomappe", action="append", default=[], metavar="MAPPE",
                        help="ekstra mappe at lede efter videoer i, fx /Volumes/GoPro (kan gentages)")
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("importer", parents=[common], help="find kurve i HoopStats-data og skriv klip.csv")
    pi.add_argument("mappe", nargs="?", default=str(HOOPSTATS), help="HoopStats-mappen (standard ~/HoopStatsLocal)")
    pi.add_argument("--ud", default=str(KLIP), help="hvor klip.csv skrives")
    pi.add_argument("--overskriv", action="store_true", help="erstat en eksisterende klip.csv")
    pi.add_argument("--video", action="append", default=[], metavar="KAMP=FIL[@SEK]",
                    help="video for en kamp; @SEK lægges til tiderne hvis de er målt fra kampstart")
    pi.add_argument("--alle-filer", action="store_true", help="brug alle datafiler, ikke kun den nyeste per kamp")
    pi.add_argument("--max-mb", type=float, default=150, help="spring datafiler over denne størrelse over")

    build = argparse.ArgumentParser(add_help=False)
    build.add_argument("--klip", default=str(KLIP), help="klip-listen (standard highlights/klip.csv)")
    build.add_argument("--max", type=float, default=300, help="max længde i sekunder (standard 300 = 5 min)")
    build.add_argument("--foer", type=float, default=5.5, help="sekunder med før kurven (standard 5.5)")
    build.add_argument("--efter", type=float, default=2.5, help="sekunder med efter kurven (standard 2.5)")
    build.add_argument("--tillad-mangler", action="store_true", help="lav videoen selvom ikke alle spillere er med")

    sub.add_parser("plan", parents=[common, build], help="vis hvilke klip der vælges, uden at lave video")
    pl = sub.add_parser("lav", parents=[common, build], help="lav highlight-videoen")
    pl.add_argument("--ud", default=str(UD / "D9_highlights.mp4"), help="output-fil")
    pl.add_argument("--hurtig", action="store_true", help="hurtig prøve i 960x540")
    pl.add_argument("--tekst", choices=["auto", "drawtext", "pillow", "ingen"], default="auto",
                    help="hvordan navne skrives på videoen (standard auto)")
    pl.add_argument("--font", help="skrifttype (.ttf) til teksten")
    pl.add_argument("--behold-tmp", action="store_true", help="behold de enkelte klip bagefter")

    args = p.parse_args(argv)
    for d in args.videomappe:
        if not Path(d).expanduser().is_dir():
            die(f"Finder ikke videomappen {d}. Skriv stien til mappen med videoerne, fx /Volumes/GoPro/DCIM, "
                "eller udelad --videomappe hvis videoerne ligger i ~/HoopStatsLocal.")
    {"importer": cmd_importer, "plan": cmd_plan, "lav": cmd_lav}[args.cmd](args)


if __name__ == "__main__":
    main()
