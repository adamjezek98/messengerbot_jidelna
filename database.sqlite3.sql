BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS `users` (
	`id`	integer,
	`userid`	text,
	`weeknotify`	text,
	`hournotify`	text,
	PRIMARY KEY(`id`)
);
CREATE TABLE IF NOT EXISTS `foods` (
	`id`	INTEGER,
	`date`	REAL,
	`daydate`	TEXT,
	`meal`	TEXT,
	PRIMARY KEY(`id`)
);
COMMIT;
