// Zero-dependency behavior tests and static HTML/DOM interface contracts.
// Minimal node stubs do not constitute a browser or layout test. Paper recipes
// remain inert text and are never evaluated by these tests.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import vm from 'node:vm';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';

const website = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const source = fs.readFileSync(path.join(website, 'app.js'), 'utf8');

function between(start, end) {
  const first = source.indexOf(start);
  assert.notEqual(first, -1, `Missing function boundary: ${start}`);
  const last = source.indexOf(end, first + start.length);
  assert.notEqual(last, -1, `Missing function boundary: ${end}`);
  return source.slice(first, last);
}

function evaluate(body, bindings = {}) {
  const context = vm.createContext({...bindings});
  vm.runInContext(body, context, {timeout: 1000});
  return context;
}

const hasSourceDefinition = ['hasCode', 'hasLocalPptx', 'hasSource'].map((name) => source.match(new RegExp('const ' + name + ' = [^\\n]+'))[0]).join('\n');
const filterDefinition = between('function filteredAssets(', 'function card(');
const samplePapers = new Map([
  ['p1', {title: 'Paper One', topic: 'document parsing', venue: 'arXiv', year: '2026'}],
  ['p2', {title: 'Paper Two', topic: 'vision', venue: 'ICLR', year: '2025'}],
]);
const sampleAssets = [
  {id: 'method', paperId: 'p1', type: 'method', title: 'Blue framework', filename: 'm.png', sourceLabel: 'Figure 1', codes: []},
  {id: 'result', paperId: 'p1', type: 'result', title: 'Main result', filename: 'r.png', sourceLabel: 'Figure 2', codes: [{language: 'python', code: 'raise RuntimeError("never execute")'}]},
  {id: 'table', paperId: 'p2', type: 'table', title: 'Comparison', filename: 't.png', sourceLabel: 'Table 1', codes: [{language: 'latex', code: '\\begin{tabular}{c}1\\end{tabular}'}]},
];

function filtered(overrides = {}, saved = []) {
  const state = {view: 'explore', type: 'all', query: '', year: 'all', paperId: null, sourceOnly: false, sort: 'curated', density: 'comfortable', ...overrides};
  const context = evaluate(`${hasSourceDefinition}\n${filterDefinition}\nresult = filteredAssets(); allTypes = filteredAssets(true);`, {
    state, assets: sampleAssets, papers: samplePapers, saved: new Set(saved),
  });
  return {ids: Array.from(context.result, (asset) => asset.id), allTypes: Array.from(context.allTypes, (asset) => asset.id)};
}

test('type, year, keyword, paper and source filters compose', () => {
  assert.deepEqual(filtered().ids, ['method', 'result', 'table']);
  assert.deepEqual(filtered({type: 'result', year: '2026', query: 'PAPER ONE', sourceOnly: true}).ids, ['result']);
  assert.deepEqual(filtered({query: 'document parsing'}).ids, ['method', 'result']);
  assert.deepEqual(filtered({paperId: 'p2'}).ids, ['table']);
  assert.deepEqual(filtered({sourceOnly: true}).ids, ['result', 'table']);
  assert.deepEqual(filtered({query: '<script>'}).ids, []);
});

test('category counts ignore type but retain other constraints', () => {
  const result = filtered({type: 'result', year: '2026'});
  assert.deepEqual(result.ids, ['result']);
  assert.deepEqual(result.allTypes, ['method', 'result']);
});

test('favorites are browser-local IDs and compose with filters', () => {
  assert.deepEqual(filtered({view: 'saved'}, ['method', 'table', 'unknown']).ids, ['method', 'table']);
  assert.deepEqual(filtered({view: 'saved', sourceOnly: true}, ['method', 'table']).ids, ['table']);
  assert.deepEqual(filtered({view: 'saved'}, []).ids, []);
});

test('sourceCount follows the same code-presence rule as the source filter', () => {
  const catalogPath = path.join(website, 'dist', 'catalog.json');
  const catalog = fs.existsSync(catalogPath) ? JSON.parse(fs.readFileSync(catalogPath, 'utf8')) : {stats: {sourceCount: 2}, assets: sampleAssets};
  const context = evaluate(`${hasSourceDefinition}\ncount = assets.filter(hasSource).length;`, {assets: catalog.assets});
  assert.equal(context.count, catalog.stats.sourceCount);
});

test('PPTX-only assets count as source without counting code plus PPTX twice', () => {
  const assets = [
    {...sampleAssets[0], downloads: [{format: 'pptx', local: true, url: 'assets/papers/p1/method_figures/m.pptx'}]},
    {...sampleAssets[1], downloads: [{format: 'pptx', local: true, url: 'assets/papers/p1/method_figures/r.pptx'}]},
    {...sampleAssets[0], id: 'external', downloads: [{format: 'pptx', local: false, url: 'https://example.com/deck.pptx'}]},
  ];
  const context = evaluate(`${hasSourceDefinition}\ncount = assets.filter(hasSource).length; pptx = assets.filter(hasLocalPptx).length; onlyCode = assets.filter(hasCode).length;`, {assets});
  assert.equal(context.count, 2);
  assert.equal(context.pptx, 2);
  assert.equal(context.onlyCode, 1);
});

test('PPTX-only cards display a PPTX badge rather than an empty SOURCE badge', () => {
  const asset = {...sampleAssets[0], downloads: [{format: 'pptx', local: true, url: 'assets/papers/p1/method_figures/m.pptx'}]};
  const context = evaluate(`${hasSourceDefinition}\n${between('function card(', 'function renderPapers(')}\nhtml = card(asset);`, {
    asset, papers: samplePapers, saved: new Set(), shortPaper: (paper) => paper.title,
    safeUrl: (url) => url, esc: String, icon: () => '', typeLabels: {method: 'METHOD'},
  });
  assert.match(context.html, /PPTX/);
  assert.match(context.html, /data-tab="code"/);
  assert.doesNotMatch(context.html, / SOURCE/);
});

