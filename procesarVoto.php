<?php

    session_start();
    
    if (isset($_GET['voto']) && isset($_GET['id'])){
        //Agregar voto a tabla de auditoria
        
        $voto = $_GET['voto'];
        
        if ($voto == 'c' || $voto == 'x' || $voto == 'r' || $voto == 'n'){

            include 'config.php';
            
            $voto = mysqli_real_escape_string($con,$_GET['voto']);
            $id = mysqli_real_escape_string($con,$_GET['id']);
            $session = session_id();
            
            $statement = "INSERT into audit_table VALUES (". $id . ",'" .$session . "','" . $voto . "')";


            $result = mysqli_query($con,$statement);

            if($voto == 'c' || $voto == 'x' || $voto == 'r'){
                //Marcar chiste como votado
                $marcarVotado = "UPDATE tweets SET votado_tweet = 1 WHERE id_tweet = ". $id;
                $result = mysqli_query($con, $marcarVotado);
            }
            else{
                $marcarDudoso = "UPDATE tweets SET dudoso_tweet = 1 WHERE id_tweet = ". $id;
                $result = mysqli_query($con, $marcarDudoso);
            }
            
        }
        mysqli_close($con);
        
    }
?>
