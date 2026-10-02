CREATE DATABASE IF NOT EXISTS creator_info;
USE creator_info;

CREATE TABLE Creators (
    id INT AUTO_INCREMENT PRIMARY KEY,
    creator_type ENUM('photographer', 'editor') NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    location VARCHAR(255) NOT NULL,
    experience INT NOT NULL,
    equipment TEXT,
    bio TEXT NOT NULL,
    profile_photo LONGBLOB,
    website VARCHAR(255),
    instagram VARCHAR(255),
    availability ENUM('full-time', 'part-time', 'weekends', 'custom') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    creator_id INT NOT NULL,
    service_name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    unit VARCHAR(50) NOT NULL, 
    FOREIGN KEY (creator_id) REFERENCES Creators(id) ON DELETE CASCADE
);

CREATE TABLE Portfolio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    creator_id INT NOT NULL,
    portfolio_link VARCHAR(255) NOT NULL,
    FOREIGN KEY (creator_id) REFERENCES Creators(id) ON DELETE CASCADE
);

CREATE TABLE PaymentMethods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    creator_id INT NOT NULL,
    method ENUM('bank-transfer', 'paypal', 'credit-card', 'cash') NOT NULL,
    FOREIGN KEY (creator_id) REFERENCES Creators(id) ON DELETE CASCADE
);