test('PPTX-only dialog hides empty code blocks and describes the file check honestly', () => {
  const heading = {textContent: ''}, description = {textContent: ''};
  const nodes = new Map(['code-toolbar', 'source-code', 'source-bottom', 'copy-rebuild-prompt'].map((id) => [id, {hidden: false}]));
  nodes.set('no-code', {hidden: true, querySelector: (selector) => selector === 'h3' ? heading : description});
  const asset = {...sampleAssets[0], downloads: [{format: 'pptx', local: true}]};
  evaluate(`${hasSourceDefinition}\n${between('function renderSourceState(', 'function openAsset(')}\nrenderSourceState(asset);`, {$: (id) => nodes.get(id), asset});
  assert.equal(nodes.get('source-code').hidden, true);
  assert.equal(nodes.get('code-toolbar').hidden, true);
  assert.equal(nodes.get('source-bottom').hidden, true);
  assert.equal(nodes.get('no-code').hidden, false);
  assert.equal(nodes.get('copy-rebuild-prompt').hidden, true);
  assert.match(heading.textContent, /PPTX/);
  assert.match(description.textContent, /暂无单独的文本代码/);
  assert.match(description.textContent, /不代表视觉或原生对象可编辑性验收/);
  assert.doesNotMatch(description.textContent, /暂无可编辑资产/);
});

test('local PPTX links download the actual filename; external sources remain external', () => {
  const safeUrlDefinition = between('const safeUrl = ', 'const cleanText = ');
  const definition = between('function downloadLinks(', 'function renderSourceState(');
  const rows = [
    {label: 'PPTX', format: 'pptx', local: true, filename: 'method.pptx', url: 'assets/papers/p1/method_figures/method.pptx'},
    {label: 'PPTX (external)', format: 'pptx', local: false, filename: 'source.pptx', url: 'https://example.com/source.pptx'},
  ];
  const context = evaluate(`${safeUrlDefinition}\n${definition}\nlocal = downloadLinks([rows[0]]); external = downloadLinks([rows[1]]);`, {rows, esc: String, icon: () => ''});
  assert.match(context.local, /href="assets\/papers\/p1\/method_figures\/method\.pptx"/);
  assert.match(context.local, /download="method\.pptx"/);
  assert.doesNotMatch(context.local, /target=/);
  assert.match(context.external, /target="_blank"/);
  assert.doesNotMatch(context.external, / download=/);
});

test('method dialog includes explicit combined paper deck without inferring per-asset source', () => {
  const asset = {...sampleAssets[0], downloads: [{label: 'Image', url: 'assets/papers/p1/method_figures/m.png'}]};
  const paper = {downloads: [{label: 'Method figures PPTX (combined)', url: 'assets/papers/p1/method_figures/method_figures_editable.pptx', format: 'pptx', local: true}]};
  const context = evaluate(`${hasSourceDefinition}\n${between('function relatedDownloads(', 'function downloadLinks(')}\nrows = relatedDownloads(asset, paper); source = hasSource(asset); resultRows = relatedDownloads({...asset, type: 'result'}, paper);`, {asset, paper});
  assert.equal(context.rows.length, 2);
  assert.equal(context.rows[1].format, 'pptx');
  assert.equal(context.source, false);
  assert.equal(context.resultRows.length, 1);
});

test('unsafe URL schemes and encoded relative traversal are rejected', () => {
  const definition = between('const safeUrl = ', 'const cleanText = ');
  const context = evaluate(`${definition}\nglobalThis.check = safeUrl;`);
  for (const url of ['javascript:alert(1)', 'data:text/html,<script>1</script>', '//evil.example/image.png', 'assets/../../private.png', 'assets/%2e%2e/%2e%2e/private.png', 'assets/%2E%2E/private.png']) {
    assert.equal(context.check(url), '#', url);
  }
  assert.equal(context.check('assets/papers/p/result_figures/figure.png'), 'assets/papers/p/result_figures/figure.png');
  assert.equal(context.check('guides/GETTING_STARTED.md'), 'guides/GETTING_STARTED.md');
  assert.equal(context.check('https://arxiv.org/abs/1234.5678'), 'https://arxiv.org/abs/1234.5678');
});

test('recipe rendering uses textContent, not HTML or eval', () => {
  const code = {language: 'python', code: '<img src=x onerror="unsafeExecuted=true">\nthrow new Error("Do not run recipes")'};
  const nodes = new Map([
    ['source-code-text', {innerHTML: 'untouched', textContent: ''}],
    ['source-help', {textContent: ''}], ['download-code', {disabled: true}],
  ]);
  const context = evaluate(between('function renderCode()', 'function citationText(') + '\nrenderCode();', {selectedCode: () => code, $: (id) => nodes.get(id), unsafeExecuted: false});
  assert.equal(nodes.get('source-code-text').textContent, code.code);
  assert.equal(nodes.get('source-code-text').innerHTML, 'untouched');
  assert.equal(context.unsafeExecuted, false);
  assert.equal(nodes.get('download-code').disabled, false);
});

test('Required Packages download remains a preamble fragment, not a broken document', () => {
  const packages = {language: 'latex', label: 'Required Packages', code: '\\usepackage{booktabs}\n\\usepackage{graphicx}\n'};
  const downloads = [];
  evaluate(between('function downloadCode()', 'function initialize()') + '\ndownloadCode();', {
    selectedCode: () => packages,
    activeAsset: {paperId: 'p1', filename: 'table.png', codes: [{language: 'latex', label: 'LaTeX Source', code: '\\begin{tabular}{c}1\\end{tabular}'}, packages]},
    download: (text, filename, mime) => downloads.push({text, filename, mime}), toast: () => {},
  });
  assert.equal(downloads.length, 1);
  assert.equal(downloads[0].text, packages.code);
  assert.match(downloads[0].filename, /_packages\.tex$/);
});

test('main LaTeX source download includes the packages before the document body', () => {
  const code = {language: 'latex', label: 'LaTeX Source', code: '\\begin{tabular}{c}1\\end{tabular}'};
  const downloads = [];
  evaluate(between('function downloadCode()', 'function initialize()') + '\ndownloadCode();', {
    selectedCode: () => code,
    activeAsset: {paperId: 'p1', filename: 'table.png', codes: [code, {language: 'latex', label: 'Required Packages', code: '\\usepackage{booktabs}'}]},
    download: (text, filename, mime) => downloads.push({text, filename, mime}), toast: () => {},
  });
  const output = downloads[0].text;
  assert.ok(output.indexOf('\\usepackage{booktabs}') < output.indexOf('\\begin{document}'));
  assert.ok(output.indexOf(code.code) > output.indexOf('\\begin{document}'));
  assert.ok(output.endsWith('\\end{document}\n'));
});

