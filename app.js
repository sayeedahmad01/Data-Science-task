// Grab DOM elements precisely matching index.html
const themeBtn = document.getElementById('themeBtn');
const sendBtn = document.getElementById('sendBtn');
const userInput = document.getElementById('userInput');
const welcomeMessage = document.getElementById('welcomeMessage');
const chatFeed = document.getElementById('chatFeed');
const newChatBtn = document.getElementById('newChatBtn');

// 1. Toggle Dark/Light Theme Layout
if (themeBtn) {
    themeBtn.addEventListener('click', () => {
        document.body.classList.toggle('light-mode');
    });
}

// 2. Clear Chat Session Trigger
if (newChatBtn) {
    newChatBtn.addEventListener('click', () => {
        chatFeed.innerHTML = '';
        chatFeed.style.display = 'none';
        if (welcomeMessage) welcomeMessage.style.display = 'block';
    });
}

// 3. Functional Chat Message Handler (Connected to Live Backend)
async function handleSendMessage() {
    const text = userInput.value.trim();
    if (!text) return; // Ignore empty inputs

    // Hide welcome message panel and activate interactive display layout
    if (welcomeMessage) welcomeMessage.style.display = 'none';
    if (chatFeed) chatFeed.style.display = 'flex';

    // Append User Message Bubble
    const userBubble = document.createElement('div');
    userBubble.classList.add('msg', 'user');
    userBubble.textContent = text;
    chatFeed.appendChild(userBubble);

    // Clear input box immediately
    userInput.value = '';
    chatFeed.scrollTop = chatFeed.scrollHeight;

    // Create placeholder for Bot response
    const botBubble = document.createElement('div');
    botBubble.classList.add('msg', 'bot');
    botBubble.textContent = "Thinking...";
    chatFeed.appendChild(botBubble);
    chatFeed.scrollTop = chatFeed.scrollHeight;

    try {
        // Dynamic path configuration optimized for Vercel builds
        const response = await fetch('http://127.0.0.1:8000/api/chat', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: text })
        });

        if (!response.ok) {
            throw new Error(`Server returned status ${response.status}`);
        }

        const data = await response.json();
        botBubble.textContent = data.reply || "No reply field returned from server.";
    } catch (error) {
        console.error("Network Error:", error);
        botBubble.textContent = "Error: Could not reach the backend API system.";
    }
    
    chatFeed.scrollTop = chatFeed.scrollHeight;
}

// 4. Bind Input Send Events safely
if (sendBtn) {
    sendBtn.addEventListener('click', handleSendMessage);
}

if (userInput) {
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSendMessage();
    });
}