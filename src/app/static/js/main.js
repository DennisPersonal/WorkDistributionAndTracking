/**
 * Work Distribution and Tracking System - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Work Distribution System JS loaded');
    
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Profile edit modal handling
    const editProfileBtn = document.getElementById('editProfileBtn');
    const editProfileModal = document.getElementById('editProfileModal');
    
    if (editProfileBtn && editProfileModal) {
        editProfileBtn.addEventListener('click', function() {
            console.log('Edit Profile button clicked');
            const modal = new bootstrap.Modal(editProfileModal);
            modal.show();
        });
    }
    
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Task progress bars
    const progressBars = document.querySelectorAll('.progress-bar[data-progress]');
    progressBars.forEach(function(bar) {
        const progress = bar.getAttribute('data-progress');
        if (progress) {
            bar.style.width = progress + '%';
            bar.textContent = progress + '%';
        }
    });
    
    // Workload color coding
    const workloadBadges = document.querySelectorAll('.workload-badge');
    workloadBadges.forEach(function(badge) {
        const workload = parseInt(badge.textContent);
        if (workload < 60) {
            badge.classList.add('bg-success');
        } else if (workload < 85) {
            badge.classList.add('bg-warning');
        } else {
            badge.classList.add('bg-danger');
        }
    });
    
    // Task status updates
    const taskStatusButtons = document.querySelectorAll('.task-status-btn');
    taskStatusButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const taskId = this.getAttribute('data-task-id');
            const newStatus = this.getAttribute('data-status');
            
            fetch(`/tasks/${taskId}/status`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrf_token]')?.value || ''
                },
                body: JSON.stringify({ status: newStatus })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Failed to update task status: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to update task status');
            });
        });
    });
    
    // AI analysis form enhancement
    const aiForm = document.getElementById('aiAnalysisForm');
    if (aiForm) {
        const taskInput = aiForm.querySelector('[name="task_input"]');
        const exampleBtn = aiForm.querySelector('.example-btn');
        
        if (exampleBtn && taskInput) {
            exampleBtn.addEventListener('click', function() {
                taskInput.value = "John should create a quarterly report by Friday. Sarah needs to prepare presentation slides for the client meeting. Mike can handle customer support tickets this week.";
            });
        }
    }
    
    // Organization chart interactions
    const orgNodes = document.querySelectorAll('.org-node');
    orgNodes.forEach(function(node) {
        node.addEventListener('click', function() {
            const userId = this.getAttribute('data-user-id');
            if (userId) {
                window.location.href = `/users/${userId}`;
            }
        });
        
        // Add hover effect
        node.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 5px 15px rgba(0,0,0,0.2)';
        });
        
        node.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });
    
    // Dashboard charts (placeholder for future implementation)
    if (typeof Chart !== 'undefined') {
        // Initialize dashboard charts here
        console.log('Chart.js is available');
    }
    
    // Print functionality
    const printButtons = document.querySelectorAll('.print-btn');
    printButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            window.print();
        });
    });
    
    // Export functionality
    const exportButtons = document.querySelectorAll('.export-btn');
    exportButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const format = this.getAttribute('data-format') || 'csv';
            const type = this.getAttribute('data-type') || 'tasks';
            
            fetch(`/export/${type}?format=${format}`)
            .then(response => response.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${type}_export.${format}`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            })
            .catch(error => {
                console.error('Export error:', error);
                alert('Failed to export data');
            });
        });
    });
});

// Utility functions
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-bg-${type} border-0`;
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '1055';
    document.body.appendChild(container);
    return container;
}

// Edit Profile modal function
function openEditProfileModal() {
    console.log('openEditProfileModal called');
    const modalElement = document.getElementById('editProfileModal');
    if (modalElement) {
        console.log('Modal element found');
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
    } else {
        console.error('Edit Profile modal not found');
        alert('Edit Profile feature is not available. Please refresh the page.');
    }
}

// Confirm dialog
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}