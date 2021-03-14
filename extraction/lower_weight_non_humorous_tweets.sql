SET FOREIGN_KEY_CHECKS = 0;
REPLACE tweets (tweet_id, text, account_id, origin, lang, weight)
SELECT tweet_id, text, account_id, origin, lang, 0 as weight
FROM votes
         NATURAL JOIN tweets
WHERE vote != 'n'
GROUP BY tweet_id
HAVING count(*) > 2
   AND group_concat(DISTINCT vote) = 'x';
SET FOREIGN_KEY_CHECKS = 1;

# To check:
SELECT *
FROM tweets
WHERE weight = 0;
