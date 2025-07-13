// MMORPG Board JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            var target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // AJAX form submissions
    document.querySelectorAll('.ajax-form').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            submitAjaxForm(this);
        });
    });

    // Load more content
    var loadMoreBtn = document.querySelector('.load-more-btn');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', function(e) {
            e.preventDefault();
            loadMoreContent(this);
        });
    }

    // Search functionality
    var searchInput = document.querySelector('#search-input');
    if (searchInput) {
        var searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                performSearch(searchInput.value);
            }, 300);
        });
    }

    // Notification updates
    updateNotificationCount();
    setInterval(updateNotificationCount, 30000); // Update every 30 seconds
});

// AJAX form submission
function submitAjaxForm(form) {
    var formData = new FormData(form);
    var submitBtn = form.querySelector('button[type="submit"]');
    var originalText = submitBtn.textContent;
    
    // Show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Отправка...';
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', data.message || 'Операция выполнена успешно!');
            if (data.redirect) {
                window.location.href = data.redirect;
            }
        } else {
            showAlert('danger', data.error || 'Произошла ошибка!');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('danger', 'Произошла ошибка при отправке формы');
    })
    .finally(() => {
        // Restore button state
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    });
}

// Load more content
function loadMoreContent(button) {
    var url = button.getAttribute('data-url');
    var container = document.querySelector(button.getAttribute('data-container'));
    
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Загрузка...';
    
    fetch(url)
    .then(response => response.text())
    .then(html => {
        container.insertAdjacentHTML('beforeend', html);
        button.remove();
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('danger', 'Ошибка при загрузке содержимого');
        button.disabled = false;
        button.innerHTML = 'Загрузить еще';
    });
}

// Show alert
function showAlert(type, message) {
    var alertContainer = document.querySelector('.alert-container') || document.body;
    var alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.parentNode.removeChild(alert);
        }
    }, 5000);
}

// Update notification count
function updateNotificationCount() {
    if (!document.querySelector('.notification-badge')) return;
    
    fetch('/notifications/api/count/')
    .then(response => response.json())
    .then(data => {
        var badge = document.querySelector('.notification-badge');
        if (data.count > 0) {
            badge.textContent = data.count;
            badge.style.display = 'block';
        } else {
            badge.style.display = 'none';
        }
    })
    .catch(error => {
        console.error('Error updating notification count:', error);
    });
}

// Mark notification as read
function markNotificationRead(notificationId) {
    fetch(`/notifications/api/${notificationId}/mark-read/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateNotificationCount();
        }
    })
    .catch(error => {
        console.error('Error marking notification as read:', error);
    });
}

// Mark all notifications as read
function markAllNotificationsRead() {
    fetch('/notifications/api/mark-all-read/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateNotificationCount();
            showAlert('success', data.message);
        }
    })
    .catch(error => {
        console.error('Error marking all notifications as read:', error);
    });
}

// Get CSRF cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Perform search
function performSearch(query) {
    if (query.length < 2) return;
    
    fetch(`/search/?q=${encodeURIComponent(query)}`)
    .then(response => response.text())
    .then(html => {
        // Update search results container
        var resultsContainer = document.querySelector('#search-results');
        if (resultsContainer) {
            resultsContainer.innerHTML = html;
        }
    })
    .catch(error => {
        console.error('Error performing search:', error);
    });
}

// Toggle post status
function togglePostStatus(postId) {
    fetch(`/api/post/${postId}/toggle-status/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            var statusBadge = document.querySelector(`[data-post-id="${postId}"] .status-badge`);
            if (statusBadge) {
                statusBadge.textContent = data.status_display;
                statusBadge.className = `badge ${data.status === 'active' ? 'bg-success' : 'bg-danger'}`;
            }
            showAlert('success', 'Статус объявления изменен');
        }
    })
    .catch(error => {
        console.error('Error toggling post status:', error);
        showAlert('danger', 'Ошибка при изменении статуса');
    });
}

// Toggle response status
function toggleResponseStatus(responseId, status) {
    fetch(`/api/response/${responseId}/toggle-status/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: new URLSearchParams({
            'status': status
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            var statusBadge = document.querySelector(`[data-response-id="${responseId}"] .status-badge`);
            if (statusBadge) {
                statusBadge.textContent = data.status_display;
                statusBadge.className = `badge ${data.status === 'accepted' ? 'bg-success' : 'bg-danger'}`;
            }
            showAlert('success', 'Статус отклика изменен');
        }
    })
    .catch(error => {
        console.error('Error toggling response status:', error);
        showAlert('danger', 'Ошибка при изменении статуса');
    });
}

// Image preview
function previewImage(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            var preview = document.querySelector('#image-preview');
            if (preview) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            }
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Confirm deletion
function confirmDelete(message) {
    return confirm(message || 'Вы уверены, что хотите удалить?');
}

// Format date
function formatDate(date) {
    return new Date(date).toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Truncate text
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Utility functions
window.MMORPGBoard = {
    showAlert: showAlert,
    updateNotificationCount: updateNotificationCount,
    markNotificationRead: markNotificationRead,
    markAllNotificationsRead: markAllNotificationsRead,
    togglePostStatus: togglePostStatus,
    toggleResponseStatus: toggleResponseStatus,
    previewImage: previewImage,
    confirmDelete: confirmDelete,
    formatDate: formatDate,
    truncateText: truncateText
}; 