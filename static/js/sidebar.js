
// Fonction globale accessible directement depuis l'attribut onclick
function toggleSidebar() {
    console.log("Fonction toggleSidebar appelée");
    const sidebar = document.getElementById("sidebar");
    const mainContent = document.getElementById("mainContent");
    
    // Toggle la classe
    sidebar.classList.toggle("collapsed");
    
    // Ajuster le contenu principal
    if (sidebar.classList.contains("collapsed")) {
        mainContent.style.marginLeft = "4rem";
    } else {
        mainContent.style.marginLeft = "16rem";
    }
}

// Chargement initial
document.addEventListener("DOMContentLoaded", function() {
    // Code d'initialisation si nécessaire
    console.log("DOM chargé, sidebar.js initialisé");
});