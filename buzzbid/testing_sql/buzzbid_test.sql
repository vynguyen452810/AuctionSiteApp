create schema BuzzBid;
use BuzzBid;
-- Adding Buzz Bidd tables
CREATE TABLE `User` (
	username varchar(50) NOT NULL,
    first_name varchar(50) NOT NULL,
    last_name varchar(50) NOT NULL,
    `password` varchar(15) NOT NULL,
    PRIMARY KEY (username)
);

CREATE TABLE AdministrativeUser (
	username varchar(50) NOT NULL,
    position varchar(100) NOT NULL,
    PRIMARY KEY (username)
);


CREATE TABLE Item (
    itemID int unsigned NOT NULL AUTO_INCREMENT,
    item_name varchar(250) NOT NULL,
    item_description varchar(250) NOT NULL,
	item_condition enum('New', 'Very Good', 'Good', 'Fair', 'Poor') NOT NULL,  
	returnable boolean NOT NULL,
	starting_bid decimal(10, 2) NOT NULL,
    min_sale_price decimal(10, 2) NOT NULL,
    auction_end_time datetime NOT NULL,
    get_it_now_price decimal(10, 2) NULL, 
    listeduser varchar(50) NOT NULL,
    category_name varchar(50) NOT NULL,
    cancelled_username varchar(50) NULL,
    cancelled_reason varchar(250) NULL,
    PRIMARY KEY (itemID)
);

 -- Seperate category table for in case Database Administrator can change it 
CREATE TABLE Category (
    category_name varchar(50) NOT NULL,
    PRIMARY KEY (category_name)
);

CREATE TABLE Bid (
    itemID int unsigned NOT NULL,
	bid_amount decimal(10, 2) NOT NULL,
    time_of_bid datetime NOT NULL, 
    username varchar(50) NULL,
    PRIMARY KEY (itemID, bid_amount) 
);

CREATE TABLE Rating (
    itemID int unsigned NOT NULL,
    rating_date_time datetime NOT NULL, 
    star int NOT NULL,
    `comment` varchar(250) NULL,
    PRIMARY KEY (itemID, rating_date_time) 
);

SELECT `password` FROM `User` WHERE username= 'jay23';

-- Constraints
ALTER TABLE AdministrativeUser
    ADD CONSTRAINT fk_AdministrativeUser_username_User_username
    FOREIGN KEY (username) 
    REFERENCES User(username)
    ON UPDATE CASCADE ON DELETE CASCADE;
    
ALTER TABLE Item
    ADD CONSTRAINT fk_Item_category_name_Category_category_name 
    FOREIGN KEY (category_name) 
    REFERENCES Category(category_name)
    ON UPDATE CASCADE;

ALTER TABLE Item
    ADD CONSTRAINT fk_Item_listeduser_User_username 
    FOREIGN KEY (listeduser) 
    REFERENCES `User`(username)
    ON UPDATE CASCADE;

ALTER TABLE Item
    ADD CONSTRAINT fk_Item_cancelled_username_User_username
    FOREIGN KEY (cancelled_username) 
    REFERENCES AdministrativeUser(username)
    ON UPDATE CASCADE;

ALTER TABLE Bid
    ADD CONSTRAINT fk_Bid_username_User_username 
    FOREIGN KEY (username) 
    REFERENCES User(username)
    ON UPDATE CASCADE;
    
ALTER TABLE Bid
    ADD CONSTRAINT fk_Bid_itemID_Item_itemID 
    FOREIGN KEY (itemID) 
    REFERENCES Item(itemID)
    ON DELETE CASCADE;
    
ALTER TABLE Rating
    ADD CONSTRAINT fk_Rating_itemID_Item_itemID 
    FOREIGN KEY (itemID) 
    REFERENCES Item(itemID)
    ON DELETE CASCADE;
    
ALTER TABLE Rating
    ADD CONSTRAINT star_check CHECK (star >= 0 AND star <= 5);

-- Alter table Rating 
-- 	Add column username varchar(50) null; 
    
--     ALTER TABLE Rating
--     ADD CONSTRAINT fk_Rating_username_User_username 
--     FOREIGN KEY (username) 
--     REFERENCES User(username)
--     ON UPDATE CASCADE;

INSERT INTO User (username, first_name,last_name,password) 
VALUES 
	('jay23', 'Jay', 'Vu', 'house'),
    ('ari123', 'Arianna', 'Dave', 'bicycle'),
    ('vn45', 'Vy', 'Nguyen', 'helloworld');
    
