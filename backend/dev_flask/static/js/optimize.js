document.getElementById('uploadForm').addEventListener('submit', async function (event) {

    event.preventDefault();
    const fileInput = document.getElementById('file');
    const file = fileInput.files[0];


    if (!file) {
        alert("Please select a CSV file to upload.");
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('loadFromDB', false); // Indicate that this is a file upload
    formData.append('numVehicles', document.getElementById('numVehicles-upload').value || 0);

    console.log("Uploading file:", file.name, "with number of vehicles:", formData.get('numVehicles'));

    // Call the upload function
    await upload(formData);

});

document.getElementById('uploadForm-db').addEventListener('submit', async function (event) {
    event.preventDefault();
    const formData = new FormData();
    const dbUploadInput = document.getElementById('numVehicles');
    formData.append('numVehicles', dbUploadInput.value);
    formData.append('loadFromDB', true);
    upload(formData);
});


async function upload(formData) {
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error("Server error:", errorText);
            return;
        }

        const result = await response.json();

        if (result) {
            // clear space for new results
            const uploadStats = document.getElementById('uploadStats');
            uploadStats.innerHTML = '';
            console.log("File uploaded successfully:", result.filename);
            window.location.href = `/optimize?filename=${encodeURIComponent(result.filename)}&numVehicles=${encodeURIComponent(result.numVehicles)}`;
        
        } else {
            alert("File upload failed.");
        }

    } catch (error) {
        console.error("Upload error:", error);
        alert("An error occurred while uploading the file.");
    }
}

$(document).ready(function() {
    // Automatically find the table inside the div and assign an ID
    $('#vehicle-table-wrapper table').attr('id', 'vehicleTable');

    // Initialize DataTables on the identified table
    $('#vehicleTable').DataTable({
        "pageLength": 10,          // Number of rows per page
        "lengthChange": false,     // Hide "show x entries"
        "ordering": true,          // Enable column sorting
        "info": false              // Hide table info (e.g., "Showing 1 to 10 of 50")
    });
});