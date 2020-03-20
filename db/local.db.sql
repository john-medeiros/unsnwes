--
-- File generated with SQLiteStudio v3.2.1 on sex mar 20 19:34:46 2020
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: rss_feed_collected
DROP TABLE IF EXISTS rss_feed_collected;

CREATE TABLE rss_feed_collected (
    feed_title                    VARCHAR (4000),
    feed_subtitle                 VARCHAR (4000),
    feed_link                     VARCHAR (4000),
    feed_entry_title              VARCHAR (4000),
    feed_entry_published_datetime VARCHAR (4000),
    feed_entry_link               VARCHAR (4000),
    feed_entry_raw                VARCHAR (4000),
    creation_time                 DATETIME,
    feed_entry_id_hash            VARCHAR (32)   UNIQUE
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
