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

// --- Upload modal and form handling ---
document.addEventListener('DOMContentLoaded', function() {
    const floating = document.getElementById('floating-add');
    const modal = document.getElementById('upload-modal');
    const uploadForm = document.getElementById('upload-form');
    const cancelBtn = document.getElementById('upload-cancel');
    const feedback = document.getElementById('upload-feedback');

    function openModal() {
        modal.style.display = 'flex';
        modal.setAttribute('aria-hidden', 'false');
    }

    function closeModal() {
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
        feedback.textContent = '';
        if (uploadForm) uploadForm.reset();
    }

    if (floating && modal) {
        floating.addEventListener('click', openModal);
    }

    if (cancelBtn && modal) {
        cancelBtn.addEventListener('click', closeModal);
    }

    // close button (×)
    const closeBtn = document.getElementById('upload-close');
    if (closeBtn) closeBtn.addEventListener('click', closeModal);

    // close on backdrop click
    if (modal) {
        modal.addEventListener('click', (ev) => {
            if (ev.target === modal) closeModal();
        });
    }

    // close on Escape
    window.addEventListener('keydown', (ev) => {
        if (ev.key === 'Escape' && modal && modal.style.display === 'flex') {
            closeModal();
        }
    });

    const allowedExt = ['.jpg', '.jpeg', '.png', '.gif', '.webp'];

    function clientAllowed(filename) {
        if (!filename) return false;
        const lower = filename.toLowerCase();
        return allowedExt.some(ext => lower.endsWith(ext));
    }

    if (uploadForm) {
        uploadForm.addEventListener('submit', (ev) => {
            ev.preventDefault();
            feedback.textContent = '';

            const title = document.getElementById('upload-title').value.trim();
            const composer = document.getElementById('upload-composer').value.trim();
            const fileInput = document.getElementById('upload-file');

            if (!title) { feedback.textContent = 'Title is required'; return; }
            if (!composer) { feedback.textContent = 'Composer is required'; return; }
            if (!fileInput || !fileInput.files || fileInput.files.length === 0) { feedback.textContent = 'Please select a file'; return; }

            const file = fileInput.files[0];
            if (!clientAllowed(file.name)) { feedback.textContent = 'Invalid file type'; return; }

            const formData = new FormData();
            formData.append('title', title);
            formData.append('composer', composer);
            formData.append('score_file', file);

            feedback.textContent = 'Uploading...';

            fetch('/upload-score', {
                method: 'POST',
                body: formData
            }).then(r => r.json().then(body => ({status: r.status, body})))
            .then(({status, body}) => {
                if (status >= 200 && status < 300) {
                    feedback.textContent = 'Upload successful';
                    uploadForm.reset();
                    setTimeout(() => {
                        modal.style.display = 'none';
                        modal.setAttribute('aria-hidden', 'true');
                        feedback.textContent = '';
                        // refresh list
                        performSearch(document.getElementById('search-input').value || '');
                    }, 900);
                } else {
                    feedback.textContent = body && body.error ? body.error : 'Upload failed';
                }
            }).catch(err => {
                console.error(err);
                feedback.textContent = 'Upload failed';
            });
        });
    }
});
