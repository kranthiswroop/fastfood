const toggleBtn = document.getElementById('chat-toggle-btn');
const chatbotBox = document.getElementById('chatbot-box');

toggleBtn.addEventListener('click', () => {
  chatbotBox.style.display = chatbotBox.style.display === 'block' ? 'none' : 'block';
});

function sendMessage() {
  const input = document.getElementById('chat-input');
  const message = input.value.trim();
  if (!message) return;

  appendMessage('You', message);
  input.value = '';

  getBotReply(message.toLowerCase());
}

function appendMessage(sender, text) {
  const chat = document.getElementById('chatbot-messages');
  const messageElement = document.createElement('p');
  messageElement.innerHTML = `<strong>${sender}:</strong> ${text}`;
  chat.appendChild(messageElement);
  chat.scrollTop = chat.scrollHeight;
}

function getBotReply(msg) {
  const chat = document.getElementById('chatbot-messages');

  // Add "typing..." placeholder
  const typingElement = document.createElement('p');
  typingElement.innerHTML = `<strong>Bot:</strong> typing...`;
  chat.appendChild(typingElement);
  chat.scrollTop = chat.scrollHeight;

  fetch(`/chatbot/?msg=${encodeURIComponent(msg)}`)
    .then(res => res.json())
    .then(data => {
      typingElement.innerHTML = `<strong>Bot:</strong> ${data.reply}`;
    })
    .catch(() => {
      typingElement.innerHTML = `<strong>Bot:</strong> Oops! Something went wrong.`;
    });
}
