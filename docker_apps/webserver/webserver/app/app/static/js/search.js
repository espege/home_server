document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('search-form');
    const resultsContainer = document.getElementById('results');

    searchForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const query = document.getElementById('search-input').value;
        performSearch(query);
    });

    // Load all songs by default when the page opens
    performSearch('');
});

function performSearch(query) {
    const resultsContainer = document.getElementById('results');

    fetch(`/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            resultsContainer.innerHTML = '';
            if (data.length > 0) {
                data.forEach(song => {
                    const songElement = document.createElement('div');
                    songElement.classList.add('song');
                    const mediaLink = song.media_links.length > 0
                        ? `<a href="${song.media_links[0]}" target="_blank">Écouter</a>`
                        : '';
                    const scoresText = song.scores.map(s =>
                        typeof s === 'string' ? s : s.name
                    ).join(', ');
                    songElement.innerHTML = `
                        <h3>${song.title}</h3>
                        <p><strong>Genre:</strong> ${song.genre}</p>
                        <p><strong>Sous-genre:</strong> ${song.subgenre}</p>
                        <p><strong>Partitions:</strong> ${scoresText || 'No scores'}</p>
                        <p><strong>Interprètes:</strong> ${song.interpreters.join(', ')}</p>
                        <p><strong>Compositeur:</strong> ${song.composers.join(', ')}</p>
                        <div style="display: flex; gap: 0.5rem;">
                            <a href="/song/${song.id}" style="padding: 0.5rem 1rem; background-color: var(--md-sys-color-secondary); color: var(--md-sys-color-on-secondary); text-decoration: none; border-radius: 6px; cursor: pointer;">Détails</a>
                            ${mediaLink}
                        </div>
                    `;
                    resultsContainer.appendChild(songElement);
                });
            } else {
                resultsContainer.innerHTML = '<p style="color: #E1E1E6; text-align: center; padding: 40px 0;">No results found.</p>';
            }
        })
        .catch(error => {
            console.error('Error fetching search results:', error);
            resultsContainer.innerHTML = '<p style="color: #CF6679; text-align: center; padding: 40px 0;">Error fetching results. Please try again later.</p>';
        });
}

function searchByGenreOrSubGenre(searchType, value) {
    if (searchType !== 'genre' && searchType !== 'subgenre') {
        console.error("searchType must be either 'genre' or 'subgenre'");
        return;
    }

    const searchInput = document.getElementById('search-input');
    const resultsContainer = document.getElementById('results');

    if (searchInput) {
        searchInput.value = '';
    }

    if (!resultsContainer) {
        return;
    }

    fetch(`/search?${searchType}=${encodeURIComponent(value)}`)
        .then(response => response.json())
        .then(data => {
            resultsContainer.innerHTML = '';

            if (data.length > 0) {
                data.forEach(song => {
                    const songElement = document.createElement('div');
                    songElement.classList.add('song');
                    const mediaLink = song.media_links.length > 0
                        ? `<a href="${song.media_links[0]}" target="_blank">Écouter</a>`
                        : '<p><em></em></p>'; // Don't show when nothing
                    const scoresText = song.scores.map(s =>
                        typeof s === 'string' ? s : s.name
                    ).join(', ');
                    songElement.innerHTML = `
                        <h3>${song.title}</h3>
                        <p><strong>Genre:</strong> ${song.genre}</p>
                        <p><strong>Sous-genre:</strong> ${song.subgenre}</p>
                        <p><strong>Partitions:</strong> ${scoresText || 'No scores'}</p>
                        <p><strong>Interprètes:</strong> ${song.interpreters.join(', ')}</p>
                        <p><strong>Compositeur:</strong> ${song.composers.join(', ')}</p>
                        <div style="display: flex; gap: 0.5rem;">
                            <a href="/song/${song.id}" style="padding: 0.5rem 1rem; background-color: var(--md-sys-color-secondary); color: var(--md-sys-color-on-secondary); text-decoration: none; border-radius: 6px; cursor: pointer;">View Details</a>
                            ${mediaLink}
                        </div>
                    `;
                    resultsContainer.appendChild(songElement);
                });

                document.querySelectorAll('.branch-title').forEach(el => {
                    const isActive = el.textContent.trim() === value;
                    el.style.color = isActive ? 'var(--md-secondary-light)' : 'var(--md-secondary)';
                });
            } else {
                resultsContainer.innerHTML = `<p style="color: #E1E1E6; text-align: center; padding: 40px 0;">No songs found in ${value} ${searchType}.</p>`;
            }
        })
        .catch(error => {
            console.error('Error fetching songs:', error);
            resultsContainer.innerHTML = '<p style="color: #CF6679; text-align: center; padding: 40px 0;">Error fetching results. Please try again later.</p>';
        });
}
