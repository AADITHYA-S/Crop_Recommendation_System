import { supabase } from "./supabaseClient.js";

// Detect login event via localStorage
if (localStorage.getItem("just_logged_in") === "true") {
  console.log("Detected login → loading recommendation history...");
  
  setTimeout(() => {
    loadAdviceOnLogin();
  }, 300);

  localStorage.removeItem("just_logged_in");
}


// fetch farmer + field
async function getFarmerFieldData() {
  console.log("Fetching farmer and field data...");
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) {
  console.warn("User not logged in yet — waiting for Supabase auth to load.");
  return null;
}

console.log("Current user:", user.id);


  const { data: farmer } = await supabase
    .from("farmers")
    .select("id, name, language")
    .eq("user_id", user.id)
    .single();

  const { data: field } = await supabase
    .from("fields")
    .select("id, area, soil_type, latitude, longitude")
    .eq("farmer_id", farmer.id)
    .single();

  return { farmer, field };
}

// load advice
export async function loadAdviceOnLogin() {
  console.log("Loading advice on login...");
  const token = localStorage.getItem("token");
  const userId = localStorage.getItem("user_id");

  if (!token || !userId) return;

  try {
    const res = await fetch("http://127.0.0.1:8000/user/last-recommendation", {
      headers: {
        "Authorization": `Bearer ${token}`,
        "user-id": userId
      }
    });

    const data = await res.json();
    renderAdvice(
  data.text ||
  data.recommendations ||
  data.recommendation ||
  data.last_recommendation ||
  data.advice ||
  data.output ||
  data.message ||
  null
);


  } catch (err) {
    console.error(err);
    document.getElementById("adviceBox").innerText = "Failed to load advice.";
  }
}

// render advice
export function renderAdvice(text) {
  const box = document.getElementById("adviceBox");
  if (!text) {
    box.innerHTML = "<em>No recommendations yet.</em>";
    return;
  }

  let html = text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/^\*\s?/gm, "• ")
    .replace(/\n{2,}/g, "<br><br>")
    .replace(/\n/g, "<br>");

  box.innerHTML = html;
}

// ensure load AFTER dashboard visible
window.addEventListener("user-logged-in", () => {
  setTimeout(() => loadAdviceOnLogin(), 300);
});

// auto load on refresh IF dashboard is visible
window.addEventListener("DOMContentLoaded", () => {
  if (!localStorage.getItem("token")) return;
  loadAdviceOnLogin();
});

// recommend
async function handleRecommend() {
  const cropType = document.getElementById("recCropType").value;
  const sowingDate = document.getElementById("recSowingDate").value;
  const n = document.getElementById("recNitrogen").value || null;
  const p = document.getElementById("recPhosphorus").value || null;
  const k = document.getElementById("recPotassium").value || null;

  const { field } = await getFarmerFieldData();
  const token = localStorage.getItem("token");

  const payload = {
    crop: cropType,
    sowing_date: sowingDate,
    n: n ? parseFloat(n) : null,
    p: p ? parseFloat(p) : null,
    k: k ? parseFloat(k) : null
  };

  const res = await fetch("http://127.0.0.1:8000/recommend", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  });

  const data = await res.json();
  const recDiv = document.getElementById("recResult");
  recDiv.innerHTML = `<h3>Crop Recommendation Result</h3><div style="white-space: pre-wrap;">${data.recommendations}</div>`;
  recDiv.classList.remove("hidden");
}

// suitability
async function runSuitability() {
    const crop = document.getElementById("suitCropType").value;
    const token = localStorage.getItem("token");
    // console.log("token:", token);
    const body = {
        crop: crop,
    };

    const res = await fetch(`http://127.0.0.1:8000/suitability`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(body)
    });

    const data = await res.json();
    console.log("Suitability Response:", data);
     console.log("Result div:", document.getElementById("suitResult"));
    renderSuitability(data);
}

function renderSuitability(data) {
    console.log("Rendering suitability...");
    let resBox = document.getElementById("suitResult");
    console.log("Before update:", document.getElementById("suitResult")?.outerHTML);

    // If div doesn't exist in the current DOM → create it
    if (!resBox) {
        resBox = document.createElement("div");
        resBox.id = "suitResult";
        resBox.className = "result-box";
        document.querySelector(".dashboard-card").appendChild(resBox);
    }
    console.log("After update:", document.getElementById("suitResult")?.outerHTML);


    resBox.classList.remove("hidden");
    resBox.style.display = "block";

    if (!data || !data.suitability) {
        resBox.innerHTML = "<p>Error: Invalid response from server.</p>";
        return;
    }

    const crop = document.getElementById("suitCropType").value;
    const s = data.suitability;

    resBox.innerHTML = `
        <h3>${crop.toUpperCase()} Suitability</h3>
        <p>Score: ${s.score}</p>
        <p>Status: ${s.label}</p>

       ${data.alternatives?.length > 0 ? `
  <h4>Suggested Alternative Crops</h4>
  <ul>
    ${data.alternatives.map(
      a => `<li>${a.crop} (score: ${a.score})</li>`
    ).join("")}
  </ul>
` : ""}
    `;
}

async function loadSuitabilityHistory() {
    const token = localStorage.getItem("token");

    const res = await fetch("http://127.0.0.1:8000/suitability-history/", {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    const history = await res.json();
    console.log("Suitability History:", history);

    const div = document.getElementById("suitHistory");
    div.innerHTML = history.map(item => `
        <div class="history-item">
            <h4>${item.crop.toUpperCase()} — ${item.status}</h4>
            <p>Score: ${item.score}</p>
            <p>Date: ${new Date(item.created_at).toLocaleString()}</p>
            <p><strong>Alternatives:</strong> 
                ${(item.alternatives || [])
                    .map(a => `${a.crop} (${a.score})`)
                    .join(", ")}
            </p>
        </div>
    `).join("");
}


// dashboard init
document.addEventListener("DOMContentLoaded", async () => {
  const { farmer, field } = (await getFarmerFieldData()) || {};
  if (!farmer) {
  console.error("No farmer found");
  return;
}

loadSuitabilityHistory();  
if (!field) {
  console.warn("No field found for farmer");
  // allow dashboard to load so history fetch still runs
}


  document.getElementById("userName").textContent = farmer.name;

  // field summary
  const info = document.createElement("div");
  info.classList.add("field-summary");
  info.innerHTML = `
    <p><strong>Soil Type:</strong> ${field.soil_type}</p>
    <p><strong>Area:</strong> ${field.area}</p>
    <p><strong>Coordinates:</strong> ${field.latitude}, ${field.longitude}</p>
  `;
  document.querySelector(".dashboard-container").prepend(info);

  document.getElementById("recommendBtn")?.addEventListener("click", handleRecommend);
  document.getElementById("suitabilityBtn")?.addEventListener("click", runSuitability);
});
