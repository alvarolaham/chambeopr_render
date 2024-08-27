window.onload = function () {
    // Check if running in Capacitor
    const isCapacitor = window.Capacitor !== undefined;

    // Cache DOM queries
    const loadingIndicator = document.getElementById('loading-indicator');
    const subServicesContainer = document.querySelector('.index-sub-service-grid-container');
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

            // Handle click or touch events for mobile devices
            const subServiceItems = subServicesContainer.querySelectorAll('.index-sub-service-item');
            let isScrolling = false; // To track whether the user is scrolling
            let touchStartX = 0;     // To store the initial touch X coordinate
            let touchStartY = 0;     // To store the initial touch Y coordinate
            let touchStartTime = 0;  // To track how long the touch lasted

            subServiceItems.forEach(item => {
                const handleTouchStart = (event) => {
                    // Record the initial touch coordinates and time
                    const touch = event.touches[0];
                    touchStartX = touch.clientX;
                    touchStartY = touch.clientY;
                    touchStartTime = new Date().getTime();
                    isScrolling = false; // Reset scrolling flag
                };

                const handleTouchMove = (event) => {
                    // If the user moves their finger significantly, they are scrolling
                    const touch = event.touches[0];
                    const deltaX = Math.abs(touch.clientX - touchStartX);
                    const deltaY = Math.abs(touch.clientY - touchStartY);

                    // If the movement exceeds a threshold, mark as scrolling
                    if (deltaX > 10 || deltaY > 10) {
                        isScrolling = true;
                    }
                };

                const handleTouchEnd = () => {
                    // Only trigger the selection if the user was not scrolling and if the touch was short
                    const touchEndTime = new Date().getTime();
                    const touchDuration = touchEndTime - touchStartTime;

                    // Only proceed with selection if it's a tap (short duration) and no scrolling occurred
                    if (!isScrolling && touchDuration < 300) {
                        const service = item.getAttribute('data-service');
                        filterServiceProfiles(service);

                        // Remove 'active' class from all sub-service items and add it to the clicked one
                        subServiceItems.forEach(i => i.classList.remove('active'));
                        item.classList.add('active');

                        // Scroll the clicked item into view
                        scrollItemIntoView(subServicesContainer, item);
                    }
                };

                // Add event listeners for touch interaction
                item.addEventListener('touchstart', handleTouchStart, { passive: true });
                item.addEventListener('touchmove', handleTouchMove, { passive: true });
                item.addEventListener('touchend', handleTouchEnd);

                const handleInteraction = (event) => {
                    const service = item.getAttribute('data-service');
                    filterServiceProfiles(service);
                    // Remove 'active' class from all sub-service items and add it to the clicked one
                    subServiceItems.forEach(i => i.classList.remove('active'));
                    item.classList.add('active');
                    // Scroll the clicked item into view
                    scrollItemIntoView(subServicesContainer, item);
                };

                // Add both click and touch events for better desktop experience
                item.addEventListener('click', handleInteraction);
            });

            // Trigger click on the first sub-service item
            if (subServiceItems.length > 0) {
                subServiceItems[0].click();
            }
        } else {
            subServicesContainer.innerHTML = `<div>No services available for this category.</div>`;
            subServicesContainer.style.display = "block";
            // Show all service profiles if no sub-services are available
            filterServiceProfiles(null);
        }
        // Add active class to the clicked service item
        serviceItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('data-category') === category) {
                item.classList.add('active');
            }
        });
    }

    // Function to filter service profiles based on clicked sub-service
    function filterServiceProfiles(service) {
        let visibleProfiles = 0; // Keep track of how many profiles are visible

        serviceProfiles.forEach(profile => {
            const services = profile.getAttribute('data-services').split(',');

            if (service === null || services.includes(service)) {
                profile.style.display = 'block'; // Show the profile
                visibleProfiles++;
            } else {
                profile.style.display = 'none'; // Hide the profile
            }
        });

        // Check if no profiles are visible and show the "No Results" message
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

    // Handle clicking on service category icons
    serviceItems.forEach(function (item) {
        item.addEventListener('click', function (event) {
            event.preventDefault();
            const category = this.getAttribute('data-category');
            displaySubServices(category);
            // Scroll the clicked service item into view
            scrollItemIntoView(document.querySelector('.index-service-grid-container'), this);
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

    // Function to trigger click on sub-service item
    function triggerSubServiceClick(service) {
        const subServiceItems = subServicesContainer.querySelectorAll('.index-sub-service-item');
        const targetItem = Array.from(subServiceItems).find(item => item.getAttribute('data-service') === service);
        if (targetItem) {
            targetItem.click();
        }
    }

    // Initial display logic
    const initialService = getUrlParameter('service');

    function initialize() {
        if (initialService) {
            const category = findCategoryForService(initialService);
            if (category) {
                displaySubServices(category);
                setTimeout(() => {
                    triggerSubServiceClick(initialService);
                }, 0);
            } else {
                displaySubServices('home_services');
            }
        } else {
            displaySubServices('home_services');
        }

        history.replaceState(null, '', location.pathname);
        setTimeout(showContent, 100);
    }

    if (isCapacitor) {
        document.addEventListener('deviceready', () => {
            setTimeout(initialize, 100);
        }, false);
    } else {
        initialize();
    }
};
