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

    if (!response.ok) {
        const errorText = await response.text();
        console.error("Login failed:", errorText);
        alert("Login failed: " + errorText);
        return;
    }

    // Parse the JSON response which now includes access_token and token_type
    const data = await response.json().catch(err => {
        console.error("Failed to parse JSON:", err);
        alert("Error parsing server response.");
        return null;
    });

    if (data && data.access_token) {
        // Optionally, store the token in localStorage if you need it for client-side operations
        localStorage.setItem("jwt_token", data.access_token);
        alert("Login successful");
        window.location.href = "/";  // Redirect after login
    } else {
        alert("Login failed: Token not provided");
    }
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