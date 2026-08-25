/**
 * AURA LOAN // Clean & Minimal Client-Side Engine
 */

// Global Chart Instances
let probDoughnutChartInstance = null;
let benchmarkBarChartInstance = null;

// Presets Data
const PRESETS = {
    prime: {
        annual_income: 95000,
        loan_amount: 18000,
        credit_score: 780,
        debt_to_income_ratio: 0.18,
        years_employed: 8.0,
        delinquencies_last_2yrs: 0
    },
    subprime: {
        annual_income: 32000,
        loan_amount: 28000,
        credit_score: 520,
        debt_to_income_ratio: 0.58,
        years_employed: 1.0,
        delinquencies_last_2yrs: 3
    },
    borderline: {
        annual_income: 60000,
        loan_amount: 22000,
        credit_score: 630,
        debt_to_income_ratio: 0.38,
        years_employed: 3.0,
        delinquencies_last_2yrs: 1
    },
    high_leverage: {
        annual_income: 175000,
        loan_amount: 95000,
        credit_score: 710,
        debt_to_income_ratio: 0.42,
        years_employed: 6.0,
        delinquencies_last_2yrs: 0
    }
};

// Document Ready Initialization
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initValidationListeners();
    initFormSubmission();
    loadTelemetryData();

    // Check URL Hash for deep linking on first load
    const initialHash = window.location.hash.replace('#', '');
    const initialPage = (initialHash && document.getElementById(initialHash)) ? initialHash : 'page-home';
    switchPage(initialPage, /* pushState= */ false);

    // Handle browser back/forward buttons
    window.addEventListener('popstate', (event) => {
        const pageId = (event.state && event.state.pageId) ? event.state.pageId : 'page-home';
        switchPage(pageId, /* pushState= */ false);
    });
});

/* ==========================================================================
   SPA NAVIGATION
   ========================================================================== */

function initNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn, .nav-link-btn');
    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetPageId = btn.getAttribute('data-target');
            switchPage(targetPageId);
        });
    });

    const refreshBtn = document.getElementById('btnRefreshTelemetry');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            loadTelemetryData(true);
        });
    }

    // Mobile Hamburger Menu Setup
    const hamburger = document.getElementById('navHamburger');
    const navLinks = document.querySelector('.nav-links');
    const navOverlay = document.getElementById('navOverlay');

    function toggleMobileMenu() {
        if (!hamburger || !navLinks || !navOverlay) return;
        hamburger.classList.toggle('open');
        navLinks.classList.toggle('mobile-open');
        navOverlay.classList.toggle('visible');
        // Prevent body scroll when menu is open
        document.body.style.overflow = hamburger.classList.contains('open') ? 'hidden' : '';
    }

    if (hamburger) hamburger.addEventListener('click', toggleMobileMenu);
    if (navOverlay) navOverlay.addEventListener('click', toggleMobileMenu);
}

