/* 
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

chistes = [];
index = 0;
pagina = 0;

$(document).ready(function() {

    obtener3ChistesDistintos();

    $("#input-id").rating({
        captionElement: "#kv-caption",
        clearCaption: '¡Votá!',
        showClear: false,
        starCaptions: {1: "¡Malísimo!", 2: "Malo", 3: "Ni ni", 4: "Bueno", 5: "¡Buenísimo!"},
        size: 'lg'
    });

    $('#input-id').on('rating.change', function(event, value, caption) {
        procesar(value);
        setTimeout(function() {
            $('#kv-caption span').text('¡Gracias!');
            setTimeout(function() {
                $('#input-id').rating('clear');
            }, 800);
        }, 700);
    });

});

    function mostrarHumor(){
        $( "#Chiste" ).html(chistes[index].text_tweet.replace(/\n/mg,"<br/>")).text(); // asi para hacer html decode
    }

    function obtener3ChistesDistintos(){
        //Ajax para llenar arrays
        $.ajax({
            url: 'obtenerTresChistes.php',
            success: function(data){
                chistes = eval(data);
                mostrarHumor();
            }
        });

    }

    function procesar(button){
        indexViejo = index;

        var urlN = 'obtenerChisteNuevo.php?id1=' + chistes[0].id_tweet + '&id2=' + chistes[1].id_tweet  + '&id3=' + chistes[2].id_tweet;
        $.ajax({
            url: urlN,
            success: function(data){
                var chiste = eval(data);
                chistes[indexViejo].id_tweet = chiste[0].id_tweet;
                chistes[indexViejo].text_tweet = chiste[0].text_tweet;
            }
        });


        //Mandar señal
        var urlP = 'procesarVoto.php?id=' + chistes[index].id_tweet + '&voto=' + button;
        $.ajax({
            url: urlP,
            success: function(){
            }
        });



        index = (index + 1) % chistes.length;

        //Cambiar para el chiste siguiente
        mostrarHumor();
        //Obtener nuevo chiste 
    }

    function Home(){
        if (pagina !== 0){
            pagina = 0;
            $('#aboutUs').removeClass();
            $("#aboutUsText").css("display", "none");
            $('#HomeText').css("display","block");
        }

    }

    function aboutUs(){
       if (pagina !== 1){
           pagina = 1;
           $("#aboutUs").addClass("active");
           $("#aboutUsText").css("display", "initial");
           $('#HomeText').css("display","none");
        } 
    }