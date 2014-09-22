<?php

include 'config.php';

ini_set('session.cookie_lifetime', 2592000); 
ini_set('session.gc_maxlifetime', 2592000);
session_start();

$id = array();


if (isset($_GET['id1'])){
    $id[0] = mysqli_real_escape_string($con, $_GET['id1']);
}

if (isset($_GET['id2'])){
    $id[1] = mysqli_real_escape_string($con,$_GET['id2']);
}

if (isset($_GET['id3'])){
    $id[2] = mysqli_real_escape_string($con, $_GET['id3']);
}

$resultCuenta = array();
$cuentas = array();

for($j = 0; $j < 3; $j++){

    //Obtener Los ids de las cuentas que se obtuvieron los chistes
    $resultCuenta[$j] = mysqli_query($con,"SELECT id_account FROM tweets WHERE id_tweet =  " . $id[$j] );

    while($row = mysqli_fetch_array($resultCuenta[$j])) {
        $cuentas[$j] = $row['id_account'];
    }
}

//Predicados generales
//No visto
$notSeen = "( id_tweet NOT IN ( SELECT id_tweet FROM audit_table WHERE session_id = '" . session_id() ."'))";
//No de las cuentas ya mostradas
$notCurrentAcount = "( T.id_account <> ". $cuentas[0] . " AND T.id_account <> ". $cuentas[1] . " AND T.id_account <> ". $cuentas[2] . " ) ";
//No de los tweets que ya estan en el buffer
$notCurrent = "( T.id_tweet <> " . $id[0] . " AND T.id_tweet <> " . $id[1] . " AND T.id_tweet <> " . $id[2] . " )";
// no Votado
$notVotado = " ( T.votado_tweet = 0 )";
// no Dudoso
$notDudoso = " ( T.dudoso_tweet = 0 )";

$json = array();
$i = 0;
if (rand(0, 1000) >= 150 ){
    // Retorna los chistes que no hayan sido presentadas a ningun usuario y que sea de distintas cuentas de los ultimos 3
    $result = mysqli_query($con,"SELECT id_tweet, text_tweet, RAND() AS rand FROM tweets AS T  WHERE " . $notVotado .  " AND " . $notCurrentAcount . " AND " . $notCurrent . " AND " . $notSeen . " AND ". $notDudoso ." ORDER BY rand LIMIT 1");
    
    while($row = mysqli_fetch_array($result)) {
        $json[$i]['id_tweet'] = $row['id_tweet'];
        $json[$i]['text_tweet'] = $row['text_tweet'];
        $i++;
    }
    
    if ( $i != 1){
        // Retorna los chistes que no hayan sido presentadas a ningun usuario y que sea de distintas cuentas de los ultimos 3
        $result = mysqli_query($con,"SELECT id_tweet, text_tweet, RAND() AS rand FROM tweets AS T WHERE " . $notVotado .  " AND " . $notCurrentAcount . " AND " . $notCurrent . " AND " . $notSeen . "ORDER BY rand LIMIT 1");

        while($row = mysqli_fetch_array($result)) {
            $json[$i]['id_tweet'] = $row['id_tweet'];
            $json[$i]['text_tweet'] = $row['text_tweet'];
            $i++;
        }         
    }
}
else{
    // Retorna los chistes que no hayan sido presentadas a ningun usuario y que sea de distintas cuentas de los ultimos 3
    $result = mysqli_query($con,"SELECT id_tweet, text_tweet, RAND() AS rand FROM tweets AS T  WHERE " . $notVotado .  " AND " . $notCurrentAcount . " AND " . $notCurrent . " AND " . $notSeen . "ORDER BY rand LIMIT 1");

    while($row = mysqli_fetch_array($result)) {
        $json[$i]['id_tweet'] = $row['id_tweet'];
        $json[$i]['text_tweet'] = $row['text_tweet'];
        $i++;
    }    
    
}



if ($i != 1){
    //Si estan todos votados
    $result = mysqli_query($con,"SELECT id_tweet, text_tweet, RAND() AS rand FROM tweets AS T WHERE " . $notCurrentAcount . " AND " . $notCurrent . " AND " . $notSeen . " ORDER BY rand LIMIT 1");

    while($row = mysqli_fetch_array($result)) {
        $json[$i]['id_tweet'] = $row['id_tweet'];
        $json[$i]['text_tweet'] = $row['text_tweet'];
        $i++;
    }
}

if ($i != 1){
    $result = mysqli_query($con,"SELECT T.id_tweet, T.text_tweet FROM tweets AS T WHERE". $notCurrentAcount . " AND " . $notCurrent  ." LIMIT 1");

    while($row = mysqli_fetch_array($result)) {
        $json[$i]['id_tweet'] = $row['id_tweet'];
        $json[$i]['text_tweet'] = $row['text_tweet'];
        $i++;
    }
}

echo json_encode($json);

mysqli_close($con);
?>

