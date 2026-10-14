// Zero-dependency unit tests of app.js pure behavior. This is not a DOM/browser
// interaction test: no jsdom is bundled, and no paper recipe is evaluated.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import vm from 'node:vm';
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
  const state = {view: 'explore', type: 'all', query: '', year: 'all', paperId: null, sourceOnly: false, ...overrides};
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
