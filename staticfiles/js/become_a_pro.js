document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("proForm");
    const businessNameInput = document.getElementById("business_name");
    const phoneNumberInput = document.getElementById("phone_number");
    const zipCodeInput = document.getElementById("zip_code");
    const servicesInput = document.getElementById("servicesInput");
    const selectedServices = document.getElementById("selectedServices");
    const selectedServicesPills = document.getElementById("become-a-pro-selectedServicesPills");
    const clearSelectionContainer = document.getElementById("become-a-pro-clearSelectionContainer");
    const clearSelectionBtn = document.getElementById("become-a-pro-clearSelectionBtn");
    const serviceSelectionPopup = new bootstrap.Modal(document.getElementById("become-a-pro-serviceSelectionPopup"));
    const servicesContainer = document.getElementById("become-a-pro-servicesContainer");

    const prZipCodes = window.prZipCodes;

    // Format category headers
    document.querySelectorAll(".become-a-pro-category-header").forEach((header) => {
        const category = header.dataset.category.replace(/_/g, " ");
        header.textContent = category
            .split(" ")
            .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
            .join(" ");
    });

    servicesInput.addEventListener("click", function () {
        serviceSelectionPopup.show();
    });

    servicesContainer.addEventListener("click", function (e) {
        if (e.target.classList.contains("become-a-pro-service-option")) {
            e.target.classList.toggle("selected");
            updateSelectedServices();
        }
    });

    clearSelectionBtn.addEventListener("click", function () {
        clearAllSelections();
    });

    function updateSelectedServices() {
        const selectedOptions = servicesContainer.querySelectorAll(".become-a-pro-service-option.selected");
        const count = selectedOptions.length;
        const selectedValues = Array.from(selectedOptions).map((option) => option.dataset.value);

        selectedServices.value = JSON.stringify(selectedValues);
        servicesInput.value = count > 0 ? `${count} service(s) selected` : "";

        clearSelectionContainer.style.display = count > 0 ? "block" : "none";

        updateServicePills(selectedValues);
    }

    function updateServicePills(services) {
        selectedServicesPills.innerHTML = "";
        services.forEach((service) => {
            const pill = document.createElement("span");
            pill.className = "become-a-pro-service-pill";
            pill.innerHTML = `
                <span class="become-a-pro-service-name">${service}</span>
                <button class="become-a-pro-remove-pill" data-service="${service}" aria-label="Remove ${service}">
                    <i class="fas fa-times"></i>
                </button>
            `;
            selectedServicesPills.appendChild(pill);
        });

        document.querySelectorAll(".become-a-pro-remove-pill").forEach((button) => {
            button.addEventListener("click", function (e) {
                e.preventDefault();
                const serviceToRemove = this.dataset.service;
                const serviceOption = servicesContainer.querySelector(`.become-a-pro-service-option[data-value="${serviceToRemove}"]`);
                if (serviceOption) {
                    serviceOption.classList.remove("selected");
                }
                updateSelectedServices();
            });
        });
    }

    function clearAllSelections() {
        document.querySelectorAll(".become-a-pro-service-option.selected").forEach((option) => {
            option.classList.remove("selected");
        });
        updateSelectedServices();
    }

    function validatePhoneNumber(phoneNumber) {
        const phoneRegex = /^(\+1|1)?[\s-]?\(?[1-9]\d{2}\)?[\s-]?\d{3}[\s-]?\d{4}$/;
        return phoneRegex.test(phoneNumber);
    }

    function validateZipCode(zipCode) {
        return prZipCodes.includes(zipCode);
    }

    function showError(input, message) {
        const formGroup = input.closest('.mb-3');
        const errorDiv = formGroup.querySelector('.become-a-pro-error-message') || document.createElement('div');
        errorDiv.className = 'become-a-pro-error-message text-danger';
        errorDiv.textContent = message;
        if (!formGroup.querySelector('.become-a-pro-error-message')) {
            formGroup.appendChild(errorDiv);
        }
    }

    function clearError(input) {
        const formGroup = input.closest('.mb-3');
        const errorDiv = formGroup.querySelector('.become-a-pro-error-message');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    form.addEventListener("submit", function (event) {
        let isValid = true;

        // Validate Business Name
        if (businessNameInput.value.trim() === "") {
            showError(businessNameInput, "Business name cannot be empty.");
            isValid = false;
        } else {
            clearError(businessNameInput);
        }

        // Validate Phone Number
        if (!validatePhoneNumber(phoneNumberInput.value)) {
            showError(phoneNumberInput, "Please enter a valid phone number.");
            isValid = false;
        } else {
            clearError(phoneNumberInput);
        }

        // Validate Zip Code
        if (!validateZipCode(zipCodeInput.value)) {
            showError(zipCodeInput, "Please enter a valid Puerto Rico zip code.");
            isValid = false;
        } else {
            clearError(zipCodeInput);
        }

        if (!isValid) {
            event.preventDefault();
        } else {
            // If the form is valid and submitted successfully, clear the stored data
            localStorage.removeItem("business_name");
            localStorage.removeItem("phone_number");
            localStorage.removeItem("zip_code");
        }
    });

    // Store valid input locally
    [businessNameInput, phoneNumberInput, zipCodeInput].forEach(input => {
        input.addEventListener('input', function() {
            localStorage.setItem(input.id, input.value);
        });

        // Restore stored value on page load
        const storedValue = localStorage.getItem(input.id);
        if (storedValue) {
            input.value = storedValue;
        }
    });

    // Function to check if the page is being reloaded
    function isPageReload() {
        const navigation = performance.getEntriesByType("navigation")[0];
        return navigation.type === "reload" || navigation.type === "back_forward";
    }

    // Clear form fields on page reload
    if (isPageReload()) {
        // Clear the form and local storage
        form.reset();
        localStorage.removeItem("business_name");
        localStorage.removeItem("phone_number");
        localStorage.removeItem("zip_code");
        clearAllSelections();
    }
});