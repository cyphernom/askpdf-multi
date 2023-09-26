//Copyright (c)2023 btCode::Orange. All rights reserved.
const pdfInput = document.getElementById('pdfInput');
const questionInput = document.getElementById('questionInput');
const chatBox = document.querySelector('.chat-box');
const submitButton = document.querySelector('button');

pdfInput.addEventListener('change', async () => {
    const files = pdfInput.files;
    const formData = new FormData();

    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }
    
    try {
        const res = await fetch('http://localhost:8000/upload/', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        console.log(data);
    } catch (err) {
        console.error("Error uploading PDF:", err);
    }
});

async function askQuestion() {
    const question = questionInput.value;

    // Append user's message to chat box
    appendMessageToChat(question, 'user-message');

    // Disable the button and provide feedback
    submitButton.disabled = true;
    submitButton.textContent = "Sending...";

    try {
        const res = await fetch(`http://localhost:8000/query/?question=${question}`);
        const data = await res.json();
        
        appendMessageToChat(data.response, 'bot-message');
    } catch (err) {
        console.error("Error querying:", err);
        appendMessageToChat(`Sorry, I couldn't process that.`, 'bot-message');
    } finally {
        // Re-enable the button and reset its text
        submitButton.disabled = false;
        submitButton.textContent = "Send";
        questionInput.value = '';  // Clear the input
    }
}

function appendMessageToChat(message, sender) {
    const messageElem = document.createElement('div');
    messageElem.className = `message ${sender}`;

    if (sender === 'bot-message') {
        message = marked.parse(message);  // Convert markdown to HTML for bot's messages
    }

    messageElem.innerHTML = message;
    chatBox.appendChild(messageElem);
    chatBox.scrollTop = chatBox.scrollHeight;  // Auto-scroll to the bottom
}
