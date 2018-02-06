<?php

const MAX_LIFETIME = 2592000;
const BATCH_SIZE = 3;
const SQL_SUB_UNSEEN = '( id_tweet NOT IN ( SELECT id_tweet FROM audit_table WHERE session_id = ? ) )';

include 'config.php';

ini_set('session.cookie_lifetime', MAX_LIFETIME);
ini_set('session.gc_maxlifetime', MAX_LIFETIME);
session_start();

function get_random_unseen_tweets($connection) {
    $statement_random_unseen_tweets = $connection->prepare(
        'SELECT id_tweet, text_tweet, RAND() AS rand FROM tweets WHERE ' . SQL_SUB_UNSEEN . ' ORDER BY rand LIMIT '
        . BATCH_SIZE);

    $statement_random_unseen_tweets->bind_param('s', session_id());
    $statement_random_unseen_tweets->execute();
    return $statement_random_unseen_tweets->get_result();
}

$json = array();
$tweets = 0;

$result = mysqli_query($connection, "SELECT T.id_tweet, T.text_tweet, RAND() AS rand FROM tweets AS T WHERE " . $sql_not_seen . " ORDER BY rand LIMIT 3");
while (($row = mysqli_fetch_array($result))) {
    $json[$tweets]['id_tweet'] = $row['id_tweet'];
    $json[$tweets]['text_tweet'] = $row['text_tweet'];
    $tweets++;
}

if ($tweets != BATCH_SIZE) {
    $result = mysqli_query($connection, "SELECT T.id_tweet, T.text_tweet FROM tweets AS T WHERE " . $sql_not_seen . " LIMIT 3");
    while (($row = mysqli_fetch_array($result)) && ($tweets < BATCH_SIZE)) {
        $json[$tweets]['id_tweet'] = $row['id_tweet'];
        $json[$tweets]['text_tweet'] = $row['text_tweet'];
        $tweets++;
    }
}

if ($tweets != BATCH_SIZE) {
    $result = mysqli_query($connection, "SELECT T.id_tweet, T.text_tweet FROM tweets AS T WHERE " . $sql_not_seen . " LIMIT 3");
    while (($row = mysqli_fetch_array($result)) && ($tweets < BATCH_SIZE)) {
        $json[$tweets]['id_tweet'] = $row['id_tweet'];
        $json[$tweets]['text_tweet'] = $row['text_tweet'];
        $tweets++;
    }
}


if ($tweets != BATCH_SIZE) {
    $result = mysqli_query($connection, "SELECT T.id_tweet, T.text_tweet FROM tweets AS T WHERE  '" . session_id() . "' NOT IN (SELECT session_id FROM audit_table AS A WHERE A.id_tweet = T.id_tweet) LIMIT 3");
    while (($row = mysqli_fetch_array($result)) && ($tweets < BATCH_SIZE)) {
        $json[$tweets]['id_tweet'] = $row['id_tweet'];
        $json[$tweets]['text_tweet'] = $row['text_tweet'];
        $tweets++;
    }
}

echo json_encode($json);

mysqli_close($connection);