INSERT INTO User (username, first_name,last_name,password) 
VALUES ('jm', 'John', 'Smith', 'hihi'),
	('mark00', 'Leo', 'Mark', 'pillow');
    
INSERT INTO AdministrativeUser (username, position) 
 VALUES ('jay23', 'Admin');
 
INSERT INTO AdministrativeUser (username, position) 
 VALUES ('mark00', 'Admin');


INSERT INTO Category (category_name ) 
VALUES 
	('Art'),
    ('Books'),
    ('Electronics'),
    ('Home & Gardens'),
    ('Sporting Goods'),
    ('Toys'),
    ('Other');


INSERT INTO item (itemID, item_name, item_description, item_condition, returnable, starting_bid, min_sale_price, auction_end_time, get_it_now_price, listeduser, category_name, cancelled_username, cancelled_reason) VALUES (1, 'dish soap', 'detergent to wash dishes', 'New', 1, 10.0, 8.0, '2012-12-21 11:00:00', 3.0, 'jay23', 'Home & Gardens', NULL, NULL);
INSERT INTO item (itemID, item_name, item_description, item_condition, returnable, starting_bid, min_sale_price, auction_end_time, get_it_now_price, listeduser, category_name, cancelled_username, cancelled_reason) VALUES (3, 'TV', 'a big screen showing interesting things', 'Fair', 1, 1000.0, 850.0, '2014-12-21 10:00:00', 5.5, 'jay23', 'Electronics', 'jay23', 'doesnot gone fit');
INSERT INTO item (itemID, item_name, item_description, item_condition, returnable, starting_bid, min_sale_price, auction_end_time, get_it_now_price, listeduser, category_name, cancelled_username, cancelled_reason) VALUES (4, 'a', 'ghsjahgs', 'New', 1, 5.0, 8.0, '2015-12-21 12:00:00', 3.0, 'ari123', 'Home & Gardens', NULL, NULL);
INSERT INTO item (itemID, item_name, item_description, item_condition, returnable, starting_bid, min_sale_price, auction_end_time, get_it_now_price, listeduser, category_name, cancelled_username, cancelled_reason) VALUES (5, 'b', 'smfgkda', 'Good', 0, 30.0, 45.0, '2016-12-21 20:00:00', 5.5, 'vn45', 'Electronics', NULL, NULL);
INSERT INTO item (itemID, item_name, item_description, item_condition, returnable, starting_bid, min_sale_price, auction_end_time, get_it_now_price, listeduser, category_name, cancelled_username, cancelled_reason) VALUES (7, 'dish soap', 'detergent to wash dishes', 'New', 1, 10.0, 8.0, '2024-03-18 19:17:51', 3.0, 'jay23', 'Home & Gardens', NULL, NULL);
INSERT INTO item (itemID, item_name, item_description, item_condition, returnable, starting_bid, min_sale_price, auction_end_time, get_it_now_price, listeduser, category_name, cancelled_username, cancelled_reason) VALUES (11, 'Sony TV 55 inch', 'detergent to wash dishes', 'New', 1, 10.0, 18.0, '2012-12-21 11:00:00', 3.0, 'jay23', 'Electronics', NULL, NULL);
INSERT INTO item (itemID, item_name, item_description, item_condition, returnable, starting_bid, min_sale_price, auction_end_time, get_it_now_price, listeduser, category_name, cancelled_username, cancelled_reason) VALUES (12, 'LG tv', 'a baseball hat bla bla', 'Good', 0, 50.0, 45.0, '2013-12-21 23:59:59', 5.0, 'ari123', 'Electronics', NULL, NULL);
INSERT INTO item (itemID, item_name, item_description, item_condition, returnable, starting_bid, min_sale_price, auction_end_time, get_it_now_price, listeduser, category_name, cancelled_username, cancelled_reason) VALUES (13, 'TV', 'a big screen showing interesting things', 'Fair', 1, 1000.0, 850.0, '2014-12-21 10:00:00', 5.5, 'jay23', 'Electronics', 'jay23', 'doesnot gone fit');
INSERT INTO item (itemID, item_name, item_description, item_condition, returnable, starting_bid, min_sale_price, auction_end_time, get_it_now_price, listeduser, category_name, cancelled_username, cancelled_reason) VALUES (14, 'Samsung 55 inch', 'detergent tv wash dishes', 'Very Good', 1, 10.0, 18.0, '2012-12-21 11:00:00', 3.0, 'jay23', 'Electronics', NULL, NULL);
INSERT INTO item (itemID, item_name, item_description, item_condition, returnable, starting_bid, min_sale_price, auction_end_time, get_it_now_price, listeduser, category_name, cancelled_username, cancelled_reason) VALUES (15, 'LG', 'a baseball hat bla TV', 'New', 0, 50.0, 45.0, '2013-12-21 23:59:59', 5.0, 'ari123', 'Electronics', NULL, NULL);
INSERT INTO item (itemID, item_name, item_description, item_condition, returnable, starting_bid, min_sale_price, auction_end_time, get_it_now_price, listeduser, category_name, cancelled_username, cancelled_reason) VALUES (16, 'Tv', 'a big screen showing interesting things', 'Fair', 1, 1000.0, 850.0, '2014-12-21 10:00:00', 5.5, 'jay23', 'Electronics', 'jay23', 'doesnot gone fit');
INSERT INTO item (itemID, item_name, item_description, item_condition, returnable, starting_bid, min_sale_price, auction_end_time, get_it_now_price, listeduser, category_name, cancelled_username, cancelled_reason) VALUES (20, 'Samsung 55 inch', 'detergent tv wash dishes', 'Very Good', 1, 10.0, 18.0, '2012-12-21 11:00:00', 3.0, 'jay23', 'Home & Gardens', NULL, NULL);
INSERT INTO item (itemID, item_name, item_description, item_condition, returnable, starting_bid, min_sale_price, auction_end_time, get_it_now_price, listeduser, category_name, cancelled_username, cancelled_reason) VALUES (22, 'LG', 'a baseball hat bla TV', 'New', 0, 50.0, 45.0, '2013-12-21 23:59:59', 5.0, 'ari123', 'Books', NULL, NULL);
INSERT INTO item (itemID, item_name, item_description, item_condition, returnable, starting_bid, min_sale_price, auction_end_time, get_it_now_price, listeduser, category_name, cancelled_username, cancelled_reason) VALUES (23, 'Tv', 'a big screen showing interesting things', 'Fair', 1, 1000.0, 850.0, '2014-12-21 10:00:00', 5.5, 'jay23', 'Other', 'jay23', 'doesnot gone fit');

