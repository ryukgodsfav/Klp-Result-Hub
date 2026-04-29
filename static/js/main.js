/**
 * KLP Roorkee — Main JavaScript
 * Handles: smooth scrolling, navbar scroll effect, partner slider
 */

// ── Navbar scroll effect ──────────────────────────────────────────────────────
// Adds a subtle shadow on scroll
window.addEventListener('scroll', function () {
    const nav = document.getElementById('mainNav');
    if (!nav) return;
    if (window.scrollY > 50) {
        nav.style.boxShadow = '0 4px 30px rgba(0,0,0,0.4)';
    } else {
        nav.style.boxShadow = '0 2px 20px rgba(0,0,0,0.3)';
    }
});

// ── Smooth scroll for anchor links ───────────────────────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            e.preventDefault();
            const offset = 80; // navbar height
            const top = target.getBoundingClientRect().top + window.scrollY - offset;
            window.scrollTo({ top, behavior: 'smooth' });
        }
    });
});

// ── Auto-dismiss flash alerts after 5 seconds ─────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            // Bootstrap 5 dismiss
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });
});
