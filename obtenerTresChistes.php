<?php

include 'config.php';

ini_set('session.cookie_lifetime', 2592000); 
ini_set('session.gc_maxlifetime', 2592000);
session_start();

//Predicados generales
//No visto
$notSeen = "( id_tweet NOT IN ( SELECT id_tweet FROM audit_table WHERE session_id = '" . session_id() ."'))";
// Votado
$notVotado = " ( T.votado_tweet = 0 )";
// Dudoso
$notDudoso = " ( T.dudoso_tweet = 0 )";

$json = array();
$i = 0;

if (rand(0, 1000) >= 150 ){
   
    $result = mysqli_query($con,"SELECT T.id_tweet, T.text_tweet FROM tweets AS T WHERE " . $notSeen . " AND " . $notVotado . " AND ". $notDudoso. " LIMIT 3");

    while($row = mysqli_fetch_array($result)) {
        $json[$i]['id_tweet'] = $row['id_tweet'];
        $json[$i]['text_tweet'] = $row['text_tweet'];
        $i++;
    }
    
    if ( $i != 3){
        // Retorna los chistes que no hayan sido presentadas a ningun usuario y que sea de distintas cuentas de los ultimos 3
        $result = mysqli_query($con,"SELECT T.id_tweet, T.text_tweet FROM tweets AS T WHERE" . $notVotado .  " AND " . $notCurrentAcount . " AND " . $notCurrent . " AND " . $notSeen . " LIMIT 1");

        while($row = mysqli_fetch_array($result) && $i < 3) {
            $json[$i]['id_tweet'] = $row['id_tweet'];
            $json[$i]['text_tweet'] = $row['text_tweet'];
            $i++;
        }         
    }
    
}
else{
 
    $result = mysqli_query($con,"SELECT T.id_tweet, T.text_tweet FROM tweets AS T WHERE " . $notSeen . " AND " . $notVotado . " LIMIT 3");

    while($row = mysqli_fetch_array($result)) {
      $json[$i]['id_tweet'] = $row['id_tweet'];
      $json[$i]['text_tweet'] = $row['text_tweet'];
      $i++;
    }
    
}


if ($i != 3){
    $result = mysqli_query($con,"SELECT T.id_tweet, T.text_tweet FROM tweets AS T WHERE " . $notSeen . " LIMIT 3");

    while($row = mysqli_fetch_array($result) && $i < 3) {
      $json[$i]['id_tweet'] = $row['id_tweet'];
      $json[$i]['text_tweet'] = $row['text_tweet'];
      $i++;
    }
}

if ($i != 3){
    $result = mysqli_query($con,"SELECT T.id_tweet, T.text_tweet FROM tweets AS T WHERE  '" . session_id() ."' NOT IN (SELECT session_id FROM audit_table AS A WHERE A.id_tweet = T.id_tweet) LIMIT 3");

    while($row = mysqli_fetch_array($result) && $i < 3) {
      $json[$i]['id_tweet'] = $row['id_tweet'];
      $json[$i]['text_tweet'] = $row['text_tweet'];
      $i++;
    }
}

echo json_encode($json);
mysqli_close($con);
?>