function nodeStub(extra = {}) {
  const classes = new Set();
  return {
    hidden: false, value: '', textContent: '', innerHTML: '', checked: false,
    dataset: {}, attributes: {}, focusCount: 0, isConnected: true,
    classList: {
      add: (name) => classes.add(name), remove: (name) => classes.delete(name),
      contains: (name) => classes.has(name),
      toggle: (name, force) => {
        const selected = force === undefined ? !classes.has(name) : Boolean(force);
        if (selected) classes.add(name); else classes.delete(name);
        return selected;
      },
    },
    setAttribute(name, value) { this.attributes[name] = String(value); },
    getAttribute(name) { return this.attributes[name] ?? null; },
    removeAttribute(name) { delete this.attributes[name]; },
    focus() { this.focusCount++; }, contains() { return false; }, closest() { return null; },
    ...extra,
  };
}

test('curated order is unchanged while newest/title sorts are stable and non-mutating', () => {
  const papers = new Map([
    ['old', {year: '2025'}], ['new-a', {year: '2026'}],
    ['new-b', {year: '2026'}], ['unknown', {year: 'Not documented'}],
  ]);
  const assets = [
    {id: 'old', paperId: 'old', title: 'Beta', type: 'method'},
    {id: 'new-a', paperId: 'new-a', title: 'Alpha', type: 'method'},
    {id: 'new-b', paperId: 'new-b', title: 'Alpha', type: 'method'},
    {id: 'unknown', paperId: 'unknown', title: 'Gamma', type: 'method'},
  ];
  const state = {view: 'explore', type: 'all', query: '', year: 'all', paperId: null, sourceOnly: false, sort: 'curated'};
  const context = evaluate(`${hasSourceDefinition}\n${filterDefinition}\ncurated = filteredAssets().map(a => a.id); state.sort = 'newest'; newest = filteredAssets().map(a => a.id); state.sort = 'title'; titled = filteredAssets().map(a => a.id);`, {state, assets, papers, saved: new Set()});
  assert.deepEqual(Array.from(context.curated), ['old', 'new-a', 'new-b', 'unknown']);
  assert.deepEqual(Array.from(context.newest), ['new-a', 'new-b', 'old', 'unknown']);
  assert.deepEqual(Array.from(context.titled), ['new-a', 'new-b', 'old', 'unknown']);
  assert.deepEqual(assets.map(a => a.id), ['old', 'new-a', 'new-b', 'unknown']);
  assert.deepEqual(filtered({sort: 'title', year: '2026', sourceOnly: true}).ids, ['result']);
});

test('density changes only layout and pressed buttons, without resetting collection state', () => {
  const grid = nodeStub();
  const buttons = ['comfortable', 'compact'].map((density) => nodeStub({dataset: {density}}));
  const state = {density: 'comfortable', query: 'document', type: 'result', limit: 54};
  const definition = between('function setDensity(', 'function syncCollectionControls(');
  const context = evaluate(`${definition}\nvalid = setDensity('compact'); invalid = setDensity('tiny');`, {
    state, $: (id) => { assert.equal(id, 'asset-grid'); return grid; },
    document: {querySelectorAll: (selector) => { assert.equal(selector, 'button[data-density]'); return buttons; }},
  });
  assert.equal(context.valid, true); assert.equal(context.invalid, false);
  assert.equal(grid.dataset.density, 'compact');
  assert.equal(buttons[0].getAttribute('aria-pressed'), 'false');
  assert.equal(buttons[1].getAttribute('aria-pressed'), 'true');
  assert.deepEqual(state, {density: 'compact', query: 'document', type: 'result', limit: 54});
});

test('paper select, clear chip and clear-filters stay in sync; reset retains sort and density', () => {
  const nodes = new Map(['search', 'year', 'source-only', 'paper-select', 'sort', 'paper-filter-chip', 'clear-filters', 'asset-grid'].map((id) => [id, nodeStub()]));
  const state = {type: 'result', query: 'blue', year: '2026', paperId: 'p1', sourceOnly: true, sort: 'newest', density: 'compact', limit: 54};
  const definitions = between('function resetFilters()', 'function updateDrawer()');
  const context = evaluate(`${definitions}\nsyncCollectionControls(); first = {paper: $('paper-select').value, chip: $('paper-filter-chip').textContent, clear: $('clear-filters').hidden}; resetFilters(); after = {paper: $('paper-select').value, chipHidden: $('paper-filter-chip').hidden, clearHidden: $('clear-filters').hidden, sort: $('sort').value};`, {
    state, papers: samplePapers, shortPaper: (paper) => paper.title, $: (id) => nodes.get(id),
    document: {querySelectorAll: () => []},
  });
  assert.equal(context.first.paper, 'p1'); assert.match(context.first.chip, /Paper One/);
  assert.equal(context.first.clear, false);
  assert.equal(context.after.paper, 'all'); assert.equal(context.after.chipHidden, true);
  assert.equal(context.after.clearHidden, true); assert.equal(context.after.sort, 'newest');
  assert.equal(state.density, 'compact'); assert.equal(state.sort, 'newest'); assert.equal(state.limit, 18);
  assert.equal(nodes.get('search').value, ''); assert.equal(nodes.get('source-only').checked, false);
});

test('card metadata is below the image and palette dots accept at most four strict HEX colors', () => {
  const asset = {...sampleAssets[0], title: '<script>not executable</script>', sourceLabel: 'Figure <1>', palette: [
    {hex: '#112233'}, {hex: '#445566'}, {hex: '#778899'}, {hex: '#AABBCC'},
    {hex: '#DDEEFF'}, {hex: '#123'}, {hex: '#112233" onclick="unsafe()'},
    {hex: 'url(javascript:unsafe())'}, null,
  ]};
  const escaping = between('const esc = ', 'const safeUrl = ');
  const context = evaluate(`${escaping}\n${hasSourceDefinition}\n${between('function card(', 'function renderPapers(')}\nhtml = card(asset);`, {
    asset, papers: samplePapers, saved: new Set(), shortPaper: (paper) => paper.title,
    safeUrl: (url) => url, icon: () => '', typeLabels: {method: 'METHOD'},
  });
  const preview = context.html.split('<div class="asset-info">')[0].split('<div class="asset-preview">')[1];
  assert.match(preview, /<img /); assert.match(preview, /data-save=/);
  assert.doesNotMatch(preview, /asset-type|asset-kicker|palette-dots/);
  assert.match(context.html, /asset-kicker/); assert.match(context.html, /Figure &lt;1&gt;/);
  assert.equal((context.html.match(/class="palette-dot"/g) || []).length, 4);
  assert.doesNotMatch(context.html, /onclick=|javascript:|<script>/);
});

