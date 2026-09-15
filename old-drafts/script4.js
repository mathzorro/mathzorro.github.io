document.addEventListener("DOMContentLoaded", function() {
    const track = document.getElementById('scroll-track');
    const stage = document.getElementById('fixed-stage');
    const slides = document.querySelectorAll('.slide');
    
    // Config: How tall should the scrollable area be?
    // 500vh means the user has to scroll 5 screen heights to see everything.
    // Adjust this multiplier to make the scroll faster or slower.
    const scrollSensitivity = 5; 
    track.style.height = (slides.length * 100) + "vh";

    function updateSlide() {
        const scrollTop = window.scrollY;
        const windowHeight = window.innerHeight;
        const totalHeight = track.offsetHeight - windowHeight;
        
        // Calculate percentage scrolled (0.0 to 1.0)
        let progress = scrollTop / totalHeight;
        
        // Map progress to slide index (0 to slides.length - 1)
        let slideIndex = Math.floor(progress * (slides.length));

        // Clamp index to prevent errors
        if (slideIndex < 0) slideIndex = 0;
        if (slideIndex >= slides.length) slideIndex = slides.length - 1;

        // 1. Activate the correct slide
        slides.forEach((slide, index) => {
            if (index === slideIndex) {
                slide.classList.add('active');
                
                // 2. Update Background Color
                const newBg = slide.getAttribute('data-bg');
                if (newBg) stage.style.backgroundColor = newBg;

                // 3. Update Text Theme (Light/Dark)
                const newTheme = slide.getAttribute('data-theme');
                if (newTheme === 'dark') {
                    stage.classList.add('theme-dark');
                } else {
                    stage.classList.remove('theme-dark');
                }

            } else {
                slide.classList.remove('active');
            }
        });
    }

    // Listen for scroll events
    window.addEventListener('scroll', updateSlide);
    
    // Listen for resize (recalculate math)
    window.addEventListener('resize', updateSlide);

    // Initial run
    updateSlide();
});