function switchPage(pageId, pushState = true) {
    // Hide all pages
    const pages = document.querySelectorAll('.page-section, .app-page');
    pages.forEach(p => p.classList.remove('active', 'active-page'));

    // Deactivate nav links
    const navButtons = document.querySelectorAll('.nav-btn, .nav-link-btn');
    navButtons.forEach(btn => btn.classList.remove('active', 'active-page'));

    // Close mobile menu if it's open
    const hamburger = document.getElementById('navHamburger');
    if (hamburger && hamburger.classList.contains('open')) {
        const navLinks = document.querySelector('.nav-links');
        const navOverlay = document.getElementById('navOverlay');
        hamburger.classList.remove('open');
        if (navLinks) navLinks.classList.remove('mobile-open');
        if (navOverlay) navOverlay.classList.remove('visible');
        document.body.style.overflow = '';
    }

    // Show target page
    const targetPage = document.getElementById(pageId);
    if (targetPage) {
        targetPage.classList.add('active');

        // Push to browser history so Back/Forward buttons work
        if (pushState) {
            history.pushState({ pageId }, '', '#' + pageId);
        } else {
            // Replace state without adding a new history entry (for initial load / popstate)
            history.replaceState({ pageId }, '', '#' + pageId);
        }

        // Update corresponding nav button
        const activeNavBtn = document.querySelector(`[data-target="${pageId}"]`);
        if (activeNavBtn) {
            activeNavBtn.classList.add('active');
        }

        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

/* ==========================================================================
   PAGE 2: LIVE REST TELEMETRY (GET APIs)
   ========================================================================== */

async function loadTelemetryData(showToast = false) {
    try {
        // Feature Dictionary fetch with progress bar
        const progressContainer = document.getElementById('featureProgressContainer');
        const progressBar = document.getElementById('featureProgressBar');
        const errorMsg = document.getElementById('featureErrorMsg');
        // Show progress bar
        if (progressContainer) progressContainer.style.display = 'block';
        if (progressBar) progressBar.style.width = '0%';
        // Simple simulated progress (increase to 70% before fetch resolves)
        let prog = 0;
        const progInterval = setInterval(() => {
            if (prog < 70) {
                prog += 5;
                if (progressBar) progressBar.style.width = prog + '%';
            }
        }, 200);
        // Fetch the feature metadata with timeout
        const fetchWithTimeout = (url, options, timeout = 5000) => {
            return Promise.race([
                fetch(url, options),
                new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), timeout))
            ]);
        };
        const featRes = await fetchWithTimeout('/api/features');
        clearInterval(progInterval);
        if (progressBar) progressBar.style.width = '100%';
        // Hide progress after short delay
        setTimeout(() => { if (progressContainer) progressContainer.style.display = 'none'; }, 500);
        if (!featRes.ok) throw new Error('Feature schema fetch failed');
        const featuresData = await featRes.json();
        // Render Feature Dictionary
        renderFeatureDictionary(featuresData.metadata);

        if (showToast) {
            triggerToast('Telemetry data updated from server.', 'success');
        }

    } catch (err) {
        console.error("Telemetry fetch error:", err);
        if (showToast) {
            triggerToast('Unable to fetch live telemetry.', 'error');
        }
    }
}

function renderFeatureDictionary(metaDict) {
    const container = document.getElementById('featureDictionaryContainer');
    if (!container || !metaDict) return;

    container.innerHTML = '';

    Object.keys(metaDict).forEach(featKey => {
        const item = metaDict[featKey];
        const card = document.createElement('div');
        card.className = 'dict-card card';
        card.innerHTML = `
            <div class="dict-top">
                <span class="dict-title">${item.label}</span>
                <span class="dict-badge">${item.type}</span>
            </div>
            <p class="dict-desc">${item.description}</p>
            <div class="dict-meta">
                <span>Range: [${item.min} &rarr; ${item.max}]</span>
                <span>Unit: ${item.unit}</span>
            </div>
        `;
        container.appendChild(card);
    });
}

/* ==========================================================================
   PAGE 3: VALIDATION
   ========================================================================== */

const VALIDATION_RULES = {
    annual_income: {
        validate: val => val >= 5000 && val <= 10000000,
        errMsg: "Annual income must be between $5,000 and $10,000,000."
    },
    loan_amount: {
        validate: val => val >= 500 && val <= 2000000,
        errMsg: "Loan amount must be between $500 and $2,000,000."
    },
    credit_score: {
        validate: val => Number.isInteger(val) && val >= 300 && val <= 850,
        errMsg: "Credit score must be an integer between 300 and 850."
    },
    debt_to_income_ratio: {
        validate: val => val >= 0.0 && val <= 1.0,
        errMsg: "Debt-to-income ratio must be between 0.0 and 1.0 (0% to 100%)."
    },
    years_employed: {
        validate: val => val >= 0.0 && val <= 50.0,
        errMsg: "Years employed must be between 0.0 and 50.0 years."
    },
    delinquencies_last_2yrs: {
        validate: val => Number.isInteger(val) && val >= 0 && val <= 30,
        errMsg: "Delinquencies count must be an integer between 0 and 30."
    }
};

function initValidationListeners() {
    Object.keys(VALIDATION_RULES).forEach(fieldId => {
        const input = document.getElementById(fieldId);
        if (!input) return;

        input.addEventListener('input', () => validateField(fieldId));
        input.addEventListener('blur', () => validateField(fieldId));
    });
}

function validateField(fieldId) {
    const input = document.getElementById(fieldId);
    const group = document.getElementById(`group-${fieldId}`);
    const errSpan = document.getElementById(`err-${fieldId}`);
    if (!input || !group) return false;

    let rawVal = input.value.trim();

    if (rawVal === '') {
        group.classList.remove('valid', 'invalid');
        return false;
    }

    let parsedVal = parseFloat(rawVal);

    if (fieldId === 'debt_to_income_ratio' && parsedVal > 1.0 && parsedVal <= 100.0) {
        parsedVal = parsedVal / 100.0;
    }

    if (fieldId === 'credit_score' || fieldId === 'delinquencies_last_2yrs') {
        parsedVal = Number(rawVal);
    }

    const rule = VALIDATION_RULES[fieldId];
    const isValid = !isNaN(parsedVal) && rule.validate(parsedVal);

    if (isValid) {
        group.classList.remove('invalid');
        group.classList.add('valid');
        return true;
    } else {
        group.classList.remove('valid');
        group.classList.add('invalid');
        if (errSpan) errSpan.textContent = rule.errMsg;
        return false;
    }
}

