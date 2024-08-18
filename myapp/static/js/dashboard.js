document.addEventListener("DOMContentLoaded", function () {
    const updateRatesModal = new bootstrap.Modal(document.getElementById("updateRatesModal"));
    const updateAvailabilityModal = new bootstrap.Modal(document.getElementById("updateAvailabilityModal"));
    const updateServicesModal = new bootstrap.Modal(document.getElementById("updateServicesModal"));
    const editBusinessNameModal = new bootstrap.Modal(document.getElementById("editBusinessNameModal"));
    const editZipCodeModal = new bootstrap.Modal(document.getElementById("editZipCodeModal"));
    const editLanguagesModal = new bootstrap.Modal(document.getElementById("editLanguagesModal"));
    const editPhoneNumberModal = new bootstrap.Modal(document.getElementById("editPhoneNumberModal"));
    const editBusinessEmailModal = new bootstrap.Modal(document.getElementById("editBusinessEmailModal"));

    const ratesModalBody = document.querySelector("#updateRatesModal .modal-body");
    const currentRatesDiv = document.getElementById("currentRates");
    const currentAvailabilityDiv = document.getElementById("currentAvailability");
    const availabilityText = document.getElementById("availabilityText");
    const charCount = document.getElementById("charCount");
    const profilePictureForm = document.getElementById("profilePictureForm");
    const saveProfilePictureBtn = document.getElementById("saveProfilePictureBtn");
    const deleteProfilePictureBtn = document.getElementById("deleteProfilePictureBtn");
    const selectedDashboardServices = new Set();
    const tempSelectedServices = new Set();
    const dashboardServicesContainer = document.getElementById("dashboard-servicesContainer");
    const selectedServicesPillsContainer = document.getElementById("dashboard-selectedServicesPills");
    const removeAllServicesBtn = document.getElementById("dashboard-removeAllServicesBtn");

    // Profile Visibility Toggle
    const profileVisibilityCheckbox = document.querySelector('.toggle-switch input[type="checkbox"]');
    profileVisibilityCheckbox.addEventListener('change', function () {
        const visibility = profileVisibilityCheckbox.checked;
        updateProfileVisibility(visibility);
    });

    async function updateProfileVisibility(visibility) {
        try {
            const payload = JSON.stringify({ profile_visibility: visibility });
            const response = await fetch(window.dashboardUrls.updateProfileVisibility, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": window.csrfToken,
                },
                body: payload,
            });

            const data = await response.json();

            if (!data.success) {
                alert("Error updating profile visibility. Please try again.");
            }
        } catch (error) {
            alert("An error occurred while updating profile visibility.");
            console.error("Error updating profile visibility:", error);
        }
    }

    async function fetchRatesAndServices() {
        try {
            const response = await fetch(window.dashboardUrls.getRatesAndServices);
            const data = await response.json();

            displayCurrentRates(data.rates, data.services);
            populateRatesModal(data.services, data.rates);
            updateSelectedServices(data.services);
            currentAvailabilityDiv.querySelector("p").textContent = data.availability || "Not set";
            highlightSelectedServices();
            formatCategoryHeaders();
        } catch (error) {
            console.error("Error fetching rates and services:", error);
        }
    }

    fetchRatesAndServices();

    function displayCurrentRates(rates, services) {
        currentRatesDiv.innerHTML = "";
        services.forEach((service) => {
            const rate = rates[service.id] || "Not set";
            currentRatesDiv.innerHTML += `
                <div>
                    <strong>${service.name}:</strong> $${rate}
                </div>
            `;
        });
    }

    function populateRatesModal(services, rates) {
        ratesModalBody.innerHTML = "";
        services.forEach((service) => {
            const serviceDiv = document.createElement("div");
            serviceDiv.className = "mb-3";
            serviceDiv.innerHTML = `
                <label for="rate-${service.id}" class="form-label">${service.name}</label>
                <input type="number" class="form-control" id="rate-${service.id}" 
                       step="0.01" min="0" placeholder="Enter rate" 
                       value="${rates[service.id] || ""}">
            `;
            ratesModalBody.appendChild(serviceDiv);
        });
    }

    function updateSelectedServices(services) {
        selectedDashboardServices.clear();
        tempSelectedServices.clear();
        selectedServicesPillsContainer.innerHTML = "";
        services.forEach(service => {
            selectedDashboardServices.add(service.id);
            tempSelectedServices.add(service.id);
            addServicePill(service.name, service.id);
        });
        updateRemoveAllServicesBtn();
    }

    function addServicePill(serviceName, serviceId) {
        const pill = document.createElement("span");
        pill.className = "dashboard-service-pill";
        pill.innerHTML = `
            ${serviceName}
            <span class="dashboard-remove-pill" data-id="${serviceId}">&times;</span>
        `;
        selectedServicesPillsContainer.appendChild(pill);

        pill.querySelector('.dashboard-remove-pill').addEventListener('click', function () {
            removeSingleService(serviceId);
        });
    }

    function removeSingleService(serviceId) {
        if (confirm("Are you sure you want to remove this service?")) {
            const updatedServices = Array.from(selectedDashboardServices).filter(id => id !== serviceId);
            updateServices(updatedServices);
        }
    }

    function updateRemoveAllServicesBtn() {
        removeAllServicesBtn.style.display = selectedDashboardServices.size > 0 ? "block" : "none";
    }

    removeAllServicesBtn.addEventListener("click", function () {
        if (confirm("Are you sure you want to remove all services?")) {
            updateServices([]);
        }
    });

    async function updateServices(services) {
        try {
            const response = await fetch(window.dashboardUrls.updateServices, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": window.csrfToken,
                },
                body: JSON.stringify({ services: services }),  // Sending services as array
            });
    
            const data = await response.json();
            if (!data.success) {
                alert("Error updating services. Please try again.");
            }
        } catch (error) {
            console.error("Error updating services:", error);
        }
    }
    

    dashboardServicesContainer.addEventListener("click", function (e) {
        if (e.target.classList.contains("service-option")) {
            e.target.classList.toggle("selected");
            const serviceId = e.target.dataset.value;
            if (tempSelectedServices.has(serviceId)) {
                tempSelectedServices.delete(serviceId);
            } else {
                tempSelectedServices.add(serviceId);
            }
        }
    });

    document.getElementById("saveServicesBtn").addEventListener("click", function () {
        const selectedServices = Array.from(tempSelectedServices);
        updateServices(selectedServices);
        updateServicesModal.hide();
    });

    function highlightSelectedServices() {
        const serviceOptions = dashboardServicesContainer.querySelectorAll(".service-option");
        serviceOptions.forEach(option => {
            const serviceId = option.dataset.value;
            if (tempSelectedServices.has(serviceId)) {
                option.classList.add("selected");
            } else {
                option.classList.remove("selected");
            }
        });
    }

    document.getElementById("updateServicesBtn").addEventListener("click", function () {
        tempSelectedServices.clear();

        const servicePills = document.querySelectorAll('.dashboard-service-pill');

        const selectedServiceNames = new Set(
            Array.from(servicePills).map(pill => pill.textContent.trim().replace('×', '').trim())
        );

        const serviceOptions = dashboardServicesContainer.querySelectorAll(".service-option");
        serviceOptions.forEach(option => {
            if (selectedServiceNames.has(option.textContent.trim())) {
                tempSelectedServices.add(option.dataset.value);
            }
        });

        highlightSelectedServices();
        updateServicesModal.show();
    });

    availabilityText.addEventListener("input", function () {
        const count = availabilityText.value.length;
        charCount.textContent = `${count}/100`;
    });

    document.getElementById("saveAvailabilityBtn").addEventListener("click", async function () {
        const newAvailability = availabilityText.value;

        try {
            const response = await fetch(window.dashboardUrls.updateAvailability, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": window.csrfToken,
                },
                body: JSON.stringify({ availability: newAvailability }),
            });

            const data = await response.json();

            if (data.success) {
                updateAvailabilityModal.hide();
                currentAvailabilityDiv.querySelector("p").textContent = newAvailability || "Not set";
            } else {
                alert("Error updating availability. Please try again.");
            }
        } catch (error) {
            console.error("Error updating availability:", error);
            alert("An error occurred while updating availability.");
        }
    });

    document.getElementById("saveRatesBtn").addEventListener("click", async function () {
        const updatedRates = {};
        document.querySelectorAll('#updateRatesModal input[type="number"]').forEach((input) => {
            const serviceId = input.id.replace("rate-", "");
            const rate = parseFloat(input.value);
            if (!isNaN(rate)) {
                updatedRates[serviceId] = rate;
            } else {
                updatedRates[serviceId] = null; // Allow setting the rate to null
            }
        });

        try {
            const response = await fetch(window.dashboardUrls.saveRates, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": window.csrfToken,
                },
                body: JSON.stringify(updatedRates),
            });

            const data = await response.json();

            if (data.success) {
                updateRatesModal.hide();
                fetchRatesAndServices();
            } else {
                alert("Error updating rates. Please try again.");
            }
        } catch (error) {
            console.error("Error updating rates:", error);
            alert("An error occurred while updating rates.");
        }
    });

    saveProfilePictureBtn.addEventListener("click", async function () {
        const formData = new FormData(profilePictureForm);

        try {
            const response = await fetch(window.dashboardUrls.uploadProfilePictureDashboard, {
                method: "POST",
                headers: {
                    "X-CSRFToken": window.csrfToken,
                },
                body: formData,
            });

            const data = await response.json();

            if (data.success) {
                const uploadProfilePictureModal = bootstrap.Modal.getInstance(document.getElementById('uploadProfilePictureModal'));
                uploadProfilePictureModal.hide();

                const profilePicContainer = document.querySelector(".profile-picture-container");
                profilePicContainer.innerHTML = `<img src="${data.profile_picture_url}" alt="Profile Picture" id="dashboard-profile-pic" />`;

                const navProfilePicContainer = document.getElementById("nav-profile-pic-container");
                if (navProfilePicContainer) {
                    navProfilePicContainer.innerHTML = `<img src="${data.profile_picture_url}" class="nav-profile-picture" alt="Profile Picture" id="navbar-profile-pic" />`;
                }

                const event = new CustomEvent('profilePicUpdated', {
                    detail: {
                        profile_pic_url: data.profile_picture_url
                    }
                });
                document.dispatchEvent(event);

                updateDeleteButtonVisibility();
            } else {
                alert("Error uploading profile picture. Please try again.");
            }
        } catch (error) {
            console.error("Error uploading profile picture:", error);
            alert("An error occurred while uploading the profile picture.");
        }
    });

    deleteProfilePictureBtn.addEventListener("click", async function () {
        if (confirm("Are you sure you want to delete the picture?")) {
            try {
                const response = await fetch(window.dashboardUrls.deleteProfilePicture, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": window.csrfToken,
                        "Content-Type": "application/json",
                    },
                });

                const data = await response.json();

                if (data.success) {
                    const uploadProfilePictureModal = bootstrap.Modal.getInstance(document.getElementById('uploadProfilePictureModal'));
                    uploadProfilePictureModal.hide();

                    const profilePictureContainer = document.querySelector(".profile-picture-container");
                    profilePictureContainer.innerHTML = '<i class="fas fa-user-circle profile-icon" id="dashboard-profile-icon"></i>';

                    const navProfilePicContainer = document.getElementById("nav-profile-pic-container");
                    if (navProfilePicContainer) {
                        navProfilePicContainer.innerHTML = '<i class="fas fa-user-circle fa-2x user-icon" id="navbar-profile-icon"></i>';
                    }

                    deleteProfilePictureBtn.style.display = "none";

                    const event = new CustomEvent('profilePicDeleted');
                    document.dispatchEvent(event);
                } else {
                    alert("Error deleting profile picture. Please try again.");
                }
            } catch (error) {
                console.error("Error deleting profile picture:", error);
                alert("An error occurred while deleting the profile picture.");
            }
        }
    });

    function updateDeleteButtonVisibility() {
        const profilePictureContainer = document.querySelector(".profile-picture-container");
        const hasProfilePicture = profilePictureContainer.querySelector("img") !== null;
        deleteProfilePictureBtn.style.display = hasProfilePicture ? "block" : "none";
    }

    updateDeleteButtonVisibility();

    document.getElementById("updateRatesBtn").addEventListener("click", function () {
        updateRatesModal.show();
    });

    document.getElementById("updateAvailabilityBtn").addEventListener("click", function () {
        availabilityText.value = currentAvailabilityDiv.querySelector("p").textContent;
        updateCharCount();
        updateAvailabilityModal.show();
    });

    function updateCharCount() {
        const count = availabilityText.value.length;
        charCount.textContent = `${count}/100`;
    }

    document.getElementById("uploadProfilePictureModal").addEventListener("show.bs.modal", function () {
        updateDeleteButtonVisibility();
    });

    function formatCategoryHeaders() {
        document.querySelectorAll(".dashboard-service-category").forEach((header) => {
            const category = header.dataset.category.replace(/_/g, " ");
            header.textContent = category
                .split(" ")
                .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
                .join(" ");
        });
    }

    document.getElementById("editBusinessNameModal").addEventListener("show.bs.modal", function () {
        const currentBusinessName = document.getElementById("business-name").textContent.trim();
        document.getElementById("editBusinessNameInput").value = currentBusinessName;
    });

    document.getElementById("editZipCodeModal").addEventListener("show.bs.modal", function () {
        const currentZipCode = document.getElementById("zip-code").textContent.trim();
        document.getElementById("editZipCodeInput").value = currentZipCode;
    });

    document.getElementById("editLanguagesModal").addEventListener("show.bs.modal", function () {
        const currentLanguages = document.getElementById("languages").textContent.trim();
        document.getElementById("editLanguagesInput").value = currentLanguages;
    });

    document.getElementById("editPhoneNumberModal").addEventListener("show.bs.modal", function () {
        const currentPhoneNumber = document.getElementById("phone-number").textContent.trim();
        document.getElementById("editPhoneNumberInput").value = currentPhoneNumber;
    });

    document.getElementById("editBusinessEmailModal").addEventListener("show.bs.modal", function () {
        const currentBusinessEmail = document.getElementById("business-email").textContent.trim();
        document.getElementById("editBusinessEmailInput").value = currentBusinessEmail;
    });

    document.getElementById("saveBusinessNameBtn").addEventListener("click", async function () {
        const newBusinessName = document.getElementById("editBusinessNameInput").value.trim();

        try {
            const response = await fetch(window.dashboardUrls.updateBusinessName, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": window.csrfToken,
                },
                body: JSON.stringify({ business_name: newBusinessName }), // Send empty string if empty
            });

            const data = await response.json();

            if (data.success) {
                document.getElementById("business-name").textContent = newBusinessName || "Not set";
                editBusinessNameModal.hide();
            } else {
                alert("Error updating business name. Please try again.");
            }
        } catch (error) {
            console.error("Error updating business name:", error);
            alert("An error occurred while updating the business name.");
        }
    });

    document.getElementById("saveZipCodeBtn").addEventListener("click", async function () {
        const newZipCode = document.getElementById("editZipCodeInput").value.trim();

        try {
            const response = await fetch(window.dashboardUrls.updateZipCode, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": window.csrfToken,
                },
                body: JSON.stringify({ zip_code: newZipCode }), // Allow empty zip code
            });

            const data = await response.json();

            if (data.success) {
                document.getElementById("zip-code").textContent = newZipCode || "Not set";
                editZipCodeModal.hide();
            } else {
                alert("Error updating zip code. Please try again.");
            }
        } catch (error) {
            console.error("Error updating zip code:", error);
            alert("An error occurred while updating the zip code.");
        }
    });

    document.getElementById("saveLanguagesBtn").addEventListener("click", async function () {
        const newLanguages = document.getElementById("editLanguagesInput").value.trim();

        try {
            const response = await fetch(window.dashboardUrls.updateLanguages, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": window.csrfToken,
                },
                body: JSON.stringify({ languages: newLanguages }), // Allow empty languages
            });

            const data = await response.json();

            if (data.success) {
                document.getElementById("languages").textContent = newLanguages || "Not set";
                editLanguagesModal.hide();
            } else {
                alert("Error updating languages. Please try again.");
            }
        } catch (error) {
            console.error("Error updating languages:", error);
            alert("An error occurred while updating the languages.");
        }
    });

    document.getElementById("savePhoneNumberBtn").addEventListener("click", async function () {
        const newPhoneNumber = document.getElementById("editPhoneNumberInput").value.trim();

        try {
            const response = await fetch(window.dashboardUrls.updatePhoneNumber, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": window.csrfToken,
                },
                body: JSON.stringify({ phone_number: newPhoneNumber }), // Allow empty phone number
            });

            const data = await response.json();

            if (data.success) {
                document.getElementById("phone-number").textContent = newPhoneNumber || "Not set";
                editPhoneNumberModal.hide();
            } else {
                alert("Error updating phone number. Please try again.");
            }
        } catch (error) {
            console.error("Error updating phone number:", error);
            alert("An error occurred while updating the phone number.");
        }
    });

    document.getElementById("saveBusinessEmailBtn").addEventListener("click", async function () {
        const newBusinessEmail = document.getElementById("editBusinessEmailInput").value.trim();

        try {
            const response = await fetch(window.dashboardUrls.updateBusinessEmail, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": window.csrfToken,
                },
                body: JSON.stringify({ business_email: newBusinessEmail }), // Allow empty business email
            });

            const data = await response.json();

            if (data.success) {
                document.getElementById("business-email").textContent = newBusinessEmail || "Not set";
                editBusinessEmailModal.hide();
            } else {
                alert("Error updating business email. Please try again.");
            }
        } catch (error) {
            console.error("Error updating business email:", error);
            alert("An error occurred while updating the business email.");
        }
    });
});
