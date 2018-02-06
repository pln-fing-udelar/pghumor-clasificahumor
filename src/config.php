<?php

function general_error_handler() {
    $last_error = error_get_last();
    if ($last_error && $last_error['type'] == E_ERROR) {
        header("HTTP/1.1 500 Internal Server Error");
        exit("Error: $last_error");
    }
}

register_shutdown_function('general_error_handler');

$connection = mysqli_connect(getenv('DB_HOST'), getenv('DB_USER'),
    getenv('MYSQL_ROOT_PASSWORD'), getenv('DB_NAME'));

if (mysqli_connect_errno()) {
    exit('Failed to connect to MySQL: ' . mysqli_connect_error());
} else {
    mysqli_set_charset($connection, 'utf8');
}
