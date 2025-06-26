let currentUser = []; // Ahora guardamos el usuario como un array
let currentChat = [];
let idUsuarioActual = 0;
cargarIdUsuarioActual();

// DOM Elements
const authScreen = document.getElementById("auth-screen");
const appContainer = document.getElementById("app-container");
const loginTab = document.getElementById("login-tab");
const signupTab = document.getElementById("signup-tab");
const loginForm = document.getElementById("login-form");
const signupForm = document.getElementById("signup-form");
const loginButton = document.getElementById("login-button");
const signupButton = document.getElementById("signup-button");
const logoutButton = document.getElementById("logout-button");

// API Endpoints
const API_BASE = "http://localhost:8000/api/usuario";
const CREATE_USER_ENDPOINT = `${API_BASE}/create`;
const LOGIN_ENDPOINT = `${API_BASE}/login`;

// Switch between login and signup tabs
loginTab.addEventListener("click", () => {
  loginTab.classList.add("active");
  signupTab.classList.remove("active");
  loginForm.classList.remove("hidden");
  signupForm.classList.add("hidden");
});

signupTab.addEventListener("click", () => {
  signupTab.classList.add("active");
  loginTab.classList.remove("active");
  signupForm.classList.remove("hidden");
  loginForm.classList.add("hidden");
});

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
    return current;
  } catch (error) {
    console.error("Ocurrió un error al obtener el usuario:", error);
  }
}

// Cargar los contactos desde el backend
async function loadContacts() {
  currentUser = await loadUser(idUsuarioActual);

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
        body: JSON.stringify({ id_usuario: idUsuarioActual }), // Ahora usamos currentUser[0].id_usuario
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
    renderContacts();
    console.error("Error al cargar los contactos:", error);
  }
}

// Buscar contactos en tiempo real
async function setupSearch() {
  const searchInput = document.querySelector(".search input");

  searchInput.addEventListener("input", async (e) => {
    const searchTerm = e.target.value.trim();

    if (searchTerm.length > 0) {
      try {
        const response = await fetch(`${API_BASE}/filtro`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            argumento: searchTerm,
            id_usuario: idUsuarioActual,
          }),
        });

        const data = await response.json();

        if (Array.isArray(data)) {
          // Mapea los resultados igual que en loadContacts
          const searchResults = data.map((contact) => ({
            id: contact.id_usuario,
            name: contact.nombre_usuario,
            avatar:
              contact.foto_perfil ||
              "https://api.dicebear.com/7.x/avataaars/svg?seed=default",
            lastMessage: contact.ultimo_mensaje,
          }));

          // Renderiza los resultados temporalmente
          renderContacts(searchResults);
        }
      } catch (error) {
        console.error("Error al buscar contactos:", error);
      }
    } else {
      // Si el campo está vacío, vuelve a cargar los contactos normales
      loadContacts();
    }
  });
}

