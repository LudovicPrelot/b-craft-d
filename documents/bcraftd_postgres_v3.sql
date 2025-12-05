-- =====================================================
-- B-CraftD v3.0 - MySQL 8.0+ Schema
-- Conversion depuis PostgreSQL v3.0
-- Date: 4 décembre 2025
-- =====================================================

-- Désactivation des vérifications temporaires
SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION';

-- =====================================================
-- TYPES ENUM (Conversion en CHECK constraints ou ENUM natif)
-- =====================================================

-- Note: MySQL supporte ENUM natif, mais pour plus de flexibilité
-- on utilise VARCHAR avec CHECK constraints comme en PostgreSQL

-- =====================================================
-- SECTION 1: TABLES CORE (7 tables)
-- =====================================================

-- Table: users
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'player',
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    coins DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    experience INT NOT NULL DEFAULT 0,
    level INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    CONSTRAINT chk_users_role CHECK (role IN ('player', 'moderator', 'admin')),
    CONSTRAINT chk_users_coins CHECK (coins >= 0),
    CONSTRAINT chk_users_experience CHECK (experience >= 0),
    CONSTRAINT chk_users_level CHECK (level >= 1 AND level <= 100),
    INDEX idx_users_email (email),
    INDEX idx_users_login (login),
    INDEX idx_users_active_role (is_active, role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: professions
DROP TABLE IF EXISTS professions;
CREATE TABLE professions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    max_level INT NOT NULL DEFAULT 50,
    parent_id INT NULL,
    unlock_level INT NOT NULL DEFAULT 1,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_professions_type CHECK (type IN ('gathering', 'crafting', 'processing')),
    CONSTRAINT chk_professions_max_level CHECK (max_level > 0),
    CONSTRAINT chk_professions_unlock_level CHECK (unlock_level >= 1),
    FOREIGN KEY (parent_id) REFERENCES professions(id) ON DELETE SET NULL,
    INDEX idx_professions_type (type),
    INDEX idx_professions_parent (parent_id),
    INDEX idx_professions_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: resources
DROP TABLE IF EXISTS resources;
CREATE TABLE resources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    rarity_id INT NOT NULL,
    type_id INT NOT NULL,
    base_value DECIMAL(10,2) NOT NULL DEFAULT 1.00,
    stack_size INT NOT NULL DEFAULT 99,
    is_tradeable TINYINT(1) NOT NULL DEFAULT 1,
    is_craftable TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_resources_base_value CHECK (base_value >= 0),
    CONSTRAINT chk_resources_stack_size CHECK (stack_size > 0),
    INDEX idx_resources_rarity (rarity_id),
    INDEX idx_resources_type (type_id),
    INDEX idx_resources_tradeable (is_tradeable)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: recipes
DROP TABLE IF EXISTS recipes;
CREATE TABLE recipes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    resource_id INT NOT NULL,
    profession_id INT NOT NULL,
    required_level INT NOT NULL DEFAULT 1,
    base_experience INT NOT NULL DEFAULT 10,
    crafting_time INT NOT NULL DEFAULT 60,
    output_quantity INT NOT NULL DEFAULT 1,
    success_rate DECIMAL(5,2) NOT NULL DEFAULT 100.00,
    workshop_id INT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_recipes_required_level CHECK (required_level >= 1),
    CONSTRAINT chk_recipes_base_experience CHECK (base_experience >= 0),
    CONSTRAINT chk_recipes_crafting_time CHECK (crafting_time > 0),
    CONSTRAINT chk_recipes_output_quantity CHECK (output_quantity > 0),
    CONSTRAINT chk_recipes_success_rate CHECK (success_rate >= 0 AND success_rate <= 100),
    FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
    FOREIGN KEY (profession_id) REFERENCES professions(id) ON DELETE CASCADE,
    INDEX idx_recipes_profession (profession_id),
    INDEX idx_recipes_resource (resource_id),
    INDEX idx_recipes_workshop (workshop_id),
    INDEX idx_recipes_craftable (profession_id, required_level, is_active, resource_id, crafting_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: inventory
DROP TABLE IF EXISTS inventory;
CREATE TABLE inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    resource_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_inventory_quantity CHECK (quantity >= 0),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
    UNIQUE KEY uq_inventory_user_resource (user_id, resource_id),
    INDEX idx_inventory_user (user_id),
    INDEX idx_inventory_resource (resource_id),
    INDEX idx_inventory_nonzero (user_id, resource_id, quantity)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: refresh_tokens
DROP TABLE IF EXISTS refresh_tokens;
CREATE TABLE refresh_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(500) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_refresh_tokens_user (user_id),
    INDEX idx_refresh_tokens_valid (user_id, expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: settings
DROP TABLE IF EXISTS settings;
CREATE TABLE settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) NOT NULL UNIQUE,
    setting_value TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_settings_key (setting_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- SECTION 2: TABLES ENVIRONNEMENT (4 tables)
-- =====================================================

-- Table: rarities
DROP TABLE IF EXISTS rarities;
CREATE TABLE rarities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    color VARCHAR(7) NOT NULL DEFAULT '#FFFFFF',
    multiplier DECIMAL(5,2) NOT NULL DEFAULT 1.00,
    drop_chance DECIMAL(5,2) NOT NULL DEFAULT 100.00,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_rarities_multiplier CHECK (multiplier > 0),
    CONSTRAINT chk_rarities_drop_chance CHECK (drop_chance >= 0 AND drop_chance <= 100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: weathers
DROP TABLE IF EXISTS weathers;
CREATE TABLE weathers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    gathering_multiplier DECIMAL(5,2) NOT NULL DEFAULT 1.00,
    crafting_multiplier DECIMAL(5,2) NOT NULL DEFAULT 1.00,
    duration_minutes INT NOT NULL DEFAULT 60,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_weathers_gathering_multiplier CHECK (gathering_multiplier >= 0),
    CONSTRAINT chk_weathers_crafting_multiplier CHECK (crafting_multiplier >= 0),
    CONSTRAINT chk_weathers_duration CHECK (duration_minutes > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: seasons
DROP TABLE IF EXISTS seasons;
CREATE TABLE seasons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    gathering_multiplier DECIMAL(5,2) NOT NULL DEFAULT 1.00,
    crafting_multiplier DECIMAL(5,2) NOT NULL DEFAULT 1.00,
    start_month INT NOT NULL,
    end_month INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_seasons_gathering_multiplier CHECK (gathering_multiplier >= 0),
    CONSTRAINT chk_seasons_crafting_multiplier CHECK (crafting_multiplier >= 0),
    CONSTRAINT chk_seasons_start_month CHECK (start_month >= 1 AND start_month <= 12),
    CONSTRAINT chk_seasons_end_month CHECK (end_month >= 1 AND end_month <= 12)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: biomes
DROP TABLE IF EXISTS biomes;
CREATE TABLE biomes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    gathering_multiplier DECIMAL(5,2) NOT NULL DEFAULT 1.00,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_biomes_gathering_multiplier CHECK (gathering_multiplier >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- SECTION 3: TABLES PROFESSIONS (4 tables)
-- =====================================================

-- Table: subclasses
DROP TABLE IF EXISTS subclasses;
CREATE TABLE subclasses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    profession_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    unlock_level INT NOT NULL DEFAULT 25,
    bonus_type VARCHAR(50) NOT NULL,
    bonus_value DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_subclasses_unlock_level CHECK (unlock_level >= 1),
    CONSTRAINT chk_subclasses_bonus_value CHECK (bonus_value >= 0),
    FOREIGN KEY (profession_id) REFERENCES professions(id) ON DELETE CASCADE,
    INDEX idx_subclasses_profession (profession_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: mastery_rank
DROP TABLE IF EXISTS mastery_rank;
CREATE TABLE mastery_rank (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rank_name VARCHAR(50) NOT NULL UNIQUE,
    min_level INT NOT NULL,
    bonus_multiplier DECIMAL(5,2) NOT NULL DEFAULT 1.00,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_mastery_rank_min_level CHECK (min_level >= 1),
    CONSTRAINT chk_mastery_rank_bonus_multiplier CHECK (bonus_multiplier >= 1.00)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: users_professions
DROP TABLE IF EXISTS users_professions;
CREATE TABLE users_professions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    profession_id INT NOT NULL,
    level INT NOT NULL DEFAULT 1,
    experience INT NOT NULL DEFAULT 0,
    mastery_rank_id INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_users_professions_level CHECK (level >= 1),
    CONSTRAINT chk_users_professions_experience CHECK (experience >= 0),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (profession_id) REFERENCES professions(id) ON DELETE CASCADE,
    FOREIGN KEY (mastery_rank_id) REFERENCES mastery_rank(id) ON DELETE RESTRICT,
    UNIQUE KEY uq_users_professions (user_id, profession_id),
    INDEX idx_users_professions_user (user_id),
    INDEX idx_users_professions_profession (profession_id),
    INDEX idx_users_professions_mastery (mastery_rank_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: users_subclasses
DROP TABLE IF EXISTS users_subclasses;
CREATE TABLE users_subclasses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    subclass_id INT NOT NULL,
    unlocked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (subclass_id) REFERENCES subclasses(id) ON DELETE CASCADE,
    UNIQUE KEY uq_users_subclasses (user_id, subclass_id),
    INDEX idx_users_subclasses_user (user_id),
    INDEX idx_users_subclasses_subclass (subclass_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- SECTION 4: TABLES RESSOURCES (6 tables)
-- =====================================================

-- Table: resources_types
DROP TABLE IF EXISTS resources_types;
CREATE TABLE resources_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: resources_professions
DROP TABLE IF EXISTS resources_professions;
CREATE TABLE resources_professions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resource_id INT NOT NULL,
    profession_id INT NOT NULL,
    drop_rate DECIMAL(5,2) NOT NULL DEFAULT 100.00,
    CONSTRAINT chk_resources_professions_drop_rate CHECK (drop_rate >= 0 AND drop_rate <= 100),
    FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
    FOREIGN KEY (profession_id) REFERENCES professions(id) ON DELETE CASCADE,
    UNIQUE KEY uq_resources_professions (resource_id, profession_id),
    INDEX idx_resources_professions_resource (resource_id),
    INDEX idx_resources_professions_profession (profession_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: resources_biomes
DROP TABLE IF EXISTS resources_biomes;
CREATE TABLE resources_biomes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resource_id INT NOT NULL,
    biome_id INT NOT NULL,
    spawn_chance DECIMAL(5,2) NOT NULL DEFAULT 100.00,
    CONSTRAINT chk_resources_biomes_spawn_chance CHECK (spawn_chance >= 0 AND spawn_chance <= 100),
    FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
    FOREIGN KEY (biome_id) REFERENCES biomes(id) ON DELETE CASCADE,
    UNIQUE KEY uq_resources_biomes (resource_id, biome_id),
    INDEX idx_resources_biomes_resource (resource_id),
    INDEX idx_resources_biomes_biome (biome_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: resources_weathers
DROP TABLE IF EXISTS resources_weathers;
CREATE TABLE resources_weathers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resource_id INT NOT NULL,
    weather_id INT NOT NULL,
    drop_multiplier DECIMAL(5,2) NOT NULL DEFAULT 1.00,
    CONSTRAINT chk_resources_weathers_drop_multiplier CHECK (drop_multiplier >= 0),
    FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
    FOREIGN KEY (weather_id) REFERENCES weathers(id) ON DELETE CASCADE,
    UNIQUE KEY uq_resources_weathers (resource_id, weather_id),
    INDEX idx_resources_weathers_resource (resource_id),
    INDEX idx_resources_weathers_weather (weather_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: resources_seasons
DROP TABLE IF EXISTS resources_seasons;
CREATE TABLE resources_seasons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resource_id INT NOT NULL,
    season_id INT NOT NULL,
    availability_multiplier DECIMAL(5,2) NOT NULL DEFAULT 1.00,
    CONSTRAINT chk_resources_seasons_availability CHECK (availability_multiplier >= 0),
    FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
    FOREIGN KEY (season_id) REFERENCES seasons(id) ON DELETE CASCADE,
    UNIQUE KEY uq_resources_seasons (resource_id, season_id),
    INDEX idx_resources_seasons_resource (resource_id),
    INDEX idx_resources_seasons_season (season_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: recipes_resources
DROP TABLE IF EXISTS recipes_resources;
CREATE TABLE recipes_resources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipe_id INT NOT NULL,
    resource_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    CONSTRAINT chk_recipes_resources_quantity CHECK (quantity > 0),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
    INDEX idx_recipes_resources_recipe (recipe_id),
    INDEX idx_recipes_resources_resource (resource_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- SECTION 5: TABLES WORKSHOPS (3 tables)
-- =====================================================

-- Table: workshops
DROP TABLE IF EXISTS workshops;
CREATE TABLE workshops (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    profession_id INT NOT NULL,
    required_level INT NOT NULL DEFAULT 1,
    base_cost DECIMAL(10,2) NOT NULL DEFAULT 100.00,
    durability INT NOT NULL DEFAULT 100,
    max_durability INT NOT NULL DEFAULT 100,
    efficiency_bonus DECIMAL(5,2) NOT NULL DEFAULT 1.00,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_workshops_required_level CHECK (required_level >= 1),
    CONSTRAINT chk_workshops_base_cost CHECK (base_cost >= 0),
    CONSTRAINT chk_workshops_durability CHECK (durability >= 0 AND durability <= max_durability),
    CONSTRAINT chk_workshops_max_durability CHECK (max_durability > 0),
    CONSTRAINT chk_workshops_efficiency_bonus CHECK (efficiency_bonus >= 0),
    FOREIGN KEY (profession_id) REFERENCES professions(id) ON DELETE CASCADE,
    INDEX idx_workshops_profession (profession_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: workshops_resources
DROP TABLE IF EXISTS workshops_resources;
CREATE TABLE workshops_resources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    workshop_id INT NOT NULL,
    resource_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    CONSTRAINT chk_workshops_resources_quantity CHECK (quantity > 0),
    FOREIGN KEY (workshop_id) REFERENCES workshops(id) ON DELETE CASCADE,
    FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
    UNIQUE KEY uq_workshops_resources (workshop_id, resource_id),
    INDEX idx_workshops_resources_workshop (workshop_id),
    INDEX idx_workshops_resources_resource (resource_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: workshops_biomes
DROP TABLE IF EXISTS workshops_biomes;
CREATE TABLE workshops_biomes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    workshop_id INT NOT NULL,
    biome_id INT NOT NULL,
    FOREIGN KEY (workshop_id) REFERENCES workshops(id) ON DELETE CASCADE,
    FOREIGN KEY (biome_id) REFERENCES biomes(id) ON DELETE CASCADE,
    UNIQUE KEY uq_workshops_biomes (workshop_id, biome_id),
    INDEX idx_workshops_biomes_workshop (workshop_id),
    INDEX idx_workshops_biomes_biome (biome_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- SECTION 6: TABLES MARCHÉ (2 tables + partitioning)
-- =====================================================

-- Table: market_status
DROP TABLE IF EXISTS market_status;
CREATE TABLE market_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    status_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: markets (partitionnée par date)
-- Note: MySQL 8.0+ supporte le partitionnement natif
DROP TABLE IF EXISTS markets;
CREATE TABLE markets (
    id INT AUTO_INCREMENT,
    seller_id INT NOT NULL,
    buyer_id INT NULL,
    resource_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    status_id INT NOT NULL DEFAULT 1,
    expires_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    CONSTRAINT chk_markets_quantity CHECK (quantity > 0),
    CONSTRAINT chk_markets_unit_price CHECK (unit_price > 0),
    CONSTRAINT chk_markets_total_price CHECK (total_price > 0),
    FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
    FOREIGN KEY (status_id) REFERENCES market_status(id) ON DELETE RESTRICT,
    INDEX idx_markets_seller (seller_id),
    INDEX idx_markets_buyer (buyer_id),
    INDEX idx_markets_resource (resource_id),
    INDEX idx_markets_status (status_id),
    INDEX idx_markets_search (resource_id, status_id, created_at),
    INDEX idx_markets_expires (expires_at),
    PRIMARY KEY (id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
PARTITION BY RANGE (YEAR(created_at)) (
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION p2026 VALUES LESS THAN (2027),
    PARTITION pfuture VALUES LESS THAN MAXVALUE
);

-- =====================================================
-- SECTION 7: TABLES DEVICES (1 table)
-- =====================================================

-- Table: devices
DROP TABLE IF EXISTS devices;
CREATE TABLE devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    device_name VARCHAR(100) NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    last_used TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_devices_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- SECTION 8: TABLES STATISTIQUES (1 table)
-- =====================================================

-- Table: user_statistics
DROP TABLE IF EXISTS user_statistics;
CREATE TABLE user_statistics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    total_items_sold INT NOT NULL DEFAULT 0,
    total_items_bought INT NOT NULL DEFAULT 0,
    total_items_crafted INT NOT NULL DEFAULT 0,
    total_sales_value DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    total_purchases_value DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    total_resources_gathered INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_user_statistics_totals CHECK (
        total_items_sold >= 0 AND 
        total_items_bought >= 0 AND 
        total_items_crafted >= 0 AND
        total_sales_value >= 0 AND
        total_purchases_value >= 0 AND
        total_resources_gathered >= 0
    ),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_statistics_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- SECTION 9: DONNÉES INITIALES
-- =====================================================

-- Insertion des raretés (5)
INSERT INTO rarities (name, color, multiplier, drop_chance) VALUES
('Commun', '#CCCCCC', 1.0, 100.0),
('Rare', '#4A90E2', 2.0, 25.0),
('Épique', '#9B59B6', 4.0, 5.0),
('Légendaire', '#F39C12', 7.0, 1.0),
('Mythique', '#E74C3C', 10.0, 0.1);

-- Insertion des météos (5)
INSERT INTO weathers (name, description, gathering_multiplier, crafting_multiplier, duration_minutes) VALUES
('Ensoleillé', 'Temps clair et ensoleillé', 1.0, 1.0, 120),
('Pluvieux', 'Pluie légère', 0.8, 1.2, 90),
('Orageux', 'Orages violents', 0.5, 0.8, 60),
('Neigeux', 'Chute de neige', 0.7, 1.1, 100),
('Venteux', 'Vent fort', 1.2, 0.9, 80);

-- Insertion des saisons (4)
INSERT INTO seasons (name, description, gathering_multiplier, crafting_multiplier, start_month, end_month) VALUES
('Printemps', 'Saison de la renaissance', 1.2, 1.0, 3, 5),
('Été', 'Saison chaude et ensoleillée', 1.0, 1.0, 6, 8),
('Automne', 'Saison des récoltes', 1.1, 1.2, 9, 11),
('Hiver', 'Saison froide', 0.8, 1.3, 12, 2);

-- Insertion des biomes (6)
INSERT INTO biomes (name, description, gathering_multiplier) VALUES
('Forêt', 'Forêt dense et sombre', 1.2),
('Montagne', 'Montagnes rocheuses', 1.0),
('Plaine', 'Vastes plaines herbeuses', 1.1),
('Rivière', 'Cours d eau douce', 1.3),
('Marais', 'Zones marécageuses', 0.9),
('Côte', 'Littoral marin', 1.4);

-- Insertion des rangs de maîtrise (5)
INSERT INTO mastery_rank (rank_name, min_level, bonus_multiplier) VALUES
('Débutant', 1, 1.00),
('Apprenti', 15, 1.10),
('Compagnon', 30, 1.25),
('Expert', 50, 1.50),
('Maître', 75, 2.00);

-- Insertion des types de ressources (7)
INSERT INTO resources_types (name, description) VALUES
('Minerai', 'Ressources minérales'),
('Bois', 'Ressources forestières'),
('Plante', 'Ressources végétales'),
('Animal', 'Ressources animales'),
('Alimentaire', 'Ressources consommables'),
('Outil', 'Outils et équipements'),
('Matériau', 'Matériaux de construction');

-- Insertion des statuts de marché (5)
INSERT INTO market_status (status_name, description) VALUES
('active', 'Offre active sur le marché'),
('sold', 'Offre vendue'),
('cancelled', 'Offre annulée par le vendeur'),
('expired', 'Offre expirée'),
('reserved', 'Offre réservée (en attente de paiement)');

-- =====================================================
-- SECTION 10: TRIGGERS MySQL (Conversion depuis PostgreSQL)
-- =====================================================

DELIMITER //

-- Trigger: Vérifier le maximum de 3 professions par utilisateur
DROP TRIGGER IF EXISTS trg_check_max_professions//
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
        SET MESSAGE_TEXT = 'Un utilisateur ne peut pas avoir plus de 3 professions actives';
    END IF;
END//

-- Trigger: Usure automatique des ateliers
DROP TRIGGER IF EXISTS trg_workshop_usage//
CREATE TRIGGER trg_workshop_usage
BEFORE UPDATE ON workshops
FOR EACH ROW
BEGIN
    IF NEW.durability < OLD.durability THEN
        SET NEW.updated_at = CURRENT_TIMESTAMP;
    END IF;
END//

-- Trigger: Validation des quantités d'inventaire
DROP TRIGGER IF EXISTS trg_check_inventory_quantity//
CREATE TRIGGER trg_check_inventory_quantity
BEFORE INSERT ON inventory
FOR EACH ROW
BEGIN
    IF NEW.quantity < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La quantité en inventaire ne peut pas être négative';
    END IF;
END//

-- Trigger: Vérification de la limite de stack
DROP TRIGGER IF EXISTS trg_check_stack_limit//
CREATE TRIGGER trg_check_stack_limit
BEFORE INSERT ON inventory
FOR EACH ROW
BEGIN
    DECLARE max_stack INT;
    
    SELECT stack_size INTO max_stack
    FROM resources
    WHERE id = NEW.resource_id;
    
    IF NEW.quantity > max_stack THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La quantité dépasse la limite de stack pour cette ressource';
    END IF;
END//

-- Trigger: Transfert vers le marché (déduction inventaire)
DROP TRIGGER IF EXISTS trg_transfer_to_market//
CREATE TRIGGER trg_transfer_to_market
AFTER INSERT ON markets
FOR EACH ROW
BEGIN
    UPDATE inventory
    SET quantity = quantity - NEW.quantity
    WHERE user_id = NEW.seller_id 
      AND resource_id = NEW.resource_id;
    
    -- Supprimer les entrées avec quantité nulle
    DELETE FROM inventory
    WHERE user_id = NEW.seller_id 
      AND resource_id = NEW.resource_id 
      AND quantity <= 0;
END//

-- Trigger: Complétion d'une transaction de marché
DROP TRIGGER IF EXISTS trg_complete_market_transaction//
CREATE TRIGGER trg_complete_market_transaction
AFTER UPDATE ON markets
FOR EACH ROW
BEGIN
    -- Si le statut passe à "sold"
    IF NEW.status_id = 2 AND OLD.status_id != 2 AND NEW.buyer_id IS NOT NULL THEN
        -- Transférer l'argent au vendeur
        UPDATE users
        SET coins = coins + NEW.total_price
        WHERE id = NEW.seller_id;
        
        -- Débiter l'acheteur
        UPDATE users
        SET coins = coins - NEW.total_price
        WHERE id = NEW.buyer_id;
        
        -- Ajouter les items à l'inventaire de l'acheteur
        INSERT INTO inventory (user_id, resource_id, quantity)
        VALUES (NEW.buyer_id, NEW.resource_id, NEW.quantity)
        ON DUPLICATE KEY UPDATE 
            quantity = quantity + NEW.quantity;
        
        -- Mettre à jour les statistiques
        UPDATE user_statistics
        SET total_items_sold = total_items_sold + NEW.quantity,
            total_sales_value = total_sales_value + NEW.total_price
        WHERE user_id = NEW.seller_id;
        
        UPDATE user_statistics
        SET total_items_bought = total_items_bought + NEW.quantity,
            total_purchases_value = total_purchases_value + NEW.total_price
        WHERE user_id = NEW.buyer_id;
    END IF;
END//

-- Trigger: Auto-expiration des offres de marché
DROP TRIGGER IF EXISTS trg_auto_expire_listings//
CREATE TRIGGER trg_auto_expire_listings
BEFORE UPDATE ON markets
FOR EACH ROW
BEGIN
    IF NEW.expires_at IS NOT NULL 
       AND NEW.expires_at <= CURRENT_TIMESTAMP 
       AND OLD.status_id = 1 THEN
        SET NEW.status_id = 4; -- expired
        
        -- Retourner les items au vendeur
        INSERT INTO inventory (user_id, resource_id, quantity)
        VALUES (NEW.seller_id, NEW.resource_id, NEW.quantity)
        ON DUPLICATE KEY UPDATE 
            quantity = quantity + NEW.quantity;
    END IF;
END//

-- Trigger: Level up automatique
DROP TRIGGER IF EXISTS trg_auto_level_up//
CREATE TRIGGER trg_auto_level_up
BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
    DECLARE required_xp INT;
    
    IF NEW.experience >= OLD.experience THEN
        SET required_xp = NEW.level * 100;
        
        WHILE NEW.experience >= required_xp AND NEW.level < 100 DO
            SET NEW.level = NEW.level + 1;
            SET NEW.experience = NEW.experience - required_xp;
            SET required_xp = NEW.level * 100;
        END WHILE;
    END IF;
END//

-- Trigger: Mise à jour automatique du rang de maîtrise
DROP TRIGGER IF EXISTS trg_update_mastery_rank//
CREATE TRIGGER trg_update_mastery_rank
BEFORE UPDATE ON users_professions
FOR EACH ROW
BEGIN
    DECLARE new_rank_id INT;
    
    IF NEW.level >= OLD.level THEN
        SELECT id INTO new_rank_id
        FROM mastery_rank
        WHERE min_level <= NEW.level
        ORDER BY min_level DESC
        LIMIT 1;
        
        SET NEW.mastery_rank_id = new_rank_id;
    END IF;
END//

-- Trigger: Empêcher l'auto-trading
DROP TRIGGER IF EXISTS trg_prevent_self_trading//
CREATE TRIGGER trg_prevent_self_trading
BEFORE UPDATE ON markets
FOR EACH ROW
BEGIN
    IF NEW.buyer_id IS NOT NULL AND NEW.buyer_id = NEW.seller_id THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Un utilisateur ne peut pas acheter ses propres offres';
    END IF;
END//

-- Trigger: Validation du format email
DROP TRIGGER IF EXISTS trg_validate_email//
CREATE TRIGGER trg_validate_email
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
    IF NEW.email NOT REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Format d email invalide';
    END IF;
END//

DELIMITER ;

-- =====================================================
-- SECTION 11: VUES (4 vues standards)
-- =====================================================

-- Vue: Détails des ressources avec rareté et type
DROP VIEW IF EXISTS v_resources_details;
CREATE VIEW v_resources_details AS
SELECT 
    r.id,
    r.name,
    r.description,
    rt.name AS type_name,
    rar.name AS rarity_name,
    rar.color AS rarity_color,
    rar.multiplier AS rarity_multiplier,
    r.base_value,
    r.base_value * rar.multiplier AS adjusted_value,
    r.stack_size,
    r.is_tradeable,
    r.is_craftable,
    r.created_at
FROM resources r
JOIN resources_types rt ON r.type_id = rt.id
JOIN rarities rar ON r.rarity_id = rar.id;

-- Vue: Progression complète des utilisateurs
DROP VIEW IF EXISTS v_user_progression;
CREATE VIEW v_user_progression AS
SELECT 
    u.id AS user_id,
    u.login,
    u.level AS character_level,
    u.experience AS character_xp,
    u.coins,
    p.name AS profession_name,
    up.level AS profession_level,
    up.experience AS profession_xp,
    mr.rank_name AS mastery_rank,
    mr.bonus_multiplier,
    us.total_items_crafted,
    us.total_resources_gathered,
    us.total_items_sold
FROM users u
LEFT JOIN users_professions up ON u.id = up.user_id
LEFT JOIN professions p ON up.profession_id = p.id
LEFT JOIN mastery_rank mr ON up.mastery_rank_id = mr.id
LEFT JOIN user_statistics us ON u.id = us.user_id;

-- Vue: État des ateliers
DROP VIEW IF EXISTS v_workshops_status;
CREATE VIEW v_workshops_status AS
SELECT 
    w.id,
    w.name,
    p.name AS profession_name,
    w.durability,
    w.max_durability,
    ROUND((w.durability * 100.0 / w.max_durability), 2) AS durability_percent,
    w.efficiency_bonus,
    CASE 
        WHEN w.durability = 0 THEN 'Cassé'
        WHEN w.durability < w.max_durability * 0.25 THEN 'Critique'
        WHEN w.durability < w.max_durability * 0.50 THEN 'Faible'
        WHEN w.durability < w.max_durability * 0.75 THEN 'Moyen'
        ELSE 'Excellent'
    END AS status,
    w.base_cost * (1 - (w.durability * 1.0 / w.max_durability)) AS estimated_repair_cost
FROM workshops w
JOIN professions p ON w.profession_id = p.id;

-- Vue: Valorisation des inventaires
DROP VIEW IF EXISTS v_inventory_value;
CREATE VIEW v_inventory_value AS
SELECT 
    i.user_id,
    u.login,
    r.name AS resource_name,
    i.quantity,
    r.base_value,
    rar.multiplier AS rarity_multiplier,
    i.quantity * r.base_value * rar.multiplier AS total_value
FROM inventory i
JOIN users u ON i.user_id = u.id
JOIN resources r ON i.resource_id = r.id
JOIN rarities rar ON r.rarity_id = rar.id
WHERE i.quantity > 0;

-- =====================================================
-- SECTION 12: FONCTIONS UTILITAIRES
-- =====================================================

DELIMITER //

-- Fonction: Obtenir les recettes craftables pour un utilisateur
DROP FUNCTION IF EXISTS get_craftable_recipes//
CREATE FUNCTION get_craftable_recipes(p_user_id INT)
RETURNS JSON
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE result JSON;
    
    SELECT JSON_ARRAYAGG(
        JSON_OBJECT(
            'recipe_id', rec.id,
            'recipe_name', rec.name,
            'profession', p.name,
            'required_level', rec.required_level,
            'user_level', up.level,
            'can_craft', up.level >= rec.required_level,
            'output_quantity', rec.output_quantity,
            'crafting_time', rec.crafting_time,
            'workshop_required', w.name
        )
    ) INTO result
    FROM recipes rec
    JOIN professions p ON rec.profession_id = p.id
    JOIN users_professions up ON up.profession_id = p.id AND up.user_id = p_user_id
    LEFT JOIN workshops w ON rec.workshop_id = w.id
    WHERE rec.is_active = 1;
    
    RETURN COALESCE(result, JSON_ARRAY());
END//

-- Fonction: Calculer le coût de réparation d'un atelier
DROP FUNCTION IF EXISTS calculate_repair_cost//
CREATE FUNCTION calculate_repair_cost(p_workshop_id INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE repair_cost DECIMAL(10,2);
    DECLARE current_durability INT;
    DECLARE max_dur INT;
    DECLARE base_price DECIMAL(10,2);
    
    SELECT durability, max_durability, base_cost
    INTO current_durability, max_dur, base_price
    FROM workshops
    WHERE id = p_workshop_id;
    
    SET repair_cost = base_price * (1 - (current_durability * 1.0 / max_dur)) * 0.5;
    
    RETURN repair_cost;
END//

DELIMITER ;

-- =====================================================
-- SECTION 13: ÉVÉNEMENTS (Tâches planifiées)
-- =====================================================

-- Note: MySQL utilise des EVENTs au lieu de pg_cron
SET GLOBAL event_scheduler = ON;

-- Événement: Nettoyage des tokens expirés (toutes les heures)
DROP EVENT IF EXISTS evt_cleanup_expired_tokens;
CREATE EVENT evt_cleanup_expired_tokens
ON SCHEDULE EVERY 1 HOUR
DO
    DELETE FROM refresh_tokens WHERE expires_at <= CURRENT_TIMESTAMP;

-- Événement: Expiration automatique des offres de marché (toutes les 5 minutes)
DROP EVENT IF EXISTS evt_expire_market_listings;
CREATE EVENT evt_expire_market_listings
ON SCHEDULE EVERY 5 MINUTE
DO
    UPDATE markets
    SET status_id = 4,
        updated_at = CURRENT_TIMESTAMP
    WHERE expires_at IS NOT NULL 
      AND expires_at <= CURRENT_TIMESTAMP
      AND status_id = 1;

-- =====================================================
-- SECTION 14: COMMENTAIRES SUR LES TABLES
-- =====================================================

-- Note: MySQL supporte les commentaires sur tables et colonnes
ALTER TABLE users COMMENT = 'Table des utilisateurs du jeu';
ALTER TABLE professions COMMENT = 'Table des professions disponibles';
ALTER TABLE resources COMMENT = 'Table des ressources du jeu';
ALTER TABLE recipes COMMENT = 'Table des recettes de crafting';
ALTER TABLE inventory COMMENT = 'Inventaire des utilisateurs';
ALTER TABLE markets COMMENT = 'Marché global (partitionné par année)';
ALTER TABLE workshops COMMENT = 'Ateliers de crafting';
ALTER TABLE user_statistics COMMENT = 'Statistiques temps réel des utilisateurs';

-- Réactivation des vérifications
SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================
-- FIN DU SCRIPT MySQL v3.0
-- =====================================================

-- Informations de version
SELECT 
    'B-CraftD MySQL v3.0' AS schema_name,
    '2025-12-04' AS creation_date,
    '27 tables, 11 triggers, 25+ index, 4 vues' AS features,
    'Conversion depuis PostgreSQL v3.0' AS source;

-- Vérification du nombre de tables
SELECT COUNT(*) AS total_tables 
FROM information_schema.tables 
WHERE table_schema = DATABASE();

-- Vérification des triggers
SELECT COUNT(*) AS total_triggers
FROM information_schema.triggers
WHERE trigger_schema = DATABASE();