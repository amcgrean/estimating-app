$(document).ready(function () {
    // Initialize Select2 for customer dropdown
    $('#customer_id').select2({
        placeholder: "Select Customer",
        allowClear: true
    });

    // Map of checkboxes to sections
    const sections = {
        'include_framing': '#framing-section',
        'include_siding': '#siding-section',
        'include_shingles': '#shingles-section',
        'include_deck': '#deck-section',
        'include_doors': '#doors-section',
        'include_windows': '#windows-section',
        'include_trim': '#trim-section'
    };

    // Add event listeners to toggle section visibility
    Object.keys(sections).forEach(id => {
        const checkbox = document.getElementById(id);
        const section = document.querySelector(sections[id]);

        if (checkbox) {
            checkbox.addEventListener('change', function () {
                section.style.display = checkbox.checked ? 'block' : 'none';
            });

            // Initialize visibility based on checkbox state
            section.style.display = checkbox.checked ? 'block' : 'none';
        }
    });
});