// Modifica renderContacts para aceptar una lista personalizada
function renderContacts(contactsList = contacts) {
  const contactsContainer = document.getElementById("contacts");

  // 1. Validar que contactsList sea un array
  if (!Array.isArray(contactsList)) {
    console.error("contactsList no es un array:", contactsList);
    contactsContainer.innerHTML =
      '<div class="no-contacts">No hay contactos disponibles</div>';
    return;
  }

  // 2. Validar array vacío
  if (contactsList.length === 0) {
    contactsContainer.innerHTML =
      '<div class="no-contacts">No se encontraron contactos</div>';
    return;
  }

  // 3. Mapear sólo si hay datos válidos
  try {
    contactsContainer.innerHTML = contactsList
      .filter((contact) => contact && contact.id) // Filtra contactos inválidos
      .map(
        (contact) => `
                <div class="contact" data-id="${contact.id}">
                    <img src="${
                      contact.avatar ||
                      "https://api.dicebear.com/7.x/avataaars/svg?seed=default"
                    }" 
                         alt="${contact.name || "Contacto"}" 
                         class="avatar">
                    <div class="contact-info">
                        <h4>${contact.name || "Usuario"}</h4>
                        <small>${contact.lastMessage || " "}</small>
                    </div>
                </div>
            `
      )
      .join("");
    // 4. Agregar event listeners
    document.querySelectorAll(".contact").forEach((contact) => {
      contact.addEventListener("click", () => {
        const contactId = parseInt(contact.dataset.id);
        if (!isNaN(contactId)) {
          currentChat = loadUser(contactId);
          loadChat(contactId);
          document
            .querySelectorAll(".contact")
            .forEach((c) => c.classList.remove("active"));
          contact.classList.add("active");
        }
      });
    });
  } catch (error) {
    console.error("Error al renderizar contactos:", error);
    contactsContainer.innerHTML =
      '<div class="error-contacts">Error al cargar contactos</div>';
  }
}
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
// Modifica la función loadChat para que limpie el search input y recargue contactos
async function loadChat(contactId) {
  try {
    // 1. Limpiar el input de búsqueda
    const searchInput = document.querySelector(".search input");
    searchInput.value = "";

    // 2. Recargar contactos (para volver a la lista completa)
    await loadContacts();

    // 3. Cargar el chat normalmente
    currentChat = await loadUser(contactId);

    if (!currentChat || !currentChat.length) {
      console.error("No se pudo cargar el usuario del chat");
      return;
    }

    document.getElementById("current-chat-name").textContent =
      currentChat[0].nombre_usuario;

    const headerAvatar = document.querySelector(".chat-header .avatar");
    headerAvatar.src =
      currentChat[0].foto_perfil ||
      "https://api.dicebear.com/7.x/avataaars/svg?seed=default";
    headerAvatar.alt = currentChat[0].nombre_usuario;

    const chatMessages = document.getElementById("chat-messages");
    chatMessages.innerHTML = "";

    try {
      const response = await fetch(
        `http://localhost:8000/api/mensaje/read/${currentChat[0].id_usuario}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id_usuario: currentUser[0].id_usuario }),
        }
      );

      const data = await response.json();

      if (data.mensajes && data.mensajes.length > 0) {
        chatMessages.innerHTML = data.mensajes
          .map(
            (message) => `
          <div class="message ${
            message.id_emisor === currentUser[0].id_usuario
              ? "sent"
              : "received"
          }">
            ${message.contenido}
            <div class="message-time">${message.fecha_envio}</div>
          </div>
        `
          )
          .join("");
      }
    } catch (error) {
      console.error("Error al cargar mensajes:", error);
    }

    chatMessages.scrollTop = chatMessages.scrollHeight;
  } catch (error) {
    console.error("Error en loadChat:", error);
  }
}
// Enviar mensaje al backend
async function sendMessage(text) {
  if (!currentChat || !text.trim()) return;

  try {
    const response = await fetch(
      `http://localhost:8000/api/mensaje/enviar/${currentChat[0].id_usuario}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          id_emisor: idUsuarioActual,
          contenido: text,
        }),
      }
    );

    const data = await response.json();

    if (response.ok) {
      // 1. Recargar SOLO los mensajes del chat actual
      await loadChat(currentChat[0].id_usuario);

      // 2. Limpiar el input
      document.getElementById("message-input").value = "";

      // 3. Opcional: Hacer scroll al final
      const chatMessages = document.getElementById("chat-messages");
      chatMessages.scrollTop = chatMessages.scrollHeight;
    } else {
      console.error("Error al enviar mensaje:", data);
    }
  } catch (error) {
    console.error("Error al enviar mensaje:", error);
  }
}

// Elimina estas líneas redundantes (ya están en DOMContentLoaded)
document
  .getElementById("send-button")
  .addEventListener("click", sendMessageHandler);
document.getElementById("message-input").addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessageHandler();
});
async function refresh() {
  console.log("CURRENT CHAT CURRENT CHAT ACTUAL PERO REFRESH", currentChat);
  console.log(
    "VIENDO QUE TIENE EL LOCALSTORAGE",
    localStorage.getItem("idUsuarioActual")
  );

  cargarIdUsuarioActual();
  console.log("VIENDO QUE TEINE IDUSUARIOACT", idUsuarioActual);
  if (idUsuarioActual == 0) {
    hideApp();
    return;
  }
  currentUser = await loadUser(idUsuarioActual);
  console.log(currentChat);
  loadContacts();
  showApp();
}

async function login(argumento, password) {
  try {
    const response = await fetch(LOGIN_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        argumento: argumento,
        passw: password,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      guardarIdUsuarioActual(data["id_usuario"]);
      
      // Resetear el estado del chat antes de mostrar la app
      currentChat = [];
      document.getElementById("current-chat-name").textContent = "Select a chat";
      document.getElementById("chat-messages").innerHTML = "";
      
      refresh();
      showApp();
    } else {
      alert(data.detail || "Credenciales inválidas");
    }
  } catch (error) {
    console.error("Login error:", error);
    alert("Error al conectar con el servidor");
  }
}

