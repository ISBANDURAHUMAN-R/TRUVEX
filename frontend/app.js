/**
 * TruVex AI - Main Application Controller
 */

window.API_BASE = window.API_BASE || ((window.location.protocol === "file:" || (window.location.port && window.location.port !== "8000")) ? "http://127.0.0.1:8000" : "");
var API_BASE = window.API_BASE;

let currentAnalysisResult = null;
let uploadedImageBase64 = null;

document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initDemoPresets();
    initImageUpload();
    initApiKeySettings();
});

// 1. Tab Navigation
function initTabs() {
    const tabs = document.querySelectorAll(".tab-btn");
    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => t.classList.remove("active"));
            tab.classList.add("active");

            const targetId = tab.getAttribute("data-tab");
            document.querySelectorAll(".tab-pane").forEach(pane => {
                pane.style.display = "none";
            });
            const activePane = document.getElementById(targetId);
            if (activePane) activePane.style.display = "block";
        });
    });
}

// 2. Demo Presets
async function initDemoPresets() {
    const container = document.getElementById("demo-presets-container");
    if (!container) return;

    try {
        const res = await fetch(`${API_BASE}/api/demos`);
        if (!res.ok) return;
        const demos = await res.json();

        container.innerHTML = demos.map(demo => `
            <button class="glass-card" style="padding:0.6rem 0.9rem;text-align:left;border:1px solid rgba(239,68,68,0.25);cursor:pointer;background:rgba(22,4,6,0.7);border-radius:0.5rem;transition:all 0.2s;" onclick="loadPresetDemo('${demo.id}')">
                <div style="font-size:0.75rem;font-weight:700;color:#ff4d6d;margin-bottom:0.2rem;">${escapeHtml(demo.category)}</div>
                <div style="font-size:0.82rem;color:#f1f5f9;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:240px;">${escapeHtml(demo.title)}</div>
            </button>
        `).join("");
    } catch (e) {
        // Fallback silent
    }
}

async function loadPresetDemo(demoId) {
    try {
        const res = await fetch(`${API_BASE}/api/demos`);
        const demos = await res.json();
        const found = demos.find(d => d.id === demoId);
        if (!found) return;

        if (found.url) {
            document.querySelector('[data-tab="tab-url"]').click();
            document.getElementById("input-url").value = found.url;
            document.getElementById("input-text").value = "";
        } else {
            document.querySelector('[data-tab="tab-text"]').click();
            document.getElementById("input-text").value = found.text;
            document.getElementById("input-url").value = "";
        }

        // Trigger analysis
        analyzeContent();
    } catch (e) {
        alert("Error loading demo: " + e.message);
    }
}

// 3. Image Upload Handling
function initImageUpload() {
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");
    const previewContainer = document.getElementById("image-preview-container");
    const previewImg = document.getElementById("image-preview");

    if (!dropZone || !fileInput) return;

    dropZone.addEventListener("click", () => fileInput.click());

    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.style.borderColor = "var(--accent-red)";
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.style.borderColor = "var(--border-subtle)";
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.style.borderColor = "var(--border-subtle)";
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            processImageFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener("change", () => {
        if (fileInput.files && fileInput.files[0]) {
            processImageFile(fileInput.files[0]);
        }
    });

    function processImageFile(file) {
        if (!file.type.startsWith("image/")) {
            alert("Please select an image file (PNG, JPG, WebP).");
            return;
        }
        const reader = new FileReader();
        reader.onload = (e) => {
            uploadedImageBase64 = e.target.result;
            previewImg.src = uploadedImageBase64;
            previewContainer.style.display = "block";
            dropZone.style.display = "none";
        };
        reader.readAsDataURL(file);
    }

    const removeBtn = document.getElementById("remove-image-btn");
    if (removeBtn) {
        removeBtn.addEventListener("click", () => {
            uploadedImageBase64 = null;
            previewImg.src = "";
            previewContainer.style.display = "none";
            dropZone.style.display = "block";
            fileInput.value = "";
        });
    }
}

// 4. API Key Settings
function initApiKeySettings() {
    const savedKey = localStorage.getItem("truvex_gemini_key") || localStorage.getItem("truthlens_gemini_key");
    const keyInput = document.getElementById("input-custom-api-key");
    if (keyInput && savedKey) {
        keyInput.value = savedKey;
    }
}

