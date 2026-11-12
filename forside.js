// Tilføjelse til forsiden: knapper til holdgeneratoren og fantasy-spillet øverst. index.html bygges forfra af build_site.py,
// så koden ligger her for sig, og deploy.sh sætter <script src="forside.js?v=..."> ind igen, hvis den mangler.
// PER, AST/TO og TS% lå her indtil 6. nov.; nu er de en del af forsiden selv (dashboard/index.html), så artifacten også har dem.
// Holdgeneratoren (hold/) kom til 12. nov.
(function () {
  const title = document.querySelector('header .d9-title');
  if (title && !document.querySelector('.d9-fantasy')) {
    document.head.append(Object.assign(document.createElement('style'), { textContent: `
.d9-topbar { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 8px 16px; }
.d9-toplinks { display: flex; flex-wrap: wrap; gap: 8px; }
.d9-fantasy { display: inline-flex; align-items: center; gap: 8px; font-size: var(--cds-font-size-body); font-weight: 600;
  text-decoration: none; color: var(--color-bg); background: var(--color-fg); border-radius: 999px; padding: 8px 16px; }
.d9-fantasy::before { content: ""; width: .6rem; height: .6rem; border-radius: 50%; background: var(--d9-accent); }
.d9-fantasy:hover { box-shadow: 0 0 0 3px var(--d9-accent); }
.d9-fantasy:focus-visible { outline: 2px solid var(--color-fg); outline-offset: 3px; }` }));
    const bar = Object.assign(document.createElement('div'), { className: 'd9-topbar' });
    const links = Object.assign(document.createElement('div'), { className: 'd9-toplinks' });
    title.before(bar);
    links.append(
      Object.assign(document.createElement('a'), { className: 'd9-fantasy', href: 'hold/', textContent: 'Holdgenerator →' }),
      Object.assign(document.createElement('a'), { className: 'd9-fantasy', href: 'fantasy/', textContent: 'Se fantasy-spillet →' }));
    bar.append(title, links);
  }
})();
