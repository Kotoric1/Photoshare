CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;

CREATE TABLE Users(
 user_id INTEGER AUTO_INCREMENT,
 email VARCHAR(255) UNIQUE NOT NULL,
 password VARCHAR(255) NOT NULL,
 first_name VARCHAR(255) NOT NULL,
 last_name VARCHAR(255) NOT NULL,
 birthday DATE,
 hometown VARCHAR(255),
 gender VARCHAR(255),
 PRIMARY KEY (user_id));

 CREATE TABLE Friends(
 user_id INTEGER,
 friend_id INTEGER,
 PRIMARY KEY (user_id, friend_id),
 FOREIGN KEY (user_id) REFERENCES Users(user_id),
 FOREIGN KEY (friend_id) REFERENCES Users(user_id));

CREATE TABLE Albums_have(
 albums_id INTEGER AUTO_INCREMENT,
 user_id INTEGER NOT NULL,
 album_name VARCHAR(255) UNIQUE,
 date DATE,
 PRIMARY KEY (albums_id),
 FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE NO ACTION);

CREATE TABLE Tags(
 tag_id INTEGER AUTO_INCREMENT,
 word VARCHAR(255) UNIQUE,
 PRIMARY KEY (tag_id)
);

CREATE TABLE Photos(
 photo_id INTEGER AUTO_INCREMENT,
 albums_id INTEGER NOT NULL,
 album_name VARCHAR(255),
 user_id INTEGER NOT NULL,
 caption VARCHAR(255),
 data LONGBLOB,
 PRIMARY KEY (photo_id),
  FOREIGN KEY (user_id) REFERENCES Users (user_id),
 FOREIGN KEY (albums_id) REFERENCES Albums_have (albums_id) ON DELETE CASCADE);

CREATE TABLE Tagged(
 photo_id INTEGER,
 tag_id INTEGER,
 PRIMARY KEY (photo_id, tag_id),
 FOREIGN KEY(photo_id) REFERENCES Photos (photo_id) ON DELETE CASCADE,
 FOREIGN KEY(tag_id) REFERENCES Tags (tag_id));

CREATE TABLE Comments(
 comment_id INTEGER AUTO_INCREMENT,
 text VARCHAR (255),
 date DATE,
  user_id INTEGER NOT NULL,
 photo_id INTEGER NOT NULL,
 PRIMARY KEY (comment_id),
 FOREIGN KEY (user_id) REFERENCES Users (user_id),
 FOREIGN KEY (photo_id) REFERENCES Photos (photo_id) ON DELETE CASCADE );

CREATE TABLE Likes(
user_id INTEGER,
 photo_id INTEGER,
 PRIMARY KEY (photo_id, user_id),
 FOREIGN KEY (user_id) REFERENCES Users (user_id),
 FOREIGN KEY (photo_id) REFERENCES Photos (photo_id) ON DELETE CASCADE);
 
 
