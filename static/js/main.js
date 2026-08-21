// Auth Modal Logic
const authModal = document.getElementById('auth-modal');
const modalClose = document.getElementById('modal-close');
const loginView = document.getElementById('login-view');
const signupView = document.getElementById('signup-view');
const loginLeft = document.getElementById('login-left-content');
const signupLeft = document.getElementById('signup-left-content');
const body = document.body;
const navbar = document.querySelector('.navbar');

function openAuthModal(viewType) {
    if (!authModal) return;
    
    // Show modal
    authModal.style.display = 'flex';
    body.style.overflow = 'hidden'; // Prevent scrolling
    
    // Switch to correct view
    switchAuthView(viewType);
}

function closeAuthModal() {
    if (!authModal) return;
    authModal.style.display = 'none';
    body.style.overflow = 'auto'; // Restore scrolling
    
    // Clear url params if any
    const url = new URL(window.location);
    url.searchParams.delete('auth');
    window.history.replaceState({}, '', url);
}

function switchAuthView(viewType) {
    if (viewType === 'login') {
        loginView.style.display = 'block';
        signupView.style.display = 'none';
        
        loginLeft.style.display = 'block';
        signupLeft.style.display = 'none';
    } else if (viewType === 'signup') {
        loginView.style.display = 'none';
        signupView.style.display = 'block';
        
        loginLeft.style.display = 'none';
        signupLeft.style.display = 'block';
    }
}

function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const icon = input.nextElementSibling.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// Event Listeners for Modal Close
if (modalClose) {
    modalClose.addEventListener('click', closeAuthModal);
}

if (authModal) {
    authModal.addEventListener('click', function(e) {
        if (e.target === authModal) {
            closeAuthModal();
        }
    });
}

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && authModal && authModal.style.display === 'flex') {
        closeAuthModal();
    }
});

// Mobile menu toggle
const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
const navLinks = document.querySelector('.nav-links');
const navbarActions = document.querySelector('.navbar-actions');

if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', () => {
        const isExpanded = navLinks.style.display === 'flex';
        
        if (isExpanded) {
            navLinks.style.display = 'none';
            navbarActions.style.display = 'none';
            navbar.style.background = 'rgba(255, 255, 255, 0.7)';
        } else {
            navLinks.style.display = 'flex';
            navLinks.style.flexDirection = 'column';
            navLinks.style.position = 'absolute';
            navLinks.style.top = '100%';
            navLinks.style.left = '0';
            navLinks.style.right = '0';
            navLinks.style.background = 'white';
            navLinks.style.padding = '1rem';
            navLinks.style.borderBottom = '1px solid var(--border-color)';
            
            navbarActions.style.display = 'flex';
            navbarActions.style.flexDirection = 'column';
            navbarActions.style.position = 'absolute';
            navbarActions.style.top = 'calc(100% + 200px)';
            navbarActions.style.left = '0';
            navbarActions.style.right = '0';
            navbarActions.style.background = 'white';
            navbarActions.style.padding = '1rem';
            
            navbar.style.background = 'white';
        }
    });
}

// Check URL parameters for auth modal opening
document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const authParam = urlParams.get('auth');
    
    if (authParam === 'login' || authParam === 'register') {
        openAuthModal(authParam === 'register' ? 'signup' : 'login');
    }
    
    // Setup number counting animation for statistics
    const statNumbers = document.querySelectorAll('.stat-number');
    if (statNumbers.length > 0) {
        const observerOptions = {
            threshold: 0.5
        };
        
        const statsObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);
        
        statNumbers.forEach(stat => {
            statsObserver.observe(stat);
        });
    }
});

// Navbar scroll effect
window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});
function handleGoogleAuth(event, view) {
    event.preventDefault();
    let role = 'client';
    if (view === 'signup') {
        let selectedRole = document.querySelector('.auth-view:not([style*="display: none"]) input[name="role"]:checked');
        if (selectedRole) {
            role = selectedRole.value;
        } else {
            alert('Please select whether you want to join as a Client or Freelancer first.');
            return;
        }
    }
    window.location.href = '/login/google?role=' + role;
}