test('card category attributes use a strict whitelist and each known category has its Chinese label', () => {
  const escaping = between('const esc = ', 'const safeUrl = ');
  const labels = source.match(/const typeLabels = [^\n]+/)[0];
  const definition = `${escaping}\n${hasSourceDefinition}\n${labels}\n${between('function card(', 'function renderPapers(')}`;
  const bindings = {papers: samplePapers, saved: new Set(), shortPaper: (paper) => paper.title, safeUrl: String, icon: () => ''};
  for (const [type, label] of [['method', '方法框架'], ['result', '结果分析'], ['table', '论文表格']]) {
    const context = evaluate(`${definition}\nhtml = card(asset);`, {...bindings, asset: {...sampleAssets[0], type}});
    assert.match(context.html, new RegExp(`<article class="asset-card" data-asset-type="${type}">`));
    assert.match(context.html, new RegExp(`<span class="asset-type ${type}">${label}</span>`));
  }
  for (const type of ['unknown', '__proto__', 'method" onclick="unsafe()', '<script>unsafe()</script>', null]) {
    const context = evaluate(`${definition}\nhtml = card(asset);`, {...bindings, asset: {...sampleAssets[0], type}});
    assert.match(context.html, /<article class="asset-card" data-asset-type="figure">/);
    assert.match(context.html, /<span class="asset-type figure">图表<\/span>/);
    assert.doesNotMatch(context.html, /onclick=|<script>|__proto__/);
  }
});

test('category rendering synchronizes modules, grid category and honest resource descriptions', () => {
  const nodes = new Map();
  const get = (id) => { if (!nodes.has(id)) nodes.set(id, nodeStub()); return nodes.get(id); };
  const buttons = ['all', 'method', 'result', 'table'].map((type) => nodeStub({dataset: {type}}));
  const state = {view: 'explore', type: 'all', limit: 18};
  const context = evaluate(`${between('function render()', 'function resetFilters()')}\nrun = render;`, {
    state, $: get, catalog: {papers: []}, saved: new Set(),
    syncCollectionControls: () => {}, renderPapers: () => {}, card: (asset) => asset.id,
    filteredAssets: (ignoreType) => sampleAssets.filter((asset) => ignoreType || state.type === 'all' || asset.type === state.type),
    document: {querySelectorAll: (selector) => selector === '[data-type]' ? buttons : []},
    typeNames: {method: '方法框架', result: '结果分析', table: '论文表格'},
  });
  for (const [type, resource] of [['all', '完整看图 · 带走配方'], ['method', 'PPTX / 配色'], ['result', 'Python'], ['table', 'LaTeX']]) {
    state.type = type; context.run();
    assert.equal(get('category-modules').hidden, false);
    assert.equal(get('asset-grid').dataset.category, type);
    assert.ok(get('catalog-note').textContent.includes(resource));
    if (type !== 'all') assert.match(get('catalog-note').textContent, /按条目提供/);
    assert.doesNotMatch(get('catalog-note').textContent, /每张|完美|完整复现|保证/);
    for (const button of buttons) {
      assert.equal(button.getAttribute('aria-pressed'), String(button.dataset.type === type));
      assert.equal(button.classList.contains('active'), button.dataset.type === type);
    }
    assert.equal(get('count-all').textContent, 3);
    assert.equal(get('count-method').textContent, 1); assert.equal(get('count-result').textContent, 1); assert.equal(get('count-table').textContent, 1);
  }
  state.view = 'papers'; context.run(); assert.equal(get('category-modules').hidden, true);
  state.view = 'saved'; context.run(); assert.equal(get('category-modules').hidden, false);
});

test('detail navigation uses the whole filtered queue and never wraps or jumps from an absent asset', () => {
  const rows = Array.from({length: 25}, (_, i) => ({id: `a${i}`}));
  const definition = between('function dialogNavigation(', 'function updateDialogNavigation(');
  const context = evaluate(`${definition}\nfirst = dialogNavigation(rows, 'a0'); pageEdge = dialogNavigation(rows, 'a17'); last = dialogNavigation(rows, 'a24'); missing = dialogNavigation(rows, 'gone'); empty = dialogNavigation([], 'a0'); single = dialogNavigation([rows[0]], 'a0');`, {rows});
  assert.equal(context.first.previousId, null); assert.equal(context.first.nextId, 'a1');
  assert.equal(context.pageEdge.nextId, 'a18'); assert.equal(context.pageEdge.total, 25);
  assert.equal(context.last.nextId, null); assert.equal(context.last.previousId, 'a23');
  assert.equal(context.missing.index, -1); assert.equal(context.missing.nextId, null); assert.equal(context.missing.previousId, null);
  assert.equal(context.empty.total, 0); assert.equal(context.single.nextId, null); assert.equal(context.single.previousId, null);
});

test('detail position and boundary-disabled buttons reflect current matches, including removed favorites', () => {
  const rows = [{id: 'a'}, {id: 'b'}];
  const nodes = new Map(['previous-asset', 'next-asset', 'dialog-position'].map(id => [id, nodeStub()]));
  const definitions = between('function dialogNavigation(', 'function navigateAsset(');
  const context = evaluate(`${definitions}\nupdateDialogNavigation(); first = [$('previous-asset').disabled, $('next-asset').disabled, $('dialog-position').textContent]; activeAsset = {id:'b'}; updateDialogNavigation(); last = [$('previous-asset').disabled, $('next-asset').disabled]; activeAsset = {id:'removed'}; updateDialogNavigation(); missing = [$('previous-asset').disabled, $('next-asset').disabled, $('dialog-position').textContent];`, {
    activeAsset: {id: 'a'}, filteredAssets: () => rows, $: (id) => nodes.get(id),
  });
  assert.deepEqual(Array.from(context.first), [true, false, '1 / 2']);
  assert.deepEqual(Array.from(context.last), [false, true]);
  assert.deepEqual(Array.from(context.missing), [true, true, '— / 2']);
});

test('next/previous updates only the dialog, preserves its selected tab, and respects boundaries', () => {
  const rows = Array.from({length: 25}, (_, i) => ({id: `a${i}`}));
  const opened = [];
  const state = {query: 'unchanged', limit: 18, sort: 'title', density: 'compact'};
  const definitions = between('function dialogNavigation(', 'function updateDialogNavigation(') + between('function navigateAsset(', 'function shouldNavigateAsset(');
  const context = evaluate(`${definitions}\nnext = navigateAsset(1); activeAsset = {id:'a0'}; firstPrevious = navigateAsset(-1); activeAsset = {id:'gone'}; missingNext = navigateAsset(1); invalid = navigateAsset(0);`, {
    state, activeAsset: {id: 'a17'}, filteredAssets: () => rows, openAsset: (id, tab) => opened.push({id, tab}),
    document: {querySelector: () => ({dataset: {detailTab: 'palette'}})},
  });
  assert.equal(context.next, true); assert.equal(context.firstPrevious, false);
  assert.equal(context.missingNext, false); assert.equal(context.invalid, false);
  assert.deepEqual(opened, [{id: 'a18', tab: 'palette'}]);
  assert.deepEqual(state, {query: 'unchanged', limit: 18, sort: 'title', density: 'compact'});
});

