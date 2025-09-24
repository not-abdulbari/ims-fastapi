CREATE TABLE IF NOT EXISTS indent ( 
    id INT AUTO_INCREMENT PRIMARY KEY, 
    product_number VARCHAR(50), 
    product_name VARCHAR(255), 
    requested_quantity INT, 
    pieces INT, 
    date DATE, 
    store_name VARCHAR(255), 
    bought_quantity INT, 
    min_weight INT, 
    max_weight INT, 
    unit VARCHAR(50) 
);