function validateAllFields() {
    let allValid = true;
    let firstInvalidInput = null;

    Object.keys(VALIDATION_RULES).forEach(fieldId => {
        const isValid = validateField(fieldId);
        if (!isValid) {
            allValid = false;
            if (!firstInvalidInput) {
                firstInvalidInput = document.getElementById(fieldId);
            }
        }
    });

    if (firstInvalidInput) {
        firstInvalidInput.focus();
    }

    return allValid;
}

/* ==========================================================================
   PRESET PROFILES & FORM ACTIONS
   ========================================================================== */

function loadPreset(presetKey) {
    switchPage('page-evaluation');

    const data = PRESETS[presetKey];
    if (!data) return;

    Object.keys(data).forEach(fieldId => {
        const input = document.getElementById(fieldId);
        if (input) {
            input.value = data[fieldId];
            validateField(fieldId);
        }
    });

    triggerToast(`Loaded "${presetKey.toUpperCase()}" sample profile.`, 'info');
}

function clearForm() {
    const form = document.getElementById('loanForm');
    if (form) form.reset();

    Object.keys(VALIDATION_RULES).forEach(fieldId => {
        const group = document.getElementById(`group-${fieldId}`);
        if (group) group.classList.remove('valid', 'invalid');
    });

    document.getElementById('resultsEmptyState').style.display = 'flex';
    document.getElementById('resultsActiveState').style.display = 'none';
}

/* ==========================================================================
   PAGE 3: FORM SUBMISSION & INFERENCE (/api/predict)
   ========================================================================== */

function initFormSubmission() {
    const form = document.getElementById('loanForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (!validateAllFields()) {
            triggerToast('Please correct highlighted fields before submitting.', 'error');
            return;
        }

        let dti = parseFloat(document.getElementById('debt_to_income_ratio').value);
        if (dti > 1.0 && dti <= 100.0) dti = dti / 100.0;

        const payload = {
            annual_income: parseFloat(document.getElementById('annual_income').value),
            loan_amount: parseFloat(document.getElementById('loan_amount').value),
            credit_score: parseInt(document.getElementById('credit_score').value, 10),
            debt_to_income_ratio: dti,
            years_employed: parseFloat(document.getElementById('years_employed').value),
            delinquencies_last_2yrs: parseInt(document.getElementById('delinquencies_last_2yrs').value, 10)
        };

        const submitBtn = document.getElementById('btnSubmitPredict');
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;

        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                const errMsg = result.validation_errors ? result.validation_errors.join(' ') : (result.error || 'Prediction failed');
                triggerToast(errMsg, 'error');
                return;
            }

            renderPredictionResults(result);
            triggerToast(`Decision: ${result.prediction} (${result.approval_percentage})`, result.is_approved ? 'success' : 'error');

        } catch (err) {
            console.error('Inference error:', err);
            triggerToast('Network error: Unable to connect to server.', 'error');
        } finally {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
        }
    });
}

/* ==========================================================================
   RESULTS & CHART.JS VISUALIZATIONS
   ========================================================================== */

function renderPredictionResults(res) {
    document.getElementById('resultsEmptyState').style.display = 'none';
    const activeState = document.getElementById('resultsActiveState');
    activeState.style.display = 'flex';

    const banner = document.getElementById('decisionBanner');
    const decisionText = document.getElementById('decisionText');
    const decisionIcon = document.getElementById('decisionIcon');
    const decisionTierPill = document.getElementById('decisionTierPill');

    banner.className = `card verdict-card ${res.is_approved ? 'approved' : 'rejected'}`;
    decisionText.textContent = res.prediction;
    decisionTierPill.textContent = res.risk_tier;

    if (res.is_approved) {
        decisionIcon.className = 'fa-solid fa-check';
    } else {
        decisionIcon.className = 'fa-solid fa-xmark';
    }

    document.getElementById('resApprovalProb').textContent = res.approval_percentage;
    document.getElementById('resRejectionProb').textContent = res.rejection_percentage;
    document.getElementById('resMarginVal').textContent = (res.decision_margin >= 0 ? '+' : '') + res.decision_margin;

    document.getElementById('legendApproveVal').textContent = res.approval_percentage;
    document.getElementById('legendRejectVal').textContent = res.rejection_percentage;

    renderProbabilityDoughnut(res.approval_probability, res.rejection_probability);
    renderBenchmarkRadarOrBar(res.inputs, res.benchmarks);
    renderRiskChecklist(res.benchmarks, res.inputs);
}

