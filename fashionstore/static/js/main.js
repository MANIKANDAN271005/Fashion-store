/* ==========================================
   FASHION STORE JAVASCRIPT
   Part 1 - Core Functions
========================================== */

"use strict";

document.addEventListener("DOMContentLoaded", () => {

    console.log("Fashion Store Loaded Successfully");

    /* ==========================================
       Mobile Navigation
    ========================================== */

    const menuBtn = document.querySelector(".menu-btn");
    const navLinks = document.querySelector(".nav-links");

    if (menuBtn && navLinks) {

        menuBtn.addEventListener("click", () => {

            navLinks.classList.toggle("show");

        });

    }

    /* ==========================================
       Sticky Navbar
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
       Active Navigation Link
    ========================================== */

    const currentPage = window.location.pathname;

    document.querySelectorAll(".navbar .nav-link").forEach(link => {

        if (link.getAttribute("href") === currentPage) {

            link.classList.add("active");

        }

    });


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

            window.scrollTo({

                top: 0,
                behavior: "smooth"

            });

        });

    }


    /* ==========================================
       Smooth Scroll
    ========================================== */

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {

        anchor.addEventListener("click", function (e) {

            const target = document.querySelector(this.getAttribute("href"));

            if (!target) return;

            e.preventDefault();

            target.scrollIntoView({

                behavior: "smooth",
                block: "start"

            });

        });

    });


    /* ==========================================
       Loading Spinner
    ========================================== */

    window.addEventListener("load", () => {

        const loader = document.querySelector(".loader");

        if (loader) {

            loader.style.opacity = "0";

            setTimeout(() => {

                loader.style.display = "none";

            }, 400);

        }

    });

});

    /* ==========================================
       Dark Mode
    ========================================== */

    const darkModeBtn = document.getElementById("darkMode");

    if (localStorage.getItem("theme") === "dark") {

        document.body.classList.add("dark-mode");

    }

    if (darkModeBtn) {

        darkModeBtn.addEventListener("click", () => {

            document.body.classList.toggle("dark-mode");

            if (document.body.classList.contains("dark-mode")) {

                localStorage.setItem("theme", "dark");

            } else {

                localStorage.setItem("theme", "light");

            }

        });

    }


    /* ==========================================
       Search Form Validation
    ========================================== */

    document.querySelectorAll("form").forEach(form => {

        if (form.querySelector("input[name='q']")) {

            form.addEventListener("submit", function (e) {

                const input = form.querySelector("input[name='q']");

                if (input.value.trim() === "") {

                    e.preventDefault();

                    alert("Please enter a product name.");

                    input.focus();

                }

            });

        }

    });


    /* ==========================================
       Live Product Search
    ========================================== */

    const searchInput = document.getElementById("searchInput");

    if (searchInput) {

        searchInput.addEventListener("keyup", function () {

            const value = this.value.toLowerCase();

            const cards = document.querySelectorAll(".product-card");

            cards.forEach(card => {

                const text = card.innerText.toLowerCase();

                if (text.includes(value)) {

                    card.parentElement.style.display = "";

                } else {

                    card.parentElement.style.display = "none";

                }

            });

        });

    }


    /* ==========================================
       Newsletter Validation
    ========================================== */

    const newsletterForm = document.getElementById("newsletter");

    if (newsletterForm) {

        newsletterForm.addEventListener("submit", function (e) {

            const email = this.querySelector("input[type='email']");

            const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

            if (!pattern.test(email.value.trim())) {

                e.preventDefault();

                alert("Please enter a valid email address.");

                email.focus();

            }

        });

    }


    /* ==========================================
       Contact Form Validation
    ========================================== */

    const contactForm = document.getElementById("contactForm");

    if (contactForm) {

        contactForm.addEventListener("submit", function (e) {

            const name = document.getElementById("name");
            const email = document.getElementById("email");
            const message = document.getElementById("message");

            if (
                !name.value.trim() ||
                !email.value.trim() ||
                !message.value.trim()
            ) {

                e.preventDefault();

                alert("Please fill all required fields.");

                return;

            }

            alert("Thank you! Your message has been sent.");

        });

    }


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

                togglePassword.innerHTML =
                    '<i class="fa-solid fa-eye-slash"></i>';

            } else {

                passwordField.type = "password";

                togglePassword.innerHTML =
                    '<i class="fa-solid fa-eye"></i>';

            }

        });

    }

        /* ==========================================
       Dark Mode
    ========================================== */

    const darkModeBtn = document.getElementById("darkMode");

    if (localStorage.getItem("theme") === "dark") {

        document.body.classList.add("dark-mode");

    }

    if (darkModeBtn) {

        darkModeBtn.addEventListener("click", () => {

            document.body.classList.toggle("dark-mode");

            if (document.body.classList.contains("dark-mode")) {

                localStorage.setItem("theme", "dark");

            } else {

                localStorage.setItem("theme", "light");

            }

        });

    }


    /* ==========================================
       Search Form Validation
    ========================================== */

    document.querySelectorAll("form").forEach(form => {

        if (form.querySelector("input[name='q']")) {

            form.addEventListener("submit", function (e) {

                const input = form.querySelector("input[name='q']");

                if (input.value.trim() === "") {

                    e.preventDefault();

                    alert("Please enter a product name.");

                    input.focus();

                }

            });

        }

    });


    /* ==========================================
       Live Product Search
    ========================================== */

    const searchInput = document.getElementById("searchInput");

    if (searchInput) {

        searchInput.addEventListener("keyup", function () {

            const value = this.value.toLowerCase();

            const cards = document.querySelectorAll(".product-card");

            cards.forEach(card => {

                const text = card.innerText.toLowerCase();

                if (text.includes(value)) {

                    card.parentElement.style.display = "";

                } else {

                    card.parentElement.style.display = "none";

                }

            });

        });

    }


    /* ==========================================
       Newsletter Validation
    ========================================== */

    const newsletterForm = document.getElementById("newsletter");

    if (newsletterForm) {

        newsletterForm.addEventListener("submit", function (e) {

            const email = this.querySelector("input[type='email']");

            const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

            if (!pattern.test(email.value.trim())) {

                e.preventDefault();

                alert("Please enter a valid email address.");

                email.focus();

            }

        });

    }


    /* ==========================================
       Contact Form Validation
    ========================================== */

    const contactForm = document.getElementById("contactForm");

    if (contactForm) {

        contactForm.addEventListener("submit", function (e) {

            const name = document.getElementById("name");
            const email = document.getElementById("email");
            const message = document.getElementById("message");

            if (
                !name.value.trim() ||
                !email.value.trim() ||
                !message.value.trim()
            ) {

                e.preventDefault();

                alert("Please fill all required fields.");

                return;

            }

            alert("Thank you! Your message has been sent.");

        });

    }


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

                togglePassword.innerHTML =
                    '<i class="fa-solid fa-eye-slash"></i>';

            } else {

                passwordField.type = "password";

                togglePassword.innerHTML =
                    '<i class="fa-solid fa-eye"></i>';

            }

        });

    }
        /* ==========================================
       Product Image Gallery
    ========================================== */

    const mainImage = document.getElementById("mainImage");
    const thumbnails = document.querySelectorAll(".thumbnail");

    if (mainImage && thumbnails.length > 0) {

        thumbnails.forEach(thumbnail => {

            thumbnail.addEventListener("click", function () {

                mainImage.src = this.src;

                thumbnails.forEach(img => img.classList.remove("active"));

                this.classList.add("active");

            });

        });

    }


    /* ==========================================
       Product Image Zoom
    ========================================== */

    if (mainImage) {

        mainImage.addEventListener("mousemove", () => {

            mainImage.style.transform = "scale(1.15)";
            mainImage.style.transition = ".3s";

        });

        mainImage.addEventListener("mouseleave", () => {

            mainImage.style.transform = "scale(1)";

        });

    }


    /* ==========================================
       Quantity Selector
    ========================================== */

    const quantityInput = document.querySelector(".quantity-input");
    const quantityButtons = document.querySelectorAll(".qty-btn");

    if (quantityInput && quantityButtons.length === 2) {

        quantityButtons[0].addEventListener("click", () => {

            let quantity = parseInt(quantityInput.value);

            if (quantity > 1) {

                quantityInput.value = quantity - 1;

            }

        });

        quantityButtons[1].addEventListener("click", () => {

            let quantity = parseInt(quantityInput.value);

            quantityInput.value = quantity + 1;

        });

    }


    /* ==========================================
       Size Selection
    ========================================== */

    const sizeButtons = document.querySelectorAll(".size-options button");

    sizeButtons.forEach(button => {

        button.addEventListener("click", () => {

            sizeButtons.forEach(btn => {

                btn.classList.remove("active-size");

            });

            button.classList.add("active-size");

        });

    });


    /* ==========================================
       Color Selection
    ========================================== */

    const colorButtons = document.querySelectorAll(".color");

    colorButtons.forEach(color => {

        color.addEventListener("click", () => {

            colorButtons.forEach(btn => {

                btn.classList.remove("active-color");

            });

            color.classList.add("active-color");

        });

    });


    /* ==========================================
       Wishlist Button Animation
    ========================================== */

    const wishlistButtons = document.querySelectorAll(".wishlist-btn");

    wishlistButtons.forEach(button => {

        button.addEventListener("click", function (e) {

            e.preventDefault();

            this.classList.toggle("active");

            const icon = this.querySelector("i");

            if (icon) {

                if (this.classList.contains("active")) {

                    icon.classList.remove("fa-regular");
                    icon.classList.add("fa-solid");

                } else {

                    icon.classList.remove("fa-solid");
                    icon.classList.add("fa-regular");

                }

            }

        });

    });


    /* ==========================================
       Add To Cart Animation
    ========================================== */

    const cartButtons = document.querySelectorAll(".cart-btn");

    cartButtons.forEach(button => {

        button.addEventListener("click", function () {

            this.innerHTML = `
                <i class="fa-solid fa-check"></i>
                Added
            `;

            this.classList.remove("btn-dark");
            this.classList.add("btn-success");

            setTimeout(() => {

                this.innerHTML = `
                    <i class="fa-solid fa-cart-shopping"></i>
                    Add to Cart
                `;

                this.classList.remove("btn-success");
                this.classList.add("btn-dark");

            }, 2000);

        });

    });


    /* ==========================================
       Product Card Hover
    ========================================== */

    const productCards = document.querySelectorAll(".product-card");

    productCards.forEach(card => {

        card.addEventListener("mouseenter", () => {

            card.style.transform = "translateY(-10px)";
            card.style.transition = ".35s";

        });

        card.addEventListener("mouseleave", () => {

            card.style.transform = "translateY(0)";

        });

    });


    /* ==========================================
       Fade Animation
    ========================================== */

    const fadeElements = document.querySelectorAll(".fade-up");

    if (fadeElements.length > 0) {

        const observer = new IntersectionObserver(entries => {

            entries.forEach(entry => {

                if (entry.isIntersecting) {

                    entry.target.classList.add("show");

                }

            });

        }, {

            threshold: 0.2

        });

        fadeElements.forEach(element => {

            observer.observe(element);

        });

    }

        /* ==========================================
       Checkout Form
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
       Auto Close Alerts
    ========================================== */

    setTimeout(() => {

        document.querySelectorAll(".alert").forEach(alert => {

            alert.classList.add("fade");

            setTimeout(() => {

                alert.remove();

            }, 500);

        });

    }, 3000);


    /* ==========================================
       Copy Coupon Code
    ========================================== */

    document.querySelectorAll(".copy-coupon").forEach(button => {

        button.addEventListener("click", function () {

            const code = this.dataset.code;

            navigator.clipboard.writeText(code);

            this.innerHTML = "Copied ✓";

            setTimeout(() => {

                this.innerHTML = "Copy Code";

            }, 2000);

        });

    });


    /* ==========================================
       Countdown Timer
    ========================================== */

    const countdown = document.getElementById("countdown");

    if (countdown) {

        let hours = 23;
        let minutes = 59;
        let seconds = 59;

        setInterval(() => {

            seconds--;

            if (seconds < 0) {

                seconds = 59;
                minutes--;

            }

            if (minutes < 0) {

                minutes = 59;
                hours--;

            }

            if (hours < 0) {

                hours = 23;

            }

            countdown.textContent =
                `${hours.toString().padStart(2, "0")} : ${minutes
                    .toString()
                    .padStart(2, "0")} : ${seconds
                    .toString()
                    .padStart(2, "0")}`;

        }, 1000);

    }


    /* ==========================================
       Product Rating
    ========================================== */

    document.querySelectorAll(".rating-select i").forEach((star, index, stars) => {

        star.addEventListener("click", () => {

            stars.forEach((item, i) => {

                if (i <= index) {

                    item.classList.remove("fa-regular");
                    item.classList.add("fa-solid");

                } else {

                    item.classList.remove("fa-solid");
                    item.classList.add("fa-regular");

                }

            });

        });

    });


    /* ==========================================
       Button Loading Effect
    ========================================== */

    document.querySelectorAll(".loading-btn").forEach(button => {

        button.addEventListener("click", function () {

            const original = this.innerHTML;

            this.disabled = true;

            this.innerHTML = `
                <span class="spinner-border spinner-border-sm"></span>
                Loading...
            `;

            setTimeout(() => {

                this.disabled = false;

                this.innerHTML = original;

            }, 1500);

        });

    });


    /* ==========================================
       Current Year
    ========================================== */

    const currentYear = document.getElementById("currentYear");

    if (currentYear) {

        currentYear.textContent = new Date().getFullYear();

    }


    /* ==========================================
       Lazy Loading Images
    ========================================== */

    const lazyImages = document.querySelectorAll("img[data-src]");

    if (lazyImages.length > 0) {

        const imageObserver = new IntersectionObserver(entries => {

            entries.forEach(entry => {

                if (entry.isIntersecting) {

                    const image = entry.target;

                    image.src = image.dataset.src;

                    image.removeAttribute("data-src");

                    imageObserver.unobserve(image);

                }

            });

        });

        lazyImages.forEach(image => {

            imageObserver.observe(image);

        });

    }


    /* ==========================================
       Console Message
    ========================================== */

    console.log("All JavaScript Modules Loaded Successfully 🚀");

    function changeImage(element){

    document.getElementById("mainImage").src = element.src;

    document.querySelectorAll(".thumbnail").forEach(function(img){
        img.classList.remove("active");
    });

    element.classList.add("active");

}

let quantity = 1;

function increaseQty(){

    quantity++;

    document.getElementById("quantity").value = quantity;

}

function decreaseQty(){

    if(quantity > 1){

        quantity--;

        document.getElementById("quantity").value = quantity;

    }

}


document.addEventListener("DOMContentLoaded", function () {

    const params = new URLSearchParams(window.location.search);

    if (params.has("q")) {

        const section = document.getElementById("shopProducts");

        if (section) {

            section.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        }

    }

});
