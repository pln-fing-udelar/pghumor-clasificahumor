select id_tweet, session_id, voto from votos into outfile '/var/lib/mysql-files/annotations.csv' fields terminated by ',' optionally enclosed by '"' escaped by '' lines terminated by '\n';
