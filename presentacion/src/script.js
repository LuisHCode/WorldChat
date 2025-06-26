let currentUser = []; // Ahora guardamos el usuario como un array
let currentChat = [];

const uriUsuario = "http://localhost:8000/api/usuario"; // Cambia esto por tu URI real

// Cargar el usuario desde el backend
async function loadUser(idUsuario, current) {
  try {
    const response = await fetch(`${uriUsuario}/read/${idUsuario}`, {
      method: "GET", // Usamos GET para obtener los datos del usuario
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`Error en la solicitud: ${response.statusText}`);
    }

    const userData = await response.json();
    console.log("Usuario recibido:", userData);

    // Guardar el objeto completo del usuario en un array
    current = userData; // Guardamos el usuario como un array
    // Llamamos a loadContacts() después de haber cargado el usuario
    return current;
  } catch (error) {
    console.error("Ocurrió un error al obtener el usuario:", error);
  }
}

// Cargar los contactos desde el backend
async function loadContacts() {
  if (!currentUser.length) {
    console.error("No hay usuario cargado.");
    return;
  }

  try {
    const response = await fetch(
      "http://localhost:8000/api/usuario/contactos",
      {
        method: "POST", // Usamos POST porque estamos enviando datos (id_usuario) en el cuerpo
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ id_usuario: currentUser[0].id_usuario }), // Ahora usamos currentUser[0].id_usuario
      }
    );

    const data = await response.json();
    console.log("Contactos recibidos:", data);

    if (Array.isArray(data)) {
      contacts = data.map((contact) => ({
        id: contact.id_usuario,
        name: contact.nombre_usuario,
        avatar:
          contact.foto_perfil ||
          "https://api.dicebear.com/7.x/avataaars/svg?seed=default", // Foto predeterminada si no tiene
        lastMessage: contact.ultimo_mensaje,
      }));

      // Llamar a la función que renderiza los contactos
      renderContacts();
    } else {
      console.error("Los datos no son un array:", data);
    }
  } catch (error) {
    console.error("Error al cargar los contactos:", error);
  }
}

// Función que renderiza los contactos en el HTML
function renderContacts() {
  const contactsContainer = document.getElementById("contacts");
  contactsContainer.innerHTML = contacts
    .map(
      (contact) => `
    <div class="contact" data-id="${contact.id}">
        <img src="${contact.avatar}" alt="${contact.name}" class="avatar">
        <div class="contact-info">
            <h4>${contact.name}</h4>
            <small>${contact.lastMessage}</small>
        </div>
    </div>
  `
    )
    .join("");

  // Agregar eventos de click a los contactos
  document.querySelectorAll(".contact").forEach((contact) => {
    contact.addEventListener("click", () => {
      const contactId = parseInt(contact.dataset.id);

      loadChat(contactId);

      // Actualizar contacto activo
      document
        .querySelectorAll(".contact")
        .forEach((c) => c.classList.remove("active"));
      contact.classList.add("active");
    });
  });
}

// Cargar los mensajes de un chat específico desde el backend
async function loadChat(contactId) {
  currentChat = await loadUser(contactId); // Esperar a que loadUser() se resuelva

  const contact = contacts.find((c) => c.id === contactId);
  document.getElementById("current-chat-name").textContent = contact.name;

  // Actualizar el avatar del contacto en la cabecera
  const headerAvatar = document.querySelector(".chat-header .avatar");
  headerAvatar.src =
    contact.avatar || "https://api.dicebear.com/7.x/avataaars/svg?seed=default";
  headerAvatar.alt = contact.name;

  const chatMessages = document.getElementById("chat-messages");
  chatMessages.innerHTML = ""; // Limpiar los mensajes previos

  // Cargar los mensajes desde el backend (ruta /api/mensaje/read/{id_receptor})
  try {
    const response = await fetch(
      `http://localhost:8000/api/mensaje/read/${contactId}`,
      {
        method: "POST", // Usamos POST para enviar el id_emisor en el cuerpo
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          id_usuario: currentUser[0].id_usuario, // Ahora usamos currentUser[0].id_usuario
        }),
      }
    );

    const data = await response.json();

    chatMessages.innerHTML = data.mensajes
      .map(
        (message) => `
      <div class="message ${
        message.id_emisor === currentUser[0].id_usuario ? "sent" : "received"
      }">
          ${message.contenido}
          <div class="message-time">${message.fecha_envio}</div>
      </div>
    `
      )
      .join("");

    // Scroll hacia el final del chat
    chatMessages.scrollTop = chatMessages.scrollHeight;
  } catch (error) {
    console.error("Error al cargar mensajes:", error);
  }
}

// Enviar mensaje al backend
async function sendMessage(text) {
  if (!currentChat || !text.trim()) return;

  const newMessage = {
    text: text,
    sent: true,
    time: new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    }),
  };

  // Enviar mensaje al backend (FastAPI)
  fetch(
    `http://localhost:8000/api/mensaje/enviar/${currentChat[0].id_usuario}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        id_emisor: currentUser[0].id_usuario, // ID del emisor
        contenido: text, // El contenido del mensaje
      }),
    }
  )
    .then((response) => response.json())
    .then((data) => {
      console.log("Mensaje enviado con éxito", data);
      loadChat(currentChat[0].id_usuario); // Cargar los mensajes nuevamente después de enviar
    })
    .catch((error) => {
      console.error("Error al enviar mensaje:", error);
    });
}

async function refresh() {
  currentChat = await loadUser(3);  
  loadContacts();
}

// Inicializar la aplicación
document.addEventListener("DOMContentLoaded", async () => {
  // Primero, cargamos el usuario
  currentUser = await loadUser(3); // Suponemos que el id del usuario actual es 1 (debería ser dinámico)

  // Una vez que se haya cargado el usuario, cargamos los contactos
  loadContacts(); // Ahora, cargamos los contactos después de que el usuario ha sido cargado

  // Manejar clic del botón de enviar
  // Manejador de eventos para el botón de enviar
  document.getElementById("send-button").addEventListener("click", () => {
    const input = document.getElementById("message-input");
    sendMessage(input.value);
    input.value = ""; // Limpiar el input después de enviar
    refresh();
  });

  // Manejador de eventos para la tecla Enter
  document.getElementById("message-input").addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      // Detecta si la tecla presionada es Enter
      const input = document.getElementById("message-input");
      sendMessage(input.value);
      input.value = ""; // Limpiar el input después de enviar
      refresh();
    }
  });

});
