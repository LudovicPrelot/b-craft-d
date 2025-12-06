-- MySQL Script for B-CraftD v3.0 - OPTIMIZED WITH TRIGGERS
-- Date: December 4, 2025
-- Version: 3.0.0

-- Drop database if exists (careful in production!)
DROP DATABASE IF EXISTS bcraftd_v3;

-- Create database
CREATE DATABASE IF NOT EXISTS bcraftd_v3 
  CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

USE bcraftd_v3;

-- -----------------------------------------------------
-- Table: weathers
-- -----------------------------------------------------
CREATE TABLE weathers (
  id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(45),
  description TEXT,
  is_active BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table: seasons
-- -----------------------------------------------------
CREATE TABLE seasons (
  id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(45),
  description TEXT,
  is_active BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table: rarities
-- -----------------------------------------------------
CREATE TABLE rarities (
  id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(45),
  description TEXT,
  multiplier DECIMAL(5,2) NOT NULL DEFAULT 1.00,
  is_active BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table: biomes
-- -----------------------------------------------------
CREATE TABLE biomes (
  id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(45),
  description TEXT,
  is_active BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table: users
-- -----------------------------------------------------
CREATE TABLE users (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  email VARCHAR(255) UNIQUE,
  login VARCHAR(50) UNIQUE NOT NULL,
  password CHAR(60) NOT NULL COMMENT 'bcrypt hash',
  role ENUM('user', 'moderator', 'admin') DEFAULT 'user' NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  is_active BOOLEAN DEFAULT TRUE,
  money_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  last_login_at TIMESTAMP NULL,
  INDEX idx_users_email (email),
  INDEX idx_users_login (login),
  INDEX idx_users_active_role (is_active, role),
  INDEX idx_users_last_login (last_login_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Table des utilisateurs du jeu';

-- -----------------------------------------------------
-- Table: professions
-- -----------------------------------------------------
CREATE TABLE professions (
  id SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  is_active BOOLEAN DEFAULT TRUE,
  is_primary BOOLEAN DEFAULT FALSE,
  image VARCHAR(512),
  profession_type ENUM('gathering', 'crafting', 'trading') NOT NULL,
  INDEX idx_professions_type_active (profession_type, is_active),
  INDEX idx_professions_primary (is_primary)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Métiers disponibles dans le jeu';

-- -----------------------------------------------------
-- Table: professions_weathers
-- -----------------------------------------------------
CREATE TABLE professions_weathers (
  profession_id SMALLINT UNSIGNED NOT NULL,
  weather_id TINYINT UNSIGNED NOT NULL,
  efficiency_multiplier DECIMAL(4,2) DEFAULT 1.00,
  PRIMARY KEY (profession_id, weather_id),
  FOREIGN KEY (profession_id) REFERENCES professions(id) ON DELETE CASCADE,
  FOREIGN KEY (weather_id) REFERENCES weathers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table: subclasses
-- -----------------------------------------------------
CREATE TABLE subclasses (
  parent_id SMALLINT UNSIGNED NOT NULL,
  child_id SMALLINT UNSIGNED NOT NULL,
  PRIMARY KEY (parent_id, child_id),
  FOREIGN KEY (parent_id) REFERENCES professions(id) ON DELETE CASCADE,
  FOREIGN KEY (child_id) REFERENCES professions(id) ON DELETE CASCADE,
  CHECK (parent_id != child_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table: mastery_rank
-- -----------------------------------------------------
CREATE TABLE mastery_rank (
  id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  level_minimum TINYINT UNSIGNED NOT NULL,
  CONSTRAINT chk_level_minimum CHECK (level_minimum >= 1 AND level_minimum <= 100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table: users_subclasses
-- -----------------------------------------------------
CREATE TABLE users_subclasses (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  user_id INT UNSIGNED NOT NULL,
  profession_id SMALLINT UNSIGNED NOT NULL,
  experience INT UNSIGNED DEFAULT 0,
  level TINYINT UNSIGNED DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY unique_user_profession (user_id, profession_id),
  INDEX idx_users_subclasses_level (level),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (profession_id) REFERENCES professions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table: users_professions
-- -----------------------------------------------------
CREATE TABLE users_professions (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  user_id INT UNSIGNED NOT NULL,
  profession_id SMALLINT UNSIGNED NOT NULL,
  mastery_rank_id TINYINT UNSIGNED NOT NULL,
  experience INT UNSIGNED DEFAULT 0,
  level TINYINT UNSIGNED DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY unique_user_profession (user_id, profession_id),
  INDEX idx_users_professions_user (user_id),
  INDEX idx_users_professions_level (level),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (profession_id) REFERENCES professions(id) ON DELETE CASCADE,
  FOREIGN KEY (mastery_rank_id) REFERENCES mastery_rank(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table: resources_types
-- -----------------------------------------------------
CREATE TABLE resources_types (
  id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(45) NOT NULL,
  description TEXT,
  is_active BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table: resources
-- -----------------------------------------------------
CREATE TABLE resources (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  resource_type_id TINYINT UNSIGNED NOT NULL,
  rarity_id TINYINT UNSIGNED NOT NULL,
  name VARCHAR(150) NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  is_active BOOLEAN DEFAULT TRUE,
  weight DECIMAL(5,2) NOT NULL DEFAULT 1.00,
  stack_size SMALLINT UNSIGNED NOT NULL DEFAULT 64 COMMENT 'Taille maximale de pile',
  is_lootable BOOLEAN DEFAULT FALSE,
  base_value DECIMAL(8,2) NOT NULL DEFAULT 0.00 COMMENT 'Valeur de base pour calculs de prix',
  INDEX idx_resources_active_lootable (is_active, is_lootable),
  INDEX idx_resources_type_rarity (resource_type_id, rarity_id),
  INDEX idx_resources_name (name),
  FOREIGN KEY (resource_type_id) REFERENCES resources_types(id),
  FOREIGN KEY (rarity_id) REFERENCES rarities(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Ressources craftables et lootables';

-- -----------------------------------------------------
-- Table: resources_professions
-- -----------------------------------------------------
CREATE TABLE resources_professions (
  resource_id INT UNSIGNED NOT NULL,
  profession_id SMALLINT UNSIGNED NOT NULL,
  PRIMARY KEY (resource_id, profession_id),
  INDEX idx_prof_resource (profession_id, resource_id),
  FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
  FOREIGN KEY (profession_id) REFERENCES professions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table: resources_biomes
-- -----------------------------------------------------
CREATE TABLE resources_biomes (
  resource_id INT UNSIGNED NOT NULL,
  biome_id TINYINT UNSIGNED NOT NULL,
  multiplier DECIMAL(5,2) NOT NULL DEFAULT 1.00,
  PRIMARY KEY (resource_id, biome_id),
  INDEX idx_biome_resource (biome_id, resource_id),
  FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
  FOREIGN KEY (biome_id) REFERENCES biomes(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table: resources_weathers
-- -----------------------------------------------------
CREATE TABLE resources_weathers (
  resource_id INT UNSIGNED NOT NULL,
  weather_id TINYINT UNSIGNED NOT NULL,
  multiplier DECIMAL(5,2) NOT NULL DEFAULT 1.00,
  PRIMARY KEY (resource_id, weather_id),
  INDEX idx_weather_resource (weather_id, resource_id),
  FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
  FOREIGN KEY (weather_id) REFERENCES weathers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table: resources_seasons
-- -----------------------------------------------------
CREATE TABLE resources_seasons (
  resource_id INT UNSIGNED NOT NULL,
  season_id TINYINT UNSIGNED NOT NULL,
  multiplier DECIMAL(5,2) NOT NULL DEFAULT 1.00,
  PRIMARY KEY (resource_id, season_id),
  INDEX idx_season_resource (season_id, resource_id),
  FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
  FOREIGN KEY (season_id) REFERENCES seasons(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table: inventory
-- -----------------------------------------------------
CREATE TABLE inventory (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  user_id INT UNSIGNED NOT NULL,
  resource_id INT UNSIGNED NOT NULL,
  quantity INT UNSIGNED NOT NULL DEFAULT 0,
  last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY unique_user_resource (user_id, resource_id),
  INDEX idx_inventory_user (user_id),
  INDEX idx_inventory_resource (resource_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Inventaire des joueurs';

-- -----------------------------------------------------
-- Table: recipes
-- -----------------------------------------------------
CREATE TABLE recipes (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  resource_id INT UNSIGNED NOT NULL,
  profession_id SMALLINT UNSIGNED NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  is_active BOOLEAN DEFAULT TRUE,
  required_level TINYINT UNSIGNED DEFAULT 1,
  crafting_time SMALLINT UNSIGNED DEFAULT 0 COMMENT 'Temps en secondes',
  INDEX idx_recipes_profession_level (profession_id, required_level, is_active),
  FOREIGN KEY (resource_id) REFERENCES resources(id),
  FOREIGN KEY (profession_id) REFERENCES professions(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Recettes de crafting';

-- -----------------------------------------------------
-- Table: recipes_resources
-- -----------------------------------------------------
CREATE TABLE recipes_resources (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  recipe_id INT UNSIGNED NOT NULL,
  resource_id INT UNSIGNED NOT NULL,
  resource_quantity DECIMAL(5,2) NOT NULL DEFAULT 1.00,
  xp_gained SMALLINT UNSIGNED DEFAULT 0,
  FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
  FOREIGN KEY (resource_id) REFERENCES resources(id),
  INDEX idx_recipe_resources (recipe_id, resource_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table: market_status
-- -----------------------------------------------------
CREATE TABLE market_status (
  id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL UNIQUE,
  description TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Statuts possibles des offres de marché';

-- Initial market status values
INSERT INTO market_status (name, description) VALUES
('active', 'Offre active en attente d\'achat'),
('sold', 'Ressource vendue avec succès'),
('cancelled', 'Offre annulée par le vendeur'),
('expired', 'Offre expirée (optionnel)'),
('reserved', 'Ressource réservée en cours de transaction');

-- -----------------------------------------------------
-- Table: markets
-- -----------------------------------------------------
CREATE TABLE markets (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  resource_id INT UNSIGNED NOT NULL,
  seller_id INT UNSIGNED NOT NULL,
  buyer_id INT UNSIGNED,
  status_id TINYINT UNSIGNED NOT NULL DEFAULT 1,
  price_unit DECIMAL(10,2) NOT NULL DEFAULT 1.00,
  quantity INT UNSIGNED NOT NULL,
  sold_at TIMESTAMP NULL,
  bought_at TIMESTAMP NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP NULL COMMENT 'Date d\'expiration de l\'offre',
  INDEX idx_markets_status_created (status_id, created_at),
  INDEX idx_markets_seller_status (seller_id, status_id),
  INDEX idx_markets_resource_status (resource_id, status_id),
  INDEX idx_markets_expires (expires_at),
  FOREIGN KEY (resource_id) REFERENCES resources(id),
  FOREIGN KEY (seller_id) REFERENCES users(id),
  FOREIGN KEY (buyer_id) REFERENCES users(id),
  FOREIGN KEY (status_id) REFERENCES market_status(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Place de marché pour échanges joueur-à-joueur';

-- -----------------------------------------------------
-- Table: workshops
-- -----------------------------------------------------
CREATE TABLE workshops (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  resource_id INT UNSIGNED NOT NULL,
  profession_id SMALLINT UNSIGNED NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  is_active BOOLEAN DEFAULT TRUE,
  usage_number INT UNSIGNED DEFAULT 0,
  max_durability SMALLINT UNSIGNED NOT NULL DEFAULT 100,
  current_durability SMALLINT UNSIGNED NOT NULL DEFAULT 100 COMMENT 'Durabilité actuelle (0 = cassé)',
  repair_cost_multiplier DECIMAL(3,2) DEFAULT 1.50,
  INDEX idx_workshops_profession (profession_id, is_active),
  FOREIGN KEY (resource_id) REFERENCES resources(id),
  FOREIGN KEY (profession_id) REFERENCES professions(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Ateliers pour produire des ressources';

-- -----------------------------------------------------
-- Table: workshops_resources
-- -----------------------------------------------------
CREATE TABLE workshops_resources (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  workshop_id INT UNSIGNED NOT NULL,
  resource_id INT UNSIGNED NOT NULL,
  resource_quantity SMALLINT UNSIGNED NOT NULL DEFAULT 1,
  xp_gained SMALLINT UNSIGNED DEFAULT 0,
  FOREIGN KEY (workshop_id) REFERENCES workshops(id) ON DELETE CASCADE,
  FOREIGN KEY (resource_id) REFERENCES resources(id),
  INDEX idx_workshop_resources (workshop_id, resource_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table: workshops_biomes
-- -----------------------------------------------------
CREATE TABLE workshops_biomes (
  workshop_id INT UNSIGNED NOT NULL,
  biome_id TINYINT UNSIGNED NOT NULL,
  bonus_multiplier DECIMAL(4,2) DEFAULT 1.00,
  PRIMARY KEY (workshop_id, biome_id),
  INDEX idx_biome_workshop (biome_id, workshop_id),
  FOREIGN KEY (workshop_id) REFERENCES workshops(id) ON DELETE CASCADE,
  FOREIGN KEY (biome_id) REFERENCES biomes(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table: devices
-- -----------------------------------------------------
CREATE TABLE devices (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255),
  user_agent TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table: refresh_tokens
-- -----------------------------------------------------
CREATE TABLE refresh_tokens (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  user_id INT UNSIGNED NOT NULL,
  device_id INT UNSIGNED NOT NULL,
  token_hash CHAR(64) NOT NULL COMMENT 'SHA-256 hash',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP NOT NULL,
  last_used_at TIMESTAMP NULL,
  UNIQUE KEY unique_user_device (user_id, device_id),
  INDEX idx_refresh_tokens_user (user_id),
  INDEX idx_refresh_tokens_expires (expires_at),
  INDEX idx_refresh_tokens_hash (token_hash),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table: settings
-- -----------------------------------------------------
CREATE TABLE settings (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  user_id INT UNSIGNED NOT NULL,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  value TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY unique_user_setting (user_id, name),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table: audit_log (for logging)
-- -----------------------------------------------------
CREATE TABLE audit_log (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  table_name VARCHAR(100) NOT NULL,
  operation ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
  record_id INT UNSIGNED,
  user_id INT UNSIGNED,
  old_data JSON,
  new_data JSON,
  changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  changed_by VARCHAR(100),
  INDEX idx_audit_log_table (table_name, changed_at),
  INDEX idx_audit_log_user (user_id),
  INDEX idx_audit_log_record (table_name, record_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Log d\'audit pour toutes les opérations critiques';

-- -----------------------------------------------------
-- Table: user_statistics
-- -----------------------------------------------------
CREATE TABLE user_statistics (
  user_id INT UNSIGNED PRIMARY KEY,
  total_crafts INT UNSIGNED DEFAULT 0,
  total_sales INT UNSIGNED DEFAULT 0,
  total_purchases INT UNSIGNED DEFAULT 0,
  total_money_earned DECIMAL(12,2) DEFAULT 0.00,
  total_money_spent DECIMAL(12,2) DEFAULT 0.00,
  last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Statistiques des utilisateurs';

-- =============================================================================
-- TRIGGERS - MySQL Implementation
-- =============================================================================

DELIMITER $$

-- -----------------------------------------------------
-- 1. INVENTORY TRIGGERS
-- -----------------------------------------------------

-- Trigger: Check inventory quantity
CREATE TRIGGER trg_check_inventory_quantity
BEFORE INSERT ON inventory
FOR EACH ROW
BEGIN
  DECLARE v_stack_size SMALLINT UNSIGNED;
  
  -- Prevent negative quantities
  IF NEW.quantity < 0 THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Inventory quantity cannot be negative';
  END IF;
  
  -- Check stack size limit
  SELECT stack_size INTO v_stack_size
  FROM resources
  WHERE id = NEW.resource_id;
  
  IF NEW.quantity > v_stack_size THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Quantity exceeds stack size limit';
  END IF;
END$$

CREATE TRIGGER trg_update_inventory_quantity
BEFORE UPDATE ON inventory
FOR EACH ROW
BEGIN
  DECLARE v_stack_size SMALLINT UNSIGNED;
  
  IF NEW.quantity < 0 THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Inventory quantity cannot be negative';
  END IF;
  
  SELECT stack_size INTO v_stack_size
  FROM resources
  WHERE id = NEW.resource_id;
  
  IF NEW.quantity > v_stack_size THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Quantity exceeds stack size limit';
  END IF;
END$$

-- -----------------------------------------------------
-- 2. MARKET TRIGGERS
-- -----------------------------------------------------

-- Trigger: Transfer items to market on listing
CREATE TRIGGER trg_transfer_to_market
BEFORE INSERT ON markets
FOR EACH ROW
BEGIN
  DECLARE v_current_quantity INT UNSIGNED;
  DECLARE v_active_status TINYINT UNSIGNED;
  
  SELECT id INTO v_active_status FROM market_status WHERE name = 'active';
  
  IF NEW.status_id = v_active_status THEN
    -- Check seller inventory
    SELECT quantity INTO v_current_quantity
    FROM inventory
    WHERE user_id = NEW.seller_id AND resource_id = NEW.resource_id;
    
    IF v_current_quantity IS NULL OR v_current_quantity < NEW.quantity THEN
      SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Insufficient resources in inventory';
    END IF;
    
    -- Deduct from seller inventory
    UPDATE inventory
    SET quantity = quantity - NEW.quantity
    WHERE user_id = NEW.seller_id AND resource_id = NEW.resource_id;
  END IF;
END$$

-- Trigger: Complete market transaction
CREATE TRIGGER trg_complete_market_transaction
BEFORE UPDATE ON markets
FOR EACH ROW
BEGIN
  DECLARE v_total_price DECIMAL(12,2);
  DECLARE v_buyer_money DECIMAL(12,2);
  DECLARE v_sold_status TINYINT UNSIGNED;
  DECLARE v_active_status TINYINT UNSIGNED;
  DECLARE v_cancelled_status TINYINT UNSIGNED;
  
  SELECT id INTO v_sold_status FROM market_status WHERE name = 'sold';
  SELECT id INTO v_active_status FROM market_status WHERE name = 'active';
  SELECT id INTO v_cancelled_status FROM market_status WHERE name = 'cancelled';
  
  -- Handle sale completion
  IF NEW.status_id = v_sold_status AND OLD.status_id = v_active_status THEN
    SET v_total_price = NEW.price_unit * NEW.quantity;
    
    -- Check buyer funds
    SELECT money_amount INTO v_buyer_money
    FROM users WHERE id = NEW.buyer_id;
    
    IF v_buyer_money < v_total_price THEN
      SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Insufficient funds';
    END IF;
    
    -- Transfer money
    UPDATE users SET money_amount = money_amount - v_total_price
    WHERE id = NEW.buyer_id;
    
    UPDATE users SET money_amount = money_amount + v_total_price
    WHERE id = NEW.seller_id;
    
    -- Add items to buyer inventory
    INSERT INTO inventory (user_id, resource_id, quantity)
    VALUES (NEW.buyer_id, NEW.resource_id, NEW.quantity)
    ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity);
    
    -- Set timestamps
    SET NEW.sold_at = CURRENT_TIMESTAMP;
    SET NEW.bought_at = CURRENT_TIMESTAMP;
    
  -- Handle cancellation
  ELSIF NEW.status_id = v_cancelled_status AND OLD.status_id = v_active_status THEN
    -- Return items to seller
    INSERT INTO inventory (user_id, resource_id, quantity)
    VALUES (NEW.seller_id, NEW.resource_id, NEW.quantity)
    ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity);
  END IF;
END$$

-- Trigger: Prevent self-trading
CREATE TRIGGER trg_prevent_self_trading
BEFORE INSERT ON markets
FOR EACH ROW
BEGIN
  IF NEW.buyer_id IS NOT NULL AND NEW.buyer_id = NEW.seller_id THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Users cannot buy from themselves';
  END IF;
END$$

CREATE TRIGGER trg_prevent_self_trading_update
BEFORE UPDATE ON markets
FOR EACH ROW
BEGIN
  IF NEW.buyer_id IS NOT NULL AND NEW.buyer_id = NEW.seller_id THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Users cannot buy from themselves';
  END IF;
END$$

-- -----------------------------------------------------
-- 3. EXPERIENCE & LEVELING TRIGGERS
-- -----------------------------------------------------

-- Trigger: Auto-level up for professions
CREATE TRIGGER trg_auto_level_up_professions
BEFORE UPDATE ON users_professions
FOR EACH ROW
BEGIN
  DECLARE v_xp_needed INT UNSIGNED;
  
  IF NEW.experience > OLD.experience THEN
    SET v_xp_needed = NEW.level * 1000;
    
    WHILE NEW.experience >= v_xp_needed AND NEW.level < 255 DO
      SET NEW.level = NEW.level + 1;
      SET NEW.experience = NEW.experience - v_xp_needed;
      SET v_xp_needed = NEW.level * 1000;
    END WHILE;
  END IF;
END$$

-- Trigger: Update mastery rank
CREATE TRIGGER trg_update_mastery_rank
BEFORE UPDATE ON users_professions
FOR EACH ROW
BEGIN
  DECLARE v_new_rank_id TINYINT UNSIGNED;
  
  IF NEW.level > OLD.level THEN
    SELECT id INTO v_new_rank_id
    FROM mastery_rank
    WHERE level_minimum <= NEW.level
    ORDER BY level_minimum DESC
    LIMIT 1;
    
    IF v_new_rank_id IS NOT NULL THEN
      SET NEW.mastery_rank_id = v_new_rank_id;
    END IF;
  END IF;
END$$

-- Trigger: Auto-level up for subclasses
CREATE TRIGGER trg_auto_level_up_subclasses
BEFORE UPDATE ON users_subclasses
FOR EACH ROW
BEGIN
  DECLARE v_xp_needed INT UNSIGNED;
  
  IF NEW.experience > OLD.experience THEN
    SET v_xp_needed = NEW.level * 1000;
    
    WHILE NEW.experience >= v_xp_needed AND NEW.level < 255 DO
      SET NEW.level = NEW.level + 1;
      SET NEW.experience = NEW.experience - v_xp_needed;
      SET v_xp_needed = NEW.level * 1000;
    END WHILE;
  END IF;
END$$

-- -----------------------------------------------------
-- 4. WORKSHOP TRIGGERS
-- -----------------------------------------------------

-- Trigger: Workshop durability decrease
CREATE TRIGGER trg_workshop_usage
AFTER INSERT ON recipes_resources
FOR EACH ROW
BEGIN
  DECLARE v_workshop_id INT UNSIGNED;
  
  SELECT w.id INTO v_workshop_id
  FROM recipes r
  JOIN workshops w ON w.profession_id = r.profession_id
  WHERE r.id = NEW.recipe_id
  LIMIT 1;
  
  IF v_workshop_id IS NOT NULL THEN
    UPDATE workshops
    SET current_durability = GREATEST(0, current_durability - 1),
        repair_cost_multiplier = repair_cost_multiplier + 0.01,
        usage_number = usage_number + 1
    WHERE id = v_workshop_id;
  END IF;
END$$

-- -----------------------------------------------------
-- 5. PROFESSION LIMIT TRIGGER
-- -----------------------------------------------------

-- Trigger: Max 3 professions per user
CREATE TRIGGER trg_check_max_professions
BEFORE INSERT ON users_professions
FOR EACH ROW
BEGIN
  DECLARE profession_count INT;
  
  SELECT COUNT(*) INTO profession_count
  FROM users_professions
  WHERE user_id = NEW.user_id;
  
  IF profession_count >= 3 THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'User cannot have more than 3 professions';
  END IF;
END$

-- -----------------------------------------------------
-- 6. SECURITY & VALIDATION TRIGGERS
-- -----------------------------------------------------

-- Trigger: Validate email format
CREATE TRIGGER trg_validate_email_insert
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
  IF NEW.email IS NOT NULL AND NEW.email NOT REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,} THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Invalid email format';
  END IF;
END$

CREATE TRIGGER trg_validate_email_update
BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
  IF NEW.email IS NOT NULL AND NEW.email NOT REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,} THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Invalid email format';
  END IF;
END$

-- -----------------------------------------------------
-- 7. STATISTICS TRIGGERS
-- -----------------------------------------------------

-- Trigger: Update market statistics on sale
CREATE TRIGGER trg_update_market_statistics
AFTER UPDATE ON markets
FOR EACH ROW
BEGIN
  DECLARE v_total_price DECIMAL(12,2);
  DECLARE v_sold_status TINYINT UNSIGNED;
  DECLARE v_active_status TINYINT UNSIGNED;
  
  SELECT id INTO v_sold_status FROM market_status WHERE name = 'sold';
  SELECT id INTO v_active_status FROM market_status WHERE name = 'active';
  
  IF NEW.status_id = v_sold_status AND OLD.status_id = v_active_status THEN
    SET v_total_price = NEW.price_unit * NEW.quantity;
    
    -- Update seller stats
    INSERT INTO user_statistics (user_id, total_sales, total_money_earned)
    VALUES (NEW.seller_id, 1, v_total_price)
    ON DUPLICATE KEY UPDATE 
      total_sales = total_sales + 1,
      total_money_earned = total_money_earned + v_total_price;
    
    -- Update buyer stats
    INSERT INTO user_statistics (user_id, total_purchases, total_money_spent)
    VALUES (NEW.buyer_id, 1, v_total_price)
    ON DUPLICATE KEY UPDATE 
      total_purchases = total_purchases + 1,
      total_money_spent = total_money_spent + v_total_price;
  END IF;
END$

-- Trigger: Track user activity on token creation
CREATE TRIGGER trg_track_user_activity
AFTER INSERT ON refresh_tokens
FOR EACH ROW
BEGIN
  UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = NEW.user_id;
END$

-- -----------------------------------------------------
-- 8. AUDIT TRIGGERS
-- -----------------------------------------------------

-- Trigger: Audit users changes
CREATE TRIGGER trg_audit_users_insert
AFTER INSERT ON users
FOR EACH ROW
BEGIN
  INSERT INTO audit_log (table_name, operation, record_id, new_data)
  VALUES ('users', 'INSERT', NEW.id, JSON_OBJECT(
    'id', NEW.id,
    'login', NEW.login,
    'email', NEW.email,
    'role', NEW.role
  ));
END$

CREATE TRIGGER trg_audit_users_update
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
  INSERT INTO audit_log (table_name, operation, record_id, old_data, new_data)
  VALUES ('users', 'UPDATE', NEW.id, 
    JSON_OBJECT('money_amount', OLD.money_amount, 'role', OLD.role),
    JSON_OBJECT('money_amount', NEW.money_amount, 'role', NEW.role)
  );
END$

CREATE TRIGGER trg_audit_users_delete
AFTER DELETE ON users
FOR EACH ROW
BEGIN
  INSERT INTO audit_log (table_name, operation, record_id, old_data)
  VALUES ('users', 'DELETE', OLD.id, JSON_OBJECT(
    'id', OLD.id,
    'login', OLD.login,
    'email', OLD.email
  ));
END$

-- Trigger: Audit market transactions
CREATE TRIGGER trg_audit_markets_insert
AFTER INSERT ON markets
FOR EACH ROW
BEGIN
  INSERT INTO audit_log (table_name, operation, record_id, user_id, new_data)
  VALUES ('markets', 'INSERT', NEW.id, NEW.seller_id, JSON_OBJECT(
    'resource_id', NEW.resource_id,
    'price_unit', NEW.price_unit,
    'quantity', NEW.quantity,
    'status_id', NEW.status_id
  ));
END$

CREATE TRIGGER trg_audit_markets_update
AFTER UPDATE ON markets
FOR EACH ROW
BEGIN
  INSERT INTO audit_log (table_name, operation, record_id, user_id, old_data, new_data)
  VALUES ('markets', 'UPDATE', NEW.id, NEW.seller_id,
    JSON_OBJECT('status_id', OLD.status_id, 'buyer_id', OLD.buyer_id),
    JSON_OBJECT('status_id', NEW.status_id, 'buyer_id', NEW.buyer_id)
  );
END$

-- Trigger: Audit inventory changes
CREATE TRIGGER trg_audit_inventory_update
AFTER UPDATE ON inventory
FOR EACH ROW
BEGIN
  IF OLD.quantity != NEW.quantity THEN
    INSERT INTO audit_log (table_name, operation, record_id, user_id, old_data, new_data)
    VALUES ('inventory', 'UPDATE', NEW.id, NEW.user_id,
      JSON_OBJECT('quantity', OLD.quantity),
      JSON_OBJECT('quantity', NEW.quantity)
    );
  END IF;
END$

DELIMITER ;

-- -----------------------------------------------------
-- INITIAL DATA
-- -----------------------------------------------------

-- Rarities
INSERT INTO rarities (name, description, multiplier, is_active) VALUES
('Commun', 'Ressource commune, facile à trouver', 1.0, TRUE),
('Peu commun', 'Ressource moins fréquente', 1.5, TRUE),
('Rare', 'Ressource difficile à obtenir', 2.5, TRUE),
('Épique', 'Ressource très rare', 5.0, TRUE),
('Légendaire', 'Ressource exceptionnelle', 10.0, TRUE);

-- Weathers
INSERT INTO weathers (name, description, is_active) VALUES
('Ensoleillé', 'Temps clair, bonus pour agriculture', TRUE),
('Pluvieux', 'Pluie, bonus pêche/herboristerie', TRUE),
('Orageux', 'Orages, malus métallurgie', TRUE),
('Neigeux', 'Neige, accès biomes alpins', TRUE),
('Venteux', 'Vent fort, bonus moulins', TRUE);

-- Seasons
INSERT INTO seasons (name, description, is_active) VALUES
('Printemps', 'Croissance rapide, bonus agriculture', TRUE),
('Été', 'Ressources abondantes', TRUE),
('Automne', 'Récoltes, bonus conservation', TRUE),
('Hiver', 'Ressources rares, bonus forge', TRUE);

-- Biomes
INSERT INTO biomes (name, description, is_active) VALUES
('Forêt tempérée', 'Bois, plantes médicinales', TRUE),
('Montagne', 'Minerais, pierre', TRUE),
('Plaine', 'Agriculture, céréales', TRUE),
('Rivière', 'Pêche, argile', TRUE),
('Marais', 'Plantes rares, tourbe', TRUE),
('Côte', 'Sel marin, coquillages', TRUE);

-- Mastery Ranks
INSERT INTO mastery_rank (name, level_minimum) VALUES
('Débutant', 1),
('Compagnon', 10),
('Artisan', 25),
('Expert', 50),
('Maître', 75);

-- Resource Types
INSERT INTO resources_types (name, description, is_active) VALUES
('Minerai', 'Ressources minérales brutes', TRUE),
('Bois', 'Ressources forestières', TRUE),
('Plante', 'Ressources végétales', TRUE),
('Animal', 'Ressources d\'origine animale', TRUE),
('Alimentaire', 'Ressources comestibles', TRUE),
('Outil', 'Équipements et outils', TRUE),
('Matériau', 'Matériaux transformés', TRUE);

-- -----------------------------------------------------
-- VIEWS
-- -----------------------------------------------------

-- View: Active resources with full details
CREATE VIEW v_resources_details AS
SELECT 
  r.id,
  r.name,
  r.description,
  rt.name AS resource_type,
  ra.name AS rarity,
  ra.multiplier AS rarity_multiplier,
  r.weight,
  r.stack_size,
  r.is_lootable,
  r.base_value,
  r.is_active
FROM resources r
JOIN resources_types rt ON r.resource_type_id = rt.id
JOIN rarities ra ON r.rarity_id = ra.id
WHERE r.is_active = TRUE;

-- View: User progression summary
CREATE VIEW v_user_progression AS
SELECT 
  u.id AS user_id,
  u.login,
  u.money_amount,
  u.role,
  COUNT(DISTINCT up.profession_id) AS total_professions,
  SUM(up.level) AS total_levels,
  AVG(up.level) AS avg_level,
  MAX(up.level) AS max_level
FROM users u
LEFT JOIN users_professions up ON u.id = up.user_id
WHERE u.is_active = TRUE
GROUP BY u.id, u.login, u.money_amount, u.role;

-- View: Market active listings
CREATE VIEW v_market_active_listings AS
SELECT 
  m.id,
  r.name AS resource_name,
  rt.name AS resource_type,
  ra.name AS rarity,
  u.login AS seller_login,
  m.price_unit,
  m.quantity,
  (m.price_unit * m.quantity) AS total_price,
  ms.name AS status,
  m.created_at,
  m.expires_at
FROM markets m
JOIN resources r ON m.resource_id = r.id
JOIN resources_types rt ON r.resource_type_id = rt.id
JOIN rarities ra ON r.rarity_id = ra.id
JOIN users u ON m.seller_id = u.id
JOIN market_status ms ON m.status_id = ms.id
WHERE ms.name = 'active'
ORDER BY m.created_at DESC;

-- View: Workshop status
CREATE VIEW v_workshops_status AS
SELECT
  w.id,
  r.name AS produces_resource,
  p.name AS profession_name,
  w.current_durability,
  w.max_durability,
  ROUND((w.current_durability / w.max_durability * 100), 2) AS durability_percent,
  w.usage_number,
  w.repair_cost_multiplier,
  w.is_active
FROM workshops w
JOIN resources r ON w.resource_id = r.id
JOIN professions p ON w.profession_id = p.id;

-- -----------------------------------------------------
-- STORED PROCEDURES
-- -----------------------------------------------------

DELIMITER $

-- Procedure: Complete a craft
CREATE PROCEDURE sp_complete_craft(
  IN p_user_id INT UNSIGNED,
  IN p_recipe_id INT UNSIGNED
)
BEGIN
  DECLARE v_profession_id SMALLINT UNSIGNED;
  DECLARE v_required_level TINYINT UNSIGNED;
  DECLARE v_user_level TINYINT UNSIGNED;
  DECLARE v_crafted_resource_id INT UNSIGNED;
  DECLARE v_xp_total SMALLINT UNSIGNED DEFAULT 0;
  DECLARE done INT DEFAULT FALSE;
  DECLARE v_resource_id INT UNSIGNED;
  DECLARE v_quantity DECIMAL(5,2);
  DECLARE v_xp SMALLINT UNSIGNED;
  
  DECLARE cur_ingredients CURSOR FOR
    SELECT resource_id, resource_quantity, xp_gained
    FROM recipes_resources
    WHERE recipe_id = p_recipe_id;
  
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
  
  -- Get recipe details
  SELECT r.profession_id, r.required_level, r.resource_id
  INTO v_profession_id, v_required_level, v_crafted_resource_id
  FROM recipes r
  WHERE r.id = p_recipe_id AND r.is_active = TRUE;
  
  IF v_profession_id IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Recipe not found or inactive';
  END IF;
  
  -- Check user profession level
  SELECT level INTO v_user_level
  FROM users_professions
  WHERE user_id = p_user_id AND profession_id = v_profession_id;
  
  IF v_user_level IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'User does not have required profession';
  END IF;
  
  IF v_user_level < v_required_level THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'User level too low for this recipe';
  END IF;
  
  -- Process ingredients
  OPEN cur_ingredients;
  
  read_loop: LOOP
    FETCH cur_ingredients INTO v_resource_id, v_quantity, v_xp;
    IF done THEN
      LEAVE read_loop;
    END IF;
    
    -- Consume resources
    UPDATE inventory
    SET quantity = quantity - CAST(v_quantity AS UNSIGNED)
    WHERE user_id = p_user_id AND resource_id = v_resource_id;
    
    IF ROW_COUNT() = 0 THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient resources';
    END IF;
    
    SET v_xp_total = v_xp_total + v_xp;
  END LOOP;
  
  CLOSE cur_ingredients;
  
  -- Add crafted item
  INSERT INTO inventory (user_id, resource_id, quantity)
  VALUES (p_user_id, v_crafted_resource_id, 1)
  ON DUPLICATE KEY UPDATE quantity = quantity + 1;
  
  -- Add XP
  UPDATE users_professions
  SET experience = experience + v_xp_total
  WHERE user_id = p_user_id AND profession_id = v_profession_id;
  
  -- Update stats
  INSERT INTO user_statistics (user_id, total_crafts)
  VALUES (p_user_id, 1)
  ON DUPLICATE KEY UPDATE total_crafts = total_crafts + 1;
  
  SELECT 'Craft completed successfully' AS message, v_xp_total AS xp_gained;
END$

-- Procedure: List user inventory
CREATE PROCEDURE sp_get_user_inventory(
  IN p_user_id INT UNSIGNED
)
BEGIN
  SELECT 
    i.id,
    r.name AS resource_name,
    rt.name AS resource_type,
    ra.name AS rarity,
    i.quantity,
    r.stack_size,
    r.weight,
    (i.quantity * r.weight) AS total_weight,
    r.base_value,
    (i.quantity * r.base_value) AS total_value
  FROM inventory i
  JOIN resources r ON i.resource_id = r.id
  JOIN resources_types rt ON r.resource_type_id = rt.id
  JOIN rarities ra ON r.rarity_id = ra.id
  WHERE i.user_id = p_user_id
  ORDER BY rt.name, r.name;
END$

-- Procedure: Get user statistics
CREATE PROCEDURE sp_get_user_stats(
  IN p_user_id INT UNSIGNED
)
BEGIN
  SELECT 
    u.login,
    u.role,
    u.money_amount,
    u.created_at,
    u.last_login_at,
    COALESCE(s.total_crafts, 0) AS total_crafts,
    COALESCE(s.total_sales, 0) AS total_sales,
    COALESCE(s.total_purchases, 0) AS total_purchases,
    COALESCE(s.total_money_earned, 0) AS total_money_earned,
    COALESCE(s.total_money_spent, 0) AS total_money_spent,
    COUNT(DISTINCT up.profession_id) AS total_professions,
    SUM(up.level) AS total_levels
  FROM users u
  LEFT JOIN user_statistics s ON u.id = s.user_id
  LEFT JOIN users_professions up ON u.id = up.user_id
  WHERE u.id = p_user_id
  GROUP BY u.id, u.login, u.role, u.money_amount, u.created_at, u.last_login_at,
           s.total_crafts, s.total_sales, s.total_purchases, 
           s.total_money_earned, s.total_money_spent;
END$

DELIMITER ;

-- -----------------------------------------------------
-- END OF SCRIPT
-- -----------------------------------------------------
-- Total Tables: 29 (including audit_log and user_statistics)
-- Total Indexes: 28
-- Total Triggers: 23
-- Total Views: 4
-- Total Procedures: 3
-- -----------------------------------------------------