document.addEventListener("DOMContentLoaded", function() {
    const track = document.getElementById('scroll-track');
    const stage = document.getElementById('fixed-stage');
    const nav = document.getElementById('main-nav'); // Select the nav
    const slides = document.querySelectorAll('.slide');
    
    // Config: Scroll sensitivity
    track.style.height = (slides.length * 100) + "vh";

    function updateSlide() {
        const scrollTop = window.scrollY;
        const windowHeight = window.innerHeight;
        const totalHeight = track.offsetHeight - windowHeight;
        
        let progress = scrollTop / totalHeight;
        let slideIndex = Math.floor(progress * (slides.length));

        if (slideIndex < 0) slideIndex = 0;
        if (slideIndex >= slides.length) slideIndex = slides.length - 1;

        slides.forEach((slide, index) => {
            if (index === slideIndex) {
                slide.classList.add('active');
                
                // Update Background
                const newBg = slide.getAttribute('data-bg');
                if (newBg) stage.style.backgroundColor = newBg;

                // Update Theme (affects Text AND Nav Bar)
                const newTheme = slide.getAttribute('data-theme');
                if (newTheme === 'dark') {
                    stage.classList.add('theme-dark');
                    nav.classList.add('theme-dark'); // Turn nav white
                } else {
                    stage.classList.remove('theme-dark');
                    nav.classList.remove('theme-dark'); // Turn nav dark
                }

            } else {
                slide.classList.remove('active');
            }
        });
    }

    window.addEventListener('scroll', updateSlide);
    window.addEventListener('resize', updateSlide);
    updateSlide();
});