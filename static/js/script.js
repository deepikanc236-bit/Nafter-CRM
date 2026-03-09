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

    const burger = document.querySelector('.burger');
    const nav = document.querySelector('.nav-links');
    if (burger && nav) {
        burger.addEventListener('click', () => {
            nav.classList.toggle('nav-active');
            burger.classList.toggle('toggle');
        });
    }

    // Scroll-in Animations using Intersection Observer
    const observerOptions = {
        threshold: 0.2
    };

    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, observerOptions);

    const animatedSections = document.querySelectorAll('.experience-section');
    animatedSections.forEach(section => {
        sectionObserver.observe(section);
    });
    // --- Dynamic Chat Widget Injection ---
    const widgetContainer = document.createElement('div');
    widgetContainer.className = 'widget-container';
    widgetContainer.innerHTML = `
        <!-- Chat Box -->
        <div class="chat-box" id="chatBox">
            <div class="chat-header">
                <div class="header-info">
                    <!-- Logo Removed as per request -->
                    <div class="header-text">
                        <h3>Nafter Web Technology</h3>
                        <p>Online</p>
                    </div>
                </div>
                <button class="close-chat" id="closeChat"><i class="fas fa-times"></i></button>
            </div>
            <div class="chat-body">
                <div class="message-bubble">
                    Hi there 👋<br>How can I help you?
                    <span class="check-time">Just now</span>
                </div>
            </div>
            <div class="chat-footer">
                <input type="text" class="chat-input" placeholder="Write a response..." id="chatInput">
                <button class="send-btn" id="sendBtn"><i class="fas fa-paper-plane"></i></button>
            </div>
        </div>

        <!-- WhatsApp Float Button (Now Top) -->
        <div class="whatsapp-float-btn" id="whatsappFloat">
            <i class="fab fa-whatsapp"></i>
        </div>

        <!-- Scroll Top Button (Now Bottom - Under WhatsApp) -->
        <button class="scroll-top-btn" id="scrollTopBtn">
            <i class="fas fa-arrow-up"></i>
        </button>
    `;
    document.body.appendChild(widgetContainer);

    // Cleanup: Remove legacy static WhatsApp buttons to prevent duplication
    const legacyBtns = document.querySelectorAll('.whatsapp-float');
    legacyBtns.forEach(btn => btn.style.display = 'none');

    // Widget Logic
    const whatsappBtn = document.getElementById('whatsappFloat');
    const chatBox = document.getElementById('chatBox');
    const closeChat = document.getElementById('closeChat');
    const sendBtn = document.getElementById('sendBtn');
    const chatInput = document.getElementById('chatInput');
    const scrollTopBtn = document.getElementById('scrollTopBtn');

    // Toggle Chat
    whatsappBtn.addEventListener('click', () => {
        chatBox.classList.toggle('open');
    });

    closeChat.addEventListener('click', () => {
        chatBox.classList.remove('open');
    });

    // Send Message to WhatsApp
    function sendMessage() {
        const msg = chatInput.value.trim();
        if (msg) {
            const phone = "918015795992";
            const url = `https://wa.me/${phone}?text=${encodeURIComponent(msg)}`;
            window.open(url, '_blank');
            chatInput.value = '';
            chatBox.classList.remove('open');
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // Scroll to Top Logic
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            scrollTopBtn.classList.add('show');
        } else {
            scrollTopBtn.classList.remove('show');
        }
    });

    scrollTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    // --- Testimonial Carousel Logic ---
    const track = document.getElementById('testimonialTrack');
    if (track) {
        const slides = Array.from(track.children);
        const nextButton = document.getElementById('nextTestimonial');
        const prevButton = document.getElementById('prevTestimonial');
        const indicators = document.querySelectorAll('.indicator');

        let currentIndex = 0;

        // update carousel position
        const updateCarousel = (index) => {
            // Move track
            track.style.transform = `translateX(-${index * 100}%)`;

            // Update Slides Opacity/Scale (optional, but good for focus)
            slides.forEach((slide, i) => {
                if (i === index) {
                    slide.classList.add('active');
                } else {
                    slide.classList.remove('active');
                }
            });

            // Update Indicators
            indicators.forEach((indicator, i) => {
                if (i === index) {
                    indicator.classList.add('active');
                } else {
                    indicator.classList.remove('active');
                }
            });
        };

        // Next Button
        if (nextButton) {
            nextButton.addEventListener('click', () => {
                currentIndex = (currentIndex + 1) % slides.length;
                updateCarousel(currentIndex);
            });
        }

        // Prev Button
        if (prevButton) {
            prevButton.addEventListener('click', () => {
                currentIndex = (currentIndex - 1 + slides.length) % slides.length;
                updateCarousel(currentIndex);
            });
        }
    }

    // Indicators Click
    indicators.forEach((indicator, index) => {
        indicator.addEventListener('click', () => {
            currentIndex = index;
            updateCarousel(currentIndex);
        });
    });

    // Auto Play (Optional)
    let autoPlayInterval = setInterval(() => {
        currentIndex = (currentIndex + 1) % slides.length;
        updateCarousel(currentIndex);
    }, 5000); // Change slides every 5 seconds

    // Pause on hover
    if (track) {
        track.addEventListener('mouseenter', () => clearInterval(autoPlayInterval));
        track.addEventListener('mouseleave', () => {
            autoPlayInterval = setInterval(() => {
                currentIndex = (currentIndex + 1) % slides.length;
                updateCarousel(currentIndex);
            }, 5000);
        });
    }

});
