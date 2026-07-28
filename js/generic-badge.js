// Callback function automatically invoked by Flickr's JSON feed
function jsonFlickrFeed(data) {
  const badgeContainer = document.getElementById('photo-badge-container');
  if (!badgeContainer || !data.items || data.items.length === 0) return;

  // Pick a random photo from the feed
  const randomIndex = Math.floor(Math.random() * data.items.length);
  const item = data.items[randomIndex];

  // Clean up title (remove timestamps like "2018-10-15 13-40-30")
  let title = item.title ? item.title.trim() : '';
  title = title.replace(/^\d{4}-\d{2}-\d{2}\s+\d{2}-\d{2}-\d{2}\s*[-–:]*\s*/, '').trim();
  
  if (!title) {
    title = "Kathy's Favorites";
  }

  // Get image URL directly from Flickr's media object
  const imgSrc = item.media ? item.media.m : '';

  // Inject the badge HTML
  badgeContainer.innerHTML = `
    <aside class="photo-badge-card">
      <a href="${item.link}" target="_blank" rel="noopener">
        <img 
          src="${imgSrc}" 
          alt="${title}" 
          class="badge-thumb" 
          loading="lazy"
        >
        <strong>${title}</strong>
      </a>
      <p style="margin: 5px 0 0 0; font-size: 11px; color: #666;">
        View on <a href="https://www.flickr.com/photos/kathysharp/sets/72157623193132607/" target="_blank" rel="noopener">Flickr</a>
      </p>
    </aside>
  `;
}

// Dynamically load Flickr's official JSONP feed script
(function loadFlickrFeed() {
  const script = document.createElement('script');
  script.src = 'https://www.flickr.com/services/feeds/photoset.gne?nsid=99505022@N00&set=72157623193132607&lang=en-us&format=json';
  document.head.appendChild(script);
})();
