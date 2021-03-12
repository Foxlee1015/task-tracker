schema="""
CREATE TABLE IF NOT EXISTS `user` (
    `id`                    INT(11) NOT NULL AUTO_INCREMENT,
    `name`                  VARCHAR(50) UNIQUE,
    `email`                 VARCHAR(50),
    `user_type`             INT(3) DEFAULT 2,
    `login_counting`        INT(5) DEFAULT 0,
    `create_datetime`       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_datetime`       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(`id`)
);

CREATE TABLE IF NOT EXISTS `task` (
    `id`                    INT(11) NOT NULL AUTO_INCREMENT,
    `title`                 VARCHAR(50),
    `text`                  VARCHAR(200),
    `repeat_type`           INT(3) DEFAULT 2,
    `user_id`               INT(11) NOT NULL,
    `create_datetime`       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_datetime`       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(`id`),
    CONSTRAINT FOREIGN KEY (`user_id`) REFERENCES `task_tracker`.`user` (`id`) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `session` (
    `id`                    INT(11) NOT NULL AUTO_INCREMENT,
    `user_id`               INT(11) NOT NULL,
    `token`                 VARCHAR(100) NOT NULL,
    `last_call_datetime`    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(`id`,`user_id`,`token`),
    CONSTRAINT FOREIGN KEY (`user_id`) REFERENCES `task_tracker`.`user` (`id`) ON UPDATE CASCADE ON DELETE CASCADE
);
"""