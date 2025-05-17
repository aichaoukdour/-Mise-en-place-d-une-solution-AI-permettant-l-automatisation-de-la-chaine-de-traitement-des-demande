
document.addEventListener("DOMContentLoaded", function () {
  // Lucide icons
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
  const button = document.querySelector(".create-user-btn");
  button.addEventListener('click', async function () {
    document.getElementById('updateUserModal').classList.remove('hidden');
  });
  document.getElementById('cancelUpdateUser').addEventListener('click', () => {
    document.getElementById('updateUserModal').classList.add('hidden');
  });

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
    const updateModal = document.getElementById('updateUserModal');
    if (event.target === deleteModal) {
      deleteModal.classList.add('hidden');
    }
    if (event.target === createModal) {
      createModal.classList.add('hidden');
    }
    if (event.target === updateModal) {
      updateModal.classList.add('hidden');
    }
  });

  document.addEventListener("DOMContentLoaded", function () {
    // Detail button navigation
    document.querySelectorAll(".details-btn").forEach(button => {
        button.addEventListener("click", function () {
            const id = this.getAttribute("data-id");
            if (id) window.location.href = `Admin/infosuivi/${id}/`;
        });
    });

    // Conversation button navigation
    document.querySelectorAll(".conv-detail").forEach(button => {
        button.addEventListener("click", function () {
            const id = this.getAttribute("data-id");
            if (id) window.location.href = `Admin/get_conversation/${id}/`;
        });
    });

    // Filtering logic
    const statusFilter = document.getElementById('filter-status');
    const periodFilter = document.getElementById('filter-period');
    const searchInput = document.getElementById('search-input');
    const rows = document.querySelectorAll('#demandes-table-body tr');

    function applyFilters() {
        const statusValue = statusFilter.value;
        const periodValue = periodFilter.value;
        const searchValue = searchInput.value.toLowerCase();
        const now = new Date();

        rows.forEach(row => {
            const rowStatus = row.getAttribute('data-status');
            const rowDate = new Date(row.getAttribute('data-date'));
            const rowSearch = row.getAttribute('data-search').toLowerCase();

            // Status filter
            const statusMatch = statusValue === 'all' || rowStatus === statusValue;

            // Period filter
            let periodMatch = true;
            if (periodValue !== 'all') {
                const timeDiff = now - rowDate;
                const daysDiff = timeDiff / (1000 * 60 * 60 * 24);

                if (periodValue === 'week' && daysDiff > 7) periodMatch = false;
                if (periodValue === 'month' && daysDiff > 30) periodMatch = false;
                if (periodValue === 'year' && daysDiff > 365) periodMatch = false;
            }

            // Search filter
            const searchMatch = rowSearch.includes(searchValue);

            // Show/hide row based on filters
            row.style.display = (statusMatch && periodMatch && searchMatch) ? '' : 'none';
        });
    }

    // Attach filter event listeners
    statusFilter.addEventListener('change', applyFilters);
    periodFilter.addEventListener('change', applyFilters);
    searchInput.addEventListener('input', applyFilters);
});

});