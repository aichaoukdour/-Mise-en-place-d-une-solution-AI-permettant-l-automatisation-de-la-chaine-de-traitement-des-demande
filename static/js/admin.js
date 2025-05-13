
document.addEventListener("DOMContentLoaded", function () {
  // Lucide icons
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }

  // Update user modal
  document.querySelectorAll('.update-user-btn').forEach(button => {
    button.addEventListener('click', async function () {
      const user_id = this.getAttribute("data-id");
      try {
        const response = await fetch(`/Admin/Update/${user_id}/`);
        const user = await response.json();
        if (user.error) {
          alert("Erreur lors du chargement de l'utilisateur : " + user.error);
          return;
        }
        document.getElementById("UpdateUserEmail").value = user.user_id;
        document.querySelector("input[name='last_name_u']").value = user.last_name_user;
        document.querySelector("input[name='first_name_u']").value = user.name_user;
        document.querySelector("input[name='email_u']").value = user.email_user;
        document.querySelector("select[name='role_agt']").value = user.user_role;
        document.getElementById('createUserModal').classList.remove('hidden');
      } catch (err) {
        console.error("Erreur AJAX :", err);
      }
    });
  });

  document.getElementById('cancelCreateUser').addEventListener('click', () => {
    document.getElementById('createUserModal').classList.add('hidden');
  });

  // Delete user modal
  document.querySelectorAll(".delete-btn").forEach(button => {
    button.addEventListener("click", function () {
      const email = this.getAttribute("data-id");
      document.getElementById("deleteUserEmail").value = email;
      document.getElementById("deleteUserModal").classList.remove("hidden");
    });
  });
  document.getElementById("cancelDeleteUser").addEventListener("click", () => {
    document.getElementById("deleteUserModal").classList.add("hidden");
  });

  // Conversation details
  document.querySelectorAll(".conv-detail").forEach(button => {
    button.addEventListener("click", function () {
      const id = this.getAttribute("data-id");
      if (id) {
        window.location.href = `/Admin/get_conversation/${id}/`;
      }
    });
  });

  // Request details
  document.querySelectorAll(".details-btn").forEach(button => {
    button.addEventListener("click", function () {
      const id = this.getAttribute("data-id");
      if (id) {
        window.location.href = `/Admin/infosuivi/${id}/`;
      }
    });
  });

  // Filter demandes by status
  const statusFilter = document.getElementById('filter-status');
  const rows = document.querySelectorAll('#demandes-table-body tr');
  function applyFilters() {
    const statusValue = statusFilter.value;
    rows.forEach(row => {
      const rowStatus = row.getAttribute('data-status');
      row.style.display = (statusValue === 'all' || rowStatus === statusValue) ? '' : 'none';
    });
  }
  statusFilter.addEventListener('change', applyFilters);

  // Close modals when clicking outside
  window.addEventListener('click', function(event) {
    const deleteModal = document.getElementById('deleteUserModal');
    const createModal = document.getElementById('createUserModal');
    if (event.target === deleteModal) {
      deleteModal.classList.add('hidden');
    }
    if (event.target === createModal) {
      createModal.classList.add('hidden');
    }
  });
});
