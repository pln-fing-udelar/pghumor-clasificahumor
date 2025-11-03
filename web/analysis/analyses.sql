SELECT COUNT(*)
FROM votes
WHERE vote = 'n';

CREATE VIEW good_quality AS
SELECT tweet_id,
       v.session_id,
       vote,
       date
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
  AND (s3.session_id IS NULL OR (s3.session_id != 'x' AND s3.session_id != 'n'));

SELECT COUNT(*)
FROM good_quality;

SELECT COUNT(*)
FROM good_quality
WHERE tweet_id = 965857626843172864
   OR tweet_id = 965758586747047936
   OR tweet_id = 301481614033170432
   OR tweet_id = 968699034540978176;

SELECT AVG(votes),
       STDDEV(votes)
FROM (SELECT COUNT(gq.tweet_id) votes
      FROM tweets t
               LEFT JOIN good_quality gq on (t.tweet_id = gq.tweet_id)
      GROUP BY t.tweet_id) temp;

SELECT AVG(votes),
       STDDEV(votes)
FROM (SELECT COUNT(gq.tweet_id) votes
      FROM tweets t
               LEFT JOIN good_quality gq on (t.tweet_id = gq.tweet_id)
      WHERE t.tweet_id != 965857626843172864
        AND t.tweet_id != 965758586747047936
        AND t.tweet_id != 301481614033170432
        AND t.tweet_id != 968699034540978176
      GROUP BY t.tweet_id) temp;

# Histogram:
SELECT votes,
       COUNT(*) tweet_count
FROM (SELECT COUNT(gq.tweet_id) votes
      FROM tweets t
               LEFT JOIN good_quality gq on (t.tweet_id = gq.tweet_id)
      GROUP BY t.tweet_id) temp
GROUP BY votes;

SELECT COUNT(IF(vote = '1', 1, NULL)) / COUNT(*) v1,
       COUNT(IF(vote = '2', 1, NULL)) / COUNT(*) v2,
       COUNT(IF(vote = '3', 1, NULL)) / COUNT(*) v3,
       COUNT(IF(vote = '4', 1, NULL)) / COUNT(*) v4,
       COUNT(IF(vote = '5', 1, NULL)) / COUNT(*) v5,
       COUNT(IF(vote = 'x', 1, NULL)) / COUNT(*) x
FROM good_quality;

SELECT category,
       COUNT(*)
FROM (SELECT IF(c = 0, 'No annotations', IF(p = x, 'Tie', IF(x > p, 'Not humorous',
                                                             ROUND((1 * v1 + 2 * v2 + 3 * v3 + 4 * v4 + 5 * v5) /
                                                                   p)))) category
      FROM (SELECT COUNT(IF(vote = '1', 1, NULL))  v1,
                   COUNT(IF(vote = '2', 1, NULL))  v2,
                   COUNT(IF(vote = '3', 1, NULL))  v3,
                   COUNT(IF(vote = '4', 1, NULL))  v4,
                   COUNT(IF(vote = '5', 1, NULL))  v5,
                   COUNT(IF(vote = 'x', 1, NULL))  x,
                   COUNT(IF(vote != 'x', 1, NULL)) p,
                   COUNT(gq.tweet_id)              c
            FROM tweets t
                     LEFT JOIN good_quality gq ON (t.tweet_id = gq.tweet_id)
            GROUP BY t.tweet_id) temp) temp2
GROUP BY category;

SELECT COUNT(*) c
FROM good_quality
GROUP BY session_id
ORDER BY c DESC;
# The top 10 sessions is the same as the top 10 when considering all non-skip votes.

SELECT AVG(c),
       STDDEV(c)
FROM (SELECT COUNT(*) c
      FROM good_quality
      GROUP BY session_id) temp;

SELECT t.tweet_id,
       COUNT(IF(vote = 'x', 1, NULL)) x,
       COUNT(IF(vote = '1', 1, NULL)) v1,
       COUNT(IF(vote = '2', 1, NULL)) v2,
       COUNT(IF(vote = '3', 1, NULL)) v3,
       COUNT(IF(vote = '4', 1, NULL)) v4,
       COUNT(IF(vote = '5', 1, NULL)) v5
FROM tweets t
         LEFT JOIN good_quality gq ON (t.tweet_id = gq.tweet_id)
GROUP BY t.tweet_id
INTO OUTFILE '/var/lib/mysql-files/annotations_by_tweet.csv' FIELDS TERMINATED BY ','
    OPTIONALLY ENCLOSED BY '"'
    ESCAPED BY '' LINES TERMINATED BY '\n';

