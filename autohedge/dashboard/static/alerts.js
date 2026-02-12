let currentEditingId = null;

// Load alerts on page load
document.addEventListener('DOMContentLoaded', () => {
    loadAlerts();
    loadNotifications();
    checkMonitorStatus();
    
    // Refresh every 30 seconds
    setInterval(loadAlerts, 30000);
    setInterval(loadNotifications, 30000);
    setInterval(checkMonitorStatus, 10000);
});

// Alert form submission
document.getElementById('alertForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const channels = Array.from(document.querySelectorAll('input[name="channels"]:checked'))
        .map(cb => cb.value);
    
    if (channels.length === 0) {
        alert('Please select at least one notification channel');
        return;
    }
    
    const alertData = {
        name: document.getElementById('alertName').value,
        alert_type: document.getElementById('alertType').value,
        stock: document.getElementById('alertStock').value.toUpperCase(),
        condition: document.getElementById('alertCondition').value,
        threshold: parseFloat(document.getElementById('alertThreshold').value),
        notification_channels: channels,
        cooldown_minutes: parseInt(document.getElementById('alertCooldown').value),
        enabled: true
    };
    
    try {
        const url = currentEditingId 
            ? `/api/alerts/${currentEditingId}`
            : '/api/alerts';
        
        const method = currentEditingId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(alertData)
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            closeModal();
            loadAlerts();
            alert(result.message || 'Alert saved successfully!');
        } else {
            alert(`Error: ${result.message}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
});

async function loadAlerts() {
    try {
        const response = await fetch('/api/alerts');
        const result = await response.json();
        
        if (result.status === 'success') {
            displayAlerts(result.data);
        }
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

function displayAlerts(alerts) {
    const container = document.getElementById('alertsList');
    
    if (alerts.length === 0) {
        container.innerHTML = `
            <p style="color: #7f8c8d; text-align: center; padding: 2rem;">
                No alerts configured. Click "Create Alert" to get started!
            </p>
        `;
        return;
    }
    
    container.innerHTML = alerts.map(alert => `
        <div class="alert-item ${alert.enabled ? '' : 'disabled'}">
            <div class="alert-header">
                <div class="alert-title">
                    ${alert.enabled ? '🔔' : '🔕'} ${alert.name}
                </div>
                <div class="alert-actions">
                    <button class="btn-small btn-test" onclick="testAlert('${alert.id}')">
                        Test
                    </button>
                    <button class="btn-small btn-toggle ${alert.enabled ? 'enabled' : ''}" 
                            onclick="toggleAlert('${alert.id}')">
                        ${alert.enabled ? 'Disable' : 'Enable'}
                    </button>
                    <button class="btn-small btn-delete" onclick="deleteAlert('${alert.id}')">
                        Delete
                    </button>
                </div>
            </div>
            <div style="color: #7f8c8d; font-size: 0.9rem;">
                <strong>${alert.stock}</strong> price ${alert.condition} 
                <strong>$${alert.threshold.toFixed(2)}</strong>
                <br>
                Channels: ${alert.notification_channels.join(', ')} | 
                Cooldown: ${alert.cooldown_minutes} min
                ${alert.last_triggered ? `<br>Last triggered: ${new Date(alert.last_triggered).toLocaleString()}` : ''}
            </div>
        </div>
    `).join('');
}

async function toggleAlert(alertId) {
    try {
        const response = await fetch(`/api/alerts/${alertId}/toggle`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            loadAlerts();
        } else {
            alert(`Error: ${result.message}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function deleteAlert(alertId) {
    if (!confirm('Are you sure you want to delete this alert?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/alerts/${alertId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            loadAlerts();
        } else {
            alert(`Error: ${result.message}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function testAlert(alertId) {
    try {
        const response = await fetch(`/api/alerts/test/${alertId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        alert(result.message);
        
        if (result.status === 'success') {
            loadNotifications();
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function loadNotifications() {
    try {
        const response = await fetch('/api/alerts/notifications');
        const result = await response.json();
        
        if (result.status === 'success') {
            displayNotifications(result.data, result.unread_count);
        }
    } catch (error) {
        console.error('Error loading notifications:', error);
    }
}

function displayNotifications(notifications, unreadCount) {
    document.getElementById('notifCount').textContent = unreadCount;
    
    if (notifications.length > 0) {
        document.getElementById('notificationsPanel').style.display = 'block';
    }
    
    const container = document.getElementById('notificationsList');
    
    if (notifications.length === 0) {
        container.innerHTML = '<p style="color: #7f8c8d; padding: 1rem;">No notifications yet</p>';
        return;
    }
    
    container.innerHTML = notifications.slice(0, 10).map(notif => `
        <div class="notification-item ${notif.read ? '' : 'unread'}">
            <div style="font-weight: 600; margin-bottom: 0.5rem;">
                ${notif.alert_name}
            </div>
            <div style="font-size: 0.9rem; color: #7f8c8d;">
                ${notif.message}
            </div>
            <div style="font-size: 0.8rem; color: #95a5a6; margin-top: 0.5rem;">
                ${new Date(notif.timestamp).toLocaleString()}
            </div>
        </div>
    `).join('');
}

async function clearNotifications() {
    if (!confirm('Clear all notifications?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/alerts/notifications', {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            loadNotifications();
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function checkMonitorStatus() {
    try {
        const response = await fetch('/api/alerts/monitor/status');
        const result = await response.json();
        
        if (result.status === 'success') {
            const status = result.data;
            const statusEl = document.getElementById('monitorStatus');
            const dot = statusEl.querySelector('.status-dot');
            
            if (status.running) {
                dot.classList.add('active');
                statusEl.innerHTML = `
                    <span class="status-dot active"></span>
                    Monitor Active (${status.active_alerts} alerts, ${status.total_checks} checks)
                `;
            } else {
                dot.classList.remove('active');
                statusEl.innerHTML = `
                    <span class="status-dot"></span>
                    Monitor Stopped
                `;
            }
        }
    } catch (error) {
        console.error('Error checking monitor status:', error);
    }
}

function showCreateAlert() {
    currentEditingId = null;
    document.getElementById('modalTitle').textContent = 'Create Alert';
    document.getElementById('alertForm').reset();
    document.querySelector('input[name="channels"][value="web"]').checked = true;
    document.getElementById('alertModal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('alertModal').style.display = 'none';
    currentEditingId = null;
}

// Close modal on outside click
window.onclick = function(event) {
    const modal = document.getElementById('alertModal');
    if (event.target === modal) {
        closeModal();
    }
}
