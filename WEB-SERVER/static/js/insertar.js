// Selecciona el formulario de inserción de usuario
const formularioInsercionUsuario = document.getElementById('formulario-insercion-usuario');

// Agrega un evento de escucha para cuando se envíe el formulario
formularioInsercionUsuario.addEventListener('submit', async (evento) => {
    evento.preventDefault(); // Evita que el formulario se envíe normalmente

    // Realiza una solicitud fetch para enviar los datos del formulario al servidor
    try {
        const respuesta = await fetch(formularioInsercionUsuario.action, {
            method: formularioInsercionUsuario.method,
            body: new FormData(formularioInsercionUsuario)
        });

        // Verifica si la respuesta es exitosa (código de estado HTTP 200-299)
        if (respuesta.ok) {
            // Muestra un mensaje de éxito en la página
            mostrarMensaje('Usuario insertado correctamente', 'success');
        } else {
            // Muestra un mensaje de error en la página
            mostrarMensaje('Error al insertar usuario', 'error');
        }
    } catch (error) {
        console.error('Error al enviar el formulario:', error);
        // Muestra un mensaje de error en la página
        mostrarMensaje('Error al enviar el formulario', 'error');
    }
});

// Función para mostrar un mensaje en la página
function mostrarMensaje(mensaje, tipo) {
    // Crea un elemento div para el mensaje
    const mensajeDiv = document.createElement('div');
    mensajeDiv.textContent = mensaje;

    // Asigna una clase CSS según el tipo de mensaje
    mensajeDiv.classList.add('mensaje', tipo);

    // Inserta el mensaje en el contenedor
    const mensajeContainer = document.getElementById('mensaje-container');
    mensajeContainer.appendChild(mensajeDiv);

    // Después de unos segundos, elimina el mensaje
    setTimeout(() => {
        mensajeDiv.remove();
    }, 5000); // Elimina el mensaje después de 5 segundos
}
