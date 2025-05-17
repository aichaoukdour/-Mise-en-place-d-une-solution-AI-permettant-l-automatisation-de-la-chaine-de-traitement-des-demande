document.addEventListener("DOMContentLoaded", function () {
    // Detail button navigation
    document.querySelectorAll(".details-btn").forEach(button => {
        button.addEventListener("click", function () {
            const id = this.getAttribute("data-id");
            if (id) window.location.href = `/Admin/infosuivi/${id}/`;
        });
    });

    // Conversation button navigation
    document.querySelectorAll(".conv-detail").forEach(button => {
        button.addEventListener("click", function () {
            const id = this.getAttribute("data-id");
            if (id) window.location.href = `/Admin/get_conversation/${id}/`;
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