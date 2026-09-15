document.addEventListener("DOMContentLoaded", function() {
    const track = document.getElementById('scroll-track');
    const stage = document.getElementById('fixed-stage');
    const slides = document.querySelectorAll('.slide');
    
    // Config: Height of scroll track based on number of slides
    track.style.height = (slides.length * 100) + "vh";

    function updateSlide() {
        const scrollTop = window.scrollY;
        const windowHeight = window.innerHeight;
        const totalHeight = track.offsetHeight - windowHeight;
        
        let progress = scrollTop / totalHeight;
        let slideIndex = Math.floor(progress * (slides.length));

        // Safety check to keep index within bounds
        if (slideIndex < 0) slideIndex = 0;
        if (slideIndex >= slides.length) slideIndex = slides.length - 1;

        slides.forEach((slide, index) => {
            if (index === slideIndex) {
                slide.classList.add('active');
                
                // Update Background Color (Always Light now)
                const newBg = slide.getAttribute('data-bg');
                if (newBg) stage.style.backgroundColor = newBg;
            } else {
                slide.classList.remove('active');
            }
        });
    }

    window.addEventListener('scroll', updateSlide);
    window.addEventListener('resize', updateSlide);
    updateSlide();
});