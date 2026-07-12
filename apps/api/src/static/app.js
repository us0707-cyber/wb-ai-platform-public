const $ = (id) => document.getElementById(id);
let token = localStorage.getItem('token') || '';
let products = [];
let stores = [];
let lastSeoResult = null;

function getErrorMessage(data, fallback = 'Неизвестная ошибка') {
  if (!data) return fallback;
  if (typeof data === 'string') return data;
  if (typeof data.message === 'string' && data.message.trim()) return data.message;
  if (typeof data.detail === 'string' && data.detail.trim()) return data.detail;
  if (Array.isArray(data.detail)) return data.detail.map((item) => item?.msg || String(item)).join(', ');
  try { return JSON.stringify(data); } catch { return fallback; }
}

async function api(path, opts = {}) {
  const headers = new Headers(opts.headers || {});
  if (!headers.has('Content-Type') && opts.body && !(opts.body instanceof FormData)) headers.set('Content-Type', 'application/json');
  if (token) headers.set('Authorization', `Bearer ${token}`);
  const response = await fetch(`/api/v1${path}`, { ...opts, headers });
  const text = await response.text();
  let data = null;
  if (text) { try { data = JSON.parse(text); } catch { data = text; } }
  if (!response.ok) {
    const error = new Error(getErrorMessage(data, `Ошибка HTTP ${response.status}`));
    error.status = response.status;
    throw error;
  }
  return data;
}

function setStatus(message, kind = 'info') {
  if (!$('status')) return;
  $('status').textContent = String(message || '');
  $('status').dataset.kind = kind;
}
function setAuthMessage(message, kind = 'info') {
  if (!$('authOut')) return;
  $('authOut').textContent = String(message || '');
  $('authOut').dataset.kind = kind;
}
function escapeHtml(value = '') {
  return String(value).replace(/[&<>'"]/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]));
}
function getInputValue(id) { return ($(id)?.value || '').trim(); }
function formatNumber(value) {
  const number = Number(value);
  return Number.isFinite(number) ? new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 2 }).format(number) : '0';
}
function formatDate(value) {
  if (!value) return '';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString('ru-RU');
}
function storeName(storeId) { return stores.find((store) => Number(store.id) === Number(storeId))?.name || `Магазин #${storeId}`; }
function statusLabel(status) {
  const labels = { draft: 'Черновик', active: 'Активен', archived: 'Архив' };
  return `<span class="badge status-${escapeHtml(status)}">${labels[status] || escapeHtml(status)}</span>`;
}

function validateAuthFields(requireEmail = false) {
  const username = getInputValue('username');
  const password = getInputValue('password');
  const email = getInputValue('email');
  if (username.length < 3) throw new Error('Логин должен содержать минимум 3 символа');
  if (password.length < 8) throw new Error('Пароль должен содержать минимум 8 символов');
  if (requireEmail && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) throw new Error('Введите корректный email');
  return { username, password, email };
}

function authState() {
  const authorized = Boolean(token);
  if ($('auth')) $('auth').hidden = authorized;
  if ($('app')) $('app').hidden = !authorized;
  if ($('logout')) $('logout').style.display = authorized ? 'block' : 'none';
  if (authorized) refresh();
}

