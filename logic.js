/* 
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

chistes = [];
index = 0;
pagina = 0;

obtener3ChistesDistintos();

function obtener3ChistesDistintos(){
    //Ajax para llenar arrays
    $.ajax({
        url: 'obtenerTresChistes.php',
        success: function(data){
            chistes = eval(data);
            $( "#Chiste" ).text( chistes[index].text_tweet );
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
    $( "#Chiste" ).text( chistes[index].text_tweet );
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
    
