// Dil değiştirme fonksiyonu
function toggleDropdown() {
    const dropdown = document.getElementById("dropdown");
    dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
}

// Sayfa dışına tıklanınca dropdown menüsünü kapat
document.addEventListener('click', function (event) {
    const isClickInside = document.querySelector('.profile-container').contains(event.target);
    if (!isClickInside) {
        const dropdown = document.getElementById('dropdown');
        dropdown.classList.remove('active');
    }
});
