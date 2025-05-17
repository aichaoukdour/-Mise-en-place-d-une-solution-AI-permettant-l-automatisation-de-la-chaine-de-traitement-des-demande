// Attendre que le document soit complètement chargé
document.addEventListener('DOMContentLoaded', function() {
    // Générer un mot de passe fort et l'afficher dans le champ de mot de passe
    generateStrongPassword();


    
});

// Fonction pour générer un mot de passe fort
function generateStrongPassword() {
    const length = 16;
    const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+';
    let password = '';

    // S'assurer qu'il y a au moins une lettre majuscule, une minuscule, un chiffre et un caractère spécial
    password += charset.charAt(Math.floor(Math.random() * 26)); // minuscule
    password += charset.charAt(26 + Math.floor(Math.random() * 26)); // majuscule
    password += charset.charAt(52 + Math.floor(Math.random() * 10)); // chiffre
    password += charset.charAt(62 + Math.floor(Math.random() * (charset.length - 62))); // caractère spécial

    // Compléter le reste du mot de passe
    for (let i = 4; i < length; i++) {
        password += charset.charAt(Math.floor(Math.random() * charset.length));
    }

    // Mélanger les caractères du mot de passe
    password = password.split('').sort(() => 0.5 - Math.random()).join('');

    // Afficher le mot de passe dans le champ
    document.getElementById('mdp').value = password;
}

// Fonction pour créer et télécharger le PDF avec les informations de l'utilisateur

