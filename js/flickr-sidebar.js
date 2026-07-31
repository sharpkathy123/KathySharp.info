document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll(".flickr-sidebar").forEach(div => {

        const topic = div.dataset.topic;
        const photo = div.dataset.photo;
        const page = div.dataset.page;
        const alt = div.dataset.alt || topic;

        // Optional custom link text
        const linkText = div.dataset.linkText || `More ${topic} photos →`;

        div.innerHTML = `
            <a href="${page}"
               target="_blank"
               rel="noopener">
                <img src="${photo}"
                     alt="${alt}"
                     loading="lazy">
            </a>

            <div class="flickr-more">
                <a href="https://www.flickr.com/photos/YOUR_USERNAME/tags/${encodeURIComponent(topic)}+favorite/"
                   target="_blank"
                   rel="noopener">
                    ${linkText}
                </a>
            </div>
        `;

    });

});