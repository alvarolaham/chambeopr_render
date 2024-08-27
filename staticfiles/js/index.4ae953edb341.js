document.addEventListener("DOMContentLoaded", function () {
    // Hide loading indicator
    const loadingIndicator = document.getElementById('loading-indicator');
    loadingIndicator.style.display = 'none';

    // Cache DOM queries
    const subServicesContainer = document.querySelector('.index-sub-service-grid-container');
    const serviceItems = document.querySelectorAll('.index-service-item');

    // Function to split the name into lines based on the 15-character rule
    function splitIntoLines(name, maxLength) {
        let lines = [];
        let words = name.split(" ");
        let currentLine = "";

        words.forEach(word => {
            if ((currentLine + " " + word).trim().length <= maxLength) {
                currentLine += (currentLine ? " " : "") + word;
            } else {
                lines.push(currentLine);
                currentLine = word;
            }
        });
        lines.push(currentLine); // Add the last line
        return lines.join("<br>");
    }

    // Function to display sub-services based on selected category
    function displaySubServices(category) {
        const services = servicesData[category];

        if (services && Array.isArray(services)) {
            let servicesHtml = services.map(service => {
                // Format the name with the custom splitting logic
                let formattedName = splitIntoLines(service.name, 15);

                return `
                    <div class="index-sub-service-item no-underline">
                        <div class="index-sub-service-icon">
                            <span class="material-symbols-outlined" aria-hidden="true">${service.icon}</span>
                        </div>
                        <span class="index-sub-services-text">${formattedName}</span>
                    </div>
                `;
            }).join('');

            subServicesContainer.innerHTML = servicesHtml;
            subServicesContainer.style.display = "flex";
            subServicesContainer.style.flexWrap = "nowrap";
            subServicesContainer.style.overflowX = "auto";
        } else {
            subServicesContainer.innerHTML = `<div>No services available for this category.</div>`;
            subServicesContainer.style.display = "block";
        }

        // Add active class to the clicked service item
        serviceItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('data-category') === category) {
                item.classList.add('active');
            }
        });
    }

    // Handle clicking on service category icons
    serviceItems.forEach(function (item) {
        item.addEventListener('click', function (event) {
            event.preventDefault();
            const category = this.getAttribute('data-category');
            displaySubServices(category);
        });
    });

    // Default display for home services on page load
    displaySubServices('home_services');
});
