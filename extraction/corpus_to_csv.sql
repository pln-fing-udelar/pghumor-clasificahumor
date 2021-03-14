SELECT tweet_id                                                                AS id,
       REPLACE(text, '"', '""')                                                AS text,
       p / c > 0.5                                                             AS is_humor,
       x                                                                       AS votes_no,
       v1                                                                      AS votes_1,
       v2                                                                      AS votes_2,
       v3                                                                      AS votes_3,
       v4                                                                      AS votes_4,
       v5                                                                      AS votes_5,
       IF(p / c > 0.5, (v1 * 1 + v2 * 2 + v3 * 3 + v4 * 4 + v5 * 5) / p, NULL) AS funniness_average
FROM (SELECT v.tweet_id,
             COUNT(IF(vote = '1', 1, NULL))  v1,
             COUNT(IF(vote = '2', 1, NULL))  v2,
             COUNT(IF(vote = '3', 1, NULL))  v3,
             COUNT(IF(vote = '4', 1, NULL))  v4,
             COUNT(IF(vote = '5', 1, NULL))  v5,
             COUNT(IF(vote = 'x', 1, NULL))  x,
             COUNT(IF(vote != 'x', 1, NULL)) p,
             COUNT(*)                        c
      FROM votes v
               LEFT JOIN (SELECT session_id
                          FROM votes
                          WHERE tweet_id = 965857626843172864
                            AND vote = 'x') s1
                         ON v.session_id = s1.session_id
               LEFT JOIN (SELECT session_id
                          FROM votes
                          WHERE tweet_id = 965758586747047936
                            AND vote = 'x') s2
                         ON v.session_id = s2.session_id
               LEFT JOIN (SELECT session_id
                          FROM votes
                          WHERE tweet_id = 301481614033170432) s3
                         ON v.session_id = s3.session_id
      WHERE vote != 'n'
        AND s1.session_id IS NOT NULL
        AND s2.session_id IS NOT NULL
        AND (s3.session_id IS NULL OR (s3.session_id != 'x' AND s3.session_id != 'n'))
      GROUP BY v.tweet_id
      HAVING p / c != 0.5
         AND c >= 3) temp
         NATURAL JOIN tweets
ORDER BY is_humor DESC, RAND()
LIMIT 20000
INTO OUTFILE '/var/lib/mysql-files/corpus.csv' FIELDS TERMINATED BY ','
    OPTIONALLY ENCLOSED BY '"'
    ESCAPED BY '' LINES TERMINATED BY '\n';
# After this, shuffle them, split in training and testing and manually add headers to the output file.
