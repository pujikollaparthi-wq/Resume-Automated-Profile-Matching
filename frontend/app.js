/**
 * AI Automated Profile Matching - Frontend Application Logic
 */

// Global State
let currentUser = null;
let authToken = localStorage.getItem("auth_token") || null;
let sampleResumes = {};
let sampleJobs = {};
let activeJobs = [];
let skillTaxonomy = {};
let selectedResumeFile = null;
let batchSelectedFiles = [];
let batchCandidateMode = "presets";
let currentMatchResult = null;

// Initialization
document.addEventListener("DOMContentLoaded", () => {
  setupDragAndDrop();
  checkAuthStatus();
  loadPresets();
  loadJobs();
  loadSkillTaxonomy();
});

// ==========================================
// VIEW SWITCHING
// ==========================================
function switchView(viewName) {
  const views = ["Home", "Matcher", "Recruiter", "Admin", "Skills", "Guide"];
  views.forEach(v => {
    const el = document.getElementById(`view${v}`);
    const navBtn = document.getElementById(`nav${v}`);
    if (el) el.style.display = (v.toLowerCase() === viewName.toLowerCase()) ? "block" : "none";
    if (navBtn) {
      if (v.toLowerCase() === viewName.toLowerCase()) {
        navBtn.classList.add("active");
      } else {
        navBtn.classList.remove("active");
      }
    }
  });

  window.scrollTo({ top: 0, behavior: "smooth" });

  if (viewName === "admin") {
    loadAdminMetrics();
  }
}

// ==========================================
// AUTHENTICATION & USER MANAGEMENT
// ==========================================
async function checkAuthStatus() {
  if (!authToken) {
    renderAuthUI(null);
    return;
  }

  try {
    const res = await fetch("/api/auth/me", {
      headers: { "Authorization": `Bearer ${authToken}` }
    });
    const data = await res.json();
    if (data.authenticated && data.user) {
      currentUser = data.user;
      renderAuthUI(currentUser);
    } else {
      currentUser = null;
      authToken = null;
      localStorage.removeItem("auth_token");
      renderAuthUI(null);
    }
  } catch (e) {
    console.error("Auth check failed:", e);
    renderAuthUI(null);
  }
}

function renderAuthUI(user) {
  const container = document.getElementById("authActions");
  if (!container) return;

  if (user) {
    const initials = (user.full_name || user.username).charAt(0).toUpperCase();
    container.innerHTML = `
      <div class="user-badge" onclick="switchView('admin')" title="Role: ${user.role}">
        <div class="user-avatar">${initials}</div>
        <div class="user-info">
          <span class="user-name">${user.full_name || user.username}</span>
          <span class="user-role-tag">${user.role.toUpperCase()}</span>
        </div>
      </div>
      <button class="btn btn-secondary btn-sm" onclick="handleLogout()">Logout</button>
    `;
  } else {
    container.innerHTML = `
      <button class="btn btn-secondary btn-sm" onclick="openAuthModal('login')">Sign In</button>
      <button class="btn btn-primary btn-sm" onclick="openAuthModal('register')">Register</button>
    `;
  }
}

function openAuthModal(tab = "login") {
  document.getElementById("authModal").classList.add("active");
  switchAuthTab(tab);
}

function closeAuthModal() {
  document.getElementById("authModal").classList.remove("active");
}

function switchAuthTab(tab) {
  const isLogin = tab === "login";
  document.getElementById("formLogin").style.display = isLogin ? "block" : "none";
  document.getElementById("formRegister").style.display = isLogin ? "none" : "block";
  document.getElementById("tabBtnLogin").classList.toggle("active", isLogin);
  document.getElementById("tabBtnRegister").classList.toggle("active", !isLogin);
}

function quickFillLogin(username, password) {
  switchAuthTab("login");
  document.getElementById("loginUsername").value = username;
  document.getElementById("loginPassword").value = password;
}