test('left/right navigation does not steal input, code, tab, editing or modified-key interactions', () => {
  const definition = between('function shouldNavigateAsset(', 'function setImageExpanded(');
  const context = evaluate(`${definition}\ncheck = shouldNavigateAsset;`);
  const plain = {closest: () => null};
  assert.equal(context.check({key: 'ArrowRight', target: plain}, true), true);
  assert.equal(context.check({key: 'ArrowLeft', target: plain}, false), false);
  for (const modifier of ['ctrlKey', 'altKey', 'metaKey', 'shiftKey', 'defaultPrevented', 'isComposing']) {
    assert.equal(context.check({key: 'ArrowRight', target: plain, [modifier]: true}, true), false, modifier);
  }
  for (const ancestor of ['input', 'textarea', 'select', 'pre', 'code', '[role="tab"]', '[data-detail-tab]', '[contenteditable]']) {
    const target = {closest: (selector) => { assert.ok(selector.includes(ancestor.replace(/\]$/, '').replace(/\[contenteditable$/, '[contenteditable'))); return {}; }};
    assert.equal(context.check({key: 'ArrowLeft', target}, true), false, ancestor);
  }
  assert.equal(context.check({key: 'ArrowRight', target: {isContentEditable: true}}, true), false);
  assert.equal(context.check({key: 'Home', target: plain}, true), false);
});

test('opening the next image resets zoom and preserves the initial outside-dialog focus', () => {
  const nodes = new Map();
  const get = (id) => { if (!nodes.has(id)) nodes.set(id, nodeStub()); return nodes.get(id); };
  const dialog = get('asset-dialog'); dialog.open = false; dialog.showModal = () => { dialog.open = true; };
  const initialFocus = nodeStub(), nextButton = nodeStub();
  const doc = {activeElement: initialFocus};
  const zoomChanges = [];
  const asset = {...sampleAssets[0], src: 'assets/papers/p1/method_figures/m.png', palette: [], downloads: [], codes: []};
  const context = evaluate(between('function openAsset(', 'function downloadCode()') + '\nopenAsset("a"); document.activeElement = nextButton; openAsset("b");', {
    assetsById: new Map([['a', {...asset, id: 'a'}], ['b', {...asset, id: 'b'}]]), papers: samplePapers,
    activeAsset: null, previousFocus: null, document: doc, nextButton,
    $: get, cleanText: String, safeUrl: String, typeLabels: {method: 'METHOD'},
    setImageExpanded: (expanded) => zoomChanges.push(expanded), renderSourceState: () => {}, renderCode: () => {},
    updateDialogSave: () => {}, updateDialogNavigation: () => {}, setTab: () => {},
    relatedDownloads: () => [], downloadLinks: () => '', esc: String, icon: () => '',
  });
  assert.equal(context.previousFocus, initialFocus); assert.equal(context.activeAsset.id, 'b');
  assert.deepEqual(zoomChanges, [false, false]); assert.equal(dialog.open, true);
});

test('zoom state and close cleanup reset aria, use the original focus, and fall back if disconnected', () => {
  const nodes = new Map(['asset-dialog', 'zoom-image', 'main'].map(id => [id, nodeStub()]));
  const original = nodeStub();
  const definitions = between('function setImageExpanded(', 'function updateDialogSave(');
  const context = evaluate(`${definitions}\nsetImageExpanded(true); enlarged = $('asset-dialog').classList.contains('image-expanded'); handleDialogClose(); activeAfter = activeAsset; previousAfter = previousFocus; previousFocus = disconnected; activeAsset = {id:'b'}; handleDialogClose();`, {
    $: (id) => nodes.get(id), activeAsset: {id: 'a'}, previousFocus: original,
    disconnected: nodeStub({isConnected: false}), updateDialogNavigation: () => {},
  });
  assert.equal(context.enlarged, true); assert.equal(context.activeAfter, null); assert.equal(context.previousAfter, null);
  assert.equal(nodes.get('asset-dialog').classList.contains('image-expanded'), false);
  assert.equal(nodes.get('zoom-image').getAttribute('aria-pressed'), 'false');
  assert.equal(original.focusCount, 1); assert.equal(nodes.get('main').focusCount, 1);
});

test('mobile navigation uses 760px, backdrop/inert/aria stay consistent, and desktop resize clears open state', () => {
  const nodes = new Map(['sidebar', 'main', 'menu-backdrop', 'mobile-menu'].map(id => [id, nodeStub()]));
  let width = 760;
  const body = nodeStub();
  const window = {matchMedia: (query) => { assert.equal(query, '(max-width:760px)'); return {matches: width <= 760}; }};
  const definitions = between('function updateDrawer()', 'function changeView(');
  const context = evaluate(`${definitions}\nupdateDrawer(); check = updateDrawer; close = closeDrawer;`, {
    $: (id) => nodes.get(id), window, document: {body, activeElement: null},
  });
  assert.equal(nodes.get('sidebar').inert, true); assert.equal(nodes.get('menu-backdrop').hidden, true);
  nodes.get('sidebar').classList.add('open'); context.check();
  assert.equal(nodes.get('main').inert, true); assert.equal(nodes.get('sidebar').inert, false);
  assert.equal(nodes.get('menu-backdrop').hidden, false); assert.equal(body.classList.contains('menu-open'), true);
  assert.equal(nodes.get('mobile-menu').getAttribute('aria-expanded'), 'true');
  context.close(true); assert.equal(nodes.get('mobile-menu').focusCount, 1);
  nodes.get('sidebar').classList.add('open'); width = 761; context.check();
  assert.equal(nodes.get('sidebar').classList.contains('open'), false);
  assert.equal(nodes.get('main').inert, false); assert.equal(nodes.get('sidebar').inert, false);
  assert.equal(nodes.get('menu-backdrop').hidden, true); assert.equal(body.classList.contains('menu-open'), false);
  width = 760; context.check(); assert.equal(nodes.get('sidebar').inert, true);
});

