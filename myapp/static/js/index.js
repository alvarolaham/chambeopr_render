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
            let isScrolling = false;
            let touchStartX = 0;
            let touchStartY = 0;
            let touchStartTime = 0;
            let scrollStartPosition = 0;

            subServiceItems.forEach(item => {
                const handleTouchStart = (event) => {
                    const touch = event.touches[0];
                    touchStartX = touch.clientX;
                    touchStartY = touch.clientY;
                    touchStartTime = new Date().getTime();
                    isScrolling = false;
                    scrollStartPosition = subServicesContainer.scrollLeft;
                };

                const handleTouchMove = (event) => {
                    if (!isScrolling) {
                        const touch = event.touches[0];
                        const deltaX = Math.abs(touch.clientX - touchStartX);
                        const deltaY = Math.abs(touch.clientY - touchStartY);

                        if (deltaX > 10 || deltaY > 10) {
                            isScrolling = true;
                        }
                    }
                };

                const handleTouchEnd = (event) => {
                    const touchEndTime = new Date().getTime();
                    const touchDuration = touchEndTime - touchStartTime;

                    if (!isScrolling && touchDuration < 300) {
                        const service = item.getAttribute('data-service');
                        filterServiceProfiles(service);

                        subServiceItems.forEach(i => i.classList.remove('active'));
                        item.classList.add('active');

                        // Only scroll into view if there was no scrolling
                        if (subServicesContainer.scrollLeft === scrollStartPosition) {
                            scrollItemIntoView(subServicesContainer, item);
                        }
                    }
                };

                item.addEventListener('touchstart', handleTouchStart, { passive: true });
                item.addEventListener('touchmove', handleTouchMove, { passive: true });
                item.addEventListener('touchend', handleTouchEnd);

                // Mouse click event for desktop
                item.addEventListener('click', (event) => {
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

    // Handle clicking on service category icons
    serviceItems.forEach(function (item) {
        item.addEventListener('click', function (event) {
            event.preventDefault();
            const category = this.getAttribute('data-category');
            displaySubServices(category);
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