function saveCustomApiKey() {
    const keyInput = document.getElementById("input-custom-api-key");
    if (!keyInput) return;
    const val = keyInput.value.trim();
    if (val) {
        localStorage.setItem("truvex_gemini_key", val);
        localStorage.removeItem("truthlens_gemini_key");
        alert("Custom Gemini API key saved! It will be used for future in-depth fact-checking queries.");
    } else {
        localStorage.removeItem("truvex_gemini_key");
        localStorage.removeItem("truthlens_gemini_key");
        alert("Custom API key removed. Using autonomous built-in engine.");
    }
    toggleSettingsModal(false);
}

// 5. Core Analysis Handler
async function analyzeContent() {
    const url = (document.getElementById("input-url")?.value || "").trim();
    const text = (document.getElementById("input-text")?.value || "").trim();
    const apiKey = localStorage.getItem("truvex_gemini_key") || localStorage.getItem("truthlens_gemini_key") || "";

    if (!url && !text && !uploadedImageBase64) {
        alert("Please paste a URL, enter news text, or upload a screenshot to analyze.");
        return;
    }

    showLoading(true);
    resetDashboard();

    const progressSteps = [
        "Detecting platform & verifying domain credentials...",
        "Extracting headline, body text & metadata...",
        "Decomposing content into atomic verifiable claims...",
        "Executing multi-query real-time web search...",
        "Cross-referencing independent evidence & stance...",
        "Checking timeline & archival recirculation signals...",
        "Calculating digital trust & confidence score..."
    ];

    let stepIdx = 0;
    const stepInterval = setInterval(() => {
        if (stepIdx < progressSteps.length) {
            updateScanProgress(progressSteps[stepIdx], ((stepIdx + 1) / progressSteps.length) * 100);
            stepIdx++;
        }
    }, 1200);

    try {
        const response = await fetch(`${API_BASE}/api/analyze`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                url: url || null,
                text: text || null,
                image_base64: uploadedImageBase64 || null,
                api_key: apiKey || null
            })
        });

        clearInterval(stepInterval);

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to analyze content");
        }

        const data = await response.json();
        currentAnalysisResult = data;
        
        renderDashboard(data);
        
        // Scroll smoothly to results
        setTimeout(() => {
            const resEl = document.getElementById("results-section");
            if (resEl) resEl.scrollIntoView({ behavior: "smooth" });
        }, 150);

    } catch (err) {
        clearInterval(stepInterval);
        alert("Analysis Error: " + err.message);
    } finally {
        showLoading(false);
    }
}

