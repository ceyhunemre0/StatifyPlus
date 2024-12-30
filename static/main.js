function toggleDropdown() {
    const dropdown = document.getElementById("dropdown");
    dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
}

/// Profil butonuna ve dropdown menüsüne erişim
const profileBtn = document.querySelector('.profile-btn');
const dropdown = document.querySelector('.dropdown');

// Dropdown menüyü açma ve kapama
profileBtn.addEventListener('click', (e) => {
    e.stopPropagation(); // Tıklama olayının yayılmasını durdur
    dropdown.classList.toggle('active'); // Aktif durumunu değiştir
});

// Sayfa üzerinde başka bir yere tıklandığında dropdown'u kapatma
document.addEventListener('click', () => {
    if (dropdown.classList.contains('active')) {
        dropdown.classList.remove('active'); // Dropdown'u kapat
    }
});

let currentIndex = 0;

function loadPlaylistTracks() {
    fetch('/api/playlist_tracks')
        .then(response => response.json())
        .then(data => {
            const trackGrid = document.getElementById('track-grid');
            trackGrid.innerHTML = '';

            data.forEach(track => {
                const trackCard = document.createElement('div');
                trackCard.className = 'track-card';
                trackCard.innerHTML = `
                    <img src="${track.imageUrl}" alt="${track.trackName}">
                    <h3>${track.trackName}</h3>
                    <p>${track.artist}</p>
                    <p>${track.album}</p>
                `;
                trackCard.addEventListener('click', () => {
                    window.open(track.spotifyUrl, '_blank');
                });

                trackGrid.appendChild(trackCard);
            });

            startCarousel();
        })
        .catch(error => console.error('Error fetching playlist tracks:', error));
}

function startCarousel() {
    const trackGrid = document.getElementById('track-grid');
    const trackCards = document.querySelectorAll('.track-card');
    const totalTracks = trackCards.length;
    const visibleTracks = 4;

    setInterval(() => {
        currentIndex += visibleTracks;
        if (currentIndex >= totalTracks) {
            currentIndex = 0;
        }
        const offset = -currentIndex * (trackCards[0].offsetWidth + 20); // 20 is the margin
        trackCards.forEach(card => {
            card.style.transform = `translateX(${offset}px)`;
        });
    }, 5000); // 5 saniyede bir kaydır
}

document.addEventListener('DOMContentLoaded', loadPlaylistTracks);

document.getElementById('random-track-btn').addEventListener('click', () => {
    fetch('/api/random_track')
        .then(response => response.json())
        .then(track => {
            console.log('Random track started:', track);
        })
        .catch(error => console.error('Error fetching random track:', error));
});