function renderProbabilityDoughnut(pApprove, pReject) {
    const canvas = document.getElementById('probDoughnutChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    if (probDoughnutChartInstance) {
        probDoughnutChartInstance.destroy();
    }

    probDoughnutChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Approval Probability', 'Default Risk'],
            datasets: [{
                data: [pApprove * 100, pReject * 100],
                backgroundColor: ['#059669', '#dc2626'],
                borderColor: ['#ffffff', '#ffffff'],
                borderWidth: 2,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#0f172a',
                    titleColor: '#ffffff',
                    bodyColor: '#e2e8f0',
                    padding: 8,
                    callbacks: {
                        label: (ctx) => ` ${ctx.label}: ${ctx.parsed.toFixed(1)}%`
                    }
                }
            },
            animation: {
                animateScale: true,
                duration: 600
            }
        }
    });
}

function renderBenchmarkRadarOrBar(inputs, benchmarks) {
    const canvas = document.getElementById('benchmarkBarChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    if (benchmarkBarChartInstance) {
        benchmarkBarChartInstance.destroy();
    }

    const creditScoreNorm = Math.min(130, Math.round((inputs.credit_score / 670) * 100));
    const dtiSafetyScore = Math.min(130, Math.round((0.36 / Math.max(0.05, inputs.debt_to_income_ratio)) * 100));
    const incomeToLoanRatio = inputs.annual_income / Math.max(1, inputs.loan_amount);
    const leverageNorm = Math.min(130, Math.round((incomeToLoanRatio / 2.5) * 100));
    const delinquencySafety = inputs.delinquencies_last_2yrs === 0 ? 100 : Math.max(10, 100 - (inputs.delinquencies_last_2yrs * 30));

    benchmarkBarChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Credit Score', 'DTI Safety', 'Income Leverage', 'Payment History'],
            datasets: [
                {
                    label: 'Applicant Score (%)',
                    data: [creditScoreNorm, dtiSafetyScore, leverageNorm, delinquencySafety],
                    backgroundColor: [
                        creditScoreNorm >= 100 ? '#059669' : '#dc2626',
                        dtiSafetyScore >= 100 ? '#059669' : '#ea580c',
                        leverageNorm >= 100 ? '#0891b2' : '#dc2626',
                        delinquencySafety >= 100 ? '#059669' : '#dc2626'
                    ],
                    borderRadius: 4
                },
                {
                    label: 'Safe Baseline (100%)',
                    data: [100, 100, 100, 100],
                    type: 'line',
                    borderColor: '#ea580c',
                    borderWidth: 1.5,
                    borderDash: [4, 4],
                    pointRadius: 2,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: '#64748b', font: { family: 'Inter', size: 10, weight: '500' } }
                },
                y: {
                    min: 0,
                    max: 130,
                    grid: { color: '#f1f5f9' },
                    ticks: {
                        color: '#64748b',
                        callback: val => `${val}%`
                    }
                }
            },
            plugins: {
                legend: {
                    labels: { color: '#334155', font: { family: 'Inter', size: 10 } }
                },
                tooltip: {
                    backgroundColor: '#0f172a'
                }
            }
        }
    });
}

