// Dil değiştirme fonksiyonu
function toggleDropdown() {
    const dropdown = document.getElementById("languageDropdown");
    dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
}

/// Profil butonuna ve dropdown menüsüne erişim
const profileBtn = document.querySelector('.profile-btn');
const dropdown = document.querySelector('.language-dropdown');

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
