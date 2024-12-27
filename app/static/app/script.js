// script.js
document.addEventListener("DOMContentLoaded", function() {
    // Handle drag-and-drop functionality for each app
    {% for app in apps %}
        let dropArea = document.getElementById('drop-area-{{ app.pk }}');
        let fileInput = document.getElementById('file-input-{{ app.pk }}');
        let uploadBtn = document.getElementById('upload-btn-{{ app.pk }}');

        // Drag over event
        dropArea.addEventListener('dragover', function(event) {
            event.preventDefault();
            event.stopPropagation();
            dropArea.style.backgroundColor = '#e9e9e9';
        });

        // Drag leave event
        dropArea.addEventListener('dragleave', function(event) {
            dropArea.style.backgroundColor = '#fff';
        });

        // Drop event
        dropArea.addEventListener('drop', function(event) {
            event.preventDefault();
            event.stopPropagation();
            let file = event.dataTransfer.files[0];
            fileInput.files = event.dataTransfer.files;
            console.log('File dropped for app {{ app.name }}: ', file.name);
            // You can implement file upload logic here for each app
        });

        // Handle file input change event (if the user selects a file instead of dragging)
        fileInput.addEventListener('change', function(event) {
            let file = fileInput.files[0];
            console.log('File selected for app {{ app.name }}: ', file.name);
            // You can implement file upload logic here
        });

        // Upload button logic (trigger file upload)
        uploadBtn.addEventListener('click', function() {
            let file = fileInput.files[0];
            if (file) {
                console.log('Uploading file for app {{ app.name }}: ', file.name);
                // Implement file upload logic here
            }
        });
    {% endfor %}
});
