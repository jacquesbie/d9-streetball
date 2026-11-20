// Tilføjelse til forsiden: knapper til holdgeneratoren og fantasy-spillet øverst. index.html bygges forfra af build_site.py,
// så koden ligger her for sig, og deploy.sh sætter <script src="forside.js?v=..."> ind igen, hvis den mangler.
// PER, AST/TO og TS% lå her indtil 6. nov.; nu er de en del af forsiden selv (dashboard/index.html), så artifacten også har dem.
// Holdgeneratoren (hold/) kom til 12. nov., kampsiden (kampe/) 19. nov.
(function () {
  // Knapperne til kampsiden, holdgeneratoren og fantasy lå her til 20. nov.; nu står de i menuen øverst og som felter
  // nederst på forsiden (dashboard/site_sider.js, bygget ind i index.html).
  // Highlights fra seneste spilledag (19. nov): altid kun én video, highlight/seneste.mp4, lagt op af
  // HoopStatsLocal/highlights/udgiv_dag.py. Kortet står øverst, før første kort; videoen hentes først ved tryk.
  fetch('highlight/seneste.json', { cache: 'no-cache' }).then((r) => (r.ok ? r.json() : null)).then((h) => {
    const first = document.querySelector('#boxscore') || document.querySelector('section.d9-card');
    if (!h || !first || document.querySelector('#hl-card')) return;
    document.head.append(Object.assign(document.createElement('style'), { textContent: `
#hl-card video { width: 100%; max-width: 44rem; aspect-ratio: 16 / 9; background: #000; border-radius: var(--cds-radius); display: block; }` }));
    const card = Object.assign(document.createElement('section'), { className: 'd9-card', id: 'hl-card' });
    card.setAttribute('aria-labelledby', 'hl-h');
    const head = document.createElement('div');
    head.append(Object.assign(document.createElement('h2'), { id: 'hl-h', textContent: h.titel }),
      Object.assign(document.createElement('p'), { className: 'd9-note', textContent: 'Den samlede video fra seneste spilledag (' + Math.floor(h.sek / 60) + ' min ' + (h.sek % 60) + ' s). Den skiftes ud, hver gang der er spillet.' }));
    const v = Object.assign(document.createElement('video'), { controls: true, preload: 'none', playsInline: true, poster: 'highlight/seneste.jpg?v=' + h.v, src: 'highlight/seneste.mp4?v=' + h.v });
    card.append(head, v); first.before(card);
  }).catch(() => {});
})();
