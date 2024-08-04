document.addEventListener("DOMContentLoaded", function () {
    console.log("Document ready");

    let typingTimer;
    const doneTypingInterval = 100; // milliseconds

    const searchInput = document.getElementById("search-input");
    const searchResults = document.getElementById("search-results");

    searchInput.addEventListener("click", function () {
        console.log("Search input clicked");
        performSearch();
    });

    searchInput.addEventListener("input", function () {
        console.log("Input detected:", this.value);
        clearTimeout(typingTimer);
        if (this.value) {
            typingTimer = setTimeout(performSearch, doneTypingInterval);
        } else {
            searchResults.style.display = "none";
        }
    });

    function performSearch() {
        const query = searchInput.value.toLowerCase().trim();
        console.log("Performing search for:", query);
        fetch(`${window.indexUrls.searchServices}?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                console.log("Received data:", data);
                displayResults(data, query);
            })
            .catch(error => {
                console.error("Fetch error:", error);
            });
    }

    function displayResults(data, query) {
        console.log("Displaying results for query:", query);
        let resultsHtml = "";
        let hasResults = false;

        for (const [category, services] of Object.entries(data.filtered_services)) {
            console.log("Processing category:", category);
            const categoryName = category.replace(/_/g, " ");
            const categoryMatches = categoryName.toLowerCase().includes(query.toLowerCase());
            console.log("Category matches:", categoryMatches);
            const filteredServices = services.filter((service) =>
                service.toLowerCase().includes(query.toLowerCase())
            );
            console.log("Filtered services:", filteredServices);

            if (categoryMatches || filteredServices.length > 0 || !query) {
                hasResults = true;
                const categoryUrl = window.indexUrls.categoryUrls[category] || "#";
                resultsHtml += `<div class="index-search-filter-result category" onclick="window.location.href='${categoryUrl}'">`;
                resultsHtml += `<span>${categoryName.charAt(0).toUpperCase() + categoryName.slice(1)}</span>`;
                resultsHtml += "</div>";

                filteredServices.forEach((service) => {
                    resultsHtml += `<div class="index-search-filter-result">`;
                    resultsHtml += `<span>${service}</span>`;
                    resultsHtml += "</div>";
                });
            }
        }

        if (!hasResults) {
            resultsHtml = '<div class="index-search-filter-result no-results">No matches found</div>';
        }
        console.log("Results HTML:", resultsHtml);
        searchResults.innerHTML = resultsHtml;
        searchResults.style.display = "block";
    }

    // Close search results when clicking outside
    document.addEventListener("click", function (event) {
        if (!event.target.closest(".index-bookiao-search-container")) {
            searchResults.style.display = "none";
        }
    });

    console.log("Search functionality initialized");
});