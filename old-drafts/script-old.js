document.addEventListener("DOMContentLoaded", function() {
    // Select all images inside the image containers
    const parallaxImages = document.querySelectorAll('.image-container img');

    function checkScroll() {
        // Iterate through each image
        parallaxImages.forEach(img => {
            const container = img.parentElement;
            
            // Get the position of the container relative to the viewport
            const rect = container.getBoundingClientRect();
            
            // Calculate if the element is in the viewport (visible on screen)
            const isVisible = rect.top < window.innerHeight && rect.bottom > 0;

            if (isVisible) {
                // Calculate the shift amount. 
                // 'speed' determines how fast the image moves relative to the scroll.
                // 0.2 means it moves at 20% of the scroll speed.
                const speed = 0.2; 
                
                // Calculate the vertical offset
                // We center the effect so the image is in its 'neutral' position when it's in the middle of the screen
                const windowHeight = window.innerHeight;
                const centerPoint = windowHeight / 2;
                const containerCenter = rect.top + (rect.height / 2);
                
                // The math: Calculate distance from center of screen -> apply speed factor
                const yPos = (containerCenter - centerPoint) * speed;

                // Apply the transformation
                img.style.transform = `translateY(${yPos}px) scale(1.1)`; 
                // Note: scale(1.1) ensures the edges don't show when the image moves
            }
        });

        // Request the next animation frame for smooth performance
        requestAnimationFrame(checkScroll);
    }

    // Start the loop
    requestAnimationFrame(checkScroll);
});