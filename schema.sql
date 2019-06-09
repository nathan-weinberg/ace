DROP DATABASE contacts;
CREATE DATABASE contacts;
USE contacts;

CREATE TABLE affiliations (
	aid integer PRIMARY KEY AUTO_INCREMENT,
	affiliation varchar(191) UNIQUE NOT NULL
);

CREATE TABLE people (
	uid integer PRIMARY KEY AUTO_INCREMENT,
	first_name varchar(191) NOT NULL,
	last_name varchar(191) NOT NULL,
	phone_number varchar(20) UNIQUE NOT NULL,
	affiliated_with integer NOT NULL,
	FOREIGN KEY (affiliated_with) REFERENCES affiliations(aid)
);
