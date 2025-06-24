// Datos de prueba de los contactos
const contacts = [
    { id: 1, name: 'John Doe', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=John', lastMessage: 'Hey, how are you?' },
    { id: 2, name: 'Jane Smith', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Jane', lastMessage: 'See you tomorrow!' },
    { id: 3, name: 'Mike Johnson', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Mike', lastMessage: 'Thanks!' }
];

let currentChat = null;  // ID del chat actual
let currentUserId = 1;   // Este debería ser el ID del usuario actual (puedes obtenerlo desde login)

// Renderizar contactos
function renderContacts() {
    const contactsContainer = document.getElementById('contacts');
    contactsContainer.innerHTML = contacts.map(contact => `
        <div class="contact" data-id="${contact.id}">
            <img src="${contact.avatar}" alt="${contact.name}" class="avatar">
            <div class="contact-info">
                <h4>${contact.name}</h4>
                <small>${contact.lastMessage}</small>
            </div>
        </div>
    `).join('');

    // Añadir evento de click a los contactos
    document.querySelectorAll('.contact').forEach(contact => {
        contact.addEventListener('click', () => {
            const contactId = parseInt(contact.dataset.id);
            loadChat(contactId);

            // Actualizar contacto activo
            document.querySelectorAll('.contact').forEach(c => c.classList.remove('active'));
            contact.classList.add('active');
        });
    });
}

// Cargar mensajes del chat desde el backend
function loadChat(contactId) {
    currentChat = contactId;
    const contact = contacts.find(c => c.id === contactId);
    document.getElementById('current-chat-name').textContent = contact.name;

    // Actualizar avatar del contacto en la cabecera
    const headerAvatar = document.querySelector('.chat-header .avatar');
    headerAvatar.src = contact.avatar;
    headerAvatar.alt = contact.name;

    // Cargar mensajes desde el backend
    fetch(`http://localhost:8000/api/chat/read/${currentChat}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        const chatMessages = document.getElementById('chat-messages');
        chatMessages.innerHTML = data.mensajes.map(message => `
            <div class="message ${message.sent ? 'sent' : 'received'}">
                ${message.contenido}
                <div class="message-time">${message.fecha_envio}</div>
            </div>
        `).join('');

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    })
    .catch(error => {
        console.error('Error al cargar mensajes:', error);
    });
}

// Enviar mensaje al backend
function sendMessage(text) {
    if (!currentChat || !text.trim()) return;

    const newMessage = {
        text: text,
        sent: true,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    // Enviar mensaje al backend (FastAPI)
    fetch(`http://localhost:8000/api/chat/enviar/chat/${currentChat}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            id_emisor: currentUserId,  // Este es el ID del usuario actual (loggeado)
            contenido_texto: text,
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Mensaje enviado con éxito', data);
        loadChat(currentChat);
    })
    .catch(error => {
        console.error('Error al enviar mensaje:', error);
    });
}

// Inicializar la aplicación
document.addEventListener('DOMContentLoaded', () => {
    renderContacts();

    // Manejar click del botón de enviar
    document.getElementById('send-button').addEventListener('click', () => {
        const input = document.getElementById('message-input');
        sendMessage(input.value);
        input.value = '';
    });

    // Manejar la tecla enter para enviar el mensaje
    document.getElementById('message-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const input = document.getElementById('message-input');
            sendMessage(input.value);
            input.value = '';
        }
    });
});
