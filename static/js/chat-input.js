/**
 * Chat Input Functionality
 * Handles textarea auto-resize, button enabling/disabling, and input visibility
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get reference to the message input and submit button
    const messageInput = document.getElementById('messageInput');
    const submitButton = document.querySelector('button[type="submit"]');
    
    if (messageInput) {
        // Auto-resize textarea based on content
        messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
            
            // Enable/disable send button based on content
            if (submitButton) {
                submitButton.disabled = this.value.trim() === '';
            }
        });
        
        // Ensure chat input is always visible by scrolling to bottom when focusing on input
        messageInput.addEventListener('focus', function() {
            window.scrollTo(0, document.body.scrollHeight);
            
            // For mobile browsers that might handle scroll differently
            setTimeout(() => {
                window.scrollTo(0, document.body.scrollHeight);
            }, 100);
        });
        
        // Initialize the textarea height and button state
        if (messageInput.value.trim() !== '') {
            messageInput.style.height = (messageInput.scrollHeight) + 'px';
            if (submitButton) {
                submitButton.disabled = false;
            }
        }
    }
    
    // Add functionality to close modal when clicking outside
    const modal = document.getElementById('fullTableModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.classList.add('hidden');
            }
        });
    }
    
    // Handle form submission
    const chatForm = document.getElementById('chatForm');
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            if (messageInput && messageInput.value.trim() === '') {
                e.preventDefault();
                return false;
            }
            
            // Additional form submission logic can be added here
        });
    }
});