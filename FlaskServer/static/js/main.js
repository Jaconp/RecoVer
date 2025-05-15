document.addEventListener('DOMContentLoaded', function() {
    // Debug authentication status
    console.log("Authentication check running...");
    const isAuthenticated = document.body.classList.contains('user-authenticated');
    console.log("Is authenticated:", isAuthenticated);
    
    // Check if user elements are present
    const userElements = document.querySelectorAll('.user-element');
    console.log("User elements found:", userElements.length);
    
    // Enable tooltips everywhere
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Enable popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    
    // Image preview for file inputs
    const fileInputs = document.querySelectorAll('.file-input');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const preview = document.querySelector(this.dataset.preview);
            const file = this.files[0];
            
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            } else {
                preview.src = '';
                preview.style.display = 'none';
            }
        });
    });
    
    // Date range validation for search form
    const dateFromInput = document.getElementById('date_from');
    const dateToInput = document.getElementById('date_to');
    
    if (dateFromInput && dateToInput) {
        dateFromInput.addEventListener('change', function() {
            dateToInput.min = this.value;
        });
        
        dateToInput.addEventListener('change', function() {
            dateFromInput.max = this.value;
        });
    }
    
    // Admin dashboard tabs
    const adminTabTriggers = document.querySelectorAll('.admin-tab-trigger');
    if (adminTabTriggers.length > 0) {
        adminTabTriggers.forEach(trigger => {
            trigger.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Hide all tab contents
                const tabContents = document.querySelectorAll('.admin-tab-content');
                tabContents.forEach(content => {
                    content.classList.remove('show', 'active');
                });
                
                // Show the selected tab content
                const targetId = this.getAttribute('data-bs-target');
                const targetContent = document.querySelector(targetId);
                targetContent.classList.add('show', 'active');
                
                // Update active state for tab triggers
                adminTabTriggers.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }
    
    // Form validation styling
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Auto-dismiss alerts after 5 seconds
    const autoAlerts = document.querySelectorAll('.alert-auto-dismiss');
    autoAlerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});
