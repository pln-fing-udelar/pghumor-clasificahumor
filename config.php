<?php

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

$con=mysqli_connect("localhost","pghumor","--PASSWORD--","chistesdb");
// Check connection
if (mysqli_connect_errno()) {
  echo "Failed to connect to MySQL: " . mysqli_connect_error();
}

mysqli_set_charset($con, "utf8")
?>
