document.addEventListener("DOMContentLoaded", function() {
    const loginBtn = document.querySelector(".l-attop .submit-btn");
    const signupBtn = document.querySelector(".s-atbottom .submit-btn");

    if (loginBtn) {
        loginBtn.addEventListener("click", handleLogin);
    } else {
        console.error("Login button not found");
    }

    if (signupBtn) {
        signupBtn.addEventListener("click", handleSignup);
    } else {
        console.error("Signup button not found");
    }
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

// Функция для обработки регистрации
async function handleSignup(event) {
    event.preventDefault();

    const username = document.querySelector('.s-atbottom input[name="username"]').value;
    const email = document.querySelector('.s-atbottom input[name="email"]').value;
    const password = document.querySelector('.s-atbottom input[name="password"]').value;

    try {
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
            alert("Signup failed: " + (data.detail[0].msg || "Error"));
        }
    } catch (error) {
        console.error("Error during signup:", error);
        alert("Signup error: " + error.message);
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