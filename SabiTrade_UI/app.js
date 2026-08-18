const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');
const chatContainer = document.getElementById('chatContainer');
const sendBtn = document.getElementById('sendBtn');
const smsBtn = document.getElementById('smsBtn');

// The local llama.cpp server endpoint
const API_URL = 'http://127.0.0.1:8080/completion';

function appendMessage(sender, text) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message');
    
    if (sender === 'user') {
        msgDiv.classList.add('user-message');
        msgDiv.innerHTML = `
            <div class="avatar user-avatar">U</div>
            <div class="bubble"><p>${escapeHTML(text)}</p></div>
        `;
    } else {
        msgDiv.classList.add('system-message');
        const formattedText = escapeHTML(text).replace(/\n/g, '<br>');
        msgDiv.innerHTML = `
            <div class="avatar system-avatar">S</div>
            <div class="bubble"><p>${formattedText}</p></div>
        `;
    }
    
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return msgDiv;
}

function showTyping() {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', 'system-message');
    msgDiv.id = 'typingIndicator';
    msgDiv.innerHTML = `
        <div class="avatar system-avatar">S</div>
        <div class="typing-indicator">
            <span></span><span></span><span></span>
        </div>
    `;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function removeTyping() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) indicator.remove();
}

function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}

// System Prompt for African Structural Adaptation
const SYSTEM_PROMPT = `You are SabiTrade, an offline assistant for African informal retail.
Follow these structural rules:
1. If the user pastes an M-Pesa, OPay, or MoMo SMS receipt, parse it and extract the Sender, Amount, Date, and Balance. Ignore telecom spam.
2. If the user mentions "Ajo" or "Esusu", treat it as a rotating savings contribution, NOT an expense.
3. If the user mentions irregular credit (e.g. "pay half next market day"), acknowledge the informal credit terms exactly as spoken.
4. Always respond in friendly Nigerian Pidgin.

### Instruction:
`;

async function processInput(text) {
    if (!text) return;

    appendMessage('user', text);
    userInput.value = '';
    
    userInput.disabled = true;
    sendBtn.disabled = true;

    showTyping();

    const prompt = SYSTEM_PROMPT + text + "\n\n### Response:\n";

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: prompt,
                n_predict: 256,
                temperature: 0.7,
                top_k: 40,
                top_p: 0.95,
                stop: ["### Instruction:", "\n\n\n"]
            })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        removeTyping();
        appendMessage('system', data.content.trim());

    } catch (error) {
        removeTyping();
        appendMessage('system', 'Sorry boss, connection fail. Make sure the offline engine dey run (llama-server).');
        console.error(error);
    } finally {
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
}

chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    processInput(userInput.value.trim());
});

smsBtn.addEventListener('click', () => {
    const sampleSMS = "OPay: You have received N50,000.00 from CHINEDU OKAFOR. Ref: 20260817001. Bal: N125,450.00. Dial *955# for loans.";
    userInput.value = sampleSMS;
});