test('static HTML includes every JS ID contract once, plus dynamic tabs/counts and the new controls', () => {
  const html = fs.readFileSync(path.join(website, 'index.html'), 'utf8');
  const ids = Array.from(html.matchAll(/\bid=["']([^"']+)["']/g), (match) => match[1]);
  assert.equal(ids.length, new Set(ids).size, 'Duplicate HTML IDs');
  const required = new Set(Array.from(source.matchAll(/\$\('([^']+)'\)/g), (match) => match[1]));
  for (const id of ['count-all', 'count-method', 'count-result', 'count-table', 'panel-code', 'panel-palette', 'panel-citation']) required.add(id);
  for (const id of required) assert.ok(ids.includes(id), `Missing required HTML ID: ${id}`);
  assert.match(html, /<nav\b[^>]*\bid=["']sidebar["']/);
  assert.match(html, /<button\b[^>]*\bdata-density=["']comfortable["']/);
  assert.match(html, /<button\b[^>]*\bdata-density=["']compact["']/);
  for (const option of ['curated', 'newest', 'title']) assert.match(html, new RegExp('<option\\b[^>]*value=["\']' + option + '["\']'));
  const scripts = [...html.matchAll(/<script\b[^>]*\bsrc=["']([^"']+)["']/g)].map((match) => match[1].split('?')[0]);
  assert.ok(scripts.includes('catalog.js') && scripts.indexOf('catalog.js') < scripts.indexOf('app.js'));
  assert.doesNotMatch(source, /\$\('(?:hero-specimen|hero-image|hero-paper-name|hero-code-preview|stat-sources)'\)/);
  assert.match(source, /method_pptx=on/);
  assert.match(source, /导出后渲染并与原图逐页核对/);
});

test('the three category modules are unique buttons with their own unique counter IDs', () => {
  const html = fs.readFileSync(path.join(website, 'index.html'), 'utf8');
  assert.equal([...html.matchAll(/\bid=["']category-modules["']/g)].length, 1);
  const buttons = [...html.matchAll(/<button\b([^>]*)>([\s\S]*?)<\/button>/g)];
  const modules = buttons.filter((match) => /\bclass=["'][^"']*\bcategory-module\b[^"']*["']/.test(match[1]));
  assert.equal(modules.length, 3);
  for (const type of ['method', 'result', 'table']) {
    const matches = modules.filter((match) => new RegExp(`\\bdata-type=["']${type}["']`).test(match[1]));
    assert.equal(matches.length, 1, `Exactly one ${type} category module`);
    assert.match(matches[0][1], /\baria-pressed=["']false["']/);
    assert.match(matches[0][2], new RegExp(`\\bid=["']count-${type}["']`));
    assert.equal([...html.matchAll(new RegExp(`\\bid=["']count-${type}["']`, 'g'))].length, 1);
    assert.equal(buttons.filter((match) => new RegExp(`\\bdata-type=["']${type}["']`).test(match[1])).length, 1);
  }
  assert.equal(buttons.filter((match) => /\bdata-type=["']all["']/.test(match[1])).length, 1);
});

// Optional real-DOM behavior smoke. Supply an already-installed linkedom entry
// through FIGARIUM_DOM_MODULE_PATH; the repository has no npm dependency and
// this test never installs packages, opens a browser, loads media or makes HTTP.
// Missing layout/focus/modal APIs are deliberately simulated, not browser QA.
function domHarness(catalog) {
  const require = createRequire(import.meta.url);
  const {parseHTML} = require(process.env.FIGARIUM_DOM_MODULE_PATH);
  const {window, document} = parseHTML(fs.readFileSync(path.join(website, 'index.html'), 'utf8'));
  let focused = document.body;
  let width = 1200;
  const storage = new Map(), clipboard = [], downloads = [], blobs = [];
  Object.defineProperty(document, 'activeElement', {get: () => focused});
  window.HTMLElement.prototype.focus = function () { focused = this; };
  window.HTMLElement.prototype.scrollIntoView = function () {};
  Object.defineProperty(window.HTMLElement.prototype, 'inert', {
    configurable: true,
    get() { return this.hasAttribute('inert'); },
    set(value) { if (value) this.setAttribute('inert', ''); else this.removeAttribute('inert'); },
  });
  // Linkedom's select.value is getter-only; mirror native selection semantics.
  Object.defineProperty(window.HTMLSelectElement.prototype, 'value', {
    configurable: true,
    get() { return this.querySelector('option[selected]')?.value ?? this.querySelector('option')?.value ?? ''; },
    set(value) { for (const option of this.querySelectorAll('option')) option.toggleAttribute('selected', option.value === String(value)); },
  });
  const dialog = document.getElementById('asset-dialog');
  Object.defineProperty(dialog, 'open', {get: () => dialog.hasAttribute('open')});
  dialog.showModal = () => { dialog.setAttribute('open', ''); };
  dialog.close = () => { dialog.removeAttribute('open'); dialog.dispatchEvent(new window.Event('close')); };
  window.HTMLAnchorElement.prototype.click = function () { downloads.push({url: this.href, filename: this.download}); };
  window.FIGARIUM_CATALOG = catalog;
  window.matchMedia = () => ({matches: width <= 760});
  window.scrollTo = () => {};
  window.isSecureContext = true;
  const location = {hash: '#explore'};
  const context = vm.createContext({
    window, document, location,
    history: {replaceState: (_state, _unused, hash) => { location.hash = hash; }},
    localStorage: {getItem: (key) => storage.get(key) ?? null, setItem: (key, value) => storage.set(key, value)},
    navigator: {clipboard: {writeText: async (value) => { clipboard.push(value); }}},
    Blob, URL: {createObjectURL: (blob) => { blobs.push(blob); return `blob:offline-test/${blobs.length}`; }, revokeObjectURL: () => {}},
    setTimeout: () => 0, clearTimeout: () => {},
    unsafeExecuted: false,
  });
  vm.runInContext(source, context, {timeout: 3000});
  const find = (selector) => {
    const node = document.querySelector(selector);
    assert.ok(node, `Missing DOM node: ${selector}`);
    return node;
  };
  const dispatch = (node, type, fields = {}) => {
    const event = new window.Event(type, {bubbles: true, cancelable: true});
    Object.assign(event, fields); node.dispatchEvent(event); return event;
  };
  return {
    window, document, context, storage, clipboard, downloads, blobs, dialog, find,
    click: (selector) => dispatch(find(selector), 'click'),
    change: (selector, value) => { const node = find(selector); node.value = value; return dispatch(node, 'change'); },
    input: (selector, value) => { const node = find(selector); node.value = value; return dispatch(node, 'input'); },
    key: (selector, key, fields) => dispatch(find(selector), 'keydown', {key, ...fields}),
    resize: (nextWidth) => { width = nextWidth; window.dispatchEvent(new window.Event('resize')); },
    cardIds: () => [...document.querySelectorAll('.asset-image-button')].map((node) => node.dataset.open),
  };
}

test('optional full DOM smoke: initialize, filters, views, PPTX, zoom, navigation and inert recipes', {
  skip: !process.env.FIGARIUM_DOM_MODULE_PATH && 'Set FIGARIUM_DOM_MODULE_PATH to an existing linkedom entry for the optional DOM smoke',
}, async () => {
  const code = '<img src=x onerror="unsafeExecuted=true">\nthrow new Error("Recipes must stay inert")';
  const papers = [
    {id: 'older', title: 'OldPaper: Original study', year: '2025', venue: 'ICLR', topic: 'vision', paperUrl: 'https://example.com/old', authors: 'A. Author', license: 'Not documented'},
    {id: 'newer', title: 'NewPaper: A newer study', year: '2026', venue: 'arXiv', topic: 'documents', paperUrl: 'https://example.com/new'},
    {id: 'unknown', title: 'UnknownPaper', year: '', venue: 'Preprint', paperUrl: 'https://example.com/unknown'},
  ];
  const assets = Array.from({length: 25}, (_, index) => {
    const paperId = index < 18 ? 'older' : index < 24 ? 'newer' : 'unknown';
    return {
      id: `a${index}`, paperId, title: `Figure ${String(index).padStart(2, '0')}`,
      type: ['method', 'result', 'table'][index % 3], filename: `figure-${index}.png`,
      sourceLabel: `Figure ${index + 1}`, page: String(index + 1),
      src: `assets/papers/${paperId}/method_figures/figure-${index}.png`,
      readmeUrl: 'https://example.com/readme', paperUrl: papers.find((paper) => paper.id === paperId).paperUrl,
      codes: index === 1 ? [{language: 'python', label: 'Python Source', code}] : [],
      palette: index === 0 ? [{hex: '#112233', role: 'Accent', color: 'Blue'}] : [],
      downloads: index === 0 ? [
        {label: 'Editable PPTX', url: 'assets/papers/older/method_figures/figure-0.pptx', format: 'pptx', filename: 'figure-0.pptx', local: true},
        {label: 'Unsafe', url: 'javascript:unsafeExecuted=true'},
      ] : [],
    };
  });
  papers[0].downloads = [{label: 'Combined PPTX', url: 'assets/papers/older/method_figures/combined.pptx', format: 'pptx', filename: 'combined.pptx', local: true}];
  const catalog = {site: {
    name: 'My <img src=x onerror=unsafeExecuted=true>', chineseName: '图圃', tagline: 'Keep the recipe.',
    description: '<script>unsafeExecuted=true</script> personal archive', repositoryUrl: 'https://github.com/example/library', featuredPaperIds: ['older'],
  }, stats: {paperCount: 3, assetCount: 25, sourceCount: 2, pptxCount: 1}, papers, assets};
  const h = domHarness(catalog);
  assert.equal(h.cardIds().length, 18);
  assert.equal(h.find('#stat-pptx').textContent, '1');
  assert.equal(h.find('#collection-heading').textContent, '图表收藏');
  assert.equal(h.find('#category-modules').hidden, false);
  assert.equal(h.find('#asset-grid').dataset.category, 'all');
  assert.equal(h.find('.asset-card[data-asset-type="method"] .asset-type').textContent, '方法框架');
  assert.equal(h.find('#paper-select').querySelectorAll('option').length, 4);
  assert.equal(h.find('.brand-wordmark strong').textContent, catalog.site.name);
  assert.equal(h.document.querySelector('.brand-wordmark img'), null);
  assert.equal(h.document.querySelector('.hero-description script'), null);
  assert.equal(h.find('.guide-doc-link').getAttribute('href'), 'guides/GETTING_STARTED.md');
  h.click('#load-more'); assert.equal(h.cardIds().length, 25);
  h.click('button[data-density="compact"]');
  assert.equal(h.find('#asset-grid').dataset.density, 'compact'); assert.equal(h.cardIds().length, 25);
  h.change('#sort', 'newest'); assert.equal(h.cardIds()[0], 'a18'); assert.equal(h.cardIds().length, 18);
  h.change('#sort', 'curated'); assert.equal(h.cardIds()[0], 'a0');
  h.change('#paper-select', 'newer'); assert.equal(h.cardIds().length, 6);
  assert.match(h.find('#paper-filter-chip').textContent, /NewPaper/);
  assert.equal(h.find('#clear-filters').hidden, false);
  h.click('#paper-filter-chip'); assert.equal(h.find('#paper-select').value, 'all');
  h.change('#year', '2026'); assert.equal(h.cardIds().length, 6);
  h.click('#clear-filters'); h.click('.category-module[data-type="result"]'); assert.equal(h.cardIds().length, 8);
  assert.equal(h.find('#asset-grid').dataset.category, 'result');
  assert.equal(h.find('.category-module[data-type="result"]').getAttribute('aria-pressed'), 'true');
  assert.equal(h.find('.category-module[data-type="result"]').classList.contains('active'), true);
  assert.match(h.find('#catalog-note').textContent, /Python/);
  assert.equal(h.document.querySelector('.asset-card:not([data-asset-type="result"])'), null);
  h.input('#search', 'figure 01'); assert.deepEqual(h.cardIds(), ['a1']);
  h.click('#clear-filters');
  h.find('#source-only').checked = true; h.change('#source-only', 'on'); assert.deepEqual(h.cardIds(), ['a0', 'a1']);
  h.click('#clear-filters');
  h.click('.nav-item[data-view="papers"]'); assert.equal(h.find('#collection-heading').textContent, '论文索引');
  assert.equal(h.find('#category-modules').hidden, true);
  assert.equal(h.find('#collection-tools').hidden, true); assert.equal(h.document.querySelectorAll('.paper-row').length, 3);
  h.click('[data-paper="newer"]'); assert.equal(h.find('#paper-select').value, 'newer'); assert.equal(h.cardIds().length, 6);
  h.click('#clear-filters');
  h.find('.asset-image-button[data-open="a0"]').focus();
  h.click('.asset-image-button[data-open="a0"]'); assert.equal(h.dialog.open, true);
  assert.match(h.find('#dialog-label').textContent, /^方法框架/);
  assert.equal(h.find('#dialog-position').textContent, '1 / 25'); assert.equal(h.find('#previous-asset').disabled, true);
  assert.equal(h.find('#source-code').hidden, true); assert.match(h.find('#no-code h3').textContent, /PPTX/);
  const pptx = h.find('#extra-downloads a[download="figure-0.pptx"]');
  assert.equal(pptx.getAttribute('target'), null); assert.equal(h.document.querySelectorAll('#extra-downloads a').length, 2);
  h.click('#zoom-image'); assert.equal(h.dialog.classList.contains('image-expanded'), true);
  h.click('#next-asset'); assert.equal(h.find('#dialog-position').textContent, '2 / 25');
  assert.equal(h.find('#zoom-image').getAttribute('aria-pressed'), 'false');
  assert.equal(h.find('#source-code').hidden, false); assert.equal(h.find('#source-code-text').textContent, code);
  assert.equal(h.document.querySelector('#source-code-text img'), null); assert.equal(h.context.unsafeExecuted, false);
  h.click('#copy-code'); await Promise.resolve(); assert.equal(h.clipboard.at(-1), code);
  h.key('#source-code-text', 'ArrowRight'); assert.equal(h.find('#dialog-position').textContent, '2 / 25');
  h.key('#tab-code', 'ArrowRight'); assert.equal(h.find('#tab-palette').getAttribute('aria-selected'), 'true');
  assert.equal(h.find('#dialog-position').textContent, '2 / 25');
  h.key('#dialog-title', 'ArrowRight', {ctrlKey: true}); assert.equal(h.find('#dialog-position').textContent, '2 / 25');
  h.key('#dialog-title', 'ArrowRight'); assert.equal(h.find('#dialog-position').textContent, '3 / 25');
  assert.equal(h.find('#panel-palette').hidden, false); assert.equal(h.find('#source-code').hidden, true);
  for (let i = 3; i < 25; i++) h.click('#next-asset');
  assert.equal(h.find('#dialog-position').textContent, '25 / 25'); assert.equal(h.find('#next-asset').disabled, true);
  assert.equal(h.cardIds().length, 18, 'Detail navigation must not alter list pagination');
  h.click('#close-dialog'); assert.equal(h.dialog.open, false);
  assert.equal(h.document.activeElement.dataset.open, 'a0', 'Closing returns to the original card, not the next button');
  h.click('[data-save="a0"]'); h.click('.nav-item[data-view="saved"]'); assert.deepEqual(h.cardIds(), ['a0']);
  assert.equal(h.find('#collection-heading').textContent, '已保存');
  h.click('.asset-image-button[data-open="a0"]'); h.click('#dialog-save');
  assert.equal(h.find('#dialog-position').textContent, '— / 0');
  assert.equal(h.find('#previous-asset').disabled, true); assert.equal(h.find('#next-asset').disabled, true);
  h.click('#close-dialog'); assert.equal(h.document.activeElement.id, 'main');
  assert.equal([...h.storage.keys()][0], 'figarium:saved:v1:' + encodeURIComponent(catalog.site.repositoryUrl));
  h.click('.nav-item[data-view="workflow"]'); assert.equal(h.find('#workflow-view').hidden, false);
  h.click('.nav-item[data-view="guide"]'); assert.equal(h.find('#guide-view').hidden, false);
  const injection = '</textarea><script>unsafeExecuted=true</script>';
  h.input('#paper-input', injection); h.click('#make-prompt');
  assert.match(h.find('#paper-prompt').value, /method_pptx=on/); assert.ok(h.find('#paper-prompt').value.includes(injection));
  assert.equal(h.document.querySelector('#generated-prompt script'), null);
  h.input('#library-name', injection); h.click('#download-config');
  assert.equal(h.downloads.at(-1).filename, 'figarium.config.json');
  assert.equal(JSON.parse(await h.blobs.at(-1).text()).name, injection); assert.equal(h.context.unsafeExecuted, false);
  h.resize(760); h.click('#mobile-menu'); assert.equal(h.find('#main').inert, true);
  assert.equal(h.find('#menu-backdrop').hidden, false); assert.equal(h.find('#mobile-menu').getAttribute('aria-expanded'), 'true');
  h.click('#menu-backdrop'); assert.equal(h.document.activeElement.id, 'mobile-menu'); assert.equal(h.find('#main').inert, false);
  h.click('#mobile-menu'); h.resize(761); h.resize(760);
  assert.equal(h.find('#sidebar').classList.contains('open'), false); assert.equal(h.find('#sidebar').inert, true);
  assert.equal(h.find('#menu-backdrop').hidden, true); assert.equal(h.document.body.classList.contains('menu-open'), false);
});

test('optional real catalog DOM smoke matches published counts and actual PPTX downloads', {
  skip: !process.env.FIGARIUM_DOM_MODULE_PATH || !fs.existsSync(path.join(website, 'dist', 'catalog.json')),
}, () => {
  const catalog = JSON.parse(fs.readFileSync(path.join(website, 'dist', 'catalog.json'), 'utf8'));
  const h = domHarness(catalog);
  assert.equal(h.cardIds().length, Math.min(18, catalog.assets.length));
  assert.equal(h.find('#stat-papers').textContent, String(catalog.stats.paperCount));
  assert.equal(h.find('#stat-assets').textContent, String(catalog.stats.assetCount));
  assert.equal(h.find('#stat-pptx').textContent, String(catalog.stats.pptxCount));
  h.find('#source-only').checked = true; h.change('#source-only', 'on');
  assert.match(h.find('#result-count').textContent, new RegExp(`找到 ${catalog.stats.sourceCount} 项图表`));
  h.click('#clear-filters');
  for (const type of ['method', 'result', 'table']) {
    h.click(`[data-type="${type}"]`);
    assert.match(h.find('#result-count').textContent, new RegExp(`找到 ${catalog.stats.counts[type]} 项图表`));
  }
  h.click('#clear-filters');
  const pptAsset = catalog.assets.find((asset) => asset.downloads?.some((row) => row.format === 'pptx' && row.local === true));
  if (pptAsset) {
    h.change('#paper-select', pptAsset.paperId);
    const button = [...h.document.querySelectorAll('.asset-image-button')].find((node) => node.dataset.open === pptAsset.id);
    assert.ok(button, 'A real local-PPTX card must be reachable in its paper'); button.click();
    const download = pptAsset.downloads.find((row) => row.format === 'pptx' && row.local === true);
    const link = [...h.document.querySelectorAll('#extra-downloads a')].find((node) => node.getAttribute('href') === download.url);
    assert.ok(link, 'Actual local PPTX must be linked from its detail');
    assert.equal(link.getAttribute('download'), download.filename); assert.equal(link.getAttribute('target'), null);
  }
});
