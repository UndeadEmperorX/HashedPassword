// static/strength.js
function scorePassword(pw) {
  let score = 0;
  if (!pw) return score;
  if (pw.length >= 8) score += 3;
  else if (pw.length >= 6) score += 1;
  if (/[a-z]/.test(pw)) score += 1;
  if (/[A-Z]/.test(pw)) score += 1;
  if (/[0-9]/.test(pw)) score += 2;
  if (/[^A-Za-z0-9]/.test(pw)) score += 3;
  return score; // 0..10-ish
}

function checkStrength() {
  const pwEl = document.getElementById("password");
  const bar = document.getElementById("strengthBar");
  const text = document.getElementById("strengthText");
  if (!pwEl) return;
  const s = scorePassword(pwEl.value);
  const percent = Math.min(100, s * 10);
  if (bar) {
    bar.style.width = percent + "%";
    if (s <= 2) bar.className = "progress-bar bg-danger";
    else if (s <= 5) bar.className = "progress-bar bg-warning";
    else bar.className = "progress-bar bg-success";
  }
  if (text) {
    if (s <= 2) text.textContent = "Armor: Paper Armor (Very weak)";
    else if (s <= 5) text.textContent = "Armor: Leather Armor (OK)";
    else text.textContent = "Armor: Diamond Armor (Strong)";
  }
}
