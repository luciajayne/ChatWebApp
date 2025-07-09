document.addEventListener('DOMContentLoaded', function() {
    const messageForm = document.getElementById('messageForm');
    const messageInput = document.getElementById('messageInput');
    const messagesDiv = document.getElementById('messages');
    
    setInterval(function() {
        fetch('/get_messages')
            .then(response => response.text())
            .then(html => {
                messagesDiv.innerHTML = html;
            });
    }, 2000);
    
    messageForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = messageInput.value;
        
        const formData = new FormData();
        formData.append('message', message);
        
        fetch('/send_message', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                messageInput.value = '';
            }
        });
    });
});