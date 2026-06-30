const API_URL = "/api/predict";

const form = document.getElementById("loanForm");
const submitBtn = document.getElementById("submitBtn");
const resultBox = document.getElementById("result");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData(form);
  const data = Object.fromEntries(formData.entries());

  const numericFields = [
    "dependents", "applicant_income", "coapplicant_income",
    "loan_amount", "loan_term_months", "credit_score",
    "residential_assets_value", "commercial_assets_value", "bank_assets_value"
  ];
  numericFields.forEach(f => data[f] = parseFloat(data[f]));

  submitBtn.disabled = true;
  submitBtn.textContent = "Checking...";
  resultBox.innerHTML = "";

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    if (!res.ok) {
      const err = await res.json();
      resultBox.innerHTML = `<p class="error">⚠️ ${err.detail || "Error processing request"}</p>`;
      return;
    }

    const result = await res.json();
    resultBox.innerHTML = `
      <div class="${result.approved ? 'approved' : 'rejected'}">
        <h3>${result.approved ? "✅ Loan Approved" : "❌ Loan Rejected"}</h3>
        <p>Model Confidence: <strong>${result.confidence}%</strong></p>
        <p>Approval Probability: <strong>${result.approval_probability}%</strong></p>
        <div class="factors">
          <strong>Top factors influencing this decision:</strong>
          <ul>${result.top_factors.map(f => `<li>${f}</li>`).join("")}</ul>
        </div>
      </div>
    `;
  } catch (err) {
    resultBox.innerHTML = `<p class="error">⚠️ Could not connect to server. Is the backend running?</p>`;
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Check Eligibility";
  }
});
