let dropdownData = {};

// Fetch dropdown data
fetch("/static/squareup_params.json")
    .then(response => response.json())
    .then(data => {
        dropdownData = data;
    })
    .catch(error => console.error("Error loading dropdown data:", error));

function updateChildDropdown() {
    let businessDropdown = document.getElementById("business_name");
    let extraDropdown = document.getElementById("extra_option");
    let selectedBusiness = businessDropdown.value;
    let extraSection = document.getElementById("extra_section");

    extraDropdown.innerHTML = ""; // Clear previous options

    if (selectedBusiness in dropdownData) {
        dropdownData[selectedBusiness].forEach(option => {
            let opt = document.createElement("option");
            opt.value = option;
            opt.textContent = option;
            extraDropdown.appendChild(opt);
        });
        extraSection.classList.remove("hidden");
    } else {
        extraSection.classList.add("hidden");
    }
}
