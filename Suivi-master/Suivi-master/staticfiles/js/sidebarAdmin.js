document.addEventListener("DOMContentLoaded", function () {
        lucide.createIcons();

        const sidebar = document.getElementById('sidebar');
        const toggleBtn = document.getElementById('toggleSidebar');
        const mainContent = document.getElementById('mainContent');
        const profileBtn = document.getElementById('profileBtn');
        const dropdown = document.getElementById('dropdown');

        // Sidebar toggle
        toggleBtn.addEventListener('click', function () {
            sidebar.classList.toggle('sidebar-collapsed');
            if (sidebar.classList.contains('sidebar-collapsed')) {
                mainContent.style.marginLeft = "80px";
                mainContent.style.width = "calc(100% - 80px)";
            } else {
                mainContent.style.marginLeft = "270px";
                mainContent.style.width = "calc(100% - 270px)";
            }
        });

        // Highlight active menu
        const currentPath = window.location.pathname;
        document.querySelectorAll(".menu-item").forEach(link => {
            if (link.getAttribute("href") === currentPath) {
                link.classList.add("active-menu");
            }
        });

        // Profile dropdown toggle
        profileBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            dropdown.classList.toggle('hidden');
        });

        // Prevent dropdown from closing when clicking inside it
        dropdown.addEventListener('click', function(e) {
            e.stopPropagation();
        });

        // Close dropdown when clicking elsewhere
        document.addEventListener('click', function () {
            if (!dropdown.classList.contains('hidden')) {
                dropdown.classList.add('hidden');
            }
        });
    });