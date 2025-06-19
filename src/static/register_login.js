document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".login-signup").forEach(section => {
        const btn = section.querySelector(".submit-btn");
        if (btn) {
            if (section.id === "login") {
                btn.addEventListener("click", handleLogin);
            } else if (section.id === "signup") {
                btn.addEventListener("click", handleSignup);
            }
        }
    });
});

async function handleLogin(event) {
    event.preventDefault();

    const email = document.querySelector('.l-attop input[name="email"]').value;
    const password = document.querySelector('.l-attop input[name="password"]').value;

    try {
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
    } catch (error) {
        console.error("Error during login:", error);
        alert("Login error: " + error.message);
    }
}

async function handleSignup(event) {
    event.preventDefault();

    const form = event.target.closest(".login-signup");

    const username = form.querySelector('input[name="username"]').value;
    const email = form.querySelector('input[name="email"]').value;
    const password = form.querySelector('input[name="password"]').value;

    try {
        const response = await fetch("/auth/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, password })
        });

        const data = await response.json();
        if (response.ok) {
            alert("Signup successful, please login.");
        } else {
            alert("Signup failed: " + (data.detail?.[0]?.msg || "Error"));
        }
    } catch (error) {
        alert("Signup error: " + error.message);
        console.error("Signup error:", error);
    }
}

$(document).ready(function() {

    $('#signup').on("click", function() {
        $(this).removeClass("s-atbottom").addClass("s-attop");
        $("#login").removeClass("l-attop").addClass("l-atbottom");
    });

    $('#login').on("click", function() {
        $(this).removeClass("l-atbottom").addClass("l-attop");
        $("#signup").removeClass("s-attop").addClass("s-atbottom");
    });
});