// 6. Dashboard Rendering
function renderDashboard(data) {
    const resultsSection = document.getElementById("results-section");
    if (!resultsSection) return;
    resultsSection.style.display = "block";

    // Inaccessible platform notice check
    const inaccessibleNotice = document.getElementById("inaccessible-platform-banner");
    if (data.is_inaccessible_platform) {
        inaccessibleNotice.style.display = "block";
        document.getElementById("inaccessible-platform-text").textContent = data.inaccessible_message || "Content could not be directly retrieved from this platform. Please paste the text or upload a screenshot.";
        // Fill prompt in text tab automatically
        document.querySelector('[data-tab="tab-text"]').click();
    } else {
        inaccessibleNotice.style.display = "none";
    }

    // 1. Final Verdict Top Banner
    const verdictBanner = document.getElementById("final-verdict-card");
    const verdictTitle = document.getElementById("final-verdict-title");
    const verdictExplanation = document.getElementById("final-verdict-explanation");
    const lastCheckedEl = document.getElementById("last-checked-label");

    verdictTitle.textContent = data.overall_verdict;
    verdictExplanation.textContent = data.verdict_explanation;
    if (lastCheckedEl) lastCheckedEl.textContent = `Verified: ${data.last_checked}`;

    // Verdict card glow border
    let glowColor = "rgba(148, 163, 184, 0.3)";
    let strokeColor = "#94a3b8";
    if (data.overall_verdict.includes("TRUE")) {
        glowColor = "rgba(16, 185, 129, 0.25)";
        strokeColor = "#10b981";
    } else if (data.overall_verdict.includes("FALSE")) {
        glowColor = "rgba(239, 68, 68, 0.25)";
        strokeColor = "#ef4444";
    } else if (data.overall_verdict.includes("MISLEADING")) {
        glowColor = "rgba(245, 158, 11, 0.25)";
        strokeColor = "#f59e0b";
    }
    verdictBanner.style.borderColor = strokeColor;
    verdictBanner.style.boxShadow = `0 0 25px ${glowColor}`;

    // Circular Gauge Animation
    updateGauge(data.trust_score, strokeColor);

    // 2. Sub-scores Grid
    document.getElementById("score-confidence").textContent = `${data.confidence}%`;
    document.getElementById("score-accuracy").textContent = `${data.claim_accuracy}%`;
    document.getElementById("score-source-cred").textContent = `${data.source_credibility}/100`;
    document.getElementById("score-evidence-strength").textContent = `${data.evidence_strength}%`;
    document.getElementById("score-manipulation-risk").textContent = `${data.manipulation_risk}%`;

    // 3. Platform & Source Info
    document.getElementById("meta-platform").textContent = data.platform;
    document.getElementById("meta-domain").textContent = data.domain;
    document.getElementById("meta-source-type").textContent = data.source_type;
    document.getElementById("meta-cred-score").textContent = `${data.source_credibility}/100`;
    document.getElementById("meta-cred-explanation").textContent = data.source_credibility_explanation;

    // 4. Misinformation Type
    const misinfoBadge = document.getElementById("misinfo-type-badge");
    misinfoBadge.textContent = data.misinformation_type;
    document.getElementById("misinfo-type-explanation").textContent = data.misinformation_type_explanation;

    // 5. Timeline Recirculation Alert
    const timelineAlert = document.getElementById("timeline-recirculation-alert");
    if (data.timeline_check && data.timeline_check.is_old_recirculated) {
        timelineAlert.style.display = "block";
        document.getElementById("timeline-alert-text").textContent = data.timeline_check.warning_message;
    } else {
        timelineAlert.style.display = "none";
    }

    // 6. Claims Counter
    const totalClaims = data.claims.length;
    const verifiedCount = data.claims.filter(c => c.verdict.includes("TRUE")).length;
    const misleadingCount = data.claims.filter(c => c.verdict === "MISLEADING").length;
    const falseCount = data.claims.filter(c => c.verdict.includes("FALSE")).length;
    const unverifiedCount = data.claims.filter(c => c.verdict === "UNVERIFIED").length;

    document.getElementById("claims-count-total").textContent = totalClaims;
    document.getElementById("claims-count-verified").textContent = verifiedCount;
    document.getElementById("claims-count-misleading").textContent = misleadingCount;
    document.getElementById("claims-count-false").textContent = falseCount;
    document.getElementById("claims-count-unverified").textContent = unverifiedCount;

    // 7. Claim-by-Claim Breakdown Cards
    renderClaimsList(data.claims);

    // 8. Original Source Discovery
    const origSourceCard = document.getElementById("original-source-card");
    if (data.original_source) {
        origSourceCard.style.display = "block";
        document.getElementById("orig-source-name").textContent = data.original_source.source_name;
        document.getElementById("orig-source-date").textContent = data.original_source.date || "Earliest Record";
        document.getElementById("orig-source-rationale").textContent = data.original_source.evidence_rationale;
        const origLink = document.getElementById("orig-source-link");
        if (data.original_source.link && data.original_source.link !== "#") {
            origLink.href = data.original_source.link;
            origLink.style.display = "inline-flex";
        } else {
            origLink.style.display = "none";
        }
    } else {
        origSourceCard.style.display = "none";
    }

    // 9. Related & Similar News
    renderRelatedNews(data.related_sources);

    // 10. Image Forensics (if present)
    const imageCard = document.getElementById("image-forensics-card");
    if (data.image_analysis) {
        imageCard.style.display = "block";
        document.getElementById("img-forensic-status").textContent = data.image_analysis.status;
        document.getElementById("img-forensic-risk").textContent = data.image_analysis.manipulation_risk;
        document.getElementById("img-forensic-notes").textContent = data.image_analysis.forensic_notes;
    } else {
        imageCard.style.display = "none";
    }

    // 11. Visual Relationship Source Graph
    renderSourceGraph(data.source_graph, "source-graph-container");
}

