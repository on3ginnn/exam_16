/**
 * Операция без полной перезагрузки страницы: фильтр списка мест.
 * GET с partial=1 возвращает HTML-фрагмент; подменяется #place-list-inner.
 */
(function () {
  const zoneEl = document.getElementById('filter-zone');
  const osEl = document.getElementById('filter-os');
  const inner = document.getElementById('place-list-inner');
  if (!zoneEl || !osEl || !inner) return;

  function reloadList() {
    const params = new URLSearchParams();
    const z = zoneEl.value;
    const o = osEl.value;
    if (z) params.set('zone', z);
    if (o) params.set('os', o);
    params.set('partial', '1');
    const url = window.location.pathname + '?' + params.toString();
    fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.text();
      })
      .then(function (html) {
        inner.innerHTML = html;
      })
      .catch(function () {
        inner.innerHTML =
          '<p class="muted">Не удалось обновить список. Обновите страницу.</p>';
      });
  }

  zoneEl.addEventListener('change', reloadList);
  osEl.addEventListener('change', reloadList);
})();
