// Modern BRB Directory Client Application
document.addEventListener("DOMContentLoaded", () => {
  let currentStateId = "";
  let currentCountyId = "";
  let currentCourtType = "";
  let currentHasPat = false;
  let currentSearch = "";

  // DOM Elements
  const stateSelect = document.getElementById("stateSelect");
  const countySelect = document.getElementById("countySelect");
  const typeSelect = document.getElementById("typeSelect");
  const patToggle = document.getElementById("patToggle");
  const searchInput = document.getElementById("searchInput");
  const statePillsContainer = document.getElementById("statePillsContainer");
  const courtsGrid = document.getElementById("courtsGrid");
  const courtModal = document.getElementById("courtModal");
  const modalBody = document.getElementById("modalBody");
  const closeModalBtn = document.getElementById("closeModalBtn");
  const syncModal = document.getElementById("syncModal");
  const closeSyncModalBtn = document.getElementById("closeSyncModalBtn");
  const openSyncBtn = document.getElementById("openSyncBtn");
  const runSyncBtn = document.getElementById("runSyncBtn");
  const syncLogsContainer = document.getElementById("syncLogsContainer");

  // Key Inputs
  const nebiusKeyInput = document.getElementById("nebiusKeyInput");
  const tavilyKeyInput = document.getElementById("tavilyKeyInput");

  // Initialize
  loadStates();
  fetchCourts();

  // Event Listeners
  stateSelect.addEventListener("change", (e) => {
    currentStateId = e.target.value;
    loadCounties(currentStateId);
    highlightStatePill(currentStateId);
    fetchCourts();
  });

  countySelect.addEventListener("change", (e) => {
    currentCountyId = e.target.value;
    fetchCourts();
  });

  typeSelect.addEventListener("change", (e) => {
    currentCourtType = e.target.value;
    fetchCourts();
  });

  patToggle.addEventListener("change", (e) => {
    currentHasPat = e.target.checked;
    fetchCourts();
  });

  let searchDebounce;
  searchInput.addEventListener("input", (e) => {
    clearTimeout(searchDebounce);
    searchDebounce = setTimeout(() => {
      currentSearch = e.target.value.trim();
      fetchCourts();
    }, 300);
  });

  closeModalBtn.addEventListener("click", () => courtModal.classList.remove("active"));
  closeSyncModalBtn.addEventListener("click", () => syncModal.classList.remove("active"));
  openSyncBtn.addEventListener("click", () => {
    syncModal.classList.add("active");
    loadSyncLogs();
  });

  runSyncBtn.addEventListener("click", runAutomatedSync);

  // Fetch States & Render Pills
  async function loadStates() {
    try {
      const res = await fetch("/api/states");
      const states = await res.json();

      stateSelect.innerHTML = '<option value="">All States (50)</option>';
      statePillsContainer.innerHTML = '<div class="state-pill active" data-state="">ALL</div>';

      states.forEach((st) => {
        const opt = document.createElement("option");
        opt.value = st.id;
        opt.textContent = `${st.name} (${st.id}) - ${st.court_count} Courts`;
        stateSelect.appendChild(opt);

        const pill = document.createElement("div");
        pill.className = "state-pill";
        pill.dataset.state = st.id;
        pill.textContent = st.id;
        pill.title = `${st.name}: ${st.court_count} courts, ${st.pat_percentage}% PAT`;
        pill.addEventListener("click", () => {
          currentStateId = st.id;
          stateSelect.value = st.id;
          highlightStatePill(st.id);
          loadCounties(st.id);
          fetchCourts();
        });
        statePillsContainer.appendChild(pill);
      });
    } catch (err) {
      console.error("Failed to load states", err);
    }
  }

  function highlightStatePill(stateId) {
    document.querySelectorAll(".state-pill").forEach((p) => {
      if (p.dataset.state === stateId) {
        p.classList.add("active");
      } else {
        p.classList.remove("active");
      }
    });
  }

  // Load Counties by State
  async function loadCounties(stateId) {
    countySelect.innerHTML = '<option value="">All Counties</option>';
    currentCountyId = "";

    if (!stateId) return;

    try {
      const res = await fetch(`/api/states/${stateId}/counties`);
      const counties = await res.json();

      counties.forEach((c) => {
        const opt = document.createElement("option");
        opt.value = c.id;
        opt.textContent = `${c.name} (${c.court_count} Courts)`;
        countySelect.appendChild(opt);
      });
    } catch (err) {
      console.error("Failed to load counties", err);
    }
  }

  // Fetch Courts with current filters
  async function fetchCourts() {
    courtsGrid.innerHTML = `
      <div class="empty-state">
        <p>Loading public records and PAT details...</p>
      </div>
    `;

    const params = new URLSearchParams();
    if (currentStateId) params.append("state_id", currentStateId);
    if (currentCountyId) params.append("county_id", currentCountyId);
    if (currentCourtType) params.append("court_type", currentCourtType);
    if (currentHasPat) params.append("has_pat", "true");
    if (currentSearch) params.append("search", currentSearch);
    params.append("limit", "60");

    try {
      const res = await fetch(`/api/courts?${params.toString()}`);
      const courts = await res.json();
      renderCourts(courts);
    } catch (err) {
      console.error("Error fetching courts", err);
      courtsGrid.innerHTML = `<div class="empty-state"><p>Error loading court directory. Please try again.</p></div>`;
    }
  }

  // Render Court Cards Grid
  function renderCourts(courts) {
    if (!courts || courts.length === 0) {
      courtsGrid.innerHTML = `
        <div class="empty-state">
          <p>No court records matched your filters.</p>
          <button class="btn btn-sm" style="margin-top: 0.75rem;" onclick="location.reload()">Reset Filters</button>
        </div>
      `;
      return;
    }

    courtsGrid.innerHTML = "";

    courts.forEach((c) => {
      const card = document.createElement("div");
      card.className = "court-card";

      const verifiedDate = c.last_verified_at ? new Date(c.last_verified_at).toLocaleDateString() : "Recently";

      const patHtml = c.has_pat ? `
        <div class="pat-card-box">
          <div class="pat-card-header">
            <span class="pat-title">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
              Public Access Terminals (PAT)
            </span>
            <span class="pat-count-tag">${c.pat_terminal_count || 2} Terminals</span>
          </div>
          <div class="pat-meta-row"><strong>Hours:</strong> ${c.pat_hours || 'Mon-Fri 8:30 AM - 4:00 PM'}</div>
          <div class="pat-meta-row"><strong>Fee:</strong> ${c.pat_fee_info || 'Free inspection, $0.50/page copy'}</div>
        </div>
      ` : `
        <div class="pat-card-box" style="background: #fef2f2; border-color: #fecaca; color: #991b1b;">
          <div class="pat-card-header">
            <span class="pat-title" style="color: #991b1b;">No PAT Onsite</span>
            <span class="pat-count-tag" style="color: #991b1b; border-color: #fecaca;">Request at Counter</span>
          </div>
        </div>
      `;

      card.innerHTML = `
        <div class="card-top">
          <div class="card-header-row">
            <div class="court-name">${c.name}</div>
            <span class="type-badge">${c.court_type}</span>
          </div>
          <div class="location-meta">
            <span>${c.city}, ${c.state_id}</span> • <span>${c.county_name}</span>
          </div>

          <div class="contact-list">
            <div class="contact-row">
              <span class="contact-label">Main Clerk Phone:</span>
              <span class="contact-value"><a href="tel:${c.main_phone}">${c.main_phone || 'N/A'}</a></span>
            </div>
            <div class="contact-row">
              <span class="contact-label">Direct Email:</span>
              <span class="contact-value">${c.email ? `<a href="mailto:${c.email}">${c.email}</a>` : 'On Request'}</span>
            </div>
            <div class="contact-row">
              <span class="contact-label">Physical Address:</span>
              <span class="contact-value" style="font-size:0.78rem;">${c.address || 'Government Plaza'}</span>
            </div>
          </div>

          ${patHtml}
        </div>

        <div class="card-actions">
          <span class="verified-tag">Auto-Synced: ${verifiedDate}</span>
          <div style="display:flex; gap:0.35rem;">
            <button class="btn btn-sm" onclick="openCourtDetail(${c.id})">Details & Fees</button>
            <button class="btn btn-sm btn-primary" onclick="quickVerifyCourt(${c.id})">Sync Now</button>
          </div>
        </div>
      `;

      courtsGrid.appendChild(card);
    });
  }

  // Open Detailed Modal
  window.openCourtDetail = async function (courtId) {
    try {
      const res = await fetch(`/api/courts/${courtId}`);
      const c = await res.json();

      modalBody.innerHTML = `
        <div style="margin-bottom: 1rem;">
          <span class="type-badge" style="margin-bottom:0.5rem; display:inline-block;">${c.court_type}</span>
          <h2 style="font-size:1.3rem; font-weight:700;">${c.name}</h2>
          <p style="color:var(--text-muted); font-size:0.88rem;">${c.county_name}, ${c.state_name} (${c.state_id})</p>
        </div>

        <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.25rem;">
          <div style="background:var(--bg-secondary); padding:0.85rem; border-radius:var(--radius);">
            <div style="font-size:0.75rem; font-weight:700; color:var(--text-secondary); margin-bottom:0.4rem; text-transform:uppercase;">Contact Information</div>
            <div style="font-size:0.85rem;"><strong>Main Line:</strong> ${c.main_phone || 'N/A'}</div>
            <div style="font-size:0.85rem;"><strong>Clerk Direct:</strong> ${c.clerk_phone || 'N/A'}</div>
            <div style="font-size:0.85rem;"><strong>Records Dept:</strong> ${c.records_phone || 'N/A'}</div>
            <div style="font-size:0.85rem;"><strong>Email:</strong> ${c.email || 'N/A'}</div>
          </div>

          <div style="background:var(--bg-secondary); padding:0.85rem; border-radius:var(--radius);">
            <div style="font-size:0.75rem; font-weight:700; color:var(--text-secondary); margin-bottom:0.4rem; text-transform:uppercase;">Fees & Search Portals</div>
            <div style="font-size:0.85rem;"><strong>Copy Fee / Page:</strong> $${c.copy_fee_per_page?.toFixed(2) || '0.50'}</div>
            <div style="font-size:0.85rem;"><strong>Certified Copy:</strong> $${c.certified_copy_fee?.toFixed(2) || '5.00'}</div>
            <div style="font-size:0.85rem; margin-top:0.25rem;"><a href="${c.online_search_url}" target="_blank" style="color:var(--accent);">Case Docket Search Portal &rarr;</a></div>
          </div>
        </div>

        <div style="background:var(--pat-green-bg); border:1px solid var(--pat-green-border); padding:1rem; border-radius:var(--radius); margin-bottom:1.25rem;">
          <h4 style="color:var(--pat-green); font-size:0.95rem; font-weight:700; margin-bottom:0.4rem;">Public Access Terminal (PAT) Operating Guidelines</h4>
          <p style="font-size:0.85rem; color:#166534; margin-bottom:0.35rem;"><strong>Workstation Terminals Available:</strong> ${c.pat_terminal_count} Onsite</p>
          <p style="font-size:0.85rem; color:#166534; margin-bottom:0.35rem;"><strong>Access Hours:</strong> ${c.pat_hours}</p>
          <p style="font-size:0.85rem; color:#166534; margin-bottom:0.35rem;"><strong>Onsite Policy & Location:</strong> ${c.pat_notes || 'Located in 1st Floor Public Records Room.'}</p>
        </div>

        <div style="font-size:0.75rem; color:var(--text-muted); display:flex; justify-content:space-between; align-items:center;">
          <span>Autonomously Verified by Nebius AI + Tavily Pipeline</span>
          <span>Last Verified: ${new Date(c.last_verified_at).toLocaleString()}</span>
        </div>
      `;

      courtModal.classList.add("active");
    } catch (err) {
      alert("Unable to fetch court details.");
    }
  };

  // Quick verify single court
  window.quickVerifyCourt = async function (courtId) {
    try {
      const res = await fetch("/api/sync/trigger", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ court_id: courtId })
      });
      const data = await res.json();
      alert(`Automated Sync Complete!\nCourt: ${data.data.court_name}\nStatus: ${data.data.status}\nChanged Fields: ${data.data.changed_fields_count}`);
      fetchCourts();
    } catch (err) {
      alert("Failed to run automated sync.");
    }
  };

  // Run Automated Sync Batch
  async function runAutomatedSync() {
    runSyncBtn.disabled = true;
    runSyncBtn.textContent = "Scanning via Nebius + Tavily...";

    const headers = { "Content-Type": "application/json" };
    if (nebiusKeyInput.value.trim()) headers["x-nebius-key"] = nebiusKeyInput.value.trim();
    if (tavilyKeyInput.value.trim()) headers["x-tavily-key"] = tavilyKeyInput.value.trim();

    try {
      const res = await fetch("/api/sync/trigger", {
        method: "POST",
        headers: headers,
        body: JSON.stringify({
          state_id: currentStateId || null,
          county_id: currentCountyId || null
        })
      });

      const data = await res.json();
      loadSyncLogs();
      fetchCourts();
      alert("Nebius AI & Tavily automated update pipeline executed successfully!");
    } catch (err) {
      alert("Error triggering sync pipeline.");
    } finally {
      runSyncBtn.disabled = false;
      runSyncBtn.textContent = "Run Autonomous Update Pipeline Now";
    }
  }

  // Load Sync Logs
  async function loadSyncLogs() {
    try {
      const res = await fetch("/api/sync/logs");
      const logs = await res.json();

      if (!logs || logs.length === 0) {
        syncLogsContainer.innerHTML = `<div class="empty-state"><p>No sync logs recorded yet.</p></div>`;
        return;
      }

      syncLogsContainer.innerHTML = logs.map(l => `
        <div class="log-item">
          <div style="font-weight:700; color:var(--text-primary);">${l.court_name} (Court #${l.court_id})</div>
          <div style="color:var(--text-secondary); margin-top:0.2rem;">Status: <span style="color:var(--pat-green); font-weight:600;">${l.status}</span> | ${new Date(l.executed_at).toLocaleString()}</div>
          ${l.changed_fields && Object.keys(l.changed_fields).length > 0 ? `
            <div style="margin-top:0.3rem; color:#0369a1;">Fields Updated: ${Object.keys(l.changed_fields).join(', ')}</div>
          ` : ''}
        </div>
      `).join('');
    } catch (err) {
      syncLogsContainer.innerHTML = `<p style="color:red; font-size:0.8rem;">Failed to load sync audit trail.</p>`;
    }
  }
});
