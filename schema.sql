CREATE DATABASE pghumor DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE pghumor;

CREATE TABLE accounts (
  account_id BIGINT UNSIGNED NOT NULL,
  name VARCHAR(100),
  followers BIGINT,
  PRIMARY KEY (account_id)
) ENGINE InnoDB;

CREATE TABLE tweets (
  tweet_id BIGINT UNSIGNED NOT NULL,
  text VARCHAR(1120) NOT NULL, # 1120 = max length of a tweet (280) * max length in bytes of a utf8 code point (4).
  account_id BIGINT UNSIGNED NOT NULL,
  origin ENUM('hose', 'humorous account') NOT NULL,
  lang ENUM('es', 'en') NOT NULL,
  weight TINYINT UNSIGNED DEFAULT 1,
  PRIMARY KEY (tweet_id),
  FOREIGN KEY (account_id) REFERENCES accounts (account_id)
) ENGINE InnoDB;

CREATE TABLE votes (
  tweet_id BIGINT UNSIGNED NOT NULL,
  session_id CHAR(100) NOT NULL,
  vote_humor CHAR(1) NOT NULL,
  vote_offensive CHAR(1) NOT NULL,
  vote_personal CHAR(1) NOT NULL,
  date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (tweet_id, session_id),
  INDEX (tweet_id),
  INDEX (session_id),
  FOREIGN KEY (tweet_id) REFERENCES tweets (tweet_id)
) ENGINE InnoDB;

CREATE TABLE annotators (
  session_id CHAR(100) NOT NULL,
  prolific_id CHAR(100) NOT NULL,
  prolific_session_id CHAR(100),
  study_id CHAR(100),
  form_sent TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  question1 CHAR(1),
  question2 CHAR(1),
  question3 CHAR(1),
  question4 CHAR(1),
  question5 CHAR(1),
  question6 CHAR(1)
) ENGINE InnoDB;

CREATE TABLE personality (
  prolific_id CHAR(100) NOT NULL,
  form_sent TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  question1 CHAR(1),
  question2 CHAR(1),
  question3 CHAR(1),
  question4 CHAR(1),
  question5 CHAR(1),
  question6 CHAR(1),
  question7 CHAR(1),
  question8 CHAR(1),
  question9 CHAR(1),
  question10 CHAR(1)
) ENGINE InnoDB;
