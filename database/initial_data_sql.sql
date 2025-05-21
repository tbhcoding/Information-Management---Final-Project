-- Sample data for the ice cream shop database

-- Insert customers
INSERT INTO `customers` VALUES 
(1, 'John', 'Smith'),
(2, 'Sarah', 'Johnson'),
(3, 'Michael', 'Williams'),
(4, 'Emma', 'Brown'),
(5, 'James', 'Jones');

-- Insert addresses
INSERT INTO `address` VALUES 
(1, '123 Main St', 'Apt 4B', 'New York', '10001'),
(2, '456 Park Ave', NULL, 'New York', '10002'),
(3, '789 Broadway', 'Suite 10', 'New York', '10003'),
(4, '321 Elm St', NULL, 'Brooklyn', '11201'),
(5, '654 Oak St', 'Apt 7C', 'Queens', '11101');

-- Insert items
INSERT INTO `item` VALUES 
('ITM001', 'VAN001', 'Vanilla Ice Cream', 'Classic', 'Small', 3.99),
('ITM002', 'VAN002', 'Vanilla Ice Cream', 'Classic', 'Medium', 4.99),
('ITM003', 'VAN003', 'Vanilla Ice Cream', 'Classic', 'Large', 5.99),
('ITM004', 'CHO001', 'Chocolate Ice Cream', 'Classic', 'Small', 3.99),
('ITM005', 'CHO002', 'Chocolate Ice Cream', 'Classic', 'Medium', 4.99),
('ITM006', 'CHO003', 'Chocolate Ice Cream', 'Classic', 'Large', 5.99),
('ITM007', 'STR001', 'Strawberry Ice Cream', 'Classic', 'Small', 3.99),
('ITM008', 'STR002', 'Strawberry Ice Cream', 'Classic', 'Medium', 4.99),
('ITM009', 'STR003', 'Strawberry Ice Cream', 'Classic', 'Large', 5.99),
('ITM010', 'MINT001', 'Mint Chocolate Chip', 'Premium', 'Small', 4.99),
('ITM011', 'MINT002', 'Mint Chocolate Chip', 'Premium', 'Medium', 5.99),
('ITM012', 'MINT003', 'Mint Chocolate Chip', 'Premium', 'Large', 6.99);

-- Insert ingredients
INSERT INTO `ingredient` VALUES 
('ING001', 'Milk', 1000, 'ml', 1.20),
('ING002', 'Cream', 500, 'ml', 2.50),
('ING003', 'Sugar', 200, 'g', 0.75),
('ING004', 'Vanilla Extract', 15, 'ml', 1.50),
('ING005', 'Cocoa Powder', 50, 'g', 1.25),
('ING006', 'Strawberries', 300, 'g', 2.75),
('ING007', 'Mint Extract', 10, 'ml', 1.40),
('ING008', 'Chocolate Chips', 100, 'g', 1.80);

-- Insert recipes
INSERT INTO `recipe` VALUES 
(1, 'VAN001', 'ING001', 200),
(2, 'VAN001', 'ING002', 100),
(3, 'VAN001', 'ING003', 40),
(4, 'VAN001', 'ING004', 5),
(5, 'CHO001', 'ING001', 200),
(6, 'CHO001', 'ING002', 100),
(7, 'CHO001', 'ING003', 40),
(8, 'CHO001', 'ING005', 15),
(9, 'STR001', 'ING001', 200),
(10, 'STR001', 'ING002', 100),
(11, 'STR001', 'ING003', 40),
(12, 'STR001', 'ING006', 100),
(13, 'MINT001', 'ING001', 200),
(14, 'MINT001', 'ING002', 100),
(15, 'MINT001', 'ING003', 40),
(16, 'MINT001', 'ING007', 5),
(17, 'MINT001', 'ING008', 30);

-- Insert inventory
INSERT INTO `inventory` VALUES 
(1, 'ITM001', 50),
(2, 'ITM002', 40),
(3, 'ITM003', 30),
(4, 'ITM004', 45),
(5, 'ITM005', 35),
(6, 'ITM006', 25),
(7, 'ITM007', 40),
(8, 'ITM008', 30),
(9, 'ITM009', 20),
(10, 'ITM010', 35),
(11, 'ITM011', 25),
(12, 'ITM012', 15);

