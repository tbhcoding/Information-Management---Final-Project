-- First drop foreign key constraints (if they exist)
SET FOREIGN_KEY_CHECKS = 0;

-- Drop all tables
DROP TABLE IF EXISTS `rotation`;
DROP TABLE IF EXISTS `shift`;
DROP TABLE IF EXISTS `staff`;
DROP TABLE IF EXISTS `inventory`;
DROP TABLE IF EXISTS `recipe`;
DROP TABLE IF EXISTS `ingredient`;
DROP TABLE IF EXISTS `item`;
DROP TABLE IF EXISTS `address`;
DROP TABLE IF EXISTS `customers`;
DROP TABLE IF EXISTS `orders`;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `orders` (
    `row_id` INT NOT NULL,
    `order_id` VARCHAR(10) NOT NULL,
    `created_at` DATETIME NOT NULL,
    `item_id` VARCHAR(10) NOT NULL,
    `item_price` DECIMAL(5,2) NOT NULL,
    `quantity` INT NOT NULL,
    `cust_id` INT NOT NULL,
    `delivery` BOOLEAN NOT NULL,
    `add_id` INT NOT NULL,
    PRIMARY KEY (`row_id`)
);

CREATE TABLE `customers` (
    `cust_id` INT NOT NULL,
    `cust_firstname` VARCHAR(50) NOT NULL,
    `cust_lastname` VARCHAR(50) NOT NULL,
    PRIMARY KEY (`cust_id`)
);

CREATE TABLE `address` (
    `add_id` INT NOT NULL,
    `delivery_address1` VARCHAR(200) NOT NULL,
    `delivery_address2` VARCHAR(200) NULL,
    `delivery_city` VARCHAR(50) NOT NULL,
    `delivery_zipcode` VARCHAR(20) NOT NULL,
    PRIMARY KEY (`add_id`)
);

CREATE TABLE `item` (
    `item_id` VARCHAR(10) NOT NULL,
    `sku` VARCHAR(20) NOT NULL,
    `item_name` VARCHAR(100) NOT NULL,
    `item_cat` VARCHAR(50) NOT NULL,
    `item_size` VARCHAR(10) NOT NULL,
    `item_price` DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (`item_id`)
);

CREATE TABLE `ingredient` (
    `ing_id` VARCHAR(10) NOT NULL,
    `ing_name` VARCHAR(200) NOT NULL,
    `ing_weight` INT NOT NULL,
    `ing_meas` VARCHAR(20) NOT NULL,
    `ing_price` DECIMAL(5,2) NOT NULL,
    PRIMARY KEY (`ing_id`)
);

CREATE TABLE `recipe` (
    `row_id` INT NOT NULL,
    `recipe_id` VARCHAR(20) NOT NULL,
    `ing_id` VARCHAR(10) NOT NULL,
    `quantity` INT NOT NULL,
    PRIMARY KEY (`row_id`)
);

CREATE TABLE `inventory` (
    `inv_id` INT NOT NULL,
    `item_id` VARCHAR(10) NOT NULL,
    `quantity` INT NOT NULL,
    PRIMARY KEY (`inv_id`)
);

CREATE TABLE `staff` (
    `staff_id` VARCHAR(20) NOT NULL,
    `first_name` VARCHAR(50) NOT NULL,
    `last_name` VARCHAR(50) NOT NULL,
    `position` VARCHAR(100) NOT NULL,
    `hourly_rate` DECIMAL(5,2) NOT NULL,
    PRIMARY KEY (`staff_id`)
);

CREATE TABLE `shift` (
    `shift_id` VARCHAR(20) NOT NULL,
    `day_of_week` VARCHAR(10) NOT NULL,
    `start_time` TIME NOT NULL,
    `end_time` TIME NOT NULL,
    PRIMARY KEY (`shift_id`)
);

CREATE TABLE `rotation` (
    `row_id` INT NOT NULL,
    `rota_id` VARCHAR(20) NOT NULL,
    `date` DATETIME NOT NULL,
    `shift_id` VARCHAR(20) NOT NULL,
    `staff_id` VARCHAR(20) NOT NULL,
    PRIMARY KEY (`row_id`)
);

ALTER TABLE `orders` ADD INDEX `idx_cust_id` (`cust_id`);
ALTER TABLE `orders` ADD INDEX `idx_item_id` (`item_id`);
ALTER TABLE `orders` ADD INDEX `idx_add_id` (`add_id`);
ALTER TABLE `orders` ADD INDEX `idx_created_at` (`created_at`);
ALTER TABLE `recipe` ADD INDEX `idx_recipe_id` (`recipe_id`);
ALTER TABLE `recipe` ADD INDEX `idx_ing_id` (`ing_id`);
ALTER TABLE `rotation` ADD INDEX `idx_shift_id` (`shift_id`);
ALTER TABLE `rotation` ADD INDEX `idx_staff_id` (`staff_id`);
ALTER TABLE `item` ADD UNIQUE INDEX `idx_sku` (`sku`);

ALTER TABLE `orders` ADD CONSTRAINT `fk_orders_cust_id` FOREIGN KEY(`cust_id`) 
REFERENCES `customers` (`cust_id`);

ALTER TABLE `orders` ADD CONSTRAINT `fk_orders_add_id` FOREIGN KEY(`add_id`)
REFERENCES `address` (`add_id`);

ALTER TABLE `orders` ADD CONSTRAINT `fk_orders_item_id` FOREIGN KEY(`item_id`)
REFERENCES `item` (`item_id`);

ALTER TABLE `recipe` ADD CONSTRAINT `fk_recipe_ing_id` FOREIGN KEY(`ing_id`)
REFERENCES `ingredient` (`ing_id`);

ALTER TABLE `recipe` ADD CONSTRAINT `fk_recipe_recipe_id` FOREIGN KEY(`recipe_id`)
REFERENCES `item` (`sku`);

ALTER TABLE `inventory` ADD CONSTRAINT `fk_inventory_item_id` FOREIGN KEY(`item_id`)
REFERENCES `item` (`item_id`);

ALTER TABLE `rotation` ADD CONSTRAINT `fk_rotation_shift_id` FOREIGN KEY(`shift_id`)
REFERENCES `shift` (`shift_id`);

ALTER TABLE `rotation` ADD CONSTRAINT `fk_rotation_staff_id` FOREIGN KEY(`staff_id`)
REFERENCES `staff` (`staff_id`);