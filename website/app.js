/* ReFigure: a static, local-first viewer. Source snippets are text, never executed. */
(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const icons = {
    grid: '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
    book: '<path d="M12 5C8 2 4 3 2 4v16c3-2 7-2 10 0 3-2 7-2 10 0V4c-2-1-6-2-10 1Zm0 0v15"/>',
    bookmark: '<path d="M6 3h12v19l-6-4-6 4V3Z"/>',
    branch: '<circle cx="6" cy="5" r="2"/><circle cx="18" cy="6" r="2"/><circle cx="6" cy="19" r="2"/><path d="M6 7v10m0-4h6a6 6 0 0 0 6-6"/>',
    sprout: '<path d="M12 22V11m0 5C4 16 3 10 3 6c6 0 9 4 9 10Zm0-5c0-6 4-9 9-9 0 6-4 9-9 9Z"/>',
    github: '<path d="M9 19c-4 1-4-2-6-2m12 5v-4c0-1-.3-1.7-1-2 3-.4 6-1.5 6-6 0-1.5-.5-2.5-1.3-3.5.2-.5.6-2-.2-3.5 0 0-1-.3-3.5 1.3a12 12 0 0 0-6 0C6.5 2.7 5.5 3 5.5 3c-.8 1.5-.4 3-.2 3.5A5 5 0 0 0 4 10c0 4.5 3 5.6 6 6-.7.3-1 1-1 2v4"/>',
    menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
    search: '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
    code: '<path d="m8 6-6 6 6 6m8-12 6 6-6 6m-3-15-2 18"/>',
    download: '<path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/>',
    copy: '<rect x="8" y="8" width="13" height="13" rx="2"/><path d="M16 8V3H3v13h5"/>',
    close: '<path d="m5 5 14 14M19 5 5 19"/>',
    shield: '<path d="m12 2 9 4v6c0 6-9 10-9 10S3 18 3 12V6l9-4Z"/><path d="m8 12 3 3 5-6"/>',
    palette: '<path d="M12 3a9 9 0 1 0 0 18h1c2 0 3-2 2-3s-1-3 1-3h2c6 0 4-12-6-12Z"/><circle cx="7" cy="10" r=".8"/><circle cx="10" cy="7" r=".8"/><circle cx="15" cy="7" r=".8"/>'
  };
  const icon = (name) => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + (icons[name] || icons.code) + '</svg>';
  document.querySelectorAll('[data-icon]').forEach((el) => { el.innerHTML = icon(el.dataset.icon); });
  const catalog = window.FIGARIUM_CATALOG;
  if (!catalog || !Array.isArray(catalog.assets) || !Array.isArray(catalog.papers)) {
    $('result-count').textContent = '图谱尚未构建。请先运行 python website/build.py，再打开 website/dist。';
    $('catalog-note').hidden = true;
    return;
  }
  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const safeUrl = (value) => {
    const url = String(value || '');
    if (/^https?:\/\//i.test(url)) return url;
    if (/^(assets|guides)\/[a-zA-Z0-9_%./~-]+$/.test(url)) {
      let decoded = url;
      try { for (let i = 0; i < 3; i++) { const next = decodeURIComponent(decoded); if (next === decoded) break; decoded = next; } }
      catch { return '#'; }
      if (!decoded.includes('\\') && !decoded.split('/').includes('..')) return url;
    }
    return '#';
  };
  const cleanText = (value) => String(value || '').replace(/\[([^\]]+)\]\([^)]+\)/g, '$1').replace(/\*\*|`/g, '');
  const papers = new Map(catalog.papers.map((p) => [p.id, p]));
  const assetsById = new Map(catalog.assets.map((a) => [a.id, a]));
  const featured = catalog.site.featuredPaperIds || [];
  const rank = (id) => featured.includes(id) ? featured.indexOf(id) : 100;
  const assets = [...catalog.assets].sort((a, b) => rank(a.paperId) - rank(b.paperId) || (Number(papers.get(b.paperId)?.year) || 0) - (Number(papers.get(a.paperId)?.year) || 0));
  const typeNames = {method: '方法框架', result: '结果分析', table: '论文表格'};
  const typeLabels = {method: '方法框架', result: '结果分析', table: '论文表格'};
  const state = {view: 'explore', type: 'all', query: '', year: 'all', paperId: null, sourceOnly: false, sort: 'curated', density: 'comfortable', limit: 18};
  // Preserve the legacy key so existing browser-local collections survive the rename.
  const storageKey = 'figarium:saved:v1:' + encodeURIComponent(catalog.site.repositoryUrl);
  let saved;
  try { saved = new Set(JSON.parse(localStorage.getItem(storageKey) || '[]').filter((id) => assetsById.has(id))); }
  catch { saved = new Set(); }
  let activeAsset = null;
  let previousFocus = null;
  let toastTimer;
  let collectionGlassFrame = null;
  function updateCollectionGlass() {
    collectionGlassFrame = null;
    const tools = $('collection-tools');
    if (tools.hidden || $('collection').hidden) {
      tools.classList.remove('is-stuck');
      return;
    }
    const style = window.getComputedStyle(tools);
    const top = Number.parseFloat(style.top);
    const rect = tools.getBoundingClientRect();
    // Follow the actual sticky position, including its containing section's end.
    tools.classList.toggle('is-stuck', style.position === 'sticky' && Number.isFinite(top)
      && window.scrollY > 0 && rect.top <= top + 1 && rect.bottom > top);
  }
  function queueCollectionGlass() {
    if (collectionGlassFrame === null) collectionGlassFrame = window.requestAnimationFrame(updateCollectionGlass);
  }
  function toast(message) {
    $('toast').textContent = message;
    $('toast').classList.add('visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => $('toast').classList.remove('visible'), 2600);
  }
  async function copy(value) {
    try {
      if (navigator.clipboard && window.isSecureContext) await navigator.clipboard.writeText(value);
      else {
        const input = document.createElement('textarea');
        input.value = value; input.style.position = 'fixed'; input.style.opacity = '0';
        ($('asset-dialog').open ? $('asset-dialog') : document.body).append(input);
        input.select();
        const copied = document.execCommand('copy'); input.remove();
        if (!copied) throw new Error('Clipboard not available');
      }
      toast('已复制，带到你的工作区继续。');
    } catch { toast('浏览器未允许复制，请手动选中内容复制。'); }
  }
  function download(value, filename, mime = 'text/plain;charset=utf-8') {
    const url = URL.createObjectURL(new Blob([value], {type: mime}));
    const a = document.createElement('a'); a.href = url; a.download = filename; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  const shortPaper = (paper) => {
    const title = cleanText(paper?.title || 'Paper');
    return title.split(':')[0].split('：')[0];
  };
  const hasCode = (a) => a.type !== 'method' && Array.isArray(a.codes) && a.codes.length > 0;
  const hasLocalPptx = (a) => Array.isArray(a.downloads) && a.downloads.some((d) => d.format === 'pptx' && d.local === true);
  const hasSource = (a) => hasCode(a) || hasLocalPptx(a);
  function updateSaved() {
    $('nav-saved-count').textContent = saved.size;
    try { localStorage.setItem(storageKey, JSON.stringify([...saved])); }
    catch { toast('此浏览器不允许持久保存，收藏仅在当前页面有效。'); }
  }
  function toggleSaved(id) {
    if (saved.has(id)) saved.delete(id); else saved.add(id);
    updateSaved();
    document.querySelectorAll('[data-save]').forEach((button) => {
      const selected = saved.has(button.dataset.save);
      button.classList.toggle('saved', selected);
      button.setAttribute('aria-pressed', String(selected));
      button.setAttribute('aria-label', selected ? '取消收藏' : '收藏图表');
    });
    if (activeAsset) updateDialogSave();
    if (state.view === 'saved') render();
    if (activeAsset) updateDialogNavigation();
  }
  function filteredAssets(ignoreType = false) {
    const query = state.query.trim().toLocaleLowerCase();
    const matches = assets.filter((a) => {
      const p = papers.get(a.paperId) || {};
      return (state.view !== 'saved' || saved.has(a.id)) &&
        (ignoreType || state.type === 'all' || a.type === state.type) &&
        (state.year === 'all' || String(p.year) === state.year) &&
        (!state.paperId || a.paperId === state.paperId) &&
        (!state.sourceOnly || hasSource(a)) &&
        (!query || [a.title, a.filename, a.sourceLabel, p.title, p.topic, p.venue].join(' ').toLocaleLowerCase().includes(query));
    });
    if (!['newest', 'title'].includes(state.sort)) return matches;
    const order = new Map(assets.map((asset, index) => [asset.id, index]));
    return matches.sort((a, b) => {
      const difference = state.sort === 'newest'
        ? (Number(papers.get(b.paperId)?.year) || 0) - (Number(papers.get(a.paperId)?.year) || 0)
        : String(a.title || '').localeCompare(String(b.title || ''), 'zh-CN', {sensitivity: 'base', numeric: true});
      return difference || order.get(a.id) - order.get(b.id);
    });
  }
  function card(a) {
    const p = papers.get(a.paperId) || {};
    const assetType = ['method', 'result', 'table'].includes(a.type) ? a.type : 'figure';
    const source = hasSource(a);
    const langs = [...new Set([...(hasLocalPptx(a) ? ['PPTX'] : []), ...(hasCode(a) ? a.codes : []).filter((c) => !/required packages/i.test(c.label)).map((c) => c.language.toUpperCase())])];
    const badge = source ? icon(a.type === 'method' ? 'download' : 'code') + ' ' + esc(langs.join(' / ') || '资源') : a.type === 'table' ? icon('book') + ' 查看详情' : icon('palette') + ' 配色 / 参考';
    const detailTab = a.type === 'result' && !source ? 'palette' : 'code';
    const colors = a.type === 'table' ? [] : [...new Set((Array.isArray(a.palette) ? a.palette : []).map((row) => String(row?.hex || '')).filter((hex) => /^#[0-9a-f]{6}$/i.test(hex)))].slice(0, 4);
    const swatches = colors.length ? '<span class="palette-dots" aria-hidden="true">' + colors.map((hex) => '<i class="palette-dot" style="background:' + hex + '" title="' + hex.toUpperCase() + '"></i>').join('') + '</span>' : '';
    return '<article class="asset-card" data-asset-type="' + assetType + '"><div class="asset-preview"><button class="asset-image-button" data-open="' + esc(a.id) + '" aria-label="查看 ' + esc(a.title) + '"><img src="' + esc(safeUrl(a.src)) + '" alt="' + esc(a.title) + '" loading="lazy" decoding="async"></button><button class="save-button' + (saved.has(a.id) ? ' saved' : '') + '" data-save="' + esc(a.id) + '" aria-label="' + (saved.has(a.id) ? '取消收藏' : '收藏图表') + '" aria-pressed="' + saved.has(a.id) + '">' + icon('bookmark') + '</button></div><div class="asset-info"><div class="asset-kicker"><span class="asset-type ' + assetType + '">' + esc(typeLabels[assetType] || '图表') + '</span><span class="asset-source-label">' + esc(a.sourceLabel || '—') + '</span>' + swatches + '</div><button class="asset-title-button" data-open="' + esc(a.id) + '"><h3>' + esc(a.title) + '</h3></button><p class="asset-paper">' + esc(shortPaper(p)) + '</p><div class="asset-bottom"><span class="asset-venue">' + esc(p.venue || 'Paper') + ' · ' + esc(p.year || '—') + '</span><button class="' + (source ? 'code-badge' : 'palette-badge') + '" data-open="' + esc(a.id) + '" data-tab="' + detailTab + '">' + (a.approximate ? '<span class="approx-dot" title="包含估读或简化"></span>' : '') + badge + '</button></div></div></article>';
  }
  function renderPapers() {
    const sorted = [...catalog.papers].sort((a, b) => rank(a.id) - rank(b.id) || Number(b.year) - Number(a.year));
    $('paper-list').innerHTML = sorted.map((p, i) => {
      const rows = assets.filter((a) => a.paperId === p.id);
      return '<button class="paper-row" data-paper="' + esc(p.id) + '"><span class="paper-number">' + String(i + 1).padStart(2, '0') + '</span><span><h3>' + esc(p.title) + '</h3><p>' + esc(p.topic || 'Research figures') + '</p><span class="paper-row-meta">' + esc(p.venue) + ' / ' + esc(p.year) + ' <b>·</b> ' + rows.length + ' 项图表 <b>·</b> ' + rows.filter(hasSource).length + ' 项可复用资源 <span>查看图卡</span></span></span><span class="paper-thumbs">' + rows.slice(0, 3).map((a) => '<img src="' + esc(safeUrl(a.src)) + '" alt="" loading="lazy">').join('') + '</span></button>';
    }).join('');
  }
  function render() {
    queueCollectionGlass();
    const isPapers = state.view === 'papers';
    const isCollection = ['explore', 'saved', 'papers'].includes(state.view);
    $('hero').hidden = state.view !== 'explore';
    $('process-strip').hidden = state.view !== 'explore';
    $('collection').hidden = !isCollection;
    $('workflow-view').hidden = state.view !== 'workflow';
    $('guide-view').hidden = state.view !== 'guide';
    $('category-modules').hidden = isPapers;
    $('collection-tools').hidden = isPapers;
    $('asset-grid').hidden = isPapers;
    $('paper-list').hidden = !isPapers;
    $('export-saved').hidden = state.view !== 'saved';
    syncCollectionControls();
    $('collection-eyebrow').textContent = isPapers ? '按论文浏览' : state.view === 'saved' ? '我的收藏' : '浏览图表';
    $('collection-heading').textContent = isPapers ? '论文索引' : state.view === 'saved' ? '已保存' : '图表收藏';
    $('collection-aside').textContent = state.view === 'saved' ? '本机收藏，可导出清单。' : isPapers ? '按论文浏览全部图表。' : '查看原图，带走可编辑资源。';
    document.querySelectorAll('.nav-item[data-view]').forEach((el) => {
      const active = el.dataset.view === state.view;
      el.classList.toggle('active', active);
      if (active) el.setAttribute('aria-current', 'page'); else el.removeAttribute('aria-current');
    });
    if (!isCollection) return;
    if (isPapers) {
      renderPapers(); $('result-count').textContent = catalog.papers.length + ' 篇真实论文 / 按论文查看图表';
      $('empty-state').hidden = true; $('load-more').hidden = true; return;
    }
    const allTypes = filteredAssets(true);
    const matches = filteredAssets();
    ['all', 'method', 'result', 'table'].forEach((type) => {
      $('count-' + type).textContent = type === 'all' ? allTypes.length : allTypes.filter((a) => a.type === type).length;
    });
    document.querySelectorAll('[data-type]').forEach((el) => {
      const active = el.dataset.type === state.type; el.classList.toggle('active', active); el.setAttribute('aria-pressed', String(active));
    });
    $('asset-grid').dataset.category = state.type;
    const categoryNotes = {
      all: '浏览原图与可复用资源',
      method: '方法框架图，按条目提供可编辑 PPT',
      result: '结果分析图，按条目提供 Python 重建代码',
      table: '论文表格，按条目提供 LaTeX 重建代码',
    };
    $('catalog-note').textContent = categoryNotes[state.type] || categoryNotes.all;
    $('asset-grid').innerHTML = matches.slice(0, state.limit).map(card).join('');
    $('result-count').textContent = '找到 ' + matches.length + ' 项图表' + (state.type === 'all' ? '' : ' · ' + typeNames[state.type]);
    $('empty-state').hidden = matches.length !== 0;
    const emptySaved = state.view === 'saved' && saved.size === 0;
    $('empty-title').textContent = emptySaved ? '还没有收藏图表' : '没有找到匹配的图表';
    $('empty-description').textContent = emptySaved ? '点击图卡右上角的书签，把想再看的图留在这里。收藏只存于本机浏览器。' : '试试其他关键词，或者换一组筛选条件。';
    $('reset-filters').textContent = emptySaved ? '浏览图表' : '重置筛选';
    $('load-more').hidden = matches.length <= state.limit;
    $('load-more').textContent = '再看 ' + Math.min(18, matches.length - state.limit) + ' 张';
  }
  function resetFilters() {
    Object.assign(state, {type: 'all', query: '', year: 'all', paperId: null, sourceOnly: false, limit: 18});
    $('search').value = ''; $('year').value = 'all'; $('source-only').checked = false;
    syncCollectionControls();
  }
  function hasActiveFilters(filters = state) {
    return Boolean(filters.type !== 'all' || filters.query.trim() || filters.year !== 'all' || filters.paperId || filters.sourceOnly);
  }
  function setDensity(density) {
    if (!['comfortable', 'compact'].includes(density)) return false;
    state.density = density;
    $('asset-grid').dataset.density = density;
    document.querySelectorAll('button[data-density]').forEach((button) => {
      const selected = button.dataset.density === density;
      button.setAttribute('aria-pressed', String(selected));
      button.classList.toggle('active', selected);
    });
    return true;
  }
  function syncCollectionControls() {
    $('paper-select').value = state.paperId || 'all';
    $('sort').value = state.sort;
    $('paper-filter-chip').hidden = !state.paperId;
    $('paper-filter-chip').textContent = state.paperId ? shortPaper(papers.get(state.paperId)) + ' × 清除论文筛选' : '';
    if ($('clear-filters')) $('clear-filters').hidden = !hasActiveFilters();
    setDensity(state.density);
  }
  function updateDrawer() {
    const mobile = window.matchMedia ? window.matchMedia('(max-width:900px)').matches : window.innerWidth <= 900;
    if (!mobile) $('sidebar').classList.remove('open');
    const open = mobile && $('sidebar').classList.contains('open');
    $('sidebar').inert = mobile && !open;
    $('main').inert = mobile && open;
    $('menu-backdrop').hidden = !open;
    document.body.classList.toggle('menu-open', open);
    $('mobile-menu').setAttribute('aria-controls', 'sidebar');
    $('mobile-menu').setAttribute('aria-expanded', String(open));
    $('mobile-menu').setAttribute('aria-label', open ? '收起导航' : '展开导航');
    if (mobile && !open && $('sidebar').contains(document.activeElement)) $('mobile-menu').focus();
    if (!mobile && document.activeElement === $('mobile-menu')) {
      ($('sidebar').querySelector('.nav-item[aria-current="page"]') || $('sidebar').querySelector('.nav-item'))?.focus();
    }
  }
  function closeDrawer(restoreFocus = false) {
    $('sidebar').classList.remove('open');
    updateDrawer();
    if (restoreFocus) $('mobile-menu').focus();
  }
  function changeView(view, scroll = true) {
    if (!['explore', 'saved', 'papers', 'workflow', 'guide'].includes(view)) return;
    state.view = view; state.limit = 18;
    closeDrawer($('sidebar').classList.contains('open'));
    history.replaceState(null, '', '#' + view); render();
    if (scroll) window.scrollTo({top: 0, behavior: 'instant'});
  }
  function dialogNavigation(rows, id) {
    const index = rows.findIndex((asset) => asset.id === id);
    return {index, total: rows.length, previousId: index > 0 ? rows[index - 1].id : null, nextId: index >= 0 && index < rows.length - 1 ? rows[index + 1].id : null};
  }
  function updateDialogNavigation() {
    const navigation = dialogNavigation(filteredAssets(), activeAsset?.id);
    $('previous-asset').disabled = !navigation.previousId;
    $('next-asset').disabled = !navigation.nextId;
    $('dialog-position').textContent = activeAsset && navigation.index < 0
      ? '筛选外图表' : (navigation.index >= 0 ? navigation.index + 1 : '—') + ' / ' + navigation.total;
  }
  function navigateAsset(direction) {
    if (!activeAsset || ![-1, 1].includes(direction)) return false;
    const navigation = dialogNavigation(filteredAssets(), activeAsset.id);
    const id = direction < 0 ? navigation.previousId : navigation.nextId;
    if (!id) return false;
    const tab = document.querySelector('[data-detail-tab][aria-selected="true"]')?.dataset.detailTab || 'code';
    openAsset(id, tab);
    return true;
  }
  function shouldNavigateAsset(event, dialogOpen) {
    if (!dialogOpen || event.defaultPrevented || event.isComposing || !['ArrowLeft', 'ArrowRight'].includes(event.key) || event.ctrlKey || event.altKey || event.metaKey || event.shiftKey) return false;
    if (event.target?.isContentEditable) return false;
    return !event.target?.closest?.('input, textarea, select, pre, code, [contenteditable]:not([contenteditable="false"]), [role="tab"], [data-detail-tab]');
  }
  function setImageExpanded(expanded) {
    $('asset-dialog').classList.toggle('image-expanded', Boolean(expanded));
    $('zoom-image').setAttribute('aria-pressed', String(Boolean(expanded)));
    $('zoom-image').setAttribute('aria-label', expanded ? '收起图像' : '放大图像');
  }
  function handleDialogClose() {
    activeAsset = null; setImageExpanded(false); updateDialogNavigation();
    const origin = previousFocus?.isConnected && !$('asset-dialog').contains(previousFocus) && !previousFocus.closest('[inert]') ? previousFocus : $('main');
    origin.focus(); previousFocus = null;
  }
  function updateDialogSave() {
    const selected = saved.has(activeAsset.id);
    $('dialog-save').innerHTML = icon('bookmark') + (selected ? ' 已保存' : ' 保存图表');
    $('dialog-save').setAttribute('aria-pressed', String(selected));
  }
  function setTab(name) {
    const tabs = [...document.querySelectorAll('[data-detail-tab]')];
    const visible = tabs.filter((button) => !button.hidden);
    const target = visible.find((button) => button.dataset.detailTab === name) || visible[0];
    const restoreFocus = tabs.some((button) => button.hidden && button === document.activeElement);
    tabs.forEach((button) => {
      const selected = button === target;
      button.setAttribute('aria-selected', String(selected)); button.tabIndex = selected ? 0 : -1;
      $('panel-' + button.dataset.detailTab).hidden = !selected;
    });
    if (restoreFocus) target?.focus();
  }
  function selectedCode() { return activeAsset?.type === 'method' ? null : activeAsset?.codes?.[Number($('code-select').value)] || null; }
  function renderCode() {
    const code = selectedCode();
    $('source-code-text').textContent = code?.code || '';
    const lang = (code?.language || '').toLowerCase();
    $('source-help').textContent = /required packages/i.test(code?.label || '') ? '这只是宏包片段，不是可单独编译的文档。请选择表格源码，下载包含宏包的完整 LaTeX 文档。' : /svg|tikz/.test(lang) ? '可编辑示意重建，不是作者原始矢量图。细节可能简化，请对照原图。' : lang === 'python' ? 'Python 重建配方；部分数值为估读，不是原始实验数据。请先审阅再运行。' : /tex|latex/.test(lang) ? 'LaTeX 重建；下载时合并该图已列出的宏包。可编译不代表数据已核验。' : '纯文本源码，仅供审阅、复制和下载；网页不会执行。';
    $('download-code').disabled = !code;
  }
  function citationText(a, p) {
    return [p.title, 'Paper: ' + p.paperUrl, 'Figure: ' + (a.sourceLabel || a.title), 'Page: ' + (a.page || 'Not documented'), 'Authors: ' + cleanText(p.authors || 'Not documented'), 'License: ' + cleanText(p.license || 'Not documented'), 'Entry: ' + a.readmeUrl].join('\n');
  }
  function relatedDownloads(a, p = {}) {
    const rows = Array.isArray(a.downloads) ? a.downloads : [];
    if (a.type === 'method') {
      const pptx = rows.filter((row) => row.format === 'pptx' && safeUrl(row.url) !== '#');
      const ownDeck = pptx.find((row) => row.local === true && safeUrl(row.url).startsWith('assets/papers/')) || pptx[0];
      return ownDeck ? [ownDeck] : [];
    }
    const seen = new Set();
    return rows.filter((row) => { if (seen.has(row.url)) return false; seen.add(row.url); return true; });
  }
  function downloadLinks(rows) {
    return rows.filter((row) => safeUrl(row.url) !== '#').map((row) => {
      const url = safeUrl(row.url);
      const localPptx = row.format === 'pptx' && row.local === true && url.startsWith('assets/papers/');
      const behavior = localPptx ? ' download="' + esc(row.filename || '') + '"' : ' target="_blank" rel="noopener noreferrer"';
      return '<a class="extra-download" href="' + esc(url) + '"' + behavior + ' title="' + esc(row.validation || '') + '">' + icon('download') + ' ' + esc(row.label) + (localPptx ? ' ↓' : ' ↗') + '</a>';
    }).join('');
  }
  function renderSourceState(a) {
    const method = a.type === 'method';
    const code = hasCode(a), pptx = method ? relatedDownloads(a).length > 0 : hasLocalPptx(a);
    $('tab-code').textContent = method ? 'PPT 与配色' : '重建源码';
    ['code-toolbar', 'source-code', 'source-bottom'].forEach((id) => { $(id).hidden = !code; });
    $('no-code').hidden = code;
    $('no-code').querySelector('h3').textContent = pptx ? '本图 PPTX，可直接下载' : method ? '本图的 PPTX 尚未收录' : a.type === 'table' ? '本表的重建源码尚未收录' : '先留下配色，也可以继续重建';
    $('no-code').querySelector('p').textContent = method
      ? pptx ? '下载对应本图的 PPTX，在 PowerPoint 中继续编辑。' : '当前没有本图对应的 PPTX。可以先查看原图与配色，或复制指令补充可编辑重建。'
      : pptx ? '本图已收录本地 PPTX。文件格式检查不代表视觉或原生对象可编辑性验收，请结合条目的重建与 QA 说明核对。' : a.type === 'table' ? '可以查看原表，或复制指令补充重建源码。' : '本图暂未收录单独的代码或 PPTX。可先查看原图和配色参考，或继续补充重建资源。';
    $('copy-rebuild-prompt').hidden = pptx;
  }
  function renderPalette(a) {
    const method = a.type === 'method', table = a.type === 'table';
    $('tab-palette').hidden = a.type !== 'result';
    $('method-palette').hidden = !method;
    const content = $('palette-content');
    (method ? $('method-palette') : $('panel-palette')).append(content);
    content.hidden = table;
    $('palette-heading').textContent = '配色';
    const palette = table ? [] : (Array.isArray(a.palette) ? a.palette : []).filter((row) => /^#[0-9a-f]{6}$/i.test(row?.hex || ''));
    $('palette-intro').textContent = table ? '' : !palette.length ? '这个条目尚未记录配色，可以在论文 README 中补充后重建网页。'
      : a.paletteSource === 'image-sample' ? '从原图自动提取的代表色，色值为近似值。点击复制。' : '配色来自论文条目的色彩手记。点击色值复制。';
    $('palette-list').innerHTML = palette.map((row) => '<button class="palette-row" data-color="' + esc(row.hex) + '"><span class="palette-swatch" style="background:' + row.hex + '"></span><span class="palette-role">' + esc(row.role || row.color) + '<small>' + esc(row.color || '') + '</small></span><span class="palette-hex">' + esc(row.hex.toUpperCase()) + ' ' + icon('copy') + '</span></button>').join('');
  }
  function openAsset(id, tab = 'code') {
    const a = assetsById.get(id); if (!a) return;
    const p = papers.get(a.paperId) || {};
    if (!$('asset-dialog').open) previousFocus = document.activeElement;
    activeAsset = a;
    setImageExpanded(false);
    $('dialog-label').textContent = (Object.hasOwn(typeLabels, a.type) ? typeLabels[a.type] : '图表') + ' / 图表详情';
    $('dialog-title').textContent = a.title;
    $('dialog-paper').textContent = cleanText(p.title) + ' · ' + (p.venue || '') + ' ' + (p.year || '');
    $('dialog-image').src = safeUrl(a.src); $('dialog-image').alt = a.title;
    $('original-link').href = safeUrl(a.src); $('dialog-readme').href = safeUrl(a.readmeUrl); $('paper-link').href = safeUrl(p.paperUrl);
    const showApproximation = a.type !== 'method' && Boolean(a.approximate);
    $('dialog-reconstruction').hidden = !showApproximation;
    $('dialog-reconstruction').textContent = showApproximation ? '重建提示：该条目包含估读数据或简化结构。请将原图视为事实来源，源码视为可编辑参考。' : '';
    renderSourceState(a);
    const codes = hasCode(a) ? a.codes : [];
    $('code-select').innerHTML = codes.map((c, i) => '<option value="' + i + '">' + esc(c.label || c.language) + '</option>').join('');
    const first = codes.findIndex((c) => !/required packages/i.test(c.label));
    if (first >= 0) $('code-select').value = String(first);
    renderCode(); updateDialogSave();
    renderPalette(a);
    const fields = [['论文', p.title], ['图表编号', a.sourceLabel || '该条目未记录'], ['页码', a.page || '该条目未记录'], ['作者', p.authors || '该条目未记录'], ['许可', p.license || '该条目未记录；请核对原论文'], ['验证状态', a.validation || '没有显式验证记录；未将“有代码”当作“已验证”']];
    $('citation-list').innerHTML = fields.map(([key, value]) => '<dt>' + esc(key) + '</dt><dd>' + esc(cleanText(value)) + '</dd>').join('');
    $('extra-downloads').innerHTML = downloadLinks(relatedDownloads(a, p));
    setTab(tab);
    updateDialogNavigation();
    if (!$('asset-dialog').open) $('asset-dialog').showModal();
  }
  function downloadCode() {
    const code = selectedCode(); if (!code) return;
    const lang = code.language.toLowerCase();
    let text = code.code, ext = 'txt', mime = 'text/plain;charset=utf-8';
    if (lang === 'python') ext = 'py';
    else if (lang === 'svg') { ext = 'svg'; mime = 'image/svg+xml;charset=utf-8'; }
    else if (/tex|latex|tikz/.test(lang)) {
      ext = 'tex';
      if (!/required packages/i.test(code.label) && !/\\documentclass/.test(text)) {
        const packages = activeAsset.codes.filter((c) => /required packages/i.test(c.label)).map((c) => c.code).join('\n');
        text = '\\documentclass{article}\n\\usepackage[margin=1in]{geometry}\n' + packages + '\n\\pagestyle{empty}\n\\begin{document}\n' + text + '\n\\end{document}\n';
      }
    }
    const stem = activeAsset.paperId + '_' + activeAsset.filename.replace(/\.[^.]+$/, '') + ( /required packages/i.test(code.label) ? '_packages' : '');
    download(text, stem + '.' + ext, mime); toast('源码已准备下载；请审阅后再运行。');
  }
  function initialize() {
    const site = catalog.site;
    const repository = safeUrl(site.repositoryUrl).replace(/\/$/, '');
    document.title = site.name + ' · ' + site.chineseName + ' — ' + site.tagline;
    document.querySelector('meta[name="description"]').content = site.description;
    document.querySelectorAll('[data-site-tagline]').forEach((el) => { el.textContent = site.tagline; });
    document.querySelectorAll('[data-site-description]').forEach((el) => { el.textContent = site.description; });
    const footerBrand = document.querySelector('footer > span:first-child');
    footerBrand.replaceChildren();
    const footerName = document.createElement('b'); footerName.textContent = site.name;
    const footerChinese = document.createElement('span'); footerChinese.textContent = site.chineseName;
    footerBrand.append(footerName, footerChinese, document.createTextNode(' · ' + site.tagline));
    document.querySelectorAll('[data-brand-name]').forEach((el) => { el.textContent = site.name; });
    document.querySelectorAll('[data-brand-chinese]').forEach((el) => { el.textContent = site.chineseName; });
    document.querySelector('.brand').setAttribute('aria-label', site.name + ' ' + site.chineseName + ' 首页');
    const heroLabel = document.querySelector('.hero .eyebrow');
    if (heroLabel) heroLabel.textContent = '由你策展的论文图库';
    document.querySelectorAll('.repo-link').forEach((el) => { el.href = repository; });
    document.querySelectorAll('.guide-doc-link').forEach((el) => { el.href = 'guides/GETTING_STARTED.md'; });
    document.querySelectorAll('.customize-doc-link').forEach((el) => { el.href = 'guides/CUSTOMIZATION.md'; });
    $('fork-link').href = repository + '/fork';
    $('clone-code').textContent = 'git clone ' + repository + '.git ReFigure';
    $('install-prompt').textContent = '$skill-installer 请从 ' + repository + ' 的 paper-asset-builder 目录安装 skill。';
    $('stat-papers').textContent = catalog.stats.paperCount; $('stat-assets').textContent = catalog.stats.assetCount;
    $('stat-pptx').textContent = catalog.stats.pptxCount ?? assets.filter(hasLocalPptx).length;
    $('nav-paper-count').textContent = catalog.stats.paperCount; $('nav-asset-count').textContent = catalog.stats.assetCount;
    updateSaved();
    [...new Set(catalog.papers.map((p) => String(p.year)))].sort().reverse().forEach((year) => {
      const option = document.createElement('option'); option.value = year; option.textContent = year; $('year').append(option);
    });
    const paperSelect = $('paper-select');
    paperSelect.replaceChildren();
    const allPapers = document.createElement('option'); allPapers.value = 'all'; allPapers.textContent = '全部论文'; paperSelect.append(allPapers);
    [...catalog.papers].sort((a, b) => shortPaper(a).localeCompare(shortPaper(b), 'zh-CN', {numeric: true})).forEach((paper) => {
      const option = document.createElement('option'); option.value = paper.id; option.textContent = shortPaper(paper); paperSelect.append(option);
    });
    const hash = location.hash.slice(1);
    changeView(['explore','saved','papers','workflow','guide'].includes(hash) ? hash : 'explore', false);
  }
  document.addEventListener('click', (event) => {
    const nav = event.target.closest('[data-view]');
    if (nav) {
      if (nav.tagName === 'A') {
        if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button > 0) return;
        event.preventDefault();
      }
      changeView(nav.dataset.view); return;
    }
    if (event.target.closest('.skip-link')) { closeDrawer(false); $('main').focus(); return; }
    const save = event.target.closest('[data-save]'); if (save) { toggleSaved(save.dataset.save); return; }
    const open = event.target.closest('[data-open]'); if (open) { openAsset(open.dataset.open, open.dataset.tab || 'code'); return; }
    const type = event.target.closest('[data-type]'); if (type) { state.type = ['all', 'method', 'result', 'table'].includes(type.dataset.type) ? type.dataset.type : 'all'; state.limit = 18; render(); return; }
    const density = event.target.closest('button[data-density]'); if (density) { setDensity(density.dataset.density); return; }
    const paper = event.target.closest('[data-paper]'); if (paper) { resetFilters(); state.paperId = paper.dataset.paper; changeView('explore', false); $('collection').scrollIntoView(); return; }
    const target = event.target.closest('[data-copy-target]'); if (target) { const node = $(target.dataset.copyTarget); copy(node.value ?? node.textContent); return; }
    const tab = event.target.closest('[data-detail-tab]'); if (tab) { setTab(tab.dataset.detailTab); return; }
    const color = event.target.closest('[data-color]'); if (color) copy(color.dataset.color);
  });
  $('search').addEventListener('input', (e) => { state.query = e.target.value; state.limit = 18; render(); });
  $('year').addEventListener('change', (e) => { state.year = e.target.value; state.limit = 18; render(); });
  $('paper-select').addEventListener('change', (e) => { state.paperId = papers.has(e.target.value) ? e.target.value : null; state.limit = 18; render(); });
  $('sort').addEventListener('change', (e) => { state.sort = ['curated', 'newest', 'title'].includes(e.target.value) ? e.target.value : 'curated'; state.limit = 18; render(); if (activeAsset) updateDialogNavigation(); });
  $('source-only').addEventListener('change', (e) => { state.sourceOnly = e.target.checked; state.limit = 18; render(); });
  $('paper-filter-chip').addEventListener('click', () => { state.paperId = null; state.limit = 18; render(); });
  $('load-more').addEventListener('click', () => { state.limit += 18; render(); });
  $('reset-filters').addEventListener('click', () => { resetFilters(); if (state.view === 'saved' && saved.size === 0) changeView('explore'); else render(); });
  $('clear-filters')?.addEventListener('click', () => { resetFilters(); render(); });
  $('mobile-menu').addEventListener('click', () => {
    $('sidebar').classList.toggle('open'); updateDrawer();
    if ($('sidebar').classList.contains('open')) ($('sidebar').querySelector('.nav-item[aria-current="page"]') || $('sidebar').querySelector('.nav-item'))?.focus();
  });
  $('menu-backdrop').addEventListener('click', () => closeDrawer(true));
  $('close-dialog').addEventListener('click', () => $('asset-dialog').close());
  $('asset-dialog').addEventListener('click', (e) => { if (e.target === $('asset-dialog')) { const rect = e.target.getBoundingClientRect(); if (e.clientX < rect.left || e.clientX > rect.right || e.clientY < rect.top || e.clientY > rect.bottom) e.target.close(); } });
  $('asset-dialog').addEventListener('close', handleDialogClose);
  $('previous-asset').addEventListener('click', () => navigateAsset(-1));
  $('next-asset').addEventListener('click', () => navigateAsset(1));
  $('zoom-image').addEventListener('click', () => setImageExpanded(!$('asset-dialog').classList.contains('image-expanded')));
  $('dialog-save').addEventListener('click', () => activeAsset && toggleSaved(activeAsset.id));
  $('code-select').addEventListener('change', renderCode);
  $('copy-code').addEventListener('click', () => selectedCode() && copy(selectedCode().code));
  $('download-code').addEventListener('click', downloadCode);
  $('copy-citation').addEventListener('click', () => activeAsset && copy(citationText(activeAsset, papers.get(activeAsset.paperId))));
  $('copy-rebuild-prompt').addEventListener('click', () => {
    if (!activeAsset) return;
    const deliverable = activeAsset.type === 'method'
      ? '补充对应本图的可编辑 PPTX。使用原生文字、形状和路径重建，导出后渲染核对；不添加 SVG/TikZ 代码。'
      : '补充可编辑重建源码。';
    copy('$paper-asset-builder 请为 ' + papers.get(activeAsset.paperId).title + ' 的 ' + activeAsset.title + ' ' + deliverable + '先读取已有条目 ' + activeAsset.readmeUrl + '，仅处理这一张；说明估读、简化或不可重建部分，不虚构原始数据。');
  });
  $('export-saved').addEventListener('click', () => download(JSON.stringify({library: catalog.site.name, note: 'Browser-local bookmarks; original image rights remain with their authors.', assets: assets.filter((a) => saved.has(a.id)).map((a) => ({id: a.id, title: a.title, paper: papers.get(a.paperId).title, paperUrl: a.paperUrl, readmeUrl: a.readmeUrl}))}, null, 2), 'refigure-inspiration.json', 'application/json'));
  $('make-prompt').addEventListener('click', () => {
    const paper = $('paper-input').value.trim();
    if (!paper) { toast('先写下论文名称、链接或本地 PDF 路径。'); $('paper-input').focus(); return; }
    $('paper-prompt').value = '$paper-asset-builder 请收集论文：' + paper + '\nselection=all, method_pptx=on：读取完整论文及附录，提取并分类全部编号图表到 materials/<PaperID>/{method_figures,result_figures,tables}，记录出处和覆盖情况。\n完成后告诉我真实的本地目录并停下来，等我人工筛选确认。确认后仅使用目录中保留的当前图片：逐图重建视觉完整、可编辑的 Method Figures PPTX（单图版及论文合并版），导出后渲染并与原图逐页核对，不以整张截图冒充可编辑重建；复杂照片/插图独立保留，说明近似和编辑边界。方法图默认只提供对应 PPTX，不添加 Editable Diagram Code 或 SVG/TikZ 代码；网页每张方法图只显示一个对应 PPTX 下载入口。\n结果图提供 Python，表格提供 LaTeX。生成含实际源码/PPTX链接和限制说明的论文 README、更新主索引，并重建 ReFigure 网页（若存在 website/build.py）。在线 LaTeX 测试及向外部上传须先得到我的授权。';
    $('generated-prompt').hidden = false;
  });
  $('download-config').addEventListener('click', () => {
    const name = $('library-name').value.trim(); if (!name) { $('library-name').focus(); return; }
    const config = {...catalog.site, name}; delete config.stats;
    // The builder still accepts the established configuration filename.
    download(JSON.stringify(config, null, 2) + '\n', 'figarium.config.json', 'application/json');
    toast('把配置放到 website/figarium.config.json 后重新构建。');
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !$('asset-dialog').open && $('sidebar').classList.contains('open')) {
      e.preventDefault(); closeDrawer(true); return;
    }
    if (e.key === '/' && !/INPUT|TEXTAREA|SELECT/.test(e.target.tagName) && !$('asset-dialog').open) {
      e.preventDefault(); closeDrawer(false); if (!['explore', 'saved'].includes(state.view)) changeView('explore', false); $('search').focus(); $('collection').scrollIntoView();
    }
    const tab = e.target.closest('[data-detail-tab]');
    if (tab && !tab.hidden && ['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(e.key)) {
      e.preventDefault(); const tabs = [...document.querySelectorAll('[data-detail-tab]')].filter((button) => !button.hidden); let i = tabs.indexOf(tab);
      i = e.key === 'Home' ? 0 : e.key === 'End' ? tabs.length - 1 : (i + (e.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
      setTab(tabs[i].dataset.detailTab); tabs[i].focus();
      return;
    }
    if (shouldNavigateAsset(e, $('asset-dialog').open)) { e.preventDefault(); navigateAsset(e.key === 'ArrowRight' ? 1 : -1); }
  });
  window.addEventListener('hashchange', () => { if (['explore','saved','papers','workflow','guide'].includes(location.hash.slice(1))) changeView(location.hash.slice(1), false); });
  window.addEventListener('resize', updateDrawer);
  window.addEventListener('scroll', queueCollectionGlass, {passive: true});
  window.addEventListener('resize', queueCollectionGlass);
  window.addEventListener('pageshow', queueCollectionGlass);
  initialize();
  document.fonts?.ready.then(queueCollectionGlass);
})();