-- Insert staff
INSERT INTO `staff` VALUES 
('STAFF001', 'Robert', 'Miller', 'Manager', 20.00),
('STAFF002', 'Jennifer', 'Davis', 'Assistant Manager', 17.50),
('STAFF003', 'David', 'Garcia', 'Cashier', 12.00),
('STAFF004', 'Lisa', 'Rodriguez', 'Ice Cream Maker', 14.00),
('STAFF005', 'Mark', 'Wilson', 'Server', 11.00),
('STAFF006', 'Emily', 'Martinez', 'Server', 11.00);

-- Insert shifts
INSERT INTO `shift` VALUES 
('SH001', 'Monday', '08:00:00', '16:00:00'),
('SH002', 'Monday', '16:00:00', '00:00:00'),
('SH003', 'Tuesday', '08:00:00', '16:00:00'),
('SH004', 'Tuesday', '16:00:00', '00:00:00'),
('SH005', 'Wednesday', '08:00:00', '16:00:00'),
('SH006', 'Wednesday', '16:00:00', '00:00:00'),
('SH007', 'Thursday', '08:00:00', '16:00:00'),
('SH008', 'Thursday', '16:00:00', '00:00:00'),
('SH009', 'Friday', '08:00:00', '16:00:00'),
('SH010', 'Friday', '16:00:00', '00:00:00'),
('SH011', 'Saturday', '08:00:00', '16:00:00'),
('SH012', 'Saturday', '16:00:00', '00:00:00'),
('SH013', 'Sunday', '08:00:00', '16:00:00'),
('SH014', 'Sunday', '16:00:00', '00:00:00');

-- Insert rotations
INSERT INTO `rotation` VALUES 
(1, 'ROT001', '2025-05-19 00:00:00', 'SH001', 'STAFF001'),
(2, 'ROT002', '2025-05-19 00:00:00', 'SH001', 'STAFF003'),
(3, 'ROT003', '2025-05-19 00:00:00', 'SH001', 'STAFF005'),
(4, 'ROT004', '2025-05-19 00:00:00', 'SH002', 'STAFF002'),
(5, 'ROT005', '2025-05-19 00:00:00', 'SH002', 'STAFF004'),
(6, 'ROT006', '2025-05-19 00:00:00', 'SH002', 'STAFF006'),
(7, 'ROT007', '2025-05-20 00:00:00', 'SH003', 'STAFF001'),
(8, 'ROT008', '2025-05-20 00:00:00', 'SH003', 'STAFF003'),
(9, 'ROT009', '2025-05-20 00:00:00', 'SH003', 'STAFF005'),
(10, 'ROT010', '2025-05-20 00:00:00', 'SH004', 'STAFF002'),
(11, 'ROT011', '2025-05-20 00:00:00', 'SH004', 'STAFF004'),
(12, 'ROT012', '2025-05-20 00:00:00', 'SH004', 'STAFF006');

-- Insert orders
INSERT INTO `orders` VALUES 
(1, 'ORD001', '2025-05-19 10:30:00', 'ITM001', 3.99, 2, 1, 0, 1),
(2, 'ORD002', '2025-05-19 11:45:00', 'ITM004', 3.99, 1, 2, 1, 2),
(3, 'ORD003', '2025-05-19 13:20:00', 'ITM007', 3.99, 3, 3, 0, 3),
(4, 'ORD004', '2025-05-19 15:10:00', 'ITM010', 4.99, 2, 4, 1, 4),
(5, 'ORD005', '2025-05-20 09:45:00', 'ITM002', 4.99, 1, 5, 0, 5),
(6, 'ORD006', '2025-05-20 12:30:00', 'ITM005', 4.99, 2, 1, 1, 1),
(7, 'ORD007', '2025-05-20 14:15:00', 'ITM008', 4.99, 1, 2, 0, 2),
(8, 'ORD008', '2025-05-20 16:50:00', 'ITM011', 5.99, 3, 3, 1, 3),
(9, 'ORD009', '2025-05-21 10:20:00', 'ITM003', 5.99, 1, 4, 0, 4),
(10, 'ORD010', '2025-05-21 11:55:00', 'ITM006', 5.99, 2, 5, 1, 5);