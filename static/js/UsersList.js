
document.addEventListener("DOMContentLoaded", function() {
    // Initialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
  
    // Role Filter functionality
    const roleFilter = document.getElementById('roleFilter');
    const usersTable = document.getElementById('usersTable');
    const userRows = usersTable.querySelectorAll('tbody tr');
    const emptyStateTemplate = document.getElementById('emptyState');
    
    roleFilter.addEventListener('change', function() {
        const selectedRole = this.value;
        let visibleRows = 0;
        
        // Remove any existing empty state
        const existingEmptyState = usersTable.querySelector('tbody tr.empty-state');
        if (existingEmptyState) {
            existingEmptyState.remove();
        }
        
        userRows.forEach(row => {
            const userRole = row.getAttribute('data-role');
            if (selectedRole === 'all' || userRole === selectedRole) {
                row.classList.remove('hidden');
                visibleRows++;
            } else {
                row.classList.add('hidden');
            }
        });
        
        // Show empty state if no rows are visible
        if (visibleRows === 0) {
            const emptyStateClone = emptyStateTemplate.content.cloneNode(true);
            const emptyRow = emptyStateClone.querySelector('tr');
            emptyRow.classList.add('empty-state');
            usersTable.querySelector('tbody').appendChild(emptyRow);
            
            // Initialize Lucide icons in the empty state
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        }
    });

    // Update User Modal
    document.querySelectorAll('.update-user-btn').forEach(button => {
        button.addEventListener('click', async function () {
            const user_id = this.getAttribute("data-id");
            try {
                const response = await fetch(`/Admin/Update/${user_id}/`);
                const user = await response.json();
                if (user.error) {
                    showToast("Erreur lors du chargement de l'utilisateur : " + user.error, "error");
                    return;
                }
                document.getElementById("UpdateUserEmail").value = user.user_id;
                document.querySelector("input[name='last_name_u']").value = user.last_name_user;
                document.querySelector("input[name='first_name_u']").value = user.name_user;
                document.querySelector("input[name='email_u']").value = user.email_user;
                document.querySelector("select[name='role_agt_u']").value = user.user_role;
                document.getElementById('UpdateUserModal').classList.remove('hidden');
            } catch (err) {
                console.error("Erreur AJAX :", err);
                showToast("Une erreur s'est produite", "error");
            }
        });
    });
    
    document.getElementById('cancelUpdateUser').addEventListener('click', () => {
        document.getElementById('UpdateUserModal').classList.add('hidden');
    });
    
    document.getElementById('closeUpdateModal')?.addEventListener('click', () => {
        document.getElementById('UpdateUserModal').classList.add('hidden');
    });

    // Delete User Modal
    document.querySelectorAll(".delete-btn").forEach(button => {
        button.addEventListener("click", function () {
            const email = this.getAttribute("data-id");
            document.getElementById("deleteUserEmail").value = email;
            document.getElementById("deleteUserModal").classList.remove('hidden');
        });
    });
    
    document.getElementById('cancelDeleteUser').addEventListener('click', () => {
        document.getElementById('deleteUserModal').classList.add('hidden');
    });

    // Create User Modal
    document.getElementById("createUserBtn").addEventListener("click", function () {
        document.getElementById("createUserModal").classList.remove('hidden');
    });
    
    document.getElementById("cancelCreateUser").addEventListener('click', function () {
        document.getElementById("createUserModal").classList.add('hidden');
    });
    
    document.getElementById('closeCreateModal')?.addEventListener('click', () => {
        document.getElementById('createUserModal').classList.add('hidden');
    });
    
    // Custom Toast function
    function showToast(message, type = 'info') {
        // Create toast container if it doesn't exist
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'fixed bottom-4 right-4 z-50 flex flex-col gap-2';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast
        const toast = document.createElement('div');
        toast.className = `flex items-center p-4 mb-4 rounded-lg shadow-lg ${
            type === 'error' ? 'bg-red-50 text-red-800' : 
            type === 'success' ? 'bg-green-50 text-green-800' : 
            'bg-blue-50 text-blue-800'
        }`;
        
        const icon = document.createElement('div');
        icon.className = 'mr-2';
        icon.innerHTML = `<i data-lucide="${
            type === 'error' ? 'alert-circle' : 
            type === 'success' ? 'check-circle' : 
            'info'
        }" class="h-5 w-5"></i>`;
        
        const text = document.createElement('div');
        text.textContent = message;
        text.className = 'text-sm font-medium';
        
        toast.appendChild(icon);
        toast.appendChild(text);
        toastContainer.appendChild(toast);
        
        // Initialize Lucide icons in the toast
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
        
        // Remove toast after 3 seconds
        setTimeout(() => {
            toast.classList.add('opacity-0', 'transition-opacity', 'duration-300');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 3000);
    }
});