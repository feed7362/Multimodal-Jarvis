document.getElementById("login-form").addEventListener("submit", async function(event) {
    event.preventDefault();
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    const response = await fetch("/auth/jwt/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({
            "username": email,
            "password": password
        })
    });

    if (response.status !== 204) {
        const errorText = await response.text();
        console.error("Login failed:", errorText);
        alert("Login failed: " + errorText);
        return;
    }
    alert("Login successful");
    window.location.href = "/";
});


// Signup
document.getElementById("signup-form").addEventListener("submit", async function(event) {
    event.preventDefault();
    const username = document.getElementById("signup-username").value;
    const email = document.getElementById("signup-email").value;
    const password = document.getElementById("signup-password").value;

    const response = await fetch("/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            "username": username,
            "email": email,
            "password": password
        })
    });

    const data = await response.json();
    console.log(data);

    if (response.ok) {
        alert("Signup successful, please login.");
    } else {
        alert("Signup failed: " + (data.detail || "Error"));
    }
});