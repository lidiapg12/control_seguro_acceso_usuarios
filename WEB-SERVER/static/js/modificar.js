$(document).ready(function() {
    $('#updateForm').on('submit', function(e) {
        e.preventDefault();
        var id_usuari = $('#id_usuari').val();
        var nueva_clave = $('#nueva_clave').val();
        $.ajax({
            type: "POST",
            url: "/actualizar_clave",
            data: {id_usuari: id_usuari, nueva_clave: nueva_clave},
            success: function(response) {
                $('#message').text(response).css('color', 'green');
            },
            error: function(response) {
                $('#message').text(response.responseText).css('color', 'red');
            }
        });
    });
});