function renderClaimsList(claims) {
    const container = document.getElementById("claims-list-container");
    if (!container) return;

    if (!claims || claims.length === 0) {
        container.innerHTML = `
            <div class="glass-card" style="padding:2rem;text-align:center;color:#64748b;">
                No testable factual claims were isolated from the input.
            </div>
        `;
        return;
    }

    container.innerHTML = claims.map((c, idx) => {
        let badgeClass = "badge-unverified";
        let cardBorderColor = "#334155";
        if (c.verdict === "TRUE") { badgeClass = "badge-true"; cardBorderColor = "rgba(16, 185, 129, 0.4)"; }
        else if (c.verdict === "MOSTLY TRUE") { badgeClass = "badge-mostly-true"; cardBorderColor = "rgba(132, 204, 22, 0.4)"; }
        else if (c.verdict === "MISLEADING") { badgeClass = "badge-misleading"; cardBorderColor = "rgba(245, 158, 11, 0.4)"; }
        else if (c.verdict === "MOSTLY FALSE") { badgeClass = "badge-mostly-false"; cardBorderColor = "rgba(249, 115, 22, 0.4)"; }
        else if (c.verdict === "FALSE") { badgeClass = "badge-false"; cardBorderColor = "rgba(239, 68, 68, 0.4)"; }

        const suppHtml = c.supporting_evidence.length > 0 ? c.supporting_evidence.map(e => `
            <div style="background:rgba(16, 185, 129, 0.05);border:1px solid rgba(16, 185, 129, 0.2);border-radius:0.5rem;padding:0.75rem;margin-bottom:0.5rem;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.25rem;">
                    <span style="font-weight:700;font-size:0.82rem;color:#34d399;">${escapeHtml(e.source_name)}</span>
                    <span class="badge badge-true" style="font-size:0.65rem;">Credibility: ${e.credibility_score}/100</span>
                </div>
                <div style="font-size:0.8rem;color:#cbd5e1;margin-bottom:0.35rem;">${escapeHtml(e.explanation)}</div>
                <a href="${e.link}" target="_blank" rel="noopener noreferrer" style="font-size:0.75rem;color:#ff4d6d;text-decoration:none;display:inline-flex;align-items:center;gap:0.25rem;">
                    View Source Article ↗
                </a>
            </div>
        `).join("") : `<div style="font-size:0.8rem;color:#64748b;font-style:italic;">No direct supporting sources found.</div>`;

        const contraHtml = c.contradicting_evidence.length > 0 ? c.contradicting_evidence.map(e => `
            <div style="background:rgba(239, 68, 68, 0.05);border:1px solid rgba(239, 68, 68, 0.2);border-radius:0.5rem;padding:0.75rem;margin-bottom:0.5rem;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.25rem;">
                    <span style="font-weight:700;font-size:0.82rem;color:#f87171;">${escapeHtml(e.source_name)}</span>
                    <span class="badge badge-false" style="font-size:0.65rem;">Credibility: ${e.credibility_score}/100</span>
                </div>
                <div style="font-size:0.8rem;color:#cbd5e1;margin-bottom:0.35rem;">${escapeHtml(e.explanation)}</div>
                <a href="${e.link}" target="_blank" rel="noopener noreferrer" style="font-size:0.75rem;color:#ff4d6d;text-decoration:none;display:inline-flex;align-items:center;gap:0.25rem;">
                    View Debunking Source ↗
                </a>
            </div>
        `).join("") : `<div style="font-size:0.8rem;color:#64748b;font-style:italic;">No contradicting sources recorded.</div>`;

        return `
            <div class="glass-card" style="padding:1.5rem;margin-bottom:1.25rem;border-left:4px solid ${cardBorderColor};">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;margin-bottom:0.75rem;">
                    <div>
                        <span style="font-size:0.75rem;font-weight:700;color:#fca5a5;text-transform:uppercase;letter-spacing:0.05em;">Claim ${idx + 1}</span>
                        <h4 style="font-size:1.05rem;font-weight:700;color:#f1f5f9;margin-top:0.2rem;">"${escapeHtml(c.claim)}"</h4>
                    </div>
                    <div style="text-align:right;flex-shrink:0;">
                        <span class="badge ${badgeClass}" style="font-size:0.8rem;">${c.verdict}</span>
                        <div style="font-size:0.72rem;color:#94a3b8;margin-top:0.25rem;">Confidence: ${c.confidence}%</div>
                    </div>
                </div>

                <div style="background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.2);border-radius:0.5rem;padding:0.85rem;margin-bottom:1.25rem;">
                    <div style="font-size:0.75rem;font-weight:700;color:#ff4d6d;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.25rem;">Why:</div>
                    <div style="font-size:0.88rem;color:#e2e8f0;line-height:1.5;">${escapeHtml(c.why)}</div>
                </div>

                <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:1rem;">
                    <div>
                        <div style="font-size:0.78rem;font-weight:700;color:#34d399;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.5rem;display:flex;align-items:center;gap:0.3rem;">
                            <span>✓</span> Supporting Evidence
                        </div>
                        ${suppHtml}
                    </div>
                    <div>
                        <div style="font-size:0.78rem;font-weight:700;color:#f87171;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.5rem;display:flex;align-items:center;gap:0.3rem;">
                            <span>✕</span> Contradicting Evidence
                        </div>
                        ${contraHtml}
                    </div>
                </div>
            </div>
        `;
    }).join("");
}