function renderRiskChecklist(benchmarks, inputs) {
    const container = document.getElementById('riskChecklistContainer');
    if (!container || !benchmarks) return;

    container.innerHTML = '';

    const checks = [
        {
            title: 'Credit Score',
            value: `${inputs.credit_score} pts`,
            passed: inputs.credit_score >= 670,
            statusText: inputs.credit_score >= 740 ? 'Excellent' : (inputs.credit_score >= 670 ? 'Good' : 'Subprime')
        },
        {
            title: 'Debt-to-Income',
            value: `${(inputs.debt_to_income_ratio * 100).toFixed(1)}%`,
            passed: inputs.debt_to_income_ratio <= 0.36,
            statusText: inputs.debt_to_income_ratio <= 0.36 ? 'Healthy' : 'Elevated'
        },
        {
            title: 'Loan-to-Income',
            value: `${(inputs.loan_amount / inputs.annual_income).toFixed(2)}x`,
            passed: (inputs.loan_amount / inputs.annual_income) <= 0.40,
            statusText: (inputs.loan_amount / inputs.annual_income) <= 0.40 ? 'Low Risk' : 'High Leverage'
        },
        {
            title: '2-Yr Delinquencies',
            value: `${inputs.delinquencies_last_2yrs} count`,
            passed: inputs.delinquencies_last_2yrs === 0,
            statusText: inputs.delinquencies_last_2yrs === 0 ? 'Clean' : 'Adverse'
        }
    ];

    checks.forEach(item => {
        const div = document.createElement('div');
        div.className = 'risk-check-item';
        div.innerHTML = `
            <div class="check-left">
                <i class="fa-solid ${item.passed ? 'fa-check text-green' : 'fa-xmark text-red'}"></i>
                <span>${item.title} <small>(${item.value})</small></span>
            </div>
            <span class="${item.passed ? 'tag-pass' : 'tag-fail'}">${item.statusText}</span>
        `;
        container.appendChild(div);
    });
}

/* ==========================================================================
   PAGE 4: SDK & CODE TAB SWITCHER
   ========================================================================== */

function switchCodeTab(lang) {
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => btn.classList.remove('active'));

    const codeBoxes = document.querySelectorAll('.snippet-box');
    codeBoxes.forEach(box => box.classList.remove('active'));

    const activeTab = event.target;
    if (activeTab) activeTab.classList.add('active');

    const targetBox = document.getElementById(`snippet-${lang}`);
    if (targetBox) targetBox.classList.add('active');
}

/* ==========================================================================
   TOAST NOTIFICATION UTILITY
   ========================================================================== */

function triggerToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    let icon = 'fa-info-circle text-turquoise';
    if (type === 'success') icon = 'fa-check text-green';
    if (type === 'error') icon = 'fa-triangle-exclamation text-red';

    toast.innerHTML = `
        <i class="fa-solid ${icon}"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 250);
    }, 3500);
}

/* ==========================================================================
   BULK UPLOAD LOGIC
   ========================================================================== */

function setEvalMode(mode) {
    const btnSingle = document.getElementById('btnModeSingle');
    const btnBulk = document.getElementById('btnModeBulk');
    const singleLayout = document.getElementById('singleLayout');
    const singlePresetBar = document.getElementById('singlePresetBar');
    const bulkLayout = document.getElementById('bulkLayout');

    if (mode === 'single') {
        btnSingle.classList.replace('btn-outline', 'btn-primary');
        btnBulk.classList.replace('btn-primary', 'btn-outline');
        singleLayout.style.display = 'grid';
        if (singlePresetBar) singlePresetBar.style.display = 'flex';
        bulkLayout.style.display = 'none';
    } else {
        btnBulk.classList.replace('btn-outline', 'btn-primary');
        btnSingle.classList.replace('btn-primary', 'btn-outline');
        singleLayout.style.display = 'none';
        if (singlePresetBar) singlePresetBar.style.display = 'none';
        bulkLayout.style.display = 'flex';
    }
}

async function handleBulkUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const loading = document.getElementById('bulkLoading');
    const errorPanel = document.getElementById('bulkErrorPanel');
    const errorList = document.getElementById('bulkErrorList');
    const resultsPanel = document.getElementById('bulkResultsPanel');
    const resultsTable = document.getElementById('bulkResultsTableBody');
    const validCount = document.getElementById('bulkValidCount');

    // Reset UI
    errorPanel.style.display = 'none';
    resultsPanel.style.display = 'none';
    errorList.innerHTML = '';
    resultsTable.innerHTML = '';

    loading.style.display = 'block';
    const progressBar = document.getElementById('bulkProgressBar');
    const progressText = document.getElementById('bulkProgressText');
    const progressDetail = document.getElementById('bulkProgressDetail');
    
    progressBar.style.width = '0%';
    progressText.innerText = '0%';
    progressDetail.innerText = 'Uploading file to server...';

    let progress = 0;
    const progressInterval = setInterval(() => {
        if (progress < 30) {
            progress += Math.floor(Math.random() * 8) + 4;
            progressDetail.innerText = 'Parsing data and validating rows...';
        } else if (progress < 60) {
            progress += Math.floor(Math.random() * 5) + 2;
            progressDetail.innerText = 'Running SVC Model Inference...';
        } else if (progress < 85) {
            progress += Math.floor(Math.random() * 3) + 1;
            progressDetail.innerText = 'Calculating probability scores...';
        } else if (progress < 95) {
            progress += 1;
            progressDetail.innerText = 'Finalizing risk tiers...';
        }
        
        if (progress > 95) progress = 95;
        
        progressBar.style.width = progress + '%';
        progressText.innerText = progress + '%';
    }, 500);

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/predict-bulk', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        progressText.innerText = '100%';
        progressDetail.innerText = 'Processing Complete!';
        
        await new Promise(r => setTimeout(r, 600)); // Let the 100% animation finish
        loading.style.display = 'none';

        if (!data.success) {
            triggerToast(data.error || "Failed to process file", "error");
            return;
        }
        // Handle Errors
        if (data.errors && data.errors.length > 0) {
            errorPanel.style.display = 'block';
            data.errors.forEach(err => {
                const li = document.createElement('li');
                li.innerHTML = `<strong>Row ${err.row}:</strong> ${err.messages.join(', ')}`;
                errorList.appendChild(li);
            });
            triggerToast(`Found errors in ${data.error_count} row(s)`, "error");
        }

        // Handle Results
        if (data.results && data.results.length > 0) {
            // Store results globally so Visual Analytics page can render charts
            window.__bulkResults = data.results;

            resultsPanel.style.display = 'block';
            validCount.innerText = data.valid_count;

            data.results.forEach(res => {
                const tr = document.createElement('tr');
                tr.style.borderBottom = '1px solid #e2e8f0';
                
                let verdictColor = res.is_approved ? '#059669' : '#dc2626';
                let verdictBg = res.is_approved ? '#ecfdf5' : '#fef2f2';
                
                tr.innerHTML = `
                    <td style="padding: 10px; font-family: monospace;">#${res.row}</td>
                    <td style="padding: 10px; font-family: monospace;">$${Number(res.inputs.annual_income).toLocaleString()}</td>
                    <td style="padding: 10px; font-family: monospace;">$${Number(res.inputs.loan_amount).toLocaleString()}</td>
                    <td style="padding: 10px; font-family: monospace;">${res.inputs.credit_score}</td>
                    <td style="padding: 10px;"><span style="background: ${verdictBg}; color: ${verdictColor}; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8rem;">${res.prediction}</span></td>
                    <td style="padding: 10px; font-weight: 600; font-family: monospace;">${res.approval_percentage}</td>
                    <td style="padding: 10px; font-size: 0.82rem; color: #64748b;">${res.risk_tier}</td>
                `;
                resultsTable.appendChild(tr);
            });
            triggerToast(`Successfully processed ${data.valid_count} rows`, "success");
        }

    } catch (err) {
        clearInterval(progressInterval);
        loading.style.display = 'none';
        triggerToast("A network error occurred while uploading.", "error");
        console.error(err);
    }
    
    // Clear input so same file can be uploaded again if needed
    event.target.value = '';
}

/* ==========================================================================
   VISUAL ANALYTICS — Page 4
   Reads from the last bulk upload result stored in window.__bulkResults.
   Called by "View Data Analytics" button and by switchPage when navigating
   to page-visual-analytics.
   ========================================================================== */

// Persistent chart instances for Visual Analytics page
let vaScatterInstance  = null;
let vaBarInstance      = null;
let vaHistogramInstance = null;

/**
 * Main entry-point.  Uses the data already in window.__bulkResults
 * (populated by handleBulkUpload).  If no data is present shows the
 * empty state panel.
 */
function loadVisualAnalytics() {
    const emptyState    = document.getElementById('vaEmptyState');
    const dashboard     = document.getElementById('vaChartsDashboard');

    const results = window.__bulkResults;

    if (!results || results.length === 0) {
        if (emptyState) emptyState.style.display = 'flex';
        if (dashboard)  dashboard.style.display  = 'none';
        return;
    }

    if (emptyState) emptyState.style.display = 'none';
    if (dashboard)  dashboard.style.display  = 'block';

    renderVAKpis(results);
    renderVAScatterChart(results);
    renderVABarChart(results);
    renderVAHistogram(results);
}

/* -------------------------------------------------------------------------- */
/* KPI Summary Strip                                                           */
/* -------------------------------------------------------------------------- */
function renderVAKpis(results) {
    const strip = document.getElementById('vaKpiStrip');
    if (!strip) return;

    const total    = results.length;
    const approved = results.filter(r => r.is_approved).length;
    const denied   = total - approved;
    const rate     = total > 0 ? ((approved / total) * 100).toFixed(1) : '0.0';

    const avgCredit = (results.reduce((s, r) => s + (r.inputs.credit_score || 0), 0) / total).toFixed(0);
    const avgDti    = (results.reduce((s, r) => s + (r.inputs.debt_to_income_ratio || 0), 0) / total * 100).toFixed(1);
    const avgLoan   = (results.reduce((s, r) => s + (r.inputs.loan_amount || 0), 0) / total).toFixed(0);

    const kpis = [
        { label: 'Total Applications', value: total,              sub: 'evaluated by SVC pipeline', color: 'var(--color-sapphire)' },
        { label: 'Approval Rate',       value: rate + '%',         sub: `${approved} approved / ${denied} denied`, color: 'var(--color-green)' },
        { label: 'Avg Credit Score',    value: avgCredit,          sub: 'FICO points mean',          color: 'var(--color-turquoise)' },
        { label: 'Avg DTI Ratio',       value: avgDti + '%',       sub: 'debt-to-income mean',       color: 'var(--color-orange)' },
        { label: 'Avg Loan Amount',     value: '$' + Number(avgLoan).toLocaleString(), sub: 'requested funds mean', color: 'var(--color-amethyst)' }
    ];

    strip.innerHTML = kpis.map(k => `
        <div class="va-kpi-card">
            <span class="va-kpi-label">${k.label}</span>
            <span class="va-kpi-value" style="color:${k.color}">${k.value}</span>
            <span class="va-kpi-sub">${k.sub}</span>
        </div>
    `).join('');
}

/* -------------------------------------------------------------------------- */
/* Scatter: DTI vs Credit Score                                                */
/* -------------------------------------------------------------------------- */
function renderVAScatterChart(results) {
    const canvas = document.getElementById('vaScatterChart');
    if (!canvas) return;

    if (vaScatterInstance) { vaScatterInstance.destroy(); vaScatterInstance = null; }

    const approvedPts = results
        .filter(r => r.is_approved)
        .map(r => ({ x: parseFloat((r.inputs.debt_to_income_ratio * 100).toFixed(2)), y: r.inputs.credit_score }));

    const deniedPts = results
        .filter(r => !r.is_approved)
        .map(r => ({ x: parseFloat((r.inputs.debt_to_income_ratio * 100).toFixed(2)), y: r.inputs.credit_score }));

    vaScatterInstance = new Chart(canvas.getContext('2d'), {
        type: 'scatter',
        data: {
            datasets: [
                {
                    label: 'Approved',
                    data: approvedPts,
                    backgroundColor: 'rgba(5,150,105,0.55)',
                    borderColor:     'rgba(5,150,105,0.9)',
                    borderWidth: 1,
                    pointRadius: 4,
                    pointHoverRadius: 6
                },
                {
                    label: 'Denied',
                    data: deniedPts,
                    backgroundColor: 'rgba(220,38,38,0.45)',
                    borderColor:     'rgba(220,38,38,0.9)',
                    borderWidth: 1,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: { display: true, text: 'Debt-to-Income Ratio (%)', color: '#64748b', font: { family: 'Inter', size: 11, weight: '600' } },
                    grid: { color: '#f1f5f9' },
                    ticks: { color: '#64748b', callback: v => v + '%' }
                },
                y: {
                    title: { display: true, text: 'Credit Score (FICO)', color: '#64748b', font: { family: 'Inter', size: 11, weight: '600' } },
                    min: 300,
                    max: 860,
                    grid: { color: '#f1f5f9' },
                    ticks: { color: '#64748b' }
                }
            },
            plugins: {
                legend: { labels: { color: '#334155', font: { family: 'Inter', size: 11 }, usePointStyle: true } },
                tooltip: {
                    backgroundColor: '#0f172a',
                    titleColor: '#ffffff',
                    bodyColor: '#e2e8f0',
                    callbacks: {
                        label: ctx => `DTI: ${ctx.parsed.x}%   FICO: ${ctx.parsed.y}`
                    }
                }
            },
            animation: { duration: 700 }
        }
    });
}

/* -------------------------------------------------------------------------- */
/* Bar: Approval Rate by Years Employed bracket                                */
/* -------------------------------------------------------------------------- */
function renderVABarChart(results) {
    const canvas = document.getElementById('vaBarChart');
    if (!canvas) return;

    if (vaBarInstance) { vaBarInstance.destroy(); vaBarInstance = null; }

    const brackets   = ['0–2 yrs', '3–5 yrs', '6–10 yrs', '11–20 yrs', '21+ yrs'];
    const totals     = [0, 0, 0, 0, 0];
    const approvals  = [0, 0, 0, 0, 0];

    results.forEach(r => {
        const ye = r.inputs.years_employed || 0;
        let idx  = 4;
        if      (ye <= 2)  idx = 0;
        else if (ye <= 5)  idx = 1;
        else if (ye <= 10) idx = 2;
        else if (ye <= 20) idx = 3;

        totals[idx]++;
        if (r.is_approved) approvals[idx]++;
    });

    const rates = totals.map((t, i) => t > 0 ? parseFloat(((approvals[i] / t) * 100).toFixed(1)) : 0);

    // Colour each bar by rate: green ≥ 60 %, orange 40–59 %, red < 40 %
    const barColors = rates.map(v =>
        v >= 60 ? 'rgba(5,150,105,0.82)'  :
        v >= 40 ? 'rgba(234,88,12,0.82)'  :
                  'rgba(220,38,38,0.82)'
    );

    vaBarInstance = new Chart(canvas.getContext('2d'), {
        type: 'bar',
        data: {
            labels: brackets,
            datasets: [{
                label: 'Approval Rate (%)',
                data: rates,
                backgroundColor: barColors,
                borderRadius: 6,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: '#64748b', font: { family: 'Inter', size: 11, weight: '500' } }
                },
                y: {
                    min: 0,
                    max: 100,
                    grid: { color: '#f1f5f9' },
                    ticks: { color: '#64748b', callback: v => v + '%' }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#0f172a',
                    titleColor: '#ffffff',
                    bodyColor: '#e2e8f0',
                    callbacks: {
                        label: ctx => ` Approval rate: ${ctx.parsed.y}%`
                    }
                }
            },
            animation: { duration: 700 }
        }
    });
}

/* -------------------------------------------------------------------------- */
/* Histogram: Loan Amount distribution — Approved vs Denied                   */
/* -------------------------------------------------------------------------- */
function renderVAHistogram(results) {
    const canvas = document.getElementById('vaHistogramChart');
    if (!canvas) return;

    if (vaHistogramInstance) { vaHistogramInstance.destroy(); vaHistogramInstance = null; }

    // Build $10 k bands up to $150 k, then "> $150k"
    const BANDS   = ['<$10k','$10–20k','$20–30k','$30–50k','$50–75k','$75–100k','$100–150k','>$150k'];
    const appBins = new Array(BANDS.length).fill(0);
    const denBins = new Array(BANDS.length).fill(0);

    function getBin(amount) {
        if (amount <  10000) return 0;
        if (amount <  20000) return 1;
        if (amount <  30000) return 2;
        if (amount <  50000) return 3;
        if (amount <  75000) return 4;
        if (amount < 100000) return 5;
        if (amount < 150000) return 6;
        return 7;
    }

    results.forEach(r => {
        const b = getBin(r.inputs.loan_amount || 0);
        if (r.is_approved) appBins[b]++; else denBins[b]++;
    });

    vaHistogramInstance = new Chart(canvas.getContext('2d'), {
        type: 'bar',
        data: {
            labels: BANDS,
            datasets: [
                {
                    label: 'Approved',
                    data: appBins,
                    backgroundColor: 'rgba(5,150,105,0.75)',
                    borderColor:     'rgba(5,150,105,1)',
                    borderWidth: 1,
                    borderRadius: 4
                },
                {
                    label: 'Denied',
                    data: denBins,
                    backgroundColor: 'rgba(220,38,38,0.65)',
                    borderColor:     'rgba(220,38,38,0.9)',
                    borderWidth: 1,
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    stacked: false,
                    grid: { display: false },
                    ticks: { color: '#64748b', font: { family: 'Inter', size: 11, weight: '500' } }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: '#f1f5f9' },
                    ticks: { color: '#64748b', precision: 0 }
                }
            },
            plugins: {
                legend: { labels: { color: '#334155', font: { family: 'Inter', size: 11 }, usePointStyle: true } },
                tooltip: {
                    backgroundColor: '#0f172a',
                    titleColor: '#ffffff',
                    bodyColor: '#e2e8f0'
                }
            },
            animation: { duration: 700 }
        }
    });
}

