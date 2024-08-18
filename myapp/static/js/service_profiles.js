// Function to parse and format rates with error handling
function parseAndFormatRate(rateString) {
    try {
        if (typeof rateString !== 'string') {
            console.warn(`Expected string but got: ${typeof rateString}`);
            return 'N/A';
        }

        let cleanedRate = rateString.replace(/[^\d.]/g, ''); // Clean up any characters that aren't digits or a period
        let rate = parseFloat(cleanedRate); // Convert the cleaned string to a float
        if (isNaN(rate)) { // If it's not a valid number, return 'N/A'
            console.warn(`Invalid rate value: ${rateString}`);
            return 'N/A';
        }
        return `$${rate.toFixed(2)}`; // Return the rate formatted to two decimal places
    } catch (error) {
        console.error(`Error parsing rate: ${error.message}`);
        return 'N/A'; // Fallback value in case of error
    }
}

// Function to update all rate displays on the page with error handling
function updateRateDisplays() {
    try {
        const rateElements = document.querySelectorAll('.pro-service-price'); // Select all elements with the class 'pro-service-price'
        rateElements.forEach(element => {
            const originalRate = element.textContent.trim(); // Get the text content of the rate element and trim any whitespace
            const formattedRate = parseAndFormatRate(originalRate); // Format the rate
            element.textContent = formattedRate; // Update the element with the formatted rate
        });
    } catch (error) {
        console.error(`Error updating rate displays: ${error.message}`);
    }
}

// Function to adjust the layout based on the screen size with error handling
function adjustLayout() {
    try {
        const cards = document.querySelectorAll('.pro-service-card'); // Select all service cards
        const isNarrow = window.innerWidth <= 400; // Check if the window width is 400px or less

        cards.forEach(card => {
            const columns = card.querySelectorAll('.pro-service-column'); // Select all columns inside the card

            if (columns.length < 3) {
                console.warn('Expected at least 3 columns, but found fewer.');
                return; // If the layout is not as expected, exit early to avoid errors
            }

            // Apply the responsive layout changes
            columns.forEach((column, index) => {
                column.style.width = isNarrow ? '100%' : ''; // If the screen is narrow, set column width to 100%, otherwise reset
                column.style.marginRight = index === 0 && !isNarrow ? '1.5rem' : '0'; // Add margin only for the first column on wider screens
            });

            if (isNarrow) {
                card.style.flexDirection = 'column'; // Stack columns vertically on narrow screens
                columns[2].style.alignItems = 'flex-start'; // Align the third column to the start
                columns[2].style.marginTop = '0.25rem'; // Add some space above the third column
                columns[2].style.paddingTop = '0.5rem'; // Add some padding to the top of the third column
                columns[2].style.borderTop = '1px solid #e0e0e0'; // Add a border to the top of the third column

                // Reorder the columns to ensure the third one is placed correctly
                if (columns[1].nextElementSibling !== columns[2]) {
                    card.insertBefore(columns[2], columns[1].nextSibling);
                }
            } else {
                // Reset the layout for wider screens
                card.style.flexDirection = ''; // Set the direction back to row (default)
                columns[2].style.alignItems = ''; // Reset alignment
                columns[2].style.marginTop = ''; // Reset margin
                columns[2].style.paddingTop = ''; // Reset padding
                columns[2].style.borderTop = ''; // Reset border

                // Ensure the third column is the last child in the flex container
                if (card.lastElementChild !== columns[2]) {
                    card.appendChild(columns[2]);
                }
            }
        });
    } catch (error) {
        console.error(`Error adjusting layout: ${error.message}`);
    }
}

// Initialize the rate formatting and layout adjustment functions with error handling
function initializeAndAdjust() {
    try {
        updateRateDisplays(); // Update rates when the page loads
        adjustLayout(); // Adjust layout when the page loads
    } catch (error) {
        console.error(`Error initializing and adjusting: ${error.message}`);
    }
}

// Add event listeners for the load and resize events
window.addEventListener('load', initializeAndAdjust);
window.addEventListener('resize', adjustLayout);

// Global error handler to catch unexpected errors
window.onerror = function (message, source, lineno, colno, error) {
    console.error(`Global error: ${message} at ${source}:${lineno}:${colno} - ${error.message}`);
};