SELECT t.tweet_id,
       COUNT(IF(vote = 'x', 1, NULL)) x,
       COUNT(IF(vote = '1', 1, NULL)) v1,
       COUNT(IF(vote = '2', 1, NULL)) v2,
       COUNT(IF(vote = '3', 1, NULL)) v3,
       COUNT(IF(vote = '4', 1, NULL)) v4,
       COUNT(IF(vote = '5', 1, NULL)) v5
FROM tweets t
         LEFT JOIN good_quality gq ON (t.tweet_id = gq.tweet_id)
         NATURAL JOIN (SELECT session_id
                       FROM good_quality
                       GROUP BY session_id
                       HAVING COUNT(*) > 1000) top_sessions
GROUP BY t.tweet_id
INTO OUTFILE '/var/lib/mysql-files/annotations_by_tweet_top.csv' FIELDS TERMINATED BY ','
    OPTIONALLY ENCLOSED BY '"'
    ESCAPED BY '' LINES TERMINATED BY '\n';

SELECT t.tweet_id,
       COUNT(IF(vote = 'x', 1, NULL)) x,
       COUNT(IF(vote = '1', 1, NULL)) v1,
       COUNT(IF(vote = '2', 1, NULL)) v2,
       COUNT(IF(vote = '3', 1, NULL)) v3,
       COUNT(IF(vote = '4', 1, NULL)) v4,
       COUNT(IF(vote = '5', 1, NULL)) v5
FROM tweets t
         LEFT JOIN votes v ON (t.tweet_id = v.tweet_id)
GROUP BY t.tweet_id
INTO OUTFILE '/var/lib/mysql-files/annotations_by_tweet_all.csv' FIELDS TERMINATED BY ','
    OPTIONALLY ENCLOSED BY '"'
    ESCAPED BY '' LINES TERMINATED BY '\n';

SELECT tweet_id,
       text,
       (1 * v1 + 2 * v2 + 3 * v3 + 4 * v4 + 5 * v5) / p funinness_average,
       p,
       x
FROM (SELECT t.tweet_id,
             text,
             COUNT(IF(vote = 'x', 1, NULL))  x,
             COUNT(IF(vote = '1', 1, NULL))  v1,
             COUNT(IF(vote = '2', 1, NULL))  v2,
             COUNT(IF(vote = '3', 1, NULL))  v3,
             COUNT(IF(vote = '4', 1, NULL))  v4,
             COUNT(IF(vote = '5', 1, NULL))  v5,
             COUNT(IF(vote != 'p', 1, NULL)) p
      FROM tweets t
               LEFT JOIN good_quality gq ON (t.tweet_id = gq.tweet_id)
      GROUP BY t.tweet_id) temp
WHERE p > x
ORDER BY funinness_average DESC;

SELECT AVG(funinness_average),
       STDDEV(funinness_average)
FROM (SELECT (1 * v1 + 2 * v2 + 3 * v3 + 4 * v4 + 5 * v5) / p funinness_average
      FROM (SELECT COUNT(IF(vote = 'x', 1, NULL))  x,
                   COUNT(IF(vote = '1', 1, NULL))  v1,
                   COUNT(IF(vote = '2', 1, NULL))  v2,
                   COUNT(IF(vote = '3', 1, NULL))  v3,
                   COUNT(IF(vote = '4', 1, NULL))  v4,
                   COUNT(IF(vote = '5', 1, NULL))  v5,
                   COUNT(IF(vote != 'p', 1, NULL)) p
            FROM tweets t
                     LEFT JOIN good_quality gq ON (t.tweet_id = gq.tweet_id)
            GROUP BY t.tweet_id) temp
      WHERE p > x) temp2;

SELECT tweet_id,
       origin
FROM tweets
INTO OUTFILE '/var/lib/mysql-files/tweets.csv' FIELDS TERMINATED BY ','
    OPTIONALLY ENCLOSED BY '"'
    ESCAPED BY '' LINES TERMINATED BY '\n';
-- Then add the CSV headers manually.

SELECT tweet_id,
       session_id,
       date,
       vote
FROM votes
INTO OUTFILE '/var/lib/mysql-files/annotations.csv' FIELDS TERMINATED BY ','
    OPTIONALLY ENCLOSED BY '"'
    ESCAPED BY '' LINES TERMINATED BY '\n';
-- Then add the CSV headers manually.
