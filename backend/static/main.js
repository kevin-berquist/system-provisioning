(() => {
  // Lightweight modal helper
  const modal = document.getElementById('modal');
  const backdrop = document.getElementById('modal-backdrop');
  const form = document.getElementById('modal-form');
  const title = document.getElementById('modal-title');
  const submitBtn = document.getElementById('modal-submit');
  const cancelBtn = document.getElementById('modal-cancel');

  const fName = document.getElementById('field-name');
  const fDb = document.getElementById('field-db');
  const fDomain = document.getElementById('field-domain');
  const hiddenGemini = document.getElementById('hidden-gemini');
  const modalMode = document.getElementById('modal-mode');
  const prodInfo = document.getElementById('prod-info');
  const prodName = document.getElementById('prod-name');
  const prodDevsite = document.getElementById('prod-devsite');
  const prodSelects = document.getElementById('prod-selects');
  const selectCluster = document.getElementById('select-cluster');
  const selectDbserver = document.getElementById('select-dbserver');
  const devFields = document.getElementById('dev-fields');

  function openModal(opts) {
    title.textContent = opts.title || 'Create';
    submitBtn.textContent = opts.submitText || 'Create';
  // base population (dev fields may be hidden for prod)
  fName.value = opts.values?.NewShoWareControlName || '';
  fDb.value = opts.values?.DatabaseName || '';
  fDomain.value = opts.values?.NewWebSiteDomain || '';
    // support either GeminiTaskID (dev) or GeminiProjID (prod)
    hiddenGemini.value = opts.values?.GeminiTaskID || opts.values?.GeminiProjID || '';
    modal.setAttribute('aria-hidden', 'false');
    modal.classList.add('open');
    fName.focus();
    form.dataset.jobType = opts.jobType || 'DEV_SETUP';
    form.dataset.endpoint = opts.endpoint || '/api/jobs/dev';
    form.dataset.payloadBase = JSON.stringify(opts.payloadBase || {});
  console.debug('openModal', { jobType: form.dataset.jobType, endpoint: form.dataset.endpoint, payloadBase: form.dataset.payloadBase });

    // If opening prod modal, show prod info and selects
    if ((opts.jobType || '').toUpperCase() === 'PROD_SETUP') {
      modalMode.value = 'prod';
      prodInfo.style.display = 'block';
      prodSelects.style.display = 'block';
      // hide dev-only inputs in prod modal
      if (devFields) devFields.style.display = 'none';
      // hide domain input in prod modal (domain is derived from CurrentDevWebSiteDomain)
      const devDomainEl = document.getElementById('dev-domain'); if (devDomainEl) devDomainEl.style.display = 'none';
      // populate prod-info display
      prodName.textContent = opts.values?.Name || '';
      prodDevsite.textContent = opts.values?.CurrentDevWebSiteDomain || '';
      // prefill domain input from CurrentDevWebSiteDomain for convenience
      fDomain.value = opts.values?.CurrentDevWebSiteDomain || opts.values?.NewWebSiteDomain || '';
      // prefill db and make readonly to prevent accidental edits
      fDb.value = opts.values?.DatabaseName || '';
      fDb.setAttribute('readonly', 'true');
    } else {
      modalMode.value = 'dev';
      prodInfo.style.display = 'none';
      prodSelects.style.display = 'none';
      if (devFields) devFields.style.display = 'block';
      // show domain input for dev flows
      const devDomainEl = document.getElementById('dev-domain'); if (devDomainEl) devDomainEl.style.display = 'block';
      fDb.removeAttribute('readonly');
    }
  }

  function closeModal() {
    modal.setAttribute('aria-hidden', 'true');
    modal.classList.remove('open');
    clearErrors();
  }

  function clearErrors() {
    document.getElementById('err-name').textContent = '';
    document.getElementById('err-db').textContent = '';
    document.getElementById('err-domain').textContent = '';
    // remove prod-specific errors if present
    const ec = document.getElementById('err-cluster'); if (ec) ec.remove();
    const ed = document.getElementById('err-dbserver'); if (ed) ed.remove();
  }

  function validate() {
    clearErrors();
    let ok = true;
  // In DEV mode the operator must supply a new name; in PROD mode Name is read-only
  if (modalMode.value !== 'prod' && !fName.value.trim()) { document.getElementById('err-name').textContent = 'Required'; ok = false; }
  if (!fDb.value.trim()) { document.getElementById('err-db').textContent = 'Required'; ok = false; }
    const d = fDomain.value.trim();
    // Domain validation only for DEV flows; for PROD it's derived and not editable
    if (modalMode.value !== 'prod') {
      if (!d) { document.getElementById('err-domain').textContent = 'Required'; ok = false; }
      else if (!/^([a-z0-9-]+\.)+[a-z]{2,}$/i.test(d)) { document.getElementById('err-domain').textContent = 'Invalid domain format'; ok = false; }
    }

    // If prod mode, ensure selects are chosen
    if (modalMode.value === 'prod') {
      if (!selectCluster.value) { document.getElementById('err-cluster')?.remove?.(); const e = document.createElement('div'); e.className='error'; e.id='err-cluster'; e.textContent='Required'; selectCluster.parentNode.appendChild(e); ok = false; }
      if (!selectDbserver.value) { document.getElementById('err-dbserver')?.remove?.(); const e = document.createElement('div'); e.className='error'; e.id='err-dbserver'; e.textContent='Required'; selectDbserver.parentNode.appendChild(e); ok = false; }
    }
    return ok;
  }

  cancelBtn.addEventListener('click', (e) => { e.preventDefault(); closeModal(); });
  backdrop.addEventListener('click', closeModal);

  form.addEventListener('submit', function(e) {
    e.preventDefault();
    if (!validate()) return;
    const endpoint = form.dataset.endpoint;
    const base = JSON.parse(form.dataset.payloadBase || '{}');
    let payload = Object.assign({}, base);
  // common fields
  payload.DatabaseName = fDb.value.trim();
  // For PROD_SETUP the NewWebSiteDomain should be derived from the selected row's CurrentDevWebSiteDomain by default
  payload.NewWebSiteDomain = (form.dataset.jobType === 'PROD_SETUP') ? (base.CurrentDevWebSiteDomain || fDomain.value.trim()) : fDomain.value.trim();
    // attach appropriate gemini field name depending on job type
    if (form.dataset.jobType === 'PROD_SETUP') {
      payload.GeminiProjID = hiddenGemini.value || payload.GeminiProjID;
      payload.CurrentDevWebSiteDomain = base.CurrentDevWebSiteDomain || '';
      // prod-specific picks
      payload.WebServerCluster = selectCluster.value;
      payload.NewDatabaseServer = selectDbserver.value;
      // remove dev-only fields if present
      delete payload.NewShoWareControlName;
    } else {
      payload.NewShoWareControlName = fName.value.trim();
      payload.GeminiTaskID = hiddenGemini.value || undefined;
    }
    submitBtn.disabled = true;
    console.debug('submitting job', payload);
    fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }).then(r => r.json()).then(j => {
      // show a brief success UI and close modal
      submitBtn.disabled = false;
      console.debug('server response', j);
      closeModal();
      // append to queued list optimistically
      appendQueued(j.filename);
    }).catch(err => {
      submitBtn.disabled = false;
      console.error('job submit failed', err);
      alert('Failed to create job (see console for details)');
    });
  });

  // wire Create Dev Site button
  document.getElementById('create-dev').addEventListener('click', function(){
    openModal({ title: 'Create Dev Site', submitText: 'Create Dev', jobType: 'DEV_SETUP', endpoint: '/api/jobs/dev', payloadBase: {} });
  });

  // wire Setup Production buttons
  document.querySelectorAll('.setup-prod').forEach(function(btn){
    btn.addEventListener('click', function(){
      const db = btn.getAttribute('data-db');
      const gemini = btn.getAttribute('data-gemini');
      const current = btn.getAttribute('data-current');
      const name = btn.getAttribute('data-name');
      openModal({
        title: 'Setup Production',
        submitText: 'Create Prod Job',
        jobType: 'PROD_SETUP',
        endpoint: '/api/jobs/prod',
        // include ShoWareControl so server and listings can use it as authoritative name
        payloadBase: { Name: name, ShoWareControl: name, DatabaseName: db, GeminiProjID: gemini, CurrentDevWebSiteDomain: current },
        values: { Name: name, DatabaseName: db, GeminiProjID: gemini, CurrentDevWebSiteDomain: current }
      });
    });
  });

  // populate prod selects from server-provided options (if present)
  (function populateProdOptions(){
    try {
      const opts = window.SHOWARE_PROD_OPTIONS || {};
      (opts.clusters || []).forEach(c => {
        const o = document.createElement('option'); o.value = c; o.textContent = c; selectCluster.appendChild(o);
      });
      (opts.dbservers || []).forEach(s => {
        const o = document.createElement('option'); o.value = s; o.textContent = s; selectDbserver.appendChild(o);
      });
    } catch (e) { /* ignore */ }
  })();

  // helper to append optimistic queued item
  function appendQueued(filename) {
    const q = document.getElementById('queued');
    const el = document.createElement('div');
    el.className = 'queued-item';
    el.textContent = filename + ' (just created)';
    q.prepend(el);
  }

})();
