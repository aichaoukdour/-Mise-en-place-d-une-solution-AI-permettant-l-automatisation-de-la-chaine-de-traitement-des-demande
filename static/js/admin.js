document.addEventListener("DOMContentLoaded", function () {
  // Lucide icons
  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }

  // Show update modal
  const createUserButton = document.querySelector(".create-user-btn");
  if (createUserButton) {
    createUserButton.addEventListener("click", async function () {
      document.getElementById("updateUserModal")?.classList.remove("hidden");
    });
  }

  // Cancel update modal
  const cancelUpdateUser = document.getElementById("cancelUpdateUser");
  if (cancelUpdateUser) {
    cancelUpdateUser.addEventListener("click", () => {
      document.getElementById("updateUserModal")?.classList.add("hidden");
    });
  }

  // Update user modal with user data
  document.querySelectorAll(".update-user-btn").forEach((button) => {
    button.addEventListener("click", async function () {
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
        document.getElementById("createUserModal")?.classList.remove("hidden");
      } catch (err) {
        console.error("Erreur AJAX :", err);
      }
    });
  });

  // Cancel create user modal
  const cancelCreateUser = document.getElementById("cancelCreateUser");
  if (cancelCreateUser) {
    cancelCreateUser.addEventListener("click", () => {
      document.getElementById("createUserModal")?.classList.add("hidden");
    });
  }

  // Delete user modal
  document.querySelectorAll(".delete-btn").forEach((button) => {
    button.addEventListener("click", function () {
      const email = this.getAttribute("data-id");
      document.getElementById("deleteUserEmail").value = email;
      document.getElementById("deleteUserModal")?.classList.remove("hidden");
    });
  });

  // Cancel delete user modal
  const cancelDeleteUser = document.getElementById("cancelDeleteUser");
  if (cancelDeleteUser) {
    cancelDeleteUser.addEventListener("click", () => {
      document.getElementById("deleteUserModal")?.classList.add("hidden");
    });
  }

  // Conversation details
  document.querySelectorAll(".conv-detail").forEach((button) => {
    button.addEventListener("click", function () {
      const id = this.getAttribute("data-id");
      if (id) {
        window.location.href = `/Admin/get_conversation/${id}/`;
      }
    });
  });

  // Request details
  document.querySelectorAll(".details-btn").forEach((button) => {
    button.addEventListener("click", function () {
      const id = this.getAttribute("data-id");
      if (id) {
        window.location.href = `/Admin/infosuivi/${id}/`;
      }
    });
  });

  // Search and filter logic
  const searchInput = document.getElementById("search-input");
  const statusFilter = document.getElementById("filter-status");

  if (!searchInput) {
    console.error("Search input (#search-input) not found");
    return;
  }
  if (!statusFilter) {
    console.error("Status filter (#filter-status) not found");
  }

  function getRows() {
    const rows = document.querySelectorAll("#demandes-table-body tr");
    console.log("Rows found:", rows.length); // Debug row count
    return rows;
  }

  function applyFilters() {
    const rows = getRows();
    const statusValue = statusFilter?.value || "all";
    const searchValue = searchInput.value
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, ""); // Normalize accents

    console.log("Applying filters:", { statusValue, searchValue }); // Debug filters

    rows.forEach((row) => {
      const rowStatus = row.getAttribute("data-status") || "";
      const rowSearch =
        row
          .getAttribute("data-search")
          ?.toLowerCase()
          .normalize("NFD")
          .replace(/[\u0300-\u036f]/g, "") || "";

      const statusMatch = statusValue === "all" || rowStatus === statusValue;
      const searchMatch = rowSearch.includes(searchValue);

      console.log("Row data:", { rowSearch, searchValue, searchMatch }); // Debug each row

      row.style.display = statusMatch && searchMatch ? "" : "none";
    });
  }

  // Debounce for performance
  let timeout;
  searchInput.addEventListener("input", () => {
    console.log("Search input:", searchInput.value); // Debug input
    clearTimeout(timeout);
    timeout = setTimeout(applyFilters, 300);
  });

  if (statusFilter) {
    statusFilter.addEventListener("change", applyFilters);
  }

  // Initial filter application
  applyFilters();

  // Close modals when clicking outside
  window.addEventListener("click", function (event) {
    const deleteModal = document.getElementById("deleteUserModal");
    const createModal = document.getElementById("createUserModal");
    const updateModal = document.getElementById("updateUserModal");
    if (event.target === deleteModal) deleteModal?.classList.add("hidden");
    if (event.target === createModal) createModal?.classList.add("hidden");
    if (event.target === updateModal) updateModal?.classList.add("hidden");
  });
});