CREATE DATABASE pghumor DEFAULT CHARSET utf8;

USE pghumor;

CREATE TABLE accounts (
  account_id BIGINT UNSIGNED NOT NULL,
  name VARCHAR(100) NOT NULL,
  followers BIGINT NOT NULL,
  PRIMARY KEY (account_id)
) ENGINE InnoDB DEFAULT CHARSET utf8;

CREATE TABLE tweets (
  tweet_id BIGINT UNSIGNED NOT NULL,
  text VARCHAR(1120) NOT NULL, # 1120 = max length of a tweet (280) * max length in bytes of a utf8 code point (4).
  account_id BIGINT UNSIGNED NOT NULL,
  origin ENUM('hose', 'humorous account') NOT NULL,
  lang ENUM('es', 'en') NOT NULL,
  PRIMARY KEY (tweet_id),
  FOREIGN KEY (account_id) REFERENCES accounts (account_id)
) ENGINE InnoDB DEFAULT CHARSET utf8;

CREATE TABLE votes (
  tweet_id BIGINT UNSIGNED NOT NULL,
  session_id CHAR(100) NOT NULL,
  vote CHAR(1) NOT NULL,
  PRIMARY KEY (tweet_id, session_id),
  INDEX (tweet_id),
  INDEX (session_id),
  FOREIGN KEY (tweet_id) REFERENCES tweets (tweet_id)
) ENGINE InnoDB DEFAULT CHARSET utf8;