INSERT INTO Rating (itemID, rating_date_time, star, comment)
VALUES
    (1, '2024-03-16 12:00:00', 5, 'Excellent condition and fast shipping'),
    (3, '2024-03-16 13:00:00', 4, 'Very good, but delayed delivery'),
    (4, '2024-03-16 14:00:00', 3, 'Item as described, average experience');

INSERT INTO bid (itemID, bid_amount, time_of_bid, username) VALUES (3, 1500.0, '2024-03-10 12:30:00', 'jay23');
INSERT INTO bid (itemID, bid_amount, time_of_bid, username) VALUES (3, 1800.0, '2024-03-08 10:30:00', 'vn45');
INSERT INTO bid (itemID, bid_amount, time_of_bid, username) VALUES (3, 2000.0, '2024-03-05 09:30:00', 'ari123');
INSERT INTO bid (itemID, bid_amount, time_of_bid, username) VALUES (11, 15.0, '2024-03-10 12:30:00', 'jay23');
INSERT INTO bid (itemID, bid_amount, time_of_bid, username) VALUES (11, 18.0, '2024-03-08 10:30:00', 'vn45');

INSERT INTO bid (itemID, bid_amount, time_of_bid, username) VALUES (25, 355.0, '2024-03-28 12:30:00', 'jay23');
INSERT INTO bid (itemID, bid_amount, time_of_bid, username) VALUES (25, 360.0, '2024-03-09 10:30:00', 'vn45');
INSERT INTO bid (itemID, bid_amount, time_of_bid, username) VALUES (25, 370.0, '2024-04-01 08:00:00', 'ari123');
INSERT INTO bid (itemID, bid_amount, time_of_bid, username) VALUES (25, 375.0, '2024-04-01 11:00:00', 'mark00');
INSERT INTO bid (itemID, bid_amount, time_of_bid, username) VALUES (25, 380.0, '2024-03-31 08:00:00', 'jm');

INSERT INTO Rating (itemID, rating_date_time, star, comment) 
	VALUES (25, '2024-03-28 12:30:00', '1', 'I do not like it'),
			(25, '2024-03-31 9:30:00', '4', 'Decent, work properly, but not great'),
			(25, '2024-04-01 10:15:00', '2', 'Nahhhh, i would not buy it again');
            
show tables;
select * from User;

