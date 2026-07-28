document.addEventListener('DOMContentLoaded', () => {
  const badgeContainer = document.getElementById('photo-badge-container');
  if (!badgeContainer) return; // Safely exit if the page doesn't have the badge container

  // Path to your central JSON file
  fetch('photos.json')
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then(photos => {
      if (!photos || photos.length === 0) return;

      // Select a random photo entry
      const randomIndex = Math.floor(Math.random() * photos.length);
      const photo = photos[randomIndex];

      // Fallback values if properties are missing
      const imgUrl = photo.url || 'photos/featured-thumb.jpg';
      const pageLink = photo.link || 'photos/index.html';
      const title = photo.title || "Kathy's Photos";

      // Dynamically insert the photo badge HTML
      badgeContainer.innerHTML = `
        <aside class="photo-badge-card">
          <a href="${pageLink}" target="_blank" rel="noopener">
            <img 
              src="${imgUrl}" 
              alt="${title}" 
              class="badge-thumb" 
              loading="lazy"
              onerror="this.onerror=null; this.src='photos/featured-thumb.jpg';"
            >
            <strong>${title}</strong>
          </a>
          <p style="margin: 5px 0 0 0; font-size: 11px; color: #666;">
            Featured Photo
          </p>
        </aside>
      `;
    })
    .catch(err => {
      console.error('Error loading photo badge JSON:', err);
    });
});
