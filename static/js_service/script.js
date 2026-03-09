/* Nafter Web Technologies - Main JS */

document.addEventListener("DOMContentLoaded", () => {
    // Preloader Logic
    const preloader = document.getElementById("preloader");
    if (preloader) {
        window.addEventListener("load", () => {
            preloader.style.opacity = "0";
            setTimeout(() => {
                preloader.style.display = "none";
            }, 500);
        });
    }

    // Mobile Navigation Toggle
    /* Note: Since we don't have a burger menu implementation in HTML yet, 
       this is placeholder logic for when we add the button in HTML. 
       Currently relying on CSS media queries for display. 
       If a burger icon is added:
    */
    /*
    const burger = document.querySelector('.burger');
    const nav = document.querySelector('.nav-links');
    if(burger && nav){
        burger.addEventListener('click', () => {
            nav.classList.toggle('nav-active');
            burger.classList.toggle('toggle');
        });
    }
    */

    // Contact Form Handling
    const contactForm = document.getElementById("enquiryForm");
    if (contactForm) {
        contactForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const formData = new FormData(contactForm);
            // Here you would typically send data to backend
            console.log("Form Submitted", Object.fromEntries(formData));

            // Visual feedback
            const btn = contactForm.querySelector(".submit-btn");
            const originalText = btn.innerText;
            btn.innerText = "Message Sent!";
            btn.style.background = "#22c55e"; // Green

            setTimeout(() => {
                contactForm.reset();
                btn.innerText = originalText;
                btn.style.background = ""; // Reset to CSS default
            }, 3000);
        });
    }

    // ------------------------------------------------------------------ 
    // -------------------- 3D Holographic Tilt Logic ------------------- 
    // ------------------------------------------------------------------ 
    const tiltCards = document.querySelectorAll("[data-tilt]");
    
    tiltCards.forEach(card => {
        card.addEventListener("mousemove", (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left; // x position within the element.
            const y = e.clientY - rect.top;  // y position within the element.
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            // Calculate rotation based on mouse position
            // Multiplier determines the intensity of the tilt
            const rotateX = ((y - centerY) / centerY) * -15; 
            const rotateY = ((x - centerX) / centerX) * 15;

            // Apply transform
            // perspective is important for the 3D effect
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
        });

        card.addEventListener("mouseleave", () => {
            // Reset state
            card.style.transform = "perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)";
        });
    });

});
