/**
 * Activity Tracker
 * Monitors user interactions and sends data to backend
 */

class ActivityTracker {
    constructor() {
        this.activities = [];
        this.settings = {
            enable_monitoring: true,
            idle_threshold: 300,
            extended_idle_threshold: 900,
            heartbeat_interval: 60,
            enable_idle_alerts: true
        };
        this.lastActivityTime = Date.now();
        this.isIdle = false;
        this.heartbeatTimer = null;
        this.sendTimer = null;
        this.initialized = false;
    }

    /**
     * Initialize the activity tracker
     */
    async init() {
        if (this.initialized) {
            console.log('Activity tracker already initialized');
            return;
        }

        console.log('Initializing activity tracker...');

        // Load settings from server
        await this.loadSettings();

        if (!this.settings.enable_monitoring) {
            console.log('Activity monitoring is disabled');
            return;
        }

        // Set up event listeners
        this.setupEventListeners();

        // Start heartbeat
        this.startHeartbeat();

        // Start periodic send timer (every 30 seconds)
        this.startSendTimer();

        this.initialized = true;
        console.log('Activity tracker initialized successfully');
    }

    /**
     * Load monitoring settings from server
     */
    async loadSettings() {
        try {
            const response = await fetch('/crm/activity/settings/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.settings = data.settings;
                    console.log('Loaded monitoring settings:', this.settings);
                }
            }
        } catch (error) {
            console.error('Error loading monitoring settings:', error);
        }
    }

    /**
     * Set up event listeners for user interactions
     */
    setupEventListeners() {
        // Mouse movement (throttled)
        let mouseMoveTimeout;
        document.addEventListener('mousemove', (e) => {
            if (mouseMoveTimeout) return;
            
            mouseMoveTimeout = setTimeout(() => {
                this.logActivity('mouse_move', {
                    x: e.clientX,
                    y: e.clientY
                });
                mouseMoveTimeout = null;
            }, 1000); // Throttle to once per second
        });

        // Mouse clicks
        document.addEventListener('click', (e) => {
            this.logActivity('mouse_click', {
                x: e.clientX,
                y: e.clientY,
                target: e.target.tagName
            });
        });

        // Keyboard input (don't capture actual keys for privacy)
        document.addEventListener('keydown', () => {
            this.logActivity('keyboard', {
                timestamp: Date.now()
            });
        });

        // Scroll events (throttled)
        let scrollTimeout;
        document.addEventListener('scroll', () => {
            if (scrollTimeout) return;
            
            scrollTimeout = setTimeout(() => {
                this.logActivity('scroll', {
                    scrollY: window.scrollY
                });
                scrollTimeout = null;
            }, 1000); // Throttle to once per second
        });

        // Window focus/blur
        window.addEventListener('focus', () => {
            this.logActivity('window_focus', {});
            this.isIdle = false;
        });

        window.addEventListener('blur', () => {
            this.logActivity('window_blur', {});
        });

        // Page visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.logActivity('window_blur', {});
            } else {
                this.logActivity('window_focus', {});
                this.isIdle = false;
            }
        });
    }

    /**
     * Log an activity
     */
    logActivity(type, details = {}) {
        this.lastActivityTime = Date.now();
        this.isIdle = false;

        const activity = {
            type: type,
            timestamp: new Date().toISOString(),
            details: details,
            page_url: window.location.href,
            page_title: document.title
        };

        this.activities.push(activity);

        // If we have too many activities, send them
        if (this.activities.length >= 50) {
            this.sendActivities();
        }
    }

    /**
     * Start heartbeat timer
     */
    startHeartbeat() {
        this.heartbeatTimer = setInterval(() => {
            // Check if user is idle
            const timeSinceActivity = (Date.now() - this.lastActivityTime) / 1000;

            if (timeSinceActivity >= this.settings.idle_threshold) {
                if (!this.isIdle) {
                    this.isIdle = true;
                    console.log('User is now idle');

                    // Show idle alert if enabled
                    if (this.settings.enable_idle_alerts && 
                        timeSinceActivity < this.settings.extended_idle_threshold) {
                        this.showIdleAlert();
                    }
                }
            }

            // Send heartbeat
            this.logActivity('heartbeat', {
                is_idle: this.isIdle,
                time_since_activity: timeSinceActivity
            });

        }, this.settings.heartbeat_interval * 1000);
    }

    /**
     * Start periodic send timer
     */
    startSendTimer() {
        this.sendTimer = setInterval(() => {
            if (this.activities.length > 0) {
                this.sendActivities();
            }
        }, 30000); // Send every 30 seconds
    }

    /**
     * Send activities to server
     */
    async sendActivities() {
        if (this.activities.length === 0) {
            return;
        }

        const activitiesToSend = [...this.activities];
        this.activities = []; // Clear the queue

        try {
            const response = await fetch('/crm/activity/log/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    activities: activitiesToSend
                })
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    console.log(`Sent ${data.activities_logged} activities to server`);
                } else {
                    console.error('Error logging activities:', data.error);
                    // Put activities back in queue if there was an error
                    this.activities = [...activitiesToSend, ...this.activities];
                }
            } else {
                console.error('Failed to send activities:', response.status);
                // Put activities back in queue
                this.activities = [...activitiesToSend, ...this.activities];
            }
        } catch (error) {
            console.error('Error sending activities:', error);
            // Put activities back in queue
            this.activities = [...activitiesToSend, ...this.activities];
        }
    }

    /**
     * Show idle alert to user
     */
    showIdleAlert() {
        // Create a subtle notification
        const alert = document.createElement('div');
        alert.className = 'activity-idle-alert';
        alert.innerHTML = `
            <div class="alert alert-warning alert-dismissible fade show" role="alert" style="position: fixed; top: 70px; right: 20px; z-index: 9999; max-width: 400px;">
                <i class="fas fa-clock"></i>
                <strong>Idle Detected</strong>
                <p class="mb-0">You've been inactive for a while. Your time is still being tracked.</p>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        document.body.appendChild(alert);

        // Auto-remove after 10 seconds
        setTimeout(() => {
            alert.remove();
        }, 10000);
    }

    /**
     * Get CSRF token from cookie
     */
    getCsrfToken() {
        const name = 'csrftoken';
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

    /**
     * Get activity summary from server
     */
    async getActivitySummary() {
        try {
            const response = await fetch('/crm/activity/summary/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    return data.summary;
                }
            }
        } catch (error) {
            console.error('Error getting activity summary:', error);
        }
        return null;
    }

    /**
     * Stop tracking
     */
    stop() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }

        if (this.sendTimer) {
            clearInterval(this.sendTimer);
            this.sendTimer = null;
        }

        // Send any remaining activities
        if (this.activities.length > 0) {
            this.sendActivities();
        }

        this.initialized = false;
        console.log('Activity tracker stopped');
    }
}

// Create global instance
window.activityTracker = new ActivityTracker();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.activityTracker.init();
    });
} else {
    window.activityTracker.init();
}

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (window.activityTracker) {
        window.activityTracker.stop();
    }
});