async function handleLoginSubmit(e) {
  e.preventDefault();
  const username = document.getElementById("loginUsername").value.trim();
  const password = document.getElementById("loginPassword").value;

  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    const data = await res.json();
    if (!res.ok) {
      alert(data.detail || "Login failed. Please check credentials.");
      return;
    }
    authToken = data.token;
    currentUser = data.user;
    localStorage.setItem("auth_token", authToken);
    renderAuthUI(currentUser);
    closeAuthModal();
  } catch (err) {
    alert("Connection error during login.");
  }
}

async function handleRegisterSubmit(e) {
  e.preventDefault();
  const full_name = document.getElementById("regFullName").value.trim();
  const username = document.getElementById("regUsername").value.trim();
  const email = document.getElementById("regEmail").value.trim();
  const password = document.getElementById("regPassword").value;
  const role = document.getElementById("regRole").value;

  try {
    const res = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ full_name, username, email, password, role })
    });
    const data = await res.json();
    if (!res.ok) {
      alert(data.detail || "Registration failed.");
      return;
    }
    authToken = data.token;
    currentUser = data.user;
    localStorage.setItem("auth_token", authToken);
    renderAuthUI(currentUser);
    closeAuthModal();
  } catch (err) {
    alert("Registration error occurred.");
  }
}

function handleLogout() {
  authToken = null;
  currentUser = null;
  localStorage.removeItem("auth_token");
  renderAuthUI(null);
  switchView("home");
}

// ==========================================
// PRESETS & JOBS LOADING
// ==========================================
async function loadPresets() {
  try {
    const res = await fetch("/api/presets");
    const data = await res.json();
    sampleResumes = data.sample_resumes || {};
    sampleJobs = data.sample_jobs || {};

    renderSampleResumeChips();
    renderSampleJobChips();
  } catch (err) {
    console.error("Failed to load presets:", err);
  }
}

async function loadJobs() {
  try {
    const res = await fetch("/api/jobs");
    activeJobs = await res.json();
    populateBatchJobSelect();
  } catch (err) {
    console.error("Failed to load active jobs:", err);
  }
}

function renderSampleResumeChips() {
  const container = document.getElementById("sampleResumesBar");
  if (!container) return;
  container.innerHTML = "";

  Object.values(sampleResumes).forEach(cand => {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "preset-chip";
    chip.textContent = `${cand.name} (${cand.title.split(" ")[1] || "Role"})`;
    chip.onclick = () => selectSampleResume(cand.id);
    container.appendChild(chip);
  });
}

function selectSampleResume(candId) {
  const cand = sampleResumes[candId];
  if (!cand) return;

  clearSelectedFile();
  document.getElementById("resumeTextInput").value = cand.text;

  // Highlight chip
  document.querySelectorAll("#sampleResumesBar .preset-chip").forEach(c => {
    c.classList.toggle("active", c.textContent.includes(cand.name));
  });
}

function renderSampleJobChips() {
  const container = document.getElementById("sampleJobsBar");
  if (!container) return;
  container.innerHTML = "";

  Object.values(sampleJobs).forEach(job => {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "preset-chip";
    chip.textContent = job.title;
    chip.onclick = () => selectSampleJob(job.id);
    container.appendChild(chip);
  });
}

function selectSampleJob(jobId) {
  const job = sampleJobs[jobId];
  if (!job) return;

  document.getElementById("targetJobTitle").value = job.title;
  document.getElementById("jobTextInput").value = job.description;

  document.querySelectorAll("#sampleJobsBar .preset-chip").forEach(c => {
    c.classList.toggle("active", c.textContent === job.title);
  });
}

function populateBatchJobSelect() {
  const select = document.getElementById("batchJobSelect");
  if (!select) return;
  select.innerHTML = "";

  if (activeJobs.length === 0) {
    select.innerHTML = `<option value="">No active jobs found</option>`;
    return;
  }

  activeJobs.forEach(j => {
    const opt = document.createElement("option");
    opt.value = j.id;
    opt.textContent = `${j.title} (${j.company})`;
    select.appendChild(opt);
  });
}