function renderRelatedNews(sources) {
    const container = document.getElementById("related-news-container");
    if (!container) return;

    if (!sources || sources.length === 0) {
        container.innerHTML = `
            <div style="color:#64748b;font-size:0.85rem;font-style:italic;">
                No separate related articles discovered in search index.
            </div>
        `;
        return;
    }

    container.innerHTML = sources.map(s => `
        <div class="glass-card" style="padding:1rem;border-radius:0.75rem;display:flex;flex-direction:column;justify-content:space-between;border-color:rgba(239,68,68,0.2);">
            <div>
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
                    <span style="font-size:0.78rem;font-weight:700;color:#ff4d6d;">${escapeHtml(s.website)}</span>
                    <span class="badge badge-red" style="font-size:0.65rem;">Trust: ${s.source_credibility}/100</span>
                </div>
                <h5 style="font-size:0.92rem;font-weight:700;color:#f1f5f9;margin-bottom:0.4rem;line-height:1.4;">
                    ${escapeHtml(s.title)}
                </h5>
                <p style="font-size:0.8rem;color:#94a3b8;line-height:1.5;margin-bottom:0.75rem;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;">
                    ${escapeHtml(s.description)}
                </p>
            </div>
            <a href="${s.link}" target="_blank" rel="noopener noreferrer" style="font-size:0.78rem;color:#ff4d6d;text-decoration:none;font-weight:700;display:inline-flex;align-items:center;gap:0.25rem;">
                Read full article ↗
            </a>
        </div>
    `).join("");
}

// 7. Gauge Controller
function updateGauge(score, color) {
    const circle = document.getElementById("gauge-circle");
    const scoreText = document.getElementById("gauge-score-value");
    if (!circle || !scoreText) return;

    const radius = 54;
    const circumference = 2 * Math.PI * radius;
    circle.style.strokeDasharray = `${circumference} ${circumference}`;

    const offset = circumference - (score / 100) * circumference;
    circle.style.strokeDashoffset = offset;
    circle.style.stroke = color;
    scoreText.textContent = score;
    scoreText.style.color = color;
}

// 8. Progress and UI Utilities
function showLoading(show) {
    const overlay = document.getElementById("loading-overlay");
    if (overlay) overlay.style.display = show ? "flex" : "none";
}

function updateScanProgress(text, pct) {
    const statusText = document.getElementById("scan-status-text");
    const progressBar = document.getElementById("scan-progress-bar");
    if (statusText) statusText.textContent = text;
    if (progressBar) progressBar.style.width = `${pct}%`;
}

function resetDashboard() {
    const results = document.getElementById("results-section");
    if (results) results.style.display = "none";
}

// 9. Modals & Drawers
function toggleHistoryDrawer(open) {
    const drawer = document.getElementById("history-drawer");
    const backdrop = document.getElementById("drawer-backdrop");
    if (drawer && backdrop) {
        if (open) {
            drawer.classList.add("open");
            backdrop.classList.add("open");
            loadHistory();
        } else {
            drawer.classList.remove("open");
            backdrop.classList.remove("open");
        }
    }
}

function toggleSettingsModal(open) {
    const modal = document.getElementById("settings-modal");
    if (modal) {
        if (open) modal.classList.add("open");
        else modal.classList.remove("open");
    }
}

function toggleMethodologyModal(open) {
    const modal = document.getElementById("methodology-modal");
    if (modal) {
        if (open) modal.classList.add("open");
        else modal.classList.remove("open");
    }
}
