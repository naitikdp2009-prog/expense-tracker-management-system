/* ==========================================================================
   Financial Assistant Chat Interface JavaScript
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.getElementById('chatMessages');

    if (!chatForm) return;

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const userText = chatInput.value.trim();
        if (!userText) return;

        // Append User Message
        appendMessage(userText, 'user');
        chatInput.value = '';

        // Typing Indicator
        const typingId = appendTypingIndicator();

        try {
            const res = await fetch('/api/chat/message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userText })
            });
            const data = await res.json();
            
            removeTypingIndicator(typingId);
            appendMessage(formatBotMarkdown(data.reply), 'bot');
        } catch (err) {
            console.error(err);
            removeTypingIndicator(typingId);
            appendMessage("Sorry, I encountered an error connecting to the financial assistant.", 'bot');
        }
    });

    // Quick suggestion buttons
    const suggestBtns = document.querySelectorAll('.chat-suggest-btn');
    suggestBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            chatInput.value = btn.textContent.trim();
            chatForm.dispatchEvent(new Event('submit'));
        });
    });
});

function appendMessage(text, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble chat-${sender}`;
    bubble.innerHTML = text;
    chatMessages.appendChild(bubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function appendTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    const id = 'typing_' + Date.now();
    const bubble = document.createElement('div');
    bubble.id = id;
    bubble.className = 'chat-bubble chat-bot';
    bubble.innerHTML = "<i class='fas fa-circle-notch fa-spin'></i> Analyzing database...";
    chatMessages.appendChild(bubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function formatBotMarkdown(text) {
    let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
    formatted = formatted.replace(/\n/g, '<br>');
    return formatted;
}
