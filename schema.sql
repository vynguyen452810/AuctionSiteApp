CREATE SCHEMA BuzzBid;
USE BuzzBid;

-- Tables
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


-- Constraints
ALTER TABLE AdministrativeUser
    ADD CONSTRAINT fk_AdministrativeUser_username_User_username
    FOREIGN KEY (username) 
    REFERENCES `User`(username)
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
    REFERENCES `User`(username)
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