$('login').onclick = async () => {
  try {
    const { username, password } = validateAuthFields(false);
    const data = await api('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) });
    token = data.access_token;
    localStorage.setItem('token', token);
    setAuthMessage('');
    loadAgentHistory();
authState();
  } catch (error) { setAuthMessage(error.message, 'error'); }
};
$('register').onclick = async () => {
  try {
    const { username, email, password } = validateAuthFields(true);
    await api('/auth/register', { method: 'POST', body: JSON.stringify({ username, email, password }) });
    setAuthMessage('Регистрация выполнена. Теперь войдите.', 'ok');
  } catch (error) { setAuthMessage(error.message, 'error'); }
};
$('logout').onclick = () => {
  localStorage.removeItem('token');
  token = '';
  products = [];
  stores = [];
  loadAgentHistory();
authState();
};

document.querySelectorAll('[data-page]').forEach((button) => {
  button.onclick = () => {
    document.querySelectorAll('.page').forEach((page) => { page.hidden = true; });
    $(button.dataset.page).hidden = false;
    $('pageTitle').textContent = button.textContent.trim();
  };
});

async function refresh() {
  try {
    setStatus('Обновление данных…');
    const [metrics, storesData, productsData] = await Promise.all([api('/dashboard/summary'), api('/stores'), api('/products')]);
    stores = Array.isArray(storesData) ? storesData : [];
    products = Array.isArray(productsData) ? productsData : [];
    renderMetrics(metrics);
    render();
    await loadAgentHistory();
    setStatus('Данные актуальны', 'ok');
  } catch (error) {
    if (error.status === 401) {
      localStorage.removeItem('token');
      token = '';
      loadAgentHistory();
authState();
      setAuthMessage('Сессия завершена. Войдите снова.', 'error');
    } else setStatus(error.message, 'error');
  }
}

function renderMetrics(metrics) {
  $('metrics').innerHTML = Object.entries(metrics || {}).map(([key, value]) => `<div class="metric"><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`).join('');
}
function storeStatusLabel(store) {
  if (store.connection_status === 'connected') return '<span class="badge ok">Подключен</span>';
  if (store.connection_status === 'error') return '<span class="badge error">Ошибка</span>';
  return '<span class="badge">Не проверен</span>';
}
function render() { renderStores(); renderProducts(); renderSelects(); renderSeoSelection(); }
function renderStores() {
  $('storeList').innerHTML = stores.length ? stores.map((store) => `
    <article class="item store-card"><div><div class="item-title"><b>${escapeHtml(store.name)}</b>${storeStatusLabel(store)}</div>
    <div class="muted">${escapeHtml(store.marketplace)} · токен ${store.has_token ? 'добавлен' : 'не добавлен'}</div>
    ${store.last_checked_at ? `<div class="muted">Проверка: ${escapeHtml(formatDate(store.last_checked_at))}</div>` : ''}
    ${store.last_error ? `<div class="error-text">${escapeHtml(store.last_error)}</div>` : ''}</div>
    <div class="actions compact"><button onclick="checkStore(${store.id})">Проверить</button><button onclick="syncStore(${store.id}, ${store.has_token ? "false" : "true"})">Синхронизировать</button><button class="secondary" onclick="editStore(${store.id})">Изменить</button><button class="danger" onclick="deleteStore(${store.id})">Удалить</button></div></article>`).join('') : '<div class="empty">Добавьте первый кабинет Wildberries.</div>';
}
function filteredProducts() {
  const query = getInputValue('productSearch').toLowerCase();
  const status = $('productStatusFilter')?.value || '';
  return products.filter((product) => {
    const haystack = [product.title, product.brand, product.vendor_code, product.nm_id, product.category].join(' ').toLowerCase();
    return (!query || haystack.includes(query)) && (!status || product.status === status);
  });
}
function renderProducts() {
  const data = filteredProducts();
  $('productList').innerHTML = data.length ? data.map((product) => `
    <article class="item product-card">
      ${product.image_url ? `<img class="product-image" src="${escapeHtml(product.image_url)}" alt="">` : '<div class="product-image product-placeholder">Нет фото</div>'}
      <div><div class="item-title"><b>${escapeHtml(product.title)}</b>${statusLabel(product.status)}</div>
      <div class="muted">${escapeHtml(storeName(product.store_id))} · ${escapeHtml(product.brand || 'Без бренда')} · ${escapeHtml(product.category || 'Без категории')}</div>
      <div class="product-meta"><span>${formatNumber(product.price)} ₽</span><span>Остаток: ${formatNumber(product.stock)}</span><span>SEO: ${formatNumber(product.seo_score)}</span>${product.seo_title ? '<span class="badge ok">SEO готов</span>' : ''}${product.vendor_code ? `<span>Артикул: ${escapeHtml(product.vendor_code)}</span>` : ''}${product.nm_id ? `<span>nmId: ${escapeHtml(product.nm_id)}</span>` : ''}</div></div>
      <div class="actions compact"><button onclick="runSeo(${product.id})">SEO</button><button class="secondary" onclick="editProduct(${product.id})">Изменить</button><button class="danger" onclick="deleteProduct(${product.id})">Удалить</button></div>
    </article>`).join('') : '<div class="empty">Товары не найдены.</div>';
}
function renderSelects() {
  const selectedStore = $('productStore')?.value || '';
  const selectedAgentProduct = $('agentProduct')?.value || '';
  $('productStore').innerHTML = stores.length ? stores.map((store) => `<option value="${store.id}">${escapeHtml(store.name)}</option>`).join('') : '<option value="">Сначала добавьте магазин</option>';
  $('agentProduct').innerHTML = products.length ? products.map((product) => `<option value="${product.id}">${escapeHtml(product.title)}</option>`).join('') : '<option value="">Сначала добавьте товар</option>';
  if (selectedStore && stores.some((store) => String(store.id) === selectedStore)) $('productStore').value = selectedStore;
  if (selectedAgentProduct && products.some((product) => String(product.id) === selectedAgentProduct)) $('agentProduct').value = selectedAgentProduct;
}

$('productSearch').oninput = renderProducts;
$('productStatusFilter').onchange = renderProducts;
$('agentProduct').onchange = renderSeoSelection;

$('addStore').onclick = async () => {
  try {
    const name = getInputValue('storeName');
    const apiToken = getInputValue('storeToken');
    if (!name) throw new Error('Введите название магазина');
    await api('/stores', { method: 'POST', body: JSON.stringify({ name, api_token: apiToken, marketplace: 'wildberries' }) });
    $('storeName').value = '';
    $('storeToken').value = '';
    await refresh();
    setStatus('Магазин добавлен', 'ok');
  } catch (error) { setStatus(error.message, 'error'); }
};

$('addProduct').onclick = async () => {
  try {
    const payload = {
      store_id: Number($('productStore').value),
      title: getInputValue('productTitle'),
      description: getInputValue('productDescription'),
      vendor_code: getInputValue('productVendorCode'),
      nm_id: getInputValue('productNmId') ? Number(getInputValue('productNmId')) : null,
      brand: getInputValue('productBrand'),
      category: getInputValue('productCategory'),
      price: Number($('productPrice').value || 0),
      stock: Number($('productStock').value || 0),
      status: $('productStatus').value,
      image_url: getInputValue('productImageUrl')
    };
    if (!payload.store_id) throw new Error('Сначала добавьте магазин');
    if (payload.title.length < 3) throw new Error('Название должно содержать минимум 3 символа');
    if (payload.price < 0 || payload.stock < 0) throw new Error('Цена и остаток не могут быть отрицательными');
    await api('/products', { method: 'POST', body: JSON.stringify(payload) });
    ['productTitle','productDescription','productVendorCode','productNmId','productBrand','productCategory','productPrice','productStock','productImageUrl'].forEach((id) => { $(id).value = ''; });
    $('productStatus').value = 'draft';
    await refresh();
    setStatus('Товар добавлен', 'ok');
  } catch (error) { setStatus(error.message, 'error'); }
};

window.editProduct = async (id) => {
  const product = products.find((item) => Number(item.id) === Number(id));
  if (!product) return setStatus('Товар не найден', 'error');
  const title = prompt('Название товара', product.title);
  if (title === null) return;
  const price = prompt('Цена', product.price);
  if (price === null) return;
  const stock = prompt('Остаток', product.stock);
  if (stock === null) return;
  const status = prompt('Статус: draft, active или archived', product.status);
  if (status === null) return;
  try {
    await api(`/products/${id}`, { method: 'PATCH', body: JSON.stringify({ title: title.trim(), price: Number(price), stock: Number(stock), status: status.trim() }) });
    await refresh();
    setStatus('Товар обновлён', 'ok');
  } catch (error) { setStatus(error.message, 'error'); }
};
window.deleteProduct = async (id) => {
  if (!confirm('Удалить товар?')) return;
  try { await api(`/products/${id}`, { method: 'DELETE' }); await refresh(); setStatus('Товар удалён', 'ok'); }
  catch (error) { setStatus(error.message, 'error'); }
};
window.checkStore = async (id) => {
  try { const result = await api(`/stores/${id}/check`, { method: 'POST' }); await refresh(); setStatus(result?.ok ? 'Подключение подтверждено' : result?.message || 'Проверка завершена', result?.ok ? 'ok' : 'error'); }
  catch (error) { setStatus(error.message, 'error'); }
};
window.editStore = async (id) => {
  const store = stores.find((item) => Number(item.id) === Number(id));
  const name = prompt('Название магазина', store?.name || '');
  if (name === null) return;
  const apiToken = prompt('Новый WB API token. Оставьте пустым, чтобы не менять.', '');
  if (apiToken === null) return;
  const payload = { name: name.trim() };
  if (apiToken.trim()) payload.api_token = apiToken.trim();
  try { await api(`/stores/${id}`, { method: 'PATCH', body: JSON.stringify(payload) }); await refresh(); setStatus('Магазин обновлён', 'ok'); }
  catch (error) { setStatus(error.message, 'error'); }
};
window.deleteStore = async (id) => {
  if (!confirm('Удалить магазин и все связанные товары?')) return;
  try { await api(`/stores/${id}`, { method: 'DELETE' }); await refresh(); setStatus('Магазин удалён', 'ok'); }
  catch (error) { setStatus(error.message, 'error'); }
};
function renderSeoSelection() {
  const id = Number($('agentProduct')?.value);
  const product = products.find((item) => Number(item.id) === id);
  if (!product || !$('seoResult')) return;
  if (lastSeoResult && Number(lastSeoResult.product_id) === id) return renderSeoResult(lastSeoResult);
  if (product.seo_title || product.seo_description) {
    renderSeoResult({
      product_id: product.id,
      title: product.seo_title,
      description: product.seo_description,
      keywords: product.keywords || [],
      recommendations: product.seo_recommendations || [],
      seo_score: product.seo_score,
      seo_updated_at: product.seo_updated_at,
      mode: 'saved'
    });
  } else {
    $('seoResult').className = 'seo-result empty';
    $('seoResult').textContent = 'Для этого товара SEO ещё не генерировалось.';
  }
}

function renderSeoResult(data) {
  if (!$('seoResult')) return;
  lastSeoResult = data;
  const keywords = Array.isArray(data.keywords) ? data.keywords : [];
  const recommendations = Array.isArray(data.recommendations) ? data.recommendations : [];
  $('seoResult').className = 'seo-result';
  $('seoResult').innerHTML = `
    <div class="seo-section score-row"><div><h4>SEO-оценка</h4><div class="seo-actions-note">Режим: ${escapeHtml(data.mode || 'local')}${data.seo_updated_at ? ` · ${escapeHtml(formatDate(data.seo_updated_at))}` : ''}</div></div><div class="score-value">${formatNumber(data.seo_score)}/100</div></div>
    <div class="seo-section"><h4>SEO-заголовок</h4><div>${escapeHtml(data.title || '')}</div></div>
    <div class="seo-section"><h4>SEO-описание</h4><div>${escapeHtml(data.description || '')}</div></div>
    <div class="seo-section"><h4>Ключевые слова</h4><div class="keyword-list">${keywords.length ? keywords.map((word) => `<span class="keyword-chip">${escapeHtml(word)}</span>`).join('') : '<span class="muted">Ключевые слова не найдены</span>'}</div></div>
    <div class="seo-section"><h4>Рекомендации</h4>${recommendations.length ? `<ul class="recommendations">${recommendations.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>` : '<span class="muted">Рекомендаций нет</span>'}</div>`;
}

async function loadAgentHistory() {
  if (!$('agentHistory') || !token) return;
  try {
    const runs = await api('/agents/runs?limit=15');
    $('agentHistory').innerHTML = runs.length ? runs.map((run) => `
      <div class="history-item"><div class="history-head"><span class="history-type">${escapeHtml(run.agent_type)}</span><span class="history-date">${escapeHtml(formatDate(run.created_at))}</span></div>
      <div class="muted">Статус: ${escapeHtml(run.status)}</div></div>`).join('') : '<div class="empty">История пока пуста.</div>';
  } catch (error) { $('agentHistory').innerHTML = `<div class="error-text">${escapeHtml(error.message)}</div>`; }
}

async function generateSeoForProduct(id, applyChanges = false) {
  const targetAudience = getInputValue('seoAudience') || 'покупатели Wildberries';
  const tone = $('seoTone')?.value || 'продающий и информативный';
  setStatus('SEO Agent анализирует товар…');
  const data = await api('/agents/seo', { method: 'POST', body: JSON.stringify({ product_id: id, target_audience: targetAudience, tone, apply_changes: applyChanges }) });
  renderSeoResult(data);
  await refresh();
  await loadAgentHistory();
  setStatus(applyChanges ? 'SEO создано и применено к товару' : 'SEO-анализ завершён', 'ok');
  return data;
}

window.runSeo = async (id) => {
  try {
    document.querySelectorAll('.page').forEach((page) => { page.hidden = true; });
    $('agents').hidden = false;
    $('pageTitle').textContent = 'AI-агенты';
    $('agentProduct').value = String(id);
    await generateSeoForProduct(id, false);
  } catch (error) { setStatus(error.message, 'error'); }
};


$('generateSeo').onclick = async () => {
  const id = Number($('agentProduct').value);
  if (!id) return setStatus('Сначала добавьте товар', 'error');
  try { await generateSeoForProduct(id, false); } catch (error) { setStatus(error.message, 'error'); }
};

$('applySeo').onclick = async () => {
  const id = Number($('agentProduct').value);
  if (!id) return setStatus('Сначала добавьте товар', 'error');
  try {
    if (!lastSeoResult || Number(lastSeoResult.product_id) !== id) {
      await generateSeoForProduct(id, false);
    }
    await api(`/agents/seo/${id}/apply`, { method: 'POST' });
    await refresh();
    await loadAgentHistory();
    setStatus('SEO-заголовок и описание применены к товару', 'ok');
  } catch (error) { setStatus(error.message, 'error'); }
};

document.querySelectorAll('[data-agent]').forEach((button) => {
  button.onclick = async () => {
    const id = Number($('agentProduct').value);
    if (!id) return setStatus('Сначала добавьте товар', 'error');
    const path = button.dataset.agent;
    let body = { product_id: id };
    if (path === 'keywords') body.seed_keywords = [];
    if (path === 'competitors') body.competitors = [];
    if (path === 'ads') body = { product_id: id, daily_budget: 1000, current_cpc: 20, conversion_rate: 0.05, margin_percent: 30 };
    try { $('agentOut').textContent = JSON.stringify(await api(`/agents/${path}`, { method: 'POST', body: JSON.stringify(body) }), null, 2); await refresh(); }
    catch (error) { $('agentOut').textContent = error.message; setStatus(error.message, 'error'); }
  };
});

loadAgentHistory();
authState();

let lastPricingResult = null;

function selectedPricingProduct() {
  const id = Number($('pricingProduct')?.value || 0);
  return products.find((product) => Number(product.id) === id) || null;
}

function fillPricingInputs(force = false) {
  const product = selectedPricingProduct();
  if (!product) return;
  const values = {
    pricingCurrent: product.price,
    pricingCost: product.cost_price,
    pricingLogistics: product.logistics_cost,
    pricingCommission: product.commission_percent || 15,
    pricingMarket: product.competitor_avg_price,
  };
  Object.entries(values).forEach(([id, value]) => {
    const node = $(id);
    if (node && (force || node.value === '')) node.value = Number(value || 0) || '';
  });
  const ads = $('pricingAds');
  if (ads && (force || ads.value === '')) {
    const sales = Number(product.sales_30d || 0);
    ads.value = sales > 0 ? (Number(product.ad_spend_30d || 0) / sales).toFixed(2) : '';
  }
}

function syncBusinessSelects() {
  const selected = $('pricingProduct')?.value;
  const options = products.length ? products.map((p) => `<option value="${p.id}">${escapeHtml(p.title)}</option>`).join('') : '<option value="">Нет товаров</option>';
  if ($('pricingProduct')) {
    $('pricingProduct').innerHTML = options;
    if (selected && products.some((p) => String(p.id) === String(selected))) $('pricingProduct').value = selected;
    fillPricingInputs(false);
  }
}

function renderAnalyticsChart(points) {
  const node = $('analyticsChart');
  if (!node) return;
  const nonZero = points.some((x) => Number(x.revenue) || Number(x.profit));
  if (!points.length || !nonZero) {
    node.className = 'analytics-chart empty';
    node.textContent = 'Нет исторических данных. Создайте демо-историю или выполните синхронизацию.';
    return;
  }
  const width = 900;
  const height = 260;
  const padding = 34;
  const maxValue = Math.max(...points.flatMap((x) => [Number(x.revenue || 0), Math.max(0, Number(x.profit || 0))]), 1);
  const step = (width - padding * 2) / Math.max(points.length - 1, 1);
  const pointString = (key) => points.map((x, index) => {
    const value = Math.max(0, Number(x[key] || 0));
    const px = padding + index * step;
    const py = height - padding - value / maxValue * (height - padding * 2);
    return `${px.toFixed(1)},${py.toFixed(1)}`;
  }).join(' ');
  const labels = points.filter((_, i) => i % Math.max(1, Math.floor(points.length / 6)) === 0).map((x, index) => {
    const originalIndex = points.indexOf(x);
    const px = padding + originalIndex * step;
    return `<text x="${px}" y="248" text-anchor="middle">${escapeHtml(String(x.day).slice(5))}</text>`;
  }).join('');
  node.className = 'analytics-chart';
  node.innerHTML = `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="График выручки и прибыли">
    <line x1="${padding}" y1="${height-padding}" x2="${width-padding}" y2="${height-padding}" class="axis" />
    <polyline points="${pointString('revenue')}" class="chart-line revenue-line" />
    <polyline points="${pointString('profit')}" class="chart-line profit-line" />
    ${labels}
  </svg><div class="chart-legend"><span><i class="legend-revenue"></i>Выручка</span><span><i class="legend-profit"></i>Прибыль</span></div>`;
}

async function loadAnalytics() {
  if (!$('analyticsMetrics')) return;
  try {
    const days = Number($('analyticsDays')?.value || 30);
    setStatus('Загрузка аналитики…');
    const [overview, trends, matrix, forecast] = await Promise.all([
      api(`/analytics/overview?days=${days}`),
      api(`/analytics/trends?days=${days}`),
      api(`/analytics/abc-xyz?days=${days}`),
      api(`/analytics/forecast?history_days=${days}`),
    ]);
    const metricLabels = {
      revenue: 'Выручка', profit: 'Прибыль', orders: 'Заказы', sales: 'Продажи', returns: 'Возвраты',
      ad_spend: 'Реклама', margin_percent: 'Маржа, %', romi_percent: 'ROMI, %',
      conversion_percent: 'Конверсия, %', average_order_value: 'Средний чек', stock_units: 'Остаток', products_count: 'Товаров'
    };
    $('analyticsMetrics').innerHTML = Object.entries(overview).map(([key, value]) => `<div class="metric"><span>${escapeHtml(metricLabels[key] || key)}</span><strong>${formatNumber(value)}${['revenue','profit','ad_spend','average_order_value'].includes(key) ? ' ₽' : ''}</strong></div>`).join('');
    renderAnalyticsChart(trends);
    $('analyticsTable').innerHTML = matrix.length ? `<div class="analytics-row analytics-head"><span>Товар</span><span>Выручка</span><span>Доля</span><span>ABC</span><span>XYZ</span><span>Вариативность</span></div>${matrix.map((x) => `<div class="analytics-row"><span>${escapeHtml(x.title)}</span><span>${formatNumber(x.revenue)} ₽</span><span>${formatNumber(x.revenue_share_percent)}%</span><span><b class="class-chip abc-${x.abc_class.toLowerCase()}">${x.abc_class}</b></span><span><b class="class-chip xyz-${x.xyz_class.toLowerCase()}">${x.xyz_class}</b></span><span>${formatNumber(x.coefficient_of_variation)}%</span></div>`).join('')}` : '<div class="empty">Нет товаров для анализа.</div>';
    $('forecastTable').innerHTML = forecast.length ? forecast.slice(0, 8).map((x) => `<article class="forecast-item"><div><b>${escapeHtml(x.title)}</b><div class="muted">Средние продажи: ${formatNumber(x.average_daily_sales)}/день · прогноз 30 дней: ${x.forecast_sales_30d}</div></div><div class="forecast-values"><span>${x.days_of_stock === null ? '∞' : formatNumber(x.days_of_stock)} дней запаса</span><strong>Заказать: ${x.suggested_reorder}</strong></div></article>`).join('') : '<div class="empty">Нет данных для прогноза.</div>';
    setStatus('Аналитика обновлена', 'ok');
  } catch (error) { setStatus(error.message, 'error'); }
}

async function loadRecommendations() {
  if (!$('recommendationList')) return;
  try {
    const items = await api('/autopilot/recommendations');
    $('recommendationList').innerHTML = items.length ? items.map((x) => `<article class="item"><div><div class="item-title"><b>${escapeHtml(x.title)}</b><span class="badge ${x.priority === 'high' ? 'error' : ''}">${escapeHtml(x.priority)}</span></div><div class="muted">${escapeHtml(x.message)}</div><div class="muted">Статус: ${escapeHtml(x.status)}</div></div>${x.status === 'open' ? `<div class="actions compact"><button onclick="actRecommendation(${x.id},'apply')">Применить</button><button class="secondary" onclick="actRecommendation(${x.id},'dismiss')">Скрыть</button></div>` : ''}</article>`).join('') : '<div class="empty">Рекомендаций пока нет.</div>';
  } catch (error) { setStatus(error.message, 'error'); }
}

window.syncStore = async (id, demoMode = false) => {
  try {
    setStatus('Синхронизация каталога…');
    const result = await api(`/stores/${id}/sync`, { method: 'POST', body: JSON.stringify({ demo_mode: demoMode }) });
    setStatus(result.ok ? `Синхронизировано товаров: ${result.total}` : result.message, result.ok ? 'ok' : 'error');
    await refresh();
  } catch (error) { setStatus(error.message, 'error'); }
};

if ($('seedAnalytics')) $('seedAnalytics').onclick = async () => { try { await api('/analytics/demo/generate?days=60', { method: 'POST' }); await loadAnalytics(); setStatus('Демо-история аналитики создана', 'ok'); } catch (error) { setStatus(error.message, 'error'); } };
if ($('refreshAnalytics')) $('refreshAnalytics').onclick = loadAnalytics;
if ($('analyticsDays')) $('analyticsDays').onchange = loadAnalytics;
if ($('pricingProduct')) $('pricingProduct').onchange = () => fillPricingInputs(true);

function optionalNumber(id) {
  const value = $(id)?.value?.trim();
  if (value === '' || value == null) return null;
  const number = Number(value);
  if (!Number.isFinite(number) || number < 0) throw new Error('Проверьте финансовые поля: значения должны быть неотрицательными числами');
  return number;
}

function actionLabel(action) {
  return ({ increase: 'повысить цену', decrease: 'снизить цену', hold: 'оставить цену', needs_data: 'нужно заполнить данные' })[action] || action;
}

if ($('analyzePrice')) $('analyzePrice').onclick = async () => {
  try {
    const productId = Number($('pricingProduct').value);
    if (!productId) throw new Error('Выберите товар');
    const payload = {
      product_id: productId,
      current_price: optionalNumber('pricingCurrent'),
      cost_price: optionalNumber('pricingCost'),
      logistics_cost: optionalNumber('pricingLogistics'),
      ad_cost_per_unit: optionalNumber('pricingAds'),
      commission_percent: optionalNumber('pricingCommission'),
      tax_percent: optionalNumber('pricingTax') ?? 6,
      market_price: optionalNumber('pricingMarket'),
      target_margin_percent: optionalNumber('pricingMargin') ?? 30,
      save_inputs: true,
    };
    lastPricingResult = await api('/pricing/analyze', { method: 'POST', body: JSON.stringify(payload) });
    $('pricingResult').classList.remove('empty');
    const warnings = lastPricingResult.warnings || [];
    const rationale = lastPricingResult.rationale || [];
    $('pricingResult').innerHTML = `
      <div class="pricing-summary">
        <div class="score-row"><h4>Рекомендуемая цена</h4><span class="score-value">${formatNumber(lastPricingResult.recommended_price)} ₽</span></div>
        <div class="pricing-kpis">
          <div class="pricing-kpi"><span>Текущая цена</span><strong>${formatNumber(lastPricingResult.current_price)} ₽</strong></div>
          <div class="pricing-kpi"><span>Точка безубыточности</span><strong>${formatNumber(lastPricingResult.break_even_price)} ₽</strong></div>
          <div class="pricing-kpi"><span>Цена по затратам</span><strong>${formatNumber(lastPricingResult.cost_based_price)} ₽</strong></div>
          <div class="pricing-kpi"><span>Рыночная цена</span><strong>${formatNumber(lastPricingResult.market_price)} ₽</strong></div>
          <div class="pricing-kpi"><span>Прибыль с единицы</span><strong>${formatNumber(lastPricingResult.estimated_profit_per_unit)} ₽</strong></div>
          <div class="pricing-kpi"><span>Расчётная маржа</span><strong>${formatNumber(lastPricingResult.estimated_margin_percent)}%</strong></div>
        </div>
        <div><b>Рекомендация:</b> ${escapeHtml(actionLabel(lastPricingResult.action))}</div>
        ${warnings.length ? `<div><b>Что заполнить:</b><ul class="warning-list">${warnings.map((x) => `<li>${escapeHtml(x)}</li>`).join('')}</ul></div>` : ''}
        <div><b>Что учтено:</b><ul class="rationale-list">${rationale.map((x) => `<li>${escapeHtml(x)}</li>`).join('')}</ul></div>
      </div>`;
    await refresh();
    fillPricingInputs(false);
  } catch (error) { setStatus(error.message, 'error'); }
};
if ($('applyPrice')) $('applyPrice').onclick = async () => { try { const id = Number($('pricingProduct').value); await api(`/pricing/${id}/apply`, { method: 'POST' }); await refresh(); setStatus('Цена применена', 'ok'); } catch (error) { setStatus(error.message, 'error'); } };
if ($('analyzeCompetitors')) $('analyzeCompetitors').onclick = async () => {
  try {
    const id = Number($('pricingProduct').value);
    if (!id) throw new Error('Выберите товар');
    const currentInput = optionalNumber('pricingCurrent');
    if (currentInput !== null) {
      await api(`/products/${id}`, { method: 'PATCH', body: JSON.stringify({ price: currentInput }) });
      await refresh();
    }
    const result = await api('/competitors/analyze', { method: 'POST', body: JSON.stringify({ product_id: id, competitors: [] }) });
    $('pricingResult').classList.remove('empty');
    $('pricingResult').innerHTML = result.average_price > 0
      ? `<h4>Средняя цена конкурентов: ${formatNumber(result.average_price)} ₽</h4><div>Диапазон: ${formatNumber(result.min_price)}–${formatNumber(result.max_price)} ₽ · Рекомендуемая цена: ${formatNumber(result.recommended_price)} ₽ · Разница: ${formatNumber(result.price_gap_percent)}%</div><ul>${result.content_gaps.map((x) => `<li>${escapeHtml(x)}</li>`).join('')}</ul>`
      : `<h4>Недостаточно данных для анализа</h4><ul class="warning-list">${(result.warnings || []).map((x) => `<li>${escapeHtml(x)}</li>`).join('')}</ul>`;
    if ($('pricingMarket') && result.average_price > 0) $('pricingMarket').value = result.average_price;
  } catch (error) { setStatus(error.message, 'error'); }
};
if ($('runAutopilot')) $('runAutopilot').onclick = async () => { await api('/autopilot/run', { method: 'POST' }); await loadRecommendations(); setStatus('Автопилот завершил анализ', 'ok'); };
if ($('refreshRecommendations')) $('refreshRecommendations').onclick = loadRecommendations;
window.actRecommendation = async (id, action) => { await api(`/autopilot/recommendations/${id}`, { method: 'POST', body: JSON.stringify({ action }) }); await refresh(); await loadRecommendations(); };

document.querySelectorAll('[data-page]').forEach((button) => {
  button.addEventListener('click', () => {
    if (button.dataset.page === 'analytics') loadAnalytics();
    if (button.dataset.page === 'autopilot') loadRecommendations();
    if (button.dataset.page === 'pricing') syncBusinessSelects();
  });
});

const originalRender = render;
render = function() { originalRender(); syncBusinessSelects(); };
