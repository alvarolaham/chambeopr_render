document.addEventListener("DOMContentLoaded", function () {
    console.log("Dashboard script loaded");

    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    window.csrfToken = csrfToken;

    const updateRatesModal = new bootstrap.Modal(document.getElementById("updateRatesModal"));
    const updateAvailabilityModal = new bootstrap.Modal(document.getElementById("updateAvailabilityModal"));
    const updateServicesModal = new bootstrap.Modal(document.getElementById("updateServicesModal"));
    const uploadProfilePictureModal = new bootstrap.Modal(document.getElementById("uploadProfilePictureModal"));

    const ratesModalBody = document.querySelector("#updateRatesModal .dashboard-modal-body");
    const servicesModalBody = document.querySelector("#updateServicesModal .dashboard-modal-body");
    const currentRatesDiv = document.getElementById("currentRates");
    const currentAvailabilityDiv = document.getElementById("currentAvailability");
    const currentServicesDiv = document.getElementById("currentServices");

    const availabilityText = document.getElementById("availabilityText");
    const charCount = document.getElementById("charCount");

    const profilePictureForm = document.getElementById("profilePictureForm");
    const saveProfilePictureBtn = document.getElementById("saveProfilePictureBtn");
    const deleteProfilePictureBtn = document.getElementById("deleteProfilePictureBtn");

    let currentRates = {};
    let currentServices = [];

    function fetchRatesAndServices() {
        console.log("Fetching rates and services");
        fetch(window.dashboardUrls.getRatesAndServices)
            .then((response) => response.json())
            .then((data) => {
                currentRates = data.rates;
                currentServices = data.services;
                displayCurrentRates(data.rates, data.services);
                populateRatesModal(data.services, data.rates);
                populateServicesModal(data.services);
                currentAvailabilityDiv.querySelector("p").textContent = data.availability || "Not set";
            })
            .catch(error => {
                console.error("Error fetching rates and services:", error);
            });
    }

    fetchRatesAndServices();

    function displayCurrentRates(rates, services) {
        currentRatesDiv.innerHTML = "<h3>Current Rates</h3>";
        services.forEach((service) => {
            const rate = rates[service.id] || "Not set";
            currentRatesDiv.innerHTML += `
                <div class="mb-2">
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
                <label for="rate-${service.id}" class="dashboard-form-label">${service.name}</label>
                <input type="number" class="dashboard-form-control" id="rate-${service.id}" 
                       step="0.01" min="0" placeholder="Enter rate" 
                       value="${rates[service.id] || ""}">
            `;
            ratesModalBody.appendChild(serviceDiv);
        });
    }

    function populateServicesModal(services) {
        servicesModalBody.innerHTML = "";
        services.forEach((service) => {
            const serviceDiv = document.createElement("div");
            serviceDiv.className = "form-check";
            serviceDiv.innerHTML = `
                <input class="form-check-input" type="checkbox" value="${service.id}" id="service-${service.id}" ${service.selected ? "checked" : ""}>
                <label class="form-check-label" for="service-${service.id}">
                    ${service.name}
                </label>
            `;
            servicesModalBody.appendChild(serviceDiv);
        });
    }

    function updateDeleteButtonVisibility() {
        console.log("Updating delete button visibility");
        const profilePictureContainer = document.querySelector(".dashboard-profile-picture-container");
        const hasProfilePicture = !profilePictureContainer.querySelector(".dashboard-profile-icon");
        deleteProfilePictureBtn.style.display = hasProfilePicture ? "block" : "none";
        console.log("Has profile picture:", hasProfilePicture);
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

    document.getElementById("updateServicesBtn").addEventListener("click", function () {
        updateServicesModal.show();
    });

    saveProfilePictureBtn.addEventListener("click", function () {
        console.log("Save profile picture button clicked");
        const formData = new FormData(profilePictureForm);

        fetch(window.dashboardUrls.uploadProfilePictureDashboard, {
            method: "POST",
            headers: {
                "X-CSRFToken": window.csrfToken,
            },
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                uploadProfilePictureModal.hide();
                const profilePicElement = document.getElementById("dashboard-profile-pic");
                if (profilePicElement) {
                    profilePicElement.src = data.profile_picture_url;
                } else {
                    const profilePicContainer = document.querySelector(".dashboard-profile-picture-container");
                    profilePicContainer.innerHTML = `<img src="${data.profile_picture_url}" class="dashboard-profile-picture" alt="Profile Picture" id="dashboard-profile-pic" />`;
                }

                // Dispatch custom event to update navbar profile picture
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
        })
        .catch(error => {
            console.error("Error uploading profile picture:", error);
            alert("An error occurred while uploading the profile picture.");
        });
    });

    deleteProfilePictureBtn.addEventListener("click", function () {
        console.log("Delete profile picture button clicked");
        if (confirm("Are you sure you want to delete the picture?")) {
            fetch(window.dashboardUrls.deleteProfilePicture, {
                method: "POST",
                headers: {
                    "X-CSRFToken": window.csrfToken,
                    "Content-Type": "application/json",
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    uploadProfilePictureModal.hide();
                    const profilePictureContainer = document.querySelector(".dashboard-profile-picture-container");
                    const navProfilePictureContainer = document.getElementById("nav-profile-pic-container");
                    profilePictureContainer.innerHTML = '<i class="fas fa-user-circle dashboard-profile-icon user-icon" id="dashboard-profile-icon"></i>';
                    if (navProfilePictureContainer) {
                        navProfilePictureContainer.innerHTML = '<i class="fas fa-user-circle fa-2x user-icon" id="navbar-profile-icon"></i>';
                    }
                    deleteProfilePictureBtn.style.display = "none";
                    alert("Profile picture deleted successfully!");
                } else {
                    alert("Error deleting profile picture. Please try again.");
                }
            })
            .catch(error => {
                console.error("Error deleting profile picture:", error);
                alert("An error occurred while deleting the profile picture.");
            });
        }
    });

    document.getElementById("saveRatesBtn").addEventListener("click", function () {
        const updatedRates = {};
        document.querySelectorAll('#updateRatesModal input[type="number"]').forEach((input) => {
            const serviceId = input.id.replace("rate-", "");
            const rate = parseFloat(input.value);
            if (!isNaN(rate)) {
                updatedRates[serviceId] = rate;
            }
        });

        fetch(window.dashboardUrls.saveRates, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": window.csrfToken,
            },
            body: JSON.stringify(updatedRates),
        })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                updateRatesModal.hide();
                displayCurrentRates(updatedRates, currentServices);
                currentRates = updatedRates;
                alert("Rates updated successfully!");
            } else {
                alert("Error updating rates. Please try again.");
            }
        })
        .catch(error => {
            console.error("Error updating rates:", error);
            alert("An error occurred while updating rates.");
        });
    });

    document.getElementById("saveAvailabilityBtn").addEventListener("click", function () {
        const newAvailability = availabilityText.value;

        fetch(window.dashboardUrls.updateAvailability, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": window.csrfToken,
            },
            body: JSON.stringify({ availability: newAvailability }),
        })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                updateAvailabilityModal.hide();
                currentAvailabilityDiv.querySelector("p").textContent = newAvailability;
                alert("Availability updated successfully!");
            } else {
                alert("Error updating availability. Please try again.");
            }
        })
        .catch(error => {
            console.error("Error updating availability:", error);
            alert("An error occurred while updating availability.");
        });
    });

    document.getElementById("saveServicesBtn").addEventListener("click", function () {
        const selectedServices = Array.from(
            document.querySelectorAll('#updateServicesModal input[type="checkbox"]:checked')
        ).map((checkbox) => checkbox.value);

        fetch(window.dashboardUrls.updateServices, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": window.csrfToken,
            },
            body: JSON.stringify({ services: selectedServices }),
        })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                updateServicesModal.hide();
                fetchRatesAndServices();
                alert("Services updated successfully!");
            } else {
                alert("Error updating services. Please try again.");
            }
        })
        .catch(error => {
            console.error("Error updating services:", error);
            alert("An error occurred while updating services.");
        });
    });

    availabilityText.addEventListener("input", updateCharCount);

    function updateCharCount() {
        const count = availabilityText.value.length;
        charCount.textContent = `${count}/100`;
    }

    document.getElementById("uploadProfilePictureModal").addEventListener("show.bs.modal", function () {
        updateDeleteButtonVisibility();
    });
});
