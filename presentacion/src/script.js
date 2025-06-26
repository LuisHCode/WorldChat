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
    // Llamamos a loadContacts() después de haber cargado el usuario
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
  currentChat = await loadUser(idUsuarioActual);
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
  console.log("VIENDO QUE TIENE EL LOCALSTORAGE", localStorage.getItem("idUsuarioActual"));
  
  cargarIdUsuarioActual();
  console.log("VIENDO QUE TEINE IDUSUARIOACT", idUsuarioActual);
  if (idUsuarioActual == 0) {
    hideApp();
    return;
  }
  currentChat = await loadUser(idUsuarioActual);
  console.log(currentChat);
  loadContacts();
  showApp();
}

// Login function
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
      // Asumimos que el login fue exitoso

      guardarIdUsuarioActual(data["id_usuario"]);
      console.log("usuario que esta ahi no se donde", idUsuarioActual);

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

// Logout function
function logout() {
  currentUser = null;
  currentChat = null;
  guardarIdUsuarioActual(0);
  contacts = [];
  hideApp();
  clearLoginForm();
  refresh();
}

// Show/hide app
function showApp() {
  authScreen.classList.add("hidden");
  appContainer.classList.remove("hidden");
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
