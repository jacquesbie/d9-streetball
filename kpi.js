// PER, AST/TO og TS% som de sidste tal i box score og i pivotens "Tal". index.html bygges forfra af build_site.py,
// så udvidelsen ligger her for sig, og deploy.sh sætter <script src="kpi.js"> ind igen, hvis den mangler.
// Den bygger på forsidens BOX_COLS, METRICS, boxFmt, fmt og drawAll; mangler de, gør den ingenting.
(function () {
  const R = (window.D9_DATA || {}).player_games;
  if (!R || typeof BOX_COLS === 'undefined' || typeof METRICS === 'undefined' || typeof boxFmt !== 'function' || typeof fmt !== 'function') {
    console.warn('kpi.js: forsiden mangler box score eller pivot, som kpi.js kan bygge videre på');
    return;
  }
  const n = (v) => (v === null || v === undefined || v === '' || !Number.isFinite(Number(v)) ? null : Number(v));
  const sum = (rs, f) => rs.reduce((t, r) => t + (f(r) || 0), 0);

  for (const r of R) {
    r.tov = n(r.TOV) ?? n(r.TO);
    // TS% på NBA-skalaen: en kurv indenfor tæller som en NBA-2'er og jeres 2'er som en 3'er, og TS% er point ÷ (2 × forsøg).
    // Der er ingen straffekast. Rammer man kun indenfor, er TS% det samme som FG%.
    const p1m = n(r.P1M), p2m = n(r.P2M), p1a = n(r.P1A), p2a = n(r.P2A);
    r.tsPts = p1m !== null && p2m !== null ? 2 * p1m + 3 * p2m : null;
    r.tsAtt = p1a !== null && p2a !== null ? 2 * (p1a + p2a) : null;
  }

  // PER efter Hollingers model, tilpasset D9: point, bomskud, rebounds og assists (plus steals, blocks og turnovers,
  // når de registreres) vægtes med, hvad en boldbesiddelse er værd i jeres kampe, og regnes pr. minut.
  // Hver kamp skaleres, så snittet i kampen er 15; det udligner format og kampe uden rebounds.
  const shot = R.filter((r) => n(r.PTS) !== null && n(r.FGA) !== null && n(r.MIN) > 0);
  const reb = shot.filter((r) => n(r.REB) !== null && n(r.OREB) !== null);
  const poss = sum(shot, (r) => n(r.FGA)) - sum(shot, (r) => n(r.OREB)) + sum(shot, (r) => r.tov);
  const vop = poss > 0 ? sum(shot, (r) => n(r.PTS)) / poss : 1;
  const trb = sum(reb, (r) => n(r.REB));
  const drbp = trb > 0 ? 1 - sum(reb, (r) => n(r.OREB)) / trb : 0.7;
  const fgm = sum(shot, (r) => n(r.FGM));
  const astVal = fgm > 0 ? sum(shot, (r) => n(r.PTS)) / fgm / 3 : 1 / 3;
  const value = (r) => {
    const orb = n(r.OREB) ?? 0, drb = n(r.DREB) ?? (n(r.REB) !== null ? n(r.REB) - orb : 0);
    return n(r.PTS) - vop * drbp * (n(r.FGA) - (n(r.FGM) || 0)) + vop * drbp * orb + vop * (1 - drbp) * drb
      + astVal * (n(r.AST) || 0) + vop * (n(r.STL) || 0) + vop * drbp * (n(r.BLK) || 0) - vop * (r.tov || 0);
  };
  const games = new Map();
  for (const r of shot) { if (!games.has(r.game_id)) games.set(r.game_id, []); games.get(r.game_id).push(r); }
  for (const rs of games.values()) {
    const perMin = sum(rs, value) / sum(rs, (r) => n(r.MIN));
    if (perMin > 0) for (const r of rs) { r.perVal = value(r); r.perExp = n(r.MIN) * perMin; }
  }

  // pct-kolonner og ratio-tal regner (a / b) × 100; PER er 15 × a / b, og AST/TO er a / b.
  const per = (v) => (v * 0.15).toFixed(1), perTo = (v) => (v / 100).toFixed(1);
  BOX_COLS.push(
    { id: 'PER', label: 'PER', pct: ['perVal', 'perExp'], kpi: per },
    { id: 'ASTTO', label: 'AST/TO', pct: ['AST', 'tov'], kpi: perTo },
    { id: 'TS', label: 'TS%', pct: ['tsPts', 'tsAtt'] },
  );
  const added = [
    { id: 'PER', label: 'PER (effektivitet, snit 15)', ratio: ['perVal', 'perExp'], kpi: per },
    { id: 'ASTTO', label: 'Assists pr. turnover (AST/TO)', ratio: ['AST', 'tov'], kpi: perTo },
    { id: 'TS', label: "True shooting (TS%, 2'ere og skud indenfor)", ratio: ['tsPts', 'tsAtt'] },
  ];
  METRICS.push(...added);
  const boxFmt0 = boxFmt, fmt0 = fmt;
  window.boxFmt = (c, v, mode) => (c.kpi ? (v === null || v === undefined ? '–' : c.kpi(v)) : boxFmt0(c, v, mode));
  window.fmt = (c, m, agg) => (m.kpi ? (c ? m.kpi(c.v) : '–') : fmt0(c, m, agg));
  if (typeof selMetric !== 'undefined') selMetric.append(...added.map((m) => new Option(m.label, m.id)));

  const note = document.querySelector('#boxscore .d9-note');
  if (note) note.after(Object.assign(document.createElement('p'), { className: 'd9-note', textContent:
    'PER, AST/TO og TS% står sidst. PER er effektivitet pr. minut, hvor 15 er snittet i de kampe, man spillede.'
    + " AST/TO kræver turnovers og vises, når de registreres. TS% regnes som i NBA, hvor en kurv indenfor svarer til en 2'er"
    + " og jeres 2'er til en 3'er (der er ingen straffekast). Rammer man kun indenfor, er TS% det samme som FG%, og 2'ere trækker op." }));
  if (typeof drawAll === 'function') drawAll();
})();
