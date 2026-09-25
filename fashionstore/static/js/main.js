/* ==========================================
   FASHION STORE JAVASCRIPT
========================================== */

"use strict";

document.addEventListener("DOMContentLoaded", () => {

    console.log("Fashion Store Loaded Successfully");

    /* ==========================================
       Sticky Navbar Shadow
    ========================================== */

    const navbar = document.querySelector(".navbar");

    function handleNavbar() {

        if (!navbar) return;

        if (window.scrollY > 60) {
            navbar.classList.add("sticky");
            navbar.classList.add("shadow");
        } else {
            navbar.classList.remove("sticky");
            navbar.classList.remove("shadow");
        }

    }

    window.addEventListener("scroll", handleNavbar);
    handleNavbar();


    /* ==========================================
       Back To Top Button
    ========================================== */

    const topBtn = document.getElementById("topBtn");

    function toggleTopButton() {
        if (!topBtn) return;
        if (window.scrollY > 300) {
            topBtn.classList.add("show");
        } else {
            topBtn.classList.remove("show");
        }
    }

    window.addEventListener("scroll", toggleTopButton);

    if (topBtn) {
        topBtn.addEventListener("click", () => {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }


    /* ==========================================
       Smooth Scroll (in-page anchors)
    ========================================== */

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener("click", function (e) {
            const targetId = this.getAttribute("href");
            if (targetId.length < 2) return;
            const target = document.querySelector(targetId);
            if (!target) return;
            e.preventDefault();
            target.scrollIntoView({ behavior: "smooth", block: "start" });
        });
    });


    /* ==========================================
       Search Form Validation (navbar + shop search)
    ========================================== */

    document.querySelectorAll("form:not([data-allow-empty-search])").forEach(form => {
        const input = form.querySelector("input[name='q']");
        if (!input) return;
        form.addEventListener("submit", function (e) {
            if (input.value.trim() === "") {
                e.preventDefault();
                input.focus();
            }
        });
    });


    /* ==========================================
       Register Form Validation
    ========================================== */

    const registerForm = document.getElementById("registerForm");

    if (registerForm) {
        registerForm.addEventListener("submit", function (e) {
            const password = document.getElementById("password");
            const confirmPassword = document.getElementById("confirmPassword");

            if (password && confirmPassword) {
                if (password.value !== confirmPassword.value) {
                    e.preventDefault();
                    alert("Passwords do not match.");
                    confirmPassword.focus();
                    return;
                }
                if (password.value.length < 6) {
                    e.preventDefault();
                    alert("Password must contain at least 6 characters.");
                    password.focus();
                }
            }
        });
    }


    /* ==========================================
       Password Show / Hide
    ========================================== */

    const togglePassword = document.getElementById("togglePassword");
    const passwordField = document.getElementById("password");

    if (togglePassword && passwordField) {
        togglePassword.addEventListener("click", () => {
            if (passwordField.type === "password") {
                passwordField.type = "text";
                togglePassword.innerHTML = '<i class="fa-solid fa-eye-slash"></i>';
            } else {
                passwordField.type = "password";
                togglePassword.innerHTML = '<i class="fa-solid fa-eye"></i>';
            }
        });
    }


    /* ==========================================
       Contact Form Validation (server handles the message)
    ========================================== */

    const contactForm = document.getElementById("contactForm");

    if (contactForm) {
        contactForm.addEventListener("submit", function (e) {
            const name = document.getElementById("name");
            const email = document.getElementById("email");
            const message = document.getElementById("message");

            if (!name.value.trim() || !email.value.trim() || !message.value.trim()) {
                e.preventDefault();
                alert("Please fill all required fields.");
            }
        });
    }


    /* ==========================================
       Checkout Form Validation
    ========================================== */

    const checkoutForm = document.getElementById("checkoutForm");

    if (checkoutForm) {
        checkoutForm.addEventListener("submit", function (e) {
            const requiredFields = checkoutForm.querySelectorAll("[required]");
            let valid = true;

            requiredFields.forEach(field => {
                if (field.value.trim() === "") {
                    valid = false;
                    field.classList.add("is-invalid");
                } else {
                    field.classList.remove("is-invalid");
                }
            });

            if (!valid) {
                e.preventDefault();
                alert("Please complete all required fields.");
            }
        });
    }


    /* ==========================================
       Delete Confirmation
    ========================================== */

    document.querySelectorAll(".delete-btn").forEach(button => {
        button.addEventListener("click", function (e) {
            if (!confirm("Are you sure you want to delete this item?")) {
                e.preventDefault();
            }
        });
    });


    /* ==========================================
       Auto Dismiss Flash Messages
       (only Django messages, not in-page notices)
    ========================================== */

    setTimeout(() => {
        document.querySelectorAll(".site-messages .alert, .admin-main > .mb-3 > .alert").forEach(alertBox => {
            alertBox.classList.remove("show");
            setTimeout(() => alertBox.remove(), 300);
        });
    }, 5000);


    /* ==========================================
       Auto-submit sort dropdowns
    ========================================== */

    document.querySelectorAll("select[data-autosubmit]").forEach(select => {
        select.addEventListener("change", () => select.form.submit());
    });


    /* ==========================================
       Fade-In-On-Scroll
    ========================================== */

    const fadeElements = document.querySelectorAll(".fade-up");

    if (fadeElements.length > 0) {
        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("show");
                }
            });
        }, { threshold: 0.2 });

        fadeElements.forEach(element => observer.observe(element));
    }


    /* ==========================================
       Current Year (footer)
    ========================================== */

    const currentYear = document.getElementById("currentYear");
    if (currentYear) {
        currentYear.textContent = new Date().getFullYear();
    }

});
