CREATE DATABASE pghumor DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE pghumor;

CREATE TABLE accounts
(
    account_id BIGINT UNSIGNED NOT NULL,
    name       VARCHAR(100),
    followers  BIGINT,
    PRIMARY KEY (account_id)
) ENGINE InnoDB;

CREATE TABLE tweets
(
    tweet_id   BIGINT UNSIGNED                   NOT NULL,
    text       VARCHAR(1120)                     NOT NULL, # 1120 = max length of a tweet (280) * max length in bytes of a utf8 code point (4).
    account_id BIGINT UNSIGNED                   NOT NULL,
    origin     ENUM ('hose', 'humorous account') NOT NULL,
    lang       ENUM ('es', 'en')                 NOT NULL,
    weight     TINYINT UNSIGNED DEFAULT 1,
    PRIMARY KEY (tweet_id),
    FOREIGN KEY (account_id) REFERENCES accounts (account_id)
) ENGINE InnoDB;

CREATE TABLE votes
(
    tweet_id     BIGINT UNSIGNED NOT NULL,
    session_id   CHAR(100)       NOT NULL,
    vote         CHAR(1)         NOT NULL,
    date         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_offensive BOOL      DEFAULT 0,
    PRIMARY KEY (tweet_id, session_id),
    INDEX (tweet_id),
    INDEX (session_id),
    FOREIGN KEY (tweet_id) REFERENCES tweets (tweet_id)
) ENGINE InnoDB;

# No foreign key between `votes` and `prolific` for `session_id` because there could be no votes, and also the ID may
# have not consented yet.
CREATE TABLE prolific
(
    session_id CHAR(100) NOT NULL,
    consent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finish_date TIMESTAMP NULL,
    comments VARCHAR(300) DEFAULT NULL,
    PRIMARY KEY (session_id)
) ENGINE InnoDB;
