window.onload = function () {
    // Check if running in Capacitor
    const isCapacitor = window.Capacitor !== undefined;

    // Cache DOM queries
    const loadingIndicator = document.getElementById('loading-indicator');
    const subServicesContainer = document.querySelector('.index-sub-service-grid-container');
    const serviceItemsContainer = document.querySelector('.index-service-grid-container'); // Service container
    const serviceItems = document.querySelectorAll('.index-service-item');
    const serviceProfiles = document.querySelectorAll('.service-profile-body');
    const serviceProfilesContainer = document.querySelector('#service-profiles-container');
    const contentContainer = document.querySelector('.content-container');

    // Hide content initially
    if (contentContainer) {
        contentContainer.style.opacity = '0';
    }

    // Function to show content
    function showContent() {
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }
        if (contentContainer) {
            contentContainer.style.opacity = '1';
        }
    }

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

    // Function to scroll item into view and center it if possible
    function scrollItemIntoView(container, item) {
        const containerRect = container.getBoundingClientRect();
        const itemRect = item.getBoundingClientRect();
        const containerWidth = containerRect.width;
        const itemWidth = itemRect.width;
        const containerScrollWidth = container.scrollWidth;

        // Calculate the ideal scroll position to center the item
        const idealScrollLeft = item.offsetLeft - (containerWidth / 2) + (itemWidth / 2);

        // Clamp the scroll position to avoid empty space at the start or end
        const maxScrollLeft = containerScrollWidth - containerWidth;
        const clampedScrollLeft = Math.max(0, Math.min(idealScrollLeft, maxScrollLeft));

        container.scrollTo({
            left: clampedScrollLeft,
            behavior: 'smooth'
        });
    }

    // Function to display sub-services based on selected category
    function displaySubServices(category) {
        const services = servicesData[category];
        if (services && Array.isArray(services)) {
            let servicesHtml = services.map(service => {
                // Format the name with the custom splitting logic
                let formattedName = splitIntoLines(service.name, 15);
                return `
                    <div class="index-sub-service-item no-underline" data-service="${service.name.toLowerCase()}">
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

            // Handle click events for both mobile and desktop
            const subServiceItems = subServicesContainer.querySelectorAll('.index-sub-service-item');

            subServiceItems.forEach(item => {
                item.addEventListener('click', (event) => {
                    event.preventDefault();
                    const service = item.getAttribute('data-service');
                    filterServiceProfiles(service);
                    subServiceItems.forEach(i => i.classList.remove('active'));
                    item.classList.add('active');
                    scrollItemIntoView(subServicesContainer, item);
                });
            });

            // Trigger click on the first sub-service item
            if (subServiceItems.length > 0) {
                subServiceItems[0].click();
            }
        } else {
            subServicesContainer.innerHTML = `<div>No services available for this category.</div>`;
            subServicesContainer.style.display = "block";
            filterServiceProfiles(null); // Show all profiles if no sub-services
        }

        // Highlight the clicked category
        serviceItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('data-category') === category) {
                item.classList.add('active');
            }
        });
    }

    // Function to filter service profiles based on clicked sub-service
    function filterServiceProfiles(service) {
        let visibleProfiles = 0;

        serviceProfiles.forEach(profile => {
            const services = profile.getAttribute('data-services').split(',');
            if (service === null || services.includes(service)) {
                profile.style.display = 'block';
                visibleProfiles++;
            } else {
                profile.style.display = 'none';
            }
        });

        const noResultsElement = serviceProfilesContainer.querySelector('[data-service="no-results"]');
        if (visibleProfiles === 0) {
            if (!noResultsElement) {
                const noResultsHtml = `
                    <div class="no-results" data-service="no-results">
                        <span class="material-symbols-outlined no-results-icon">search_off</span>
                        <h2 class="pro-service-name">No results</h2> 
                    </div>
                `;
                serviceProfilesContainer.insertAdjacentHTML('beforeend', noResultsHtml);
            }
        } else if (noResultsElement) {
            noResultsElement.remove();
        }
    }

    // Debounce logic to prevent double clicks
    let isCategoryClickInProgress = false;

    // Handle clicking on service category icons
    serviceItems.forEach(function (item) {
        item.addEventListener('click', function (event) {
            event.preventDefault();
            if (isCategoryClickInProgress) return; // Prevent double clicks
            isCategoryClickInProgress = true;

            const category = this.getAttribute('data-category');
            displaySubServices(category);
            scrollItemIntoView(serviceItemsContainer, this); // Center the clicked category

            // Allow another click after some time
            setTimeout(() => {
                isCategoryClickInProgress = false;
            }, 300);
        });
    });

    // Function to get URL parameters
    function getUrlParameter(name) {
        name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
        const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
        const results = regex.exec(location.search);
        return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
    }

    // Function to find the category for a given service
    function findCategoryForService(service) {
        for (const [category, services] of Object.entries(servicesData)) {
            if (services.some(s => s.name.toLowerCase() === service.toLowerCase())) {
                return category;
            }
        }
        return null;
    }

    // Function to trigger click on service category
    function triggerServiceCategoryClick(category) {
        const targetCategory = Array.from(serviceItems).find(item => item.getAttribute('data-category') === category);
        if (targetCategory) {
            targetCategory.click();
        }
    }

    // Updated function to trigger clicks on both service category and sub-service item
    function triggerSubServiceClick(service) {
        const category = findCategoryForService(service);
        if (category) {
            // First, trigger the click on the service category
            triggerServiceCategoryClick(category);

            // Wait for the sub-services to be populated
            setTimeout(() => {
                const subServiceItems = subServicesContainer.querySelectorAll('.index-sub-service-item');
                const targetItem = Array.from(subServiceItems).find(item => item.getAttribute('data-service').toLowerCase() === service.toLowerCase());
                if (targetItem) {
                    targetItem.click();
                }
                // Scroll the category into view
                const categoryItem = Array.from(serviceItems).find(item => item.getAttribute('data-category') === category);
                if (categoryItem) {
                    scrollItemIntoView(serviceItemsContainer, categoryItem);
                }
            }, 100); // Small delay to ensure sub-services are loaded
        }
    }

    // Initial display logic
    const initialService = getUrlParameter('service');
    const initialCategory = getUrlParameter('category');

    function initialize() {
        if (initialService) {
            triggerSubServiceClick(initialService);
        } else if (initialCategory) {
            triggerServiceCategoryClick(initialCategory);
        } else {
            displaySubServices('home_services'); // Default category
        }

        history.replaceState(null, '', location.pathname); // Clean up URL
        setTimeout(showContent, 100);
    }

    if (isCapacitor) {
        document.addEventListener('deviceready', () => {
            setTimeout(initialize, 100);
        }, false);
    } else {
        initialize();
    }

    // Add this function to handle service clicks from the search modal
    window.handleServiceClick = function(service, category) {
        if (servicesModal) {
            servicesModal.closeModal();
        }
        
        // Use a small delay to ensure the modal is closed before triggering the clicks
        setTimeout(() => {
            triggerSubServiceClick(service);
        }, 50);
    };
};