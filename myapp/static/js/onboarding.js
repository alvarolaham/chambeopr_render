document.addEventListener("DOMContentLoaded", function () {
    const uploadPhotoModal = new bootstrap.Modal(document.getElementById("uploadPhotoModal"));
    const setRatesModal = new bootstrap.Modal(document.getElementById("setRatesModal"));
    const setAvailabilityModal = new bootstrap.Modal(document.getElementById("setAvailabilityModal"));
    const modalBody = document.querySelector("#setRatesModal .modal-body");
    const ratesInput = document.getElementById("id_rates");
    const availabilityInput = document.getElementById("id_availability");
    const availabilityText = document.getElementById("availabilityText");
    const charCount = document.getElementById("charCount");
    const profileProgress = document.getElementById("profileProgress");

    // Parse existing rates
    let existingRates = {};
    try {
        existingRates = JSON.parse(ratesInput.value || "{}");
    } catch (e) {
        console.error("Error parsing existing rates:", e);
    }

    // Fetch services and populate rates modal
    fetch(window.onboardingUrls.getServices)
        .then((response) => response.json())
        .then((services) => {
            modalBody.innerHTML = "";
            services.forEach((service) => {
                const serviceDiv = document.createElement("div");
                serviceDiv.className = "mb-3";
                serviceDiv.innerHTML = `
                    <label for="rate-${service.id}" class="form-label">${service.name}</label>
                    <input type="number" class="form-control" id="rate-${service.id}" 
                           step="0.01" min="0" placeholder="Enter rate" 
                           value="${existingRates[service.id] || ""}">
                `;
                modalBody.appendChild(serviceDiv);
            });
        });

    // Show upload photo modal when option is clicked
    document.getElementById("uploadPhotoOption").addEventListener("click", function () {
        uploadPhotoModal.show();
    });

    // Show rates modal when option is clicked
    document.getElementById("setRatesOption").addEventListener("click", function () {
        setRatesModal.show();
    });

    // Handle saving the rates
    document.getElementById("saveRatesBtn").addEventListener("click", function () {
        const rates = {};
        document.querySelectorAll('#setRatesModal input[type="number"]').forEach((input) => {
            const serviceId = input.id.replace("rate-", "");
            const rate = parseFloat(input.value);
            if (!isNaN(rate)) {
                rates[serviceId] = rate;
            }
        });
        // Update the hidden input with the new rates
        ratesInput.value = JSON.stringify(rates);
        setRatesModal.hide();
        alert("Rates saved. Don't forget to submit the form to save all changes.");
        checkCompletion();
    });

    // Show availability modal when option is clicked
    document.getElementById("setAvailabilityOption").addEventListener("click", function () {
        availabilityText.value = availabilityInput.value || "";
        updateCharCount();
        setAvailabilityModal.show();
    });

    // Update character count
    availabilityText.addEventListener("input", updateCharCount);

    function updateCharCount() {
        const count = availabilityText.value.length;
        charCount.textContent = `${count}/100`;
    }

    // Handle saving the availability
    document.getElementById("saveAvailabilityBtn").addEventListener("click", function () {
        availabilityInput.value = availabilityText.value;
        setAvailabilityModal.hide();
        alert("Availability saved. Don't forget to submit the form to save all changes.");
        checkCompletion();
    });

    // Handle saving the profile picture
    document.getElementById("savePhotoBtn").addEventListener("click", function () {
        const formData = new FormData(document.getElementById("uploadPhotoForm"));
        fetch(window.onboardingUrls.uploadProfilePicture, {
            method: "POST",
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    document.getElementById("uploadPhotoCheck").style.display = "flex";
                    alert("Profile picture uploaded successfully.");
                } else {
                    alert("Failed to upload profile picture.");
                }
                uploadPhotoModal.hide();
                checkCompletion();
            })
            .catch((error) => {
                console.error("Error uploading profile picture:", error);
                alert("An error occurred while uploading the profile picture.");
            });
    });

    // Function to check profile completion
    function checkCompletion() {
        let completed = 0;
        if (ratesInput.value && Object.keys(JSON.parse(ratesInput.value)).length > 0) {
            document.getElementById("setRatesCheck").style.display = "flex";
            completed++;
        } else {
            document.getElementById("setRatesCheck").style.display = "none";
        }
        if (availabilityInput.value) {
            document.getElementById("setAvailabilityCheck").style.display = "flex";
            completed++;
        } else {
            document.getElementById("setAvailabilityCheck").style.display = "none";
        }
        if (document.getElementById("uploadPhotoCheck").style.display === "flex") {
            completed++;
        }
        const completionPercentage = (completed / 3) * 100; // Adjust denominator based on the number of fields
        profileProgress.style.width = `${completionPercentage}%`;
        profileProgress.setAttribute("aria-valuenow", completionPercentage);
        profileProgress.classList.add("bg-success");
    }

    // Handle form submission via AJAX
    document.getElementById("profileForm").addEventListener("submit", function (e) {
        e.preventDefault();
        const formData = new FormData(this);
        fetch(window.onboardingUrls.onboarding, {
            method: "POST",
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    window.location.href = data.redirect_url;
                } else {
                    alert("Failed to save profile. Please correct the errors and try again.");
                }
            })
            .catch((error) => {
                console.error("Error saving profile:", error);
                alert("An error occurred while saving the profile.");
            });
    });

    // Initial check for completion
    checkCompletion();
});