// ==========================================
// RESUME DRAG & DROP AND FILE HANDLING
// ==========================================
function setupDragAndDrop() {
  const dropzone = document.getElementById("resumeDropzone");
  if (!dropzone) return;

  ["dragenter", "dragover"].forEach(eventName => {
    dropzone.addEventListener(eventName, e => {
      e.preventDefault();
      dropzone.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach(eventName => {
    dropzone.addEventListener(eventName, e => {
      e.preventDefault();
      dropzone.classList.remove("dragover");
    });
  });

  dropzone.addEventListener("drop", e => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      applySelectedResumeFile(files[0]);
    }
  });
}

function handleResumeFileSelected(input) {
  if (input.files && input.files.length > 0) {
    applySelectedResumeFile(input.files[0]);
  }
}

function applySelectedResumeFile(file) {
  selectedResumeFile = file;
  document.getElementById("selectedFileName").textContent = file.name;
  document.getElementById("fileSelectedBadge").style.display = "inline-flex";
  document.getElementById("resumeTextInput").value = "";
}

function clearSelectedFile(e) {
  if (e) e.stopPropagation();
  selectedResumeFile = null;
  const input = document.getElementById("resumeFileInput");
  if (input) input.value = "";
  const badge = document.getElementById("fileSelectedBadge");
  if (badge) badge.style.display = "none";
}

// ==========================================
// CANDIDATE PROFILE MATCHING TRIGGER
// ==========================================
async function triggerProfileMatching() {
  const resumeText = document.getElementById("resumeTextInput").value.trim();
  const jobTitle = document.getElementById("targetJobTitle").value.trim();
  const jobText = document.getElementById("jobTextInput").value.trim();

  if (!selectedResumeFile && !resumeText) {
    alert("Please upload a resume file (PDF/DOCX) or paste resume text.");
    return;
  }

  if (!jobText) {
    alert("Please select or paste a target Job Description.");
    return;
  }

  const btn = document.getElementById("btnRunMatch");
  const originalHtml = btn.innerHTML;
  btn.innerHTML = `<span style="display:inline-block; animation:spin 1s linear infinite;">⏳</span> Analyzing with AI & NLP...`;
  btn.disabled = true;

  try {
    const formData = new FormData();
    if (selectedResumeFile) {
      formData.append("resume_file", selectedResumeFile);
    } else {
      formData.append("resume_text", resumeText);
    }
    formData.append("job_title", jobTitle || "Target Role");
    formData.append("job_text", jobText);

    const headers = {};
    if (authToken) {
      headers["Authorization"] = `Bearer ${authToken}`;
    }

    const res = await fetch("/api/match", {
      method: "POST",
      headers: headers,
      body: formData
    });

    const data = await res.json();
    if (!res.ok) {
      alert(data.detail || "Profile matching evaluation failed.");
      return;
    }

    currentMatchResult = data;
    renderMatchResults(data);
  } catch (err) {
    console.error(err);
    alert("Error occurred while contacting NLP matching service.");
  } finally {
    btn.innerHTML = originalHtml;
    btn.disabled = false;
  }
}

// ==========================================
// RENDER MATCH RESULTS & GAUGE ANIMATION
// ==========================================
function renderMatchResults(res) {
  const resultsArea = document.getElementById("matchResultsArea");
  resultsArea.style.display = "block";

  // Score Dial Animation
  animateScoreDial(res.match_score);

  // Verdict & Badges
  const verdictBadge = document.getElementById("verdictBadge");
  verdictBadge.textContent = res.verdict;
  verdictBadge.className = `verdict-badge ${res.verdict_badge || 'badge-success'}`;

  const atsStatusBadge = document.getElementById("atsStatusBadge");
  atsStatusBadge.textContent = `ATS: ${res.ats_status}`;
  atsStatusBadge.style.color = res.ats_status === "PASSED" ? "#34D399" : (res.ats_status === "REVIEW" ? "#FBBF24" : "#FB7185");

  document.getElementById("resCandidateName").textContent = res.candidate.name || "Candidate Profile";
  document.getElementById("resJobTitle").textContent = res.job_title || "Target Position";

  // Mini metrics
  document.getElementById("valSkillScore").textContent = `${res.skill_score}%`;
  document.getElementById("valTfidfScore").textContent = `${res.tfidf_score}% (Sim: ${res.raw_cosine_similarity})`;
  const expYears = res.candidate.years_experience || 0;
  document.getElementById("valExperience").textContent = expYears > 0 ? `${expYears} Years Detected` : "Standard Experience";

  // Matched Skills
  const matchedContainer = document.getElementById("matchedSkillsList");
  matchedContainer.innerHTML = "";
  document.getElementById("matchedSkillsCount").textContent = res.matched_skills.length;
  if (res.matched_skills.length === 0) {
    matchedContainer.innerHTML = `<span style="color:var(--text-dim); font-size:0.85rem;">No exact keyword skill overlap found.</span>`;
  } else {
    res.matched_skills.forEach(s => {
      matchedContainer.appendChild(createSkillBadge(s.name, "matched"));
    });
  }

  // Missing Skills
  const missingContainer = document.getElementById("missingSkillsList");
  missingContainer.innerHTML = "";
  document.getElementById("missingSkillsCount").textContent = res.missing_skills.length;
  if (res.missing_skills.length === 0) {
    missingContainer.innerHTML = `<span style="color:var(--accent-emerald); font-size:0.85rem;">Full coverage! No critical required skills missing.</span>`;
  } else {
    res.missing_skills.forEach(s => {
      missingContainer.appendChild(createSkillBadge(s.name, "missing"));
    });
  }

  // Bonus Skills
  const bonusContainer = document.getElementById("bonusSkillsList");
  bonusContainer.innerHTML = "";
  document.getElementById("bonusSkillsCount").textContent = res.bonus_skills.length;
  if (res.bonus_skills.length === 0) {
    bonusContainer.innerHTML = `<span style="color:var(--text-dim); font-size:0.85rem;">No additional skills detected.</span>`;
  } else {
    res.bonus_skills.forEach(s => {
      bonusContainer.appendChild(createSkillBadge(s.name, "bonus"));
    });
  }

  // AI Recommendations
  const recList = document.getElementById("aiRecommendationsList");
  recList.innerHTML = "";
  (res.recommendations || []).forEach(r => {
    const li = document.createElement("li");
    li.className = "rec-item";
    li.innerHTML = `
      <svg class="rec-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
      <div>${r}</div>
    `;
    recList.appendChild(li);
  });

  resultsArea.scrollIntoView({ behavior: "smooth", block: "start" });
}

function animateScoreDial(targetScore) {
  const circle = document.getElementById("dialProgressCircle");
  const valueDisplay = document.getElementById("dialScoreValue");
  const totalCircumference = 263.89; // 2 * PI * 42

  const offset = totalCircumference - (targetScore / 100) * totalCircumference;
  circle.style.strokeDashoffset = offset;

  let current = 0;
  const duration = 1000;
  const stepTime = 20;
  const steps = duration / stepTime;
  const increment = targetScore / steps;

  const timer = setInterval(() => {
    current += increment;
    if (current >= targetScore) {
      current = targetScore;
      clearInterval(timer);
    }
    valueDisplay.innerHTML = `${Math.round(current)}<span>%</span>`;
  }, stepTime);
}

function createSkillBadge(name, type) {
  const badge = document.createElement("span");
  badge.className = `skill-badge ${type}`;
  let icon = "";
  if (type === "matched") icon = "✓ ";
  else if (type === "missing") icon = "✗ ";
  else if (type === "bonus") icon = "+ ";
  badge.textContent = icon + name;
  return badge;
}

// Print / Export ATS Candidate Evaluation Report
function printEvaluationReport() {
  window.print();
}

// ==========================================
// RECRUITER BATCH SCREENING
// ==========================================
function setBatchCandidateMode(mode) {
  batchCandidateMode = mode;
  const label = document.getElementById("batchFilesLabel");
  if (mode === "presets") {
    batchSelectedFiles = [];
    label.textContent = "Selected: 4 Diverse Sample Candidates Pool (Alex Morgan, Priya Sharma, Marcus Vance, Jordan Lee)";
  }
}

function handleBatchFilesSelected(input) {
  if (input.files && input.files.length > 0) {
    batchSelectedFiles = Array.from(input.files);
    batchCandidateMode = "files";
    document.getElementById("batchFilesLabel").textContent = `Selected: ${batchSelectedFiles.length} Uploaded Resume File(s)`;
  }
}

function handleBatchJobChange(jobId) {
  // Update internal state if needed
}

async function triggerBatchScreening() {
  const jobId = document.getElementById("batchJobSelect").value;
  if (!jobId) {
    alert("Please select a target requisition role.");
    return;
  }

  const formData = new FormData();
  formData.append("job_id", jobId);

  if (batchCandidateMode === "files" && batchSelectedFiles.length > 0) {
    batchSelectedFiles.forEach(f => {
      formData.append("resume_files", f);
    });
  } else {
    // Send sample candidate keys
    formData.append("candidate_preset_keys", "ml_senior,fullstack_dev,devops_eng,junior_intern");
  }

  try {
    const res = await fetch("/api/match/batch", {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    if (!res.ok) {
      alert(data.detail || "Batch screening failed.");
      return;
    }
    renderBatchLeaderboard(data);
  } catch (err) {
    console.error(err);
    alert("Error performing batch applicant ranking.");
  }
}

function renderBatchLeaderboard(data) {
  const card = document.getElementById("batchLeaderboardCard");
  card.style.display = "block";

  document.getElementById("batchTargetJobLabel").textContent = `Requisition: ${data.job_title}`;
  document.getElementById("batchCountBadge").textContent = `${data.total_evaluated} Applicants Ranked`;

  const tbody = document.getElementById("batchLeaderboardBody");
  tbody.innerHTML = "";

  data.leaderboard.forEach((cand, idx) => {
    const tr = document.createElement("tr");

    let rankClass = "rank-other";
    if (cand.rank === 1) rankClass = "rank-1";
    else if (cand.rank === 2) rankClass = "rank-2";
    else if (cand.rank === 3) rankClass = "rank-3";

    tr.innerHTML = `
      <td>
        <span class="rank-badge ${rankClass}">#${cand.rank}</span>
      </td>
      <td>
        <div style="font-weight: 700; color: #fff;">${cand.candidate.name}</div>
        <div style="font-size: 0.8rem; color: var(--text-muted);">${cand.source_label || "Uploaded Document"}</div>
      </td>
      <td style="width: 220px;">
        <div style="font-weight: 800; font-size: 1.1rem; color: #fff;">${cand.match_score}%</div>
        <div class="score-progress-bar">
          <div class="score-progress-fill" style="width: ${cand.match_score}%;"></div>
        </div>
      </td>
      <td>
        <span style="color: var(--accent-emerald); font-weight: 700;">${cand.stats.matched_count}</span> Matched / 
        <span style="color: var(--accent-rose); font-weight: 700;">${cand.stats.missing_count}</span> Missing
      </td>
      <td>
        <span class="verdict-badge ${cand.verdict_badge}">${cand.verdict.split(" - ")[0]}</span>
      </td>
      <td style="text-align: right;">
        <button class="btn btn-secondary btn-sm" onclick='viewCandidateAudit(${JSON.stringify(cand).replace(/'/g, "&apos;")})'>Audit</button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  card.scrollIntoView({ behavior: "smooth", block: "start" });
}

function viewCandidateAudit(cand) {
  const modal = document.getElementById("candidateAuditModal");
  const body = document.getElementById("auditModalBody");

  body.innerHTML = `
    <div style="margin-bottom: 20px;">
      <span class="verdict-badge ${cand.verdict_badge}">${cand.verdict}</span>
      <h3 style="font-size: 1.5rem; font-weight: 800; color: #fff; margin-top: 8px;">${cand.candidate.name}</h3>
      <p style="color: var(--accent-cyan); font-size: 0.9rem;">${cand.source_label}</p>
    </div>

    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px;">
      <div class="mini-metric-pill">
        <div class="mini-metric-title">Overall Match</div>
        <div class="mini-metric-value">${cand.match_score}%</div>
      </div>
      <div class="mini-metric-pill">
        <div class="mini-metric-title">Skill Match</div>
        <div class="mini-metric-value">${cand.skill_score}%</div>
      </div>
      <div class="mini-metric-pill">
        <div class="mini-metric-title">TF-IDF Sim</div>
        <div class="mini-metric-value">${cand.tfidf_score}%</div>
      </div>
    </div>

    <div style="margin-bottom: 16px;">
      <h4 style="font-size: 0.95rem; font-weight: 700; color: var(--accent-emerald); margin-bottom: 8px;">Matched Skills (${cand.matched_skills.length})</h4>
      <div class="skill-tag-container">
        ${cand.matched_skills.map(s => `<span class="skill-badge matched">✓ ${s.name}</span>`).join("")}
      </div>
    </div>

    <div style="margin-bottom: 16px;">
      <h4 style="font-size: 0.95rem; font-weight: 700; color: var(--accent-rose); margin-bottom: 8px;">Missing Required Skills (${cand.missing_skills.length})</h4>
      <div class="skill-tag-container">
        ${cand.missing_skills.map(s => `<span class="skill-badge missing">✗ ${s.name}</span>`).join("")}
      </div>
    </div>

    <div>
      <h4 style="font-size: 0.95rem; font-weight: 700; color: var(--accent-cyan); margin-bottom: 8px;">AI Screening Recommendations</h4>
      <ul class="recommendations-list">
        ${cand.recommendations.map(r => `<li class="rec-item"><div>${r}</div></li>`).join("")}
      </ul>
    </div>
  `;

  modal.classList.add("active");
}

function closeCandidateAuditModal() {
  document.getElementById("candidateAuditModal").classList.remove("active");
}

// ==========================================
// ADMIN DASHBOARD & METRICS
// ==========================================
async function loadAdminMetrics() {
  if (!authToken) {
    // Show login prompt modal if user isn't logged in
    openAuthModal("login");
    return;
  }

  try {
    const res = await fetch("/api/admin/metrics", {
      headers: { "Authorization": `Bearer ${authToken}` }
    });
    if (res.status === 403 || res.status === 401) {
      alert("Admin or Recruiter privileges required to view metrics. Please login with admin credentials.");
      quickFillLogin("admin", "admin123");
      return;
    }
    const data = await res.json();
    renderAdminMetrics(data);
  } catch (err) {
    console.error("Admin metrics fetch error:", err);
  }
}

function renderAdminMetrics(data) {
  document.getElementById("adminTotalEvals").textContent = data.summary.total_evaluations;
  document.getElementById("adminAvgScore").innerHTML = `${data.summary.average_match_score}<span>%</span>`;
  document.getElementById("adminTotalUsers").textContent = data.summary.total_users;
  document.getElementById("adminTotalJobs").textContent = data.summary.total_jobs;

  // Top Skills
  const skillsContainer = document.getElementById("adminTopSkillsList");
  skillsContainer.innerHTML = "";
  data.top_in_demand_skills.forEach(item => {
    const row = document.createElement("div");
    row.style.cssText = "display: flex; align-items: center; justify-content: space-between; font-size: 0.88rem;";
    row.innerHTML = `
      <span style="font-weight: 600;">${item.skill}</span>
      <span style="background: rgba(99,102,241,0.2); color: #A5B4FC; padding: 2px 8px; border-radius: var(--radius-full); font-weight: 700; font-size: 0.78rem;">${item.count} jobs</span>
    `;
    skillsContainer.appendChild(row);
  });

  // Active Jobs
  renderAdminJobsList();

  // Recent Evaluations
  const evalBody = document.getElementById("adminRecentEvalsBody");
  evalBody.innerHTML = "";
  data.recent_evaluations.forEach(ev => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>#${ev.id}</td>
      <td style="font-weight: 600; color: #fff;">${ev.candidate_name}</td>
      <td>${ev.job_title}</td>
      <td style="font-weight: 700; color: var(--accent-cyan);">${ev.match_score}%</td>
      <td><span class="verdict-badge ${ev.match_score >= 75 ? 'badge-success' : 'badge-warning'}">${ev.verdict.split(" - ")[0]}</span></td>
      <td style="font-size: 0.8rem; color: var(--text-dim);">${ev.created_at || "Recent"}</td>
    `;
    evalBody.appendChild(tr);
  });
}

function renderAdminJobsList() {
  const container = document.getElementById("adminJobsList");
  if (!container) return;
  container.innerHTML = "";

  activeJobs.forEach(job => {
    const div = document.createElement("div");
    div.style.cssText = "display: flex; align-items: center; justify-content: space-between; padding: 10px; background: rgba(255,255,255,0.03); border-radius: var(--radius-md); border: 1px solid var(--border-subtle);";
    div.innerHTML = `
      <div>
        <div style="font-weight: 700; font-size: 0.9rem; color: #fff;">${job.title}</div>
        <div style="font-size: 0.76rem; color: var(--text-muted);">${job.company} • ${job.experience_required}</div>
      </div>
      <button class="btn btn-danger btn-sm" onclick="handleDeleteJob(${job.id})">Delete</button>
    `;
    container.appendChild(div);
  });
}

function openNewJobModal() {
  document.getElementById("newJobModal").classList.add("active");
}

function closeNewJobModal() {
  document.getElementById("newJobModal").classList.remove("active");
}

async function handleCreateJobSubmit(e) {
  e.preventDefault();
  const title = document.getElementById("newJobTitle").value.trim();
  const company = document.getElementById("newJobCompany").value.trim();
  const department = document.getElementById("newJobDept").value.trim();
  const experience_required = document.getElementById("newJobExp").value.trim();
  const rawSkills = document.getElementById("newJobSkills").value.trim();
  const description = document.getElementById("newJobDesc").value.trim();

  const required_skills = rawSkills.split(",").map(s => s.trim()).filter(Boolean);

  try {
    const res = await fetch("/api/jobs", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${authToken}`
      },
      body: JSON.stringify({
        title, company, department, experience_required, description, required_skills
      })
    });
    if (!res.ok) {
      alert("Failed to post job. Please ensure you are logged in as Admin or Recruiter.");
      return;
    }
    alert("Job requisition posted successfully!");
    closeNewJobModal();
    await loadJobs();
    loadAdminMetrics();
  } catch (err) {
    alert("Error creating job.");
  }
}

async function handleDeleteJob(jobId) {
  if (!confirm("Are you sure you want to delete this job requisition?")) return;

  try {
    const res = await fetch(`/api/jobs/${jobId}`, {
      method: "DELETE",
      headers: { "Authorization": `Bearer ${authToken}` }
    });
    if (!res.ok) {
      alert("Failed to delete job.");
      return;
    }
    await loadJobs();
    loadAdminMetrics();
  } catch (err) {
    alert("Error deleting job.");
  }
}

// ==========================================
// SKILL TAXONOMY EXPLORER
// ==========================================
async function loadSkillTaxonomy() {
  try {
    const res = await fetch("/api/skills");
    skillTaxonomy = await res.json();
    renderTaxonomy(skillTaxonomy);
  } catch (err) {
    console.error("Failed to load skills taxonomy:", err);
  }
}

function renderTaxonomy(tax) {
  const container = document.getElementById("taxonomyContainer");
  if (!container) return;
  container.innerHTML = "";

  Object.entries(tax).forEach(([category, skills]) => {
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <div class="card-header">
        <h4 class="card-title" style="font-size: 1rem;">${category}</h4>
        <span style="font-size: 0.74rem; color: var(--accent-cyan);">${skills.length} skills</span>
      </div>
      <div class="skill-tag-container">
        ${skills.map(s => `<span class="skill-badge matched" style="font-size:0.75rem;">${s}</span>`).join("")}
      </div>
    `;
    container.appendChild(card);
  });
}

function filterTaxonomySkills(query) {
  const q = query.toLowerCase().trim();
  if (!q) {
    renderTaxonomy(skillTaxonomy);
    return;
  }

  const filtered = {};
  Object.entries(skillTaxonomy).forEach(([category, skills]) => {
    const matching = skills.filter(s => s.toLowerCase().includes(q));
    if (matching.length > 0) {
      filtered[category] = matching;
    }
  });
  renderTaxonomy(filtered);
}
