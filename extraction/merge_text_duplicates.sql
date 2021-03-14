CREATE TABLE duplicates
( # This isn't temporary because it cannot be reused inside a sub-select.
    tweet_id  BIGINT UNSIGNED NOT NULL,
    unique_id BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (tweet_id)
) ENGINE InnoDB
AS
SELECT t.tweet_id, d.unique_id
FROM tweets t
         JOIN
     (SELECT text, MIN(tweet_id) unique_id
      FROM tweets
      GROUP BY text
      HAVING COUNT(*) >= 2) d
     ON t.text = d.text;

# To see the votes from the same session to duplicate tweets, but with different vote value:
SELECT unique_id, session_id, GROUP_CONCAT(vote ORDER BY date)
FROM votes
         NATURAL JOIN duplicates
GROUP BY unique_id, session_id
HAVING COUNT(DISTINCT vote) > 1;

UPDATE IGNORE votes v, duplicates d,
    (SELECT unique_id, session_id, RIGHT(GROUP_CONCAT(vote ORDER BY date), 1) as vote, MAX(date) as date
     FROM votes
              NATURAL JOIN duplicates
     GROUP BY unique_id, session_id) m
SET v.tweet_id = d.unique_id,
    v.vote     = m.vote,
    v.date     = m.date
WHERE v.tweet_id = d.tweet_id
  AND (d.unique_id = m.unique_id AND v.session_id = m.session_id);

# In case some tuples were not deleted because of duplicates:
# noinspection SqlWithoutWhere
DELETE
FROM votes
    USING votes
              NATURAL JOIN (SELECT tweet_id FROM duplicates WHERE tweet_id != unique_id) d;

# noinspection SqlWithoutWhere
DELETE
FROM tweets
    USING tweets
              NATURAL JOIN (SELECT tweet_id FROM duplicates WHERE tweet_id != unique_id) d;

DROP TABLE duplicates;
