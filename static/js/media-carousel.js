// Media carousel functionality for explore cards

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all media carousels on the page
    const carousels = document.querySelectorAll('[data-media-carousel]');
    
    carousels.forEach(carousel => {
        const media = carousel.querySelectorAll('[data-media-item]');
        
        if (media.length === 0) return;
        
        let currentIndex = 0;
        
        // Show first media by default
        function showMedia(index) {
            media.forEach((item, i) => {
                item.style.display = i === index ? 'block' : 'none';
                
                // Auto-play videos
                if (item.tagName === 'VIDEO' && i === index) {
                    item.play().catch(() => {
                        // Video play failed, continue silently
                    });
                }
            });
            
            // Update media count indicator
            const indicator = carousel.parentElement.querySelector('[data-media-count]');
            if (indicator) {
                indicator.textContent = `${index + 1} / ${media.length}`;
            }
        }
        
        function nextMedia() {
            currentIndex = (currentIndex + 1) % media.length;
            showMedia(currentIndex);
        }
        
        function prevMedia() {
            currentIndex = (currentIndex - 1 + media.length) % media.length;
            showMedia(currentIndex);
        }
        
        // Initialize display
        showMedia(0);
        
        // Attach navigation handlers
        const prevBtn = carousel.parentElement.querySelector('[data-media-prev]');
        const nextBtn = carousel.parentElement.querySelector('[data-media-next]');
        
        if (prevBtn) {
            prevBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                prevMedia();
            });
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                nextMedia();
            });
        }
        
        // Optional: Auto-cycle through media every 5 seconds
        // Uncomment if desired
        /*
        setInterval(() => {
            if (carousel.offsetParent !== null) { // Only if visible
                nextMedia();
            }
        }, 5000);
        */
    });
});

// Load media from API for dynamic rendering
async function loadMediaForCard(card, itemId, itemType) {
    try {
        const endpoint = itemType === 'venue' 
            ? `/api/venues/${itemId}/profile/`
            : `/api/services/${itemId}/profile/`;
            
        const response = await fetch(endpoint);
        const data = await response.json();
        
        if (data.media && data.media.length > 0) {
            const carousel = card.querySelector('[data-media-carousel]');
            if (!carousel) return;
            
            // Clear existing media
            carousel.innerHTML = '';
            
            // Add new media items
            data.media.forEach((mediaItem, index) => {
                const tag = mediaItem.is_video ? 'video' : 'img';
                const element = document.createElement(tag);
                element.class = 'media-item';
                element.setAttribute('data-media-item', '');
                element.src = mediaItem.file;
                
                if (mediaItem.is_video) {
                    element.setAttribute('muted', '');
                    element.setAttribute('loop', '');
                }
                
                if (!mediaItem.is_video) {
                    element.alt = data.title || 'Media';
                }
                
                element.style.display = index === 0 ? 'block' : 'none';
                carousel.appendChild(element);
            });
            
            // Update indicator
            const indicator = card.querySelector('[data-media-count]');
            if (indicator) {
                indicator.textContent = `1 / ${data.media.length}`;
            }
        }
    } catch (error) {
        console.error('Error loading media:', error);
    }
}
