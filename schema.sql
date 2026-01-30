-- Initial schema for farmer_updated app (run once when MySQL starts, e.g. in Docker init)
-- Database is created by MYSQL_DATABASE=farmer_updated in docker-compose

USE farmer_updated;

CREATE TABLE IF NOT EXISTS Farmers (
    FarmerID INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    language VARCHAR(50),
    field_size VARCHAR(100),
    contact_info VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS CropTypes (
    CropTypeID INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS Queries (
    QueryID INT AUTO_INCREMENT PRIMARY KEY,
    FarmerID INT NOT NULL,
    title VARCHAR(500),
    description TEXT,
    image_url VARCHAR(500),
    audio_url VARCHAR(500),
    crop_type VARCHAR(255),
    FOREIGN KEY (FarmerID) REFERENCES Farmers(FarmerID) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS Responses (
    ResponseID INT AUTO_INCREMENT PRIMARY KEY,
    QueryID INT NOT NULL,
    ResponderID INT NOT NULL,
    response_text TEXT,
    is_expert TINYINT(1) DEFAULT 0,
    votes INT DEFAULT 0,
    FOREIGN KEY (QueryID) REFERENCES Queries(QueryID) ON DELETE CASCADE,
    FOREIGN KEY (ResponderID) REFERENCES Farmers(FarmerID) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ResponseLikes (
    ResponseID INT NOT NULL,
    FarmerID INT NOT NULL,
    PRIMARY KEY (ResponseID, FarmerID),
    FOREIGN KEY (ResponseID) REFERENCES Responses(ResponseID) ON DELETE CASCADE,
    FOREIGN KEY (FarmerID) REFERENCES Farmers(FarmerID) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS Equipment (
    EquipmentID INT AUTO_INCREMENT PRIMARY KEY,
    OwnerID INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(255),
    `condition` VARCHAR(100),
    hourly_rate DECIMAL(10,2),
    availability_status VARCHAR(50) DEFAULT 'Available',
    FOREIGN KEY (OwnerID) REFERENCES Farmers(FarmerID) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS LendingRequests (
    RequestID INT AUTO_INCREMENT PRIMARY KEY,
    EquipmentID INT NOT NULL,
    LenderID INT NOT NULL,
    BorrowerID INT NOT NULL,
    start_date DATE,
    duration INT,
    status VARCHAR(50) DEFAULT 'Pending',
    FOREIGN KEY (EquipmentID) REFERENCES Equipment(EquipmentID) ON DELETE CASCADE,
    FOREIGN KEY (LenderID) REFERENCES Farmers(FarmerID) ON DELETE CASCADE,
    FOREIGN KEY (BorrowerID) REFERENCES Farmers(FarmerID) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS Reviews (
    ReviewID INT AUTO_INCREMENT PRIMARY KEY,
    FromFarmerID INT NOT NULL,
    ToFarmerID INT NOT NULL,
    rating INT,
    feedback TEXT,
    type VARCHAR(100),
    FOREIGN KEY (FromFarmerID) REFERENCES Farmers(FarmerID) ON DELETE CASCADE,
    FOREIGN KEY (ToFarmerID) REFERENCES Farmers(FarmerID) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
