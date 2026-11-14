/**
 * TruVex AI - History & Export Management
 */

window.API_BASE = window.API_BASE || ((window.location.protocol === "file:" || (window.location.port && window.location.port !== "8000")) ? "http://127.0.0.1:8000" : "");
var API_BASE = window.API_BASE;

async function loadHistory() {
    const listContainer = document.getElementById("history-list");
    if (!listContainer) return;

    listContainer.innerHTML = `
        <div style="text-align:center;padding:2rem;color:#fca5a5;">
            <div class="cyber-scan-glow" style="display:inline-block;margin-bottom:0.5rem;font-size:1.5rem;">⏳</div>
            <div style="font-weight:600;">Loading verified history...</div>
        </div>
    `;

    try {
        const res = await fetch(`${API_BASE}/api/history`);
        if (!res.ok) throw new Error("Failed to load history");
        const items = await res.json();

        if (items.length === 0) {
            listContainer.innerHTML = `
                <div style="text-align:center;padding:3rem 1rem;color:#94a3b8;">
                    <div style="font-size:2rem;margin-bottom:0.5rem;">📂</div>
                    <div style="font-weight:700;color:#fca5a5;">No Past Analyses</div>
                    <div style="font-size:0.8rem;margin-top:0.25rem;">Analyzed articles and posts will be logged here.</div>
                </div>
            `;
            return;
        }

        listContainer.innerHTML = items.map(item => {
            let badgeClass = "badge-unverified";
            if (item.verdict.includes("TRUE")) badgeClass = "badge-true";
            else if (item.verdict.includes("FALSE")) badgeClass = "badge-false";
            else if (item.verdict.includes("MISLEADING")) badgeClass = "badge-misleading";

            const dateStr = item.analysis_timestamp ? new Date(item.analysis_timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : 'Recent';

            return `
                <div class="glass-card" style="padding:1rem;margin-bottom:0.75rem;cursor:pointer;border-left:3px solid ${getVerdictBorderColor(item.verdict)};" onclick="viewSavedAnalysis('${item.id}')">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
                        <span class="badge ${badgeClass}" style="font-size:0.65rem;">${item.verdict}</span>
                        <span style="font-size:0.75rem;color:#64748b;">${dateStr}</span>
                    </div>
                    <div style="font-weight:600;font-size:0.88rem;color:#f1f5f9;margin-bottom:0.4rem;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;">
                        ${escapeHtml(item.title || "Untitled Content")}
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;font-size:0.75rem;color:#94a3b8;">
                        <span>📱 ${escapeHtml(item.platform || "Web")}</span>
                        <span style="font-weight:700;color:${getScoreColor(item.trust_score)}">Score: ${item.trust_score}/100</span>
                    </div>
                </div>
            `;
        }).join("");

    } catch (err) {
        listContainer.innerHTML = `
            <div style="text-align:center;padding:2rem;color:#f87171;font-size:0.85rem;">
                Error loading history: ${err.message}
            </div>
        `;
    }
}

async function viewSavedAnalysis(id) {
    toggleHistoryDrawer(false);
    showLoading(true);
    try {
        const res = await fetch(`${API_BASE}/api/history/${id}`);
        if (!res.ok) throw new Error("Could not retrieve analysis details.");
        const data = await res.json();
        currentAnalysisResult = data;
        renderDashboard(data);
        window.scrollTo({ top: document.getElementById("results-section").offsetTop - 20, behavior: "smooth" });
    } catch (err) {
        alert("Failed to load analysis: " + err.message);
    } finally {
        showLoading(false);
    }
}

async function clearHistory() {
    if (!confirm("Are you sure you want to clear all analysis history?")) return;
    try {
        await fetch(`${API_BASE}/api/history`, { method: "DELETE" });
        loadHistory();
    } catch (err) {
        alert("Failed to clear history: " + err.message);
    }
}

function exportAsJson() {
    if (!currentAnalysisResult) {
        alert("No active analysis result to export.");
        return;
    }
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(currentAnalysisResult, null, 2));
    const dlAnchorElem = document.createElement('a');
    dlAnchorElem.setAttribute("href", dataStr);
    dlAnchorElem.setAttribute("download", `TruVex_Analysis_${currentAnalysisResult.id.substring(0, 8)}.json`);
    dlAnchorElem.click();
}

function copyMarkdownReport() {
    if (!currentAnalysisResult) {
        alert("No active analysis to copy.");
        return;
    }
    const r = currentAnalysisResult;
    const md = `
# TruVex AI - Verification Report
**Date:** ${r.last_checked}
**Platform:** ${r.platform} | **Domain:** ${r.domain}
**Headline / Claim:** ${r.title}

## Verdict: ${r.overall_verdict}
- **Trust Score:** ${r.trust_score}/100
- **Confidence:** ${r.confidence}%
- **Claim Accuracy:** ${r.claim_accuracy}%
- **Source Credibility:** ${r.source_credibility}/100
- **Misinformation Type:** ${r.misinformation_type}

### Analysis Summary:
${r.verdict_explanation}

### Extracted Claims & Fact-Checking:
${r.claims.map((c, i) => `
#### Claim ${i + 1}: "${c.claim}"
- **Status:** ${c.verdict} (Confidence: ${c.confidence}%)
- **Rationale:** ${c.why}
- **Supporting Sources:** ${c.supporting_evidence.map(e => `[${e.source_name}](${e.link})`).join(', ') || 'None'}
- **Contradicting Sources:** ${c.contradicting_evidence.map(e => `[${e.source_name}](${e.link})`).join(', ') || 'None'}
`).join('\n')}

*AI-generated confidence estimate based on available evidence by TruVex AI.*
`.trim();

    navigator.clipboard.writeText(md).then(() => {
        alert("Markdown report copied to clipboard!");
    }).catch(err => {
        alert("Could not copy report: " + err.message);
    });
}

function printReport() {
    window.print();
}

function getVerdictBorderColor(verdict) {
    if (!verdict) return "#64748b";
    if (verdict.includes("TRUE")) return "#10b981";
    if (verdict.includes("FALSE")) return "#ef4444";
    if (verdict.includes("MISLEADING")) return "#f59e0b";
    return "#94a3b8";
}

function getScoreColor(score) {
    if (score >= 75) return "#34d399";
    if (score >= 50) return "#fbbf24";
    return "#f87171";
}

function escapeHtml(str) {
    if (!str) return "";
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}
