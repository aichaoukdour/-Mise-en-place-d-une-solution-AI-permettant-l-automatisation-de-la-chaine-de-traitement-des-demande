
    document.addEventListener("DOMContentLoaded", function() {
        lucide.createIcons();
        
        // Détection de la page active basée sur l'URL
        const currentPath = window.location.pathname;
        
        // Retirer la classe active-menu de tous les liens
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active-menu');
        });
        
        // Ajouter la classe active-menu selon l'URL actuelle
        if (currentPath.includes('accueil')) {
            document.getElementById('nav-accueil').classList.add('active-menu');
        } else if (currentPath.includes('suivi')) {
            document.getElementById('nav-rapports').classList.add('active-menu');
        } else if (currentPath.includes('chat')) {
            document.getElementById('nav-chatbot').classList.add('active-menu');
        }
        
        // Pour la démonstration, vous pouvez également ajouter ces écouteurs d'événements
        // pour changer manuellement la page active en cliquant sur les liens
        document.getElementById('nav-accueil').addEventListener('click', function(e) {
            activateLink('nav-accueil');
        });
        
        document.getElementById('nav-rapports').addEventListener('click', function(e) {
            activateLink('nav-rapports');
        });
        
        document.getElementById('nav-chatbot').addEventListener('click', function(e) {
            activateLink('nav-chatbot');
        });
    });
    
    function activateLink(linkId) {
        // Retirer la classe active de tous les liens
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active-menu');
        });
        
        // Ajouter la classe active au lien cliqué
        document.getElementById(linkId).classList.add('active-menu');
    }

    function toggleDropdown() {
        const dropdown = document.getElementById('dropdown');
        dropdown.classList.toggle('hidden');
    }

    document.addEventListener('click', function(event) {
        const dropdown = document.getElementById('dropdown');
        const profileBtn = document.getElementById('profileBtn');
        
        if (!dropdown.contains(event.target) && !profileBtn.contains(event.target)) {
            dropdown.classList.add('hidden');
        }
    });