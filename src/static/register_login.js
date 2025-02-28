document.getElementById("login-form").addEventListener("submit", async function(event) {
    event.preventDefault();
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    const response = await fetch("/auth/jwt/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ "username": email, "password": password }) // here internal logic in FastApi need to be override
    });

    const data = await response.json().catch(err => {
        console.error("Failed to parse JSON:", err);
        alert("Error parsing server response.");
        return null;
    });


    if (!response.ok) {
        const errorText = await response.text(); // Get the raw response text
        console.error("Login failed:", errorText);
        alert("Login failed: " + errorText);
        return;
    }

    if (response.ok) {
        localStorage.setItem("jwt_token", data.access_token);
        alert("Login successful");
        window.location.href = "/templates/main_page.html";  // Redirect after login
    } else {
        alert("Login failed: " + (data.detail || "Invalid credentials"));
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