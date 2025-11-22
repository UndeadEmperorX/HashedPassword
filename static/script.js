async function sendToBackend() {
  const password = document.getElementById("password").value;
  if (!password) {
    alert("Please enter a password");
    return;
  }

  try {
    const response = await fetch("/hash", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password })
    });

    const data = await response.json();

    document.getElementById("output").innerHTML = `
      <p><strong>Entered Password:</strong> ${password}</p>
      <p><strong>Generated Salt:</strong> ${data.salt}</p>
      <p><strong>Salted Hash:</strong> ${data.hash}</p>
    `;
  } catch (error) {
    document.getElementById("output").innerHTML = `<p>Error: ${error}</p>`;
  }
}