function createUserPDF() {
    // Récupérer les valeurs du formulaire
    const firstName = document.getElementById('first_name').value;
    const lastName = document.getElementById('last_name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const role = document.getElementById('role').value;

    // Ajouter d'abord le script jsPDF
    const jsPDFScript = document.createElement('script');
    jsPDFScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
    document.head.appendChild(jsPDFScript);

    jsPDFScript.onload = function() {
        // Après le chargement de jsPDF, charger le plugin autoTable
        const autoTableScript = document.createElement('script');
        autoTableScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.25/jspdf.plugin.autotable.min.js';
        document.head.appendChild(autoTableScript);

        autoTableScript.onload = function() {
            // Les deux scripts sont chargés et prêts à être utilisés
            // Utiliser un délai pour s'assurer que les scripts sont complètement initialisés
            setTimeout(function() {
                generatePDF();
            }, 100);
        };

        autoTableScript.onerror = function() {
            console.error("Erreur lors du chargement du plugin autoTable");
            alert("Impossible de charger les bibliothèques nécessaires pour le PDF");
        };
    };

    jsPDFScript.onerror = function() {
        console.error("Erreur lors du chargement de jsPDF");
        alert("Impossible de charger les bibliothèques nécessaires pour le PDF");
    };

    function generatePDF() {
        try {
            // Créer le PDF
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();

            // Vérifier si autoTable est disponible
            if (typeof doc.autoTable !== 'function') {
                console.error("Le plugin autoTable n'est pas disponible");
                alert("Une erreur est survenue lors de la création du PDF. Le plugin autoTable n'est pas disponible.");
                return;
            }

            // Ajouter un titre
            doc.setFontSize(18);
            doc.text('Informations Utilisateur', 105, 20, { align: 'center' });

            // Utiliser le chemin absolu vers le logo statique Django
            const logoPath = document.getElementById('logo-path').getAttribute('data-src');

            // Précharger l'image du logo
            const logoImg = new Image();
            logoImg.crossOrigin = "Anonymous"; // Pour éviter les problèmes CORS
            logoImg.src = logoPath; // Chemin vers le logo statique Django

            logoImg.onload = function() {
                try {
                    // Ajouter le logo
                    const imgWidth = 25;
                    const imgHeight = 25;
                    doc.addImage(logoImg, 'PNG', 105 - (imgWidth/2), 35 - (imgHeight/2), imgWidth, imgHeight);
                } catch (error) {
                    console.error("Erreur lors de l'ajout de l'image:", error);
                    // Fallback avec initiales
                    doc.setFillColor(128, 0, 128);
                    doc.circle(105, 40, 10, 'F');
                    doc.setTextColor(255, 255, 255);
                    doc.setFontSize(14);
                    doc.text(`${firstName.charAt(0)}${lastName.charAt(0)}`, 105, 43, { align: 'center' });
                }

                // Réinitialiser la couleur du texte
                doc.setTextColor(0, 0, 0);
                doc.setFontSize(12);

                // Section des informations personnelles
                doc.text('Informations Personnelles', 20, 60);
                doc.setDrawColor(128, 0, 128);
                doc.line(20, 62, 190, 62);

                // Tableau des informations personnelles
                doc.autoTable({
                    startY: 65,
                    head: [['Nom', 'Prénom', 'Email', 'Rôle']],
                    body: [[lastName, firstName, email, role]],
                    theme: 'grid',
                    headStyles: { fillColor: [128, 0, 128] }
                });

                // Récupérer la position finale du premier tableau
                const finalY = doc.lastAutoTable.finalY;

                // Section des informations d'authentification
                doc.text('Informations d\'Authentification', 20, finalY + 15);
                doc.setDrawColor(128, 0, 128);
                doc.line(20, finalY + 17, 190, finalY + 17);

                // Tableau des informations d'authentification
                doc.autoTable({
                    startY: finalY + 20,
                    head: [['Email', 'Mot de Passe']],
                    body: [[email, password]],
                    theme: 'grid',
                    headStyles: { fillColor: [128, 0, 128] }
                });

                // Ajouter la date et l'heure de création
                const now = new Date();
                const dateString = now.toLocaleDateString('fr-FR');
                const timeString = now.toLocaleTimeString('fr-FR');
                doc.setFontSize(10);
                doc.text(`Document créé le ${dateString} à ${timeString}`, 105, 280, { align: 'center' });

                // Télécharger le PDF
                doc.save(`utilisateur_${lastName}_${firstName}.pdf`);
            };

            logoImg.onerror = function() {
                console.error("Erreur de chargement du logo");

                // Continuer sans logo
                doc.setFillColor(128, 0, 128);
                doc.circle(105, 40, 10, 'F');
                doc.setTextColor(255, 255, 255);
                doc.setFontSize(14);
                doc.text(`${firstName.charAt(0)}${lastName.charAt(0)}`, 105, 43, { align: 'center' });

                // Réinitialiser la couleur du texte
                doc.setTextColor(0, 0, 0);
                doc.setFontSize(12);

                // Section des informations personnelles
                doc.text('Informations Personnelles', 20, 60);
                doc.setDrawColor(128, 0, 128);
                doc.line(20, 62, 190, 62);

                // Tableau des informations personnelles
                doc.autoTable({
                    startY: 65,
                    head: [['Nom', 'Prénom', 'Email', 'Rôle']],
                    body: [[lastName, firstName, email, role]],
                    theme: 'grid',
                    headStyles: { fillColor: [128, 0, 128] }
                });

                // Récupérer la position finale du premier tableau
                const finalY = doc.lastAutoTable.finalY;

                // Section des informations d'authentification
                doc.text('Informations d\'Authentification', 20, finalY + 15);
                doc.setDrawColor(128, 0, 128);
                doc.line(20, finalY + 17, 190, finalY + 17);

                // Tableau des informations d'authentification
                doc.autoTable({
                    startY: finalY + 20,
                    head: [['Email', 'Mot de Passe']],
                    body: [[email, password]],
                    theme: 'grid',
                    headStyles: { fillColor: [128, 0, 128] }
                });

                // Ajouter la date et l'heure de création
                const now = new Date();
                const dateString = now.toLocaleDateString('fr-FR');
                const timeString = now.toLocaleTimeString('fr-FR');
                doc.setFontSize(10);
                doc.text(`Document créé le ${dateString} à ${timeString}`, 105, 280, { align: 'center' });

                // Télécharger le PDF
                doc.save(`${lastName}_${firstName}.pdf`);
            };

            // Définir un timeout au cas où l'image ne charge pas
            setTimeout(function() {
                if (!logoImg.complete) {
                    logoImg.onerror();
                }
            }, 1000);
        } catch (error) {
            console.error("Erreur lors de la création du PDF:", error);
            alert("Une erreur est survenue lors de la création du PDF. Veuillez réessayer.");
        }
    }
        
}
    