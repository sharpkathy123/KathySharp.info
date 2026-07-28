document.addEventListener('DOMContentLoaded', () => {
  const badgeContainer = document.getElementById('photo-badge-container');
  if (!badgeContainer) return; // Exit safely if the container isn't on the page

  // Public Flickr RSS Feed for Album 72157623193132607 converted to JSON
  const rssFeedUrl = 'https://www.flickr.com/services/feeds/photoset.gne?nsid=99505022@N00&set=72157623193132607&lang=en-us&format=rss_200';
  const apiUrl = `https://api.rss2json.com/v1/api.json?rss_url=${encodeURIComponent(rssFeedUrl)}`;

  fetch(apiUrl)
    .then(response => {
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return response.json();
    })
    .then(data => {
      if (data.items && data.items.length > 0) {
        // Pick a random photo from the feed
        const randomIndex = Math.floor(Math.random() * data.items.length);
        const item = data.items[randomIndex];

        // Clean up title by stripping leading date/timestamps (e.g. "2018-10-15 13-40-30")
        let title = item.title ? item.title.trim() : '';
        title = title.replace(/^\d{4}-\d{2}-\d{2}\s+\d{2}-\d{2}-\d{2}\s*[-–:]*\s*/, '').trim();
        
        // Fallback if the photo has no text caption beyond the timestamp
        if (!title) {
          title = "Kathy's Favorites";
        }

        // Use the enclosure/thumbnail URL from the feed
        const imgSrc = item.thumbnail || (item.enclosure ? item.enclosure.link : '');

        // Inject the badge HTML
        badgeContainer.innerHTML = `
          <aside class="photo-badge-card">
            <a href="${item.link}" target="_blank" rel="noopener">
              <img 
                src="${imgSrc}" 
                alt="${title}" 
                class="badge-thumb" 
                loading="lazy"
                onerror="this.onerror=null; this.src='photos/featured-thumb.jpg';"
              >
              <strong>${title}</strong>
            </a>
            <p style="margin: 5px 0 0 0; font-size: 11px; color: #666;">
              View on <a href="https://www.flickr.com/photos/kathysharp/sets/72157623193132607/" target="_blank" rel="noopener">Flickr</a>
            </p>
          </aside>
        `;
      }
    })
    .catch(err => {
      console.error('Error loading Flickr RSS feed:', err);
    });
});