// Signup function
async function signup(userData) {
  try {
    const response = await fetch(CREATE_USER_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(userData),
    });

    const data = await response.json();

    if (response.ok) {
      alert("Cuenta creada con éxito. Por favor inicia sesión.");
      loginTab.click();
      clearSignupForm();
    } else {
      alert(data.detail || "Error al registrar usuario");
    }
  } catch (error) {
    console.error("Signup error:", error);
    alert("Error al conectar con el servidor");
  }
}

function cargarIdUsuarioActual() {
  idUsuarioActual = localStorage.getItem("idUsuarioActual");
}

function guardarIdUsuarioActual(valor) {
  idUsuarioActual = valor; // Ajusta según lo que devuelva tu API
  localStorage.setItem("idUsuarioActual", idUsuarioActual);
}

function logout() {
  currentUser = [];
  currentChat = [];
  guardarIdUsuarioActual(0);
  contacts = [];
  
  // Limpiar la interfaz del chat
  document.getElementById("current-chat-name").textContent = "Select a chat";
  document.getElementById("chat-messages").innerHTML = "";
  document.querySelector(".chat-header .avatar").src = "https://api.dicebear.com/7.x/avataaars/svg?seed=default";
  
  // Remover clase 'active' de todos los contactos
  document.querySelectorAll(".contact").forEach(c => c.classList.remove("active"));
  
  hideApp();
  clearLoginForm();
}

function showApp() {
  authScreen.classList.add("hidden");
  appContainer.classList.remove("hidden");
  
  // Resetear el chat al estado inicial
  document.getElementById("current-chat-name").textContent = "Select a chat";
  document.getElementById("chat-messages").innerHTML = "";
  document.querySelector(".chat-header .avatar").src = "https://api.dicebear.com/7.x/avataaars/svg?seed=default";
  
  // Asegurarse que ningún contacto aparece como activo
  document.querySelectorAll(".contact").forEach(c => c.classList.remove("active"));
}

function hideApp() {
  authScreen.classList.remove("hidden");
  appContainer.classList.add("hidden");
}

// Clear forms
function clearLoginForm() {
  document.getElementById("login-argumento").value = "";
  document.getElementById("login-password").value = "";
}

function clearSignupForm() {
  document.getElementById("signup-username").value = "";
  document.getElementById("signup-fullname").value = "";
  document.getElementById("signup-phone").value = "";
  document.getElementById("signup-email").value = "";
  document.getElementById("signup-password").value = "";
  document.getElementById("signup-photo").value = "";
}

// Event listeners
loginButton.addEventListener("click", () => {
  const argumento = document.getElementById("login-argumento").value;
  const password = document.getElementById("login-password").value;

  if (argumento && password) {
    login(argumento, password);
  } else {
    alert("Por favor completa todos los campos");
  }
});

signupButton.addEventListener("click", () => {
  const userData = {
    nombre_usuario: document.getElementById("signup-username").value,
    nombre_completo: document.getElementById("signup-fullname").value,
    telefono: document.getElementById("signup-phone").value,
    correo: document.getElementById("signup-email").value,
    contrasenna: document.getElementById("signup-password").value,
    foto_perfil: document.getElementById("signup-photo").value || "",
    estado: "Activo",
  };

  // Validación básica
  if (
    !userData.nombre_usuario ||
    !userData.nombre_completo ||
    !userData.telefono ||
    !userData.correo ||
    !userData.contrasenna
  ) {
    alert("Por favor completa todos los campos obligatorios");
    return;
  }

  // Validación de contraseña (simplificada)
  if (userData.contrasenna.length < 8) {
    alert("La contraseña debe tener al menos 8 caracteres");
    return;
  }

  signup(userData);
});

logoutButton.addEventListener("click", logout);

// Initialize app
document.addEventListener("DOMContentLoaded", () => {
  refresh();
  loadContacts();
  setupSearch();
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

  // Resto de tus event listeners originales
  document
    .getElementById("send-button")
    .addEventListener("click", sendMessageHandler);
  document.getElementById("message-input").addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessageHandler();
  });
});

function sendMessageHandler() {
  const input = document.getElementById("message-input");
  if (currentChat && input.value.trim()) {
    sendMessage(input.value);
    input.value = "";
  }
}

// Resto de tus funciones originales (loadUser, loadContacts, renderContacts, loadChat, sendMessage, refresh)
// Asegúrate de que todas las llamadas fetch incluyan el id_usuario en el cuerpo cuando sea necesario
