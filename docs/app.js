(function () {
  const registry = window.BONES_REGISTRY || [];
  const byShortcode = new Map(registry.map((item) => [item.shortcode, item]));
  const search = document.querySelector('#search');
  const cards = document.querySelector('#cards');
  const counts = document.querySelector('#counts');
  let filter = 'all';

  function copy(value, button) {
    navigator.clipboard?.writeText(value);
    const original = button.textContent;
    button.textContent = 'Copied';
    setTimeout(() => { button.textContent = original; }, 900);
  }

  function filtered() {
    const query = (search.value || '').toLowerCase();
    return registry.filter((item) => (filter === 'all' || item.category === filter) && [item.id, item.label, item.shortcode, item.codepoint, ...item.aliases, ...Object.values(item.external_ids || {})].some((value) => String(value).toLowerCase().includes(query)));
  }

  function render() {
    const items = filtered();
    counts.textContent = `${items.length} of ${registry.length} objects`;
    cards.replaceChildren(...items.map((item) => {
      const card = document.createElement('article');
      card.className = 'card';
      card.innerHTML = `<div class="glyph bones-emoji" role="img" aria-label="${item.accessible_label}">${item.char}</div><h3>${item.label}</h3><div class="meta">${item.id}<br>${item.codepoint} · ${item.shortcode}</div><div class="card-actions"><button data-copy="${item.shortcode}">Copy shortcode</button><button data-copy="${item.char}">Copy character</button></div>`;
      card.querySelectorAll('[data-copy]').forEach((button) => button.addEventListener('click', () => copy(button.dataset.copy, button)));
      return card;
    }));
  }

  function shape(value) {
    return value.replace(/:[a-z0-9_]+:/g, (token) => byShortcode.has(token) ? byShortcode.get(token).char : token);
  }

  document.querySelectorAll('[data-filter]').forEach((button) => button.addEventListener('click', () => {
    document.querySelectorAll('[data-filter]').forEach((candidate) => candidate.classList.toggle('active', candidate === button));
    filter = button.dataset.filter;
    render();
  }));
  search.addEventListener('input', render);
  const playground = document.querySelector('#playground');
  const ligatureOutput = document.querySelector('#ligature-output');
  const unicodeOutput = document.querySelector('#unicode-output');
  function updatePlayground() {
    ligatureOutput.textContent = playground.value;
    unicodeOutput.textContent = shape(playground.value);
  }
  playground.addEventListener('input', updatePlayground);
  updatePlayground();
  render();
}());
