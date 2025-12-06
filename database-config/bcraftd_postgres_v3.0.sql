-- =====================================================
-- B-CraftD v3.0 - PostgreSQL 16+ Schema COMPLET
-- Date: 4 décembre 2025
-- 27 tables + 11 triggers + 40+ index + 9 vues
-- =====================================================

SET client_encoding = 'UTF8';

-- Types ENUM
DROP TYPE IF EXISTS user_role CASCADE;
CREATE TYPE user_role AS ENUM ('player', 'moderator', 'admin');
DROP TYPE IF EXISTS profession_type CASCADE;
CREATE TYPE profession_type AS ENUM ('gathering', 'crafting', 'processing');
DROP TYPE IF EXISTS market_status_type CASCADE;
CREATE TYPE market_status_type AS ENUM ('active', 'sold', 'cancelled', 'expired', 'reserved');

-- =====================================================
-- TABLES CORE (7)
-- =====================================================

DROP TABLE IF EXISTS users CASCADE;
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    login VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'player',
    is_active BOOLEAN NOT NULL DEFAULT true,
    coins NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    experience INTEGER NOT NULL DEFAULT 0,
    level INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    CONSTRAINT chk_users_coins CHECK (coins >= 0),
    CONSTRAINT chk_users_experience CHECK (experience >= 0),
    CONSTRAINT chk_users_level CHECK (level >= 1 AND level <= 100)
);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_login ON users(login);
CREATE INDEX idx_users_active_role ON users(is_active, role);

DROP TABLE IF EXISTS professions CASCADE;
CREATE TABLE professions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    type profession_type NOT NULL,
    description TEXT,
    max_level INTEGER NOT NULL DEFAULT 50,
    parent_id INTEGER REFERENCES professions(id) ON DELETE SET NULL,
    unlock_level INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_professions_max_level CHECK (max_level > 0),
    CONSTRAINT chk_professions_unlock_level CHECK (unlock_level >= 1)
);
CREATE INDEX idx_professions_type ON professions(type);
CREATE INDEX idx_professions_parent ON professions(parent_id);
CREATE INDEX idx_professions_active ON professions(is_active);

DROP TABLE IF EXISTS resources CASCADE;
CREATE TABLE resources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    rarity_id INTEGER NOT NULL,
    type_id INTEGER NOT NULL,
    base_value NUMERIC(10,2) NOT NULL DEFAULT 1.00,
    stack_size INTEGER NOT NULL DEFAULT 99,
    is_tradeable BOOLEAN NOT NULL DEFAULT true,
    is_craftable BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_resources_base_value CHECK (base_value >= 0),
    CONSTRAINT chk_resources_stack_size CHECK (stack_size > 0)
);
CREATE INDEX idx_resources_rarity ON resources(rarity_id);
CREATE INDEX idx_resources_type ON resources(type_id);
CREATE INDEX idx_resources_tradeable ON resources(is_tradeable);

DROP TABLE IF EXISTS recipes CASCADE;
CREATE TABLE recipes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    resource_id INTEGER NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    profession_id INTEGER NOT NULL REFERENCES professions(id) ON DELETE CASCADE,
    required_level INTEGER NOT NULL DEFAULT 1,
    base_experience INTEGER NOT NULL DEFAULT 10,
    crafting_time INTEGER NOT NULL DEFAULT 60,
    output_quantity INTEGER NOT NULL DEFAULT 1,
    success_rate NUMERIC(5,2) NOT NULL DEFAULT 100.00,
    workshop_id INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_recipes_required_level CHECK (required_level >= 1),
    CONSTRAINT chk_recipes_base_experience CHECK (base_experience >= 0),
    CONSTRAINT chk_recipes_crafting_time CHECK (crafting_time > 0),
    CONSTRAINT chk_recipes_output_quantity CHECK (output_quantity > 0),
    CONSTRAINT chk_recipes_success_rate CHECK (success_rate >= 0 AND success_rate <= 100)
);
CREATE INDEX idx_recipes_profession ON recipes(profession_id);
CREATE INDEX idx_recipes_resource ON recipes(resource_id);
CREATE INDEX idx_recipes_workshop ON recipes(workshop_id);
CREATE INDEX idx_recipes_craftable ON recipes(profession_id, required_level, is_active) INCLUDE (resource_id, crafting_time);

DROP TABLE IF EXISTS inventory CASCADE;
CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    resource_id INTEGER NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_inventory_quantity CHECK (quantity >= 0),
    CONSTRAINT uq_inventory_user_resource UNIQUE (user_id, resource_id)
);
CREATE INDEX idx_inventory_user ON inventory(user_id);
CREATE INDEX idx_inventory_resource ON inventory(resource_id);
CREATE INDEX idx_inventory_nonzero ON inventory(user_id, resource_id) WHERE quantity > 0;

DROP TABLE IF EXISTS refresh_tokens CASCADE;
CREATE TABLE refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(500) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_valid ON refresh_tokens (expires_at, user_id);

DROP TABLE IF EXISTS settings CASCADE;
CREATE TABLE settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) NOT NULL UNIQUE,
    setting_value TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_settings_key ON settings(setting_key);

-- =====================================================
-- TABLES ENVIRONNEMENT (4)
-- =====================================================

DROP TABLE IF EXISTS rarities CASCADE;
CREATE TABLE rarities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    color VARCHAR(7) NOT NULL DEFAULT '#FFFFFF',
    multiplier NUMERIC(5,2) NOT NULL DEFAULT 1.00,
    drop_chance NUMERIC(5,2) NOT NULL DEFAULT 100.00,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_rarities_multiplier CHECK (multiplier > 0),
    CONSTRAINT chk_rarities_drop_chance CHECK (drop_chance >= 0 AND drop_chance <= 100)
);

DROP TABLE IF EXISTS weathers CASCADE;
CREATE TABLE weathers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    gathering_multiplier NUMERIC(5,2) NOT NULL DEFAULT 1.00,
    crafting_multiplier NUMERIC(5,2) NOT NULL DEFAULT 1.00,
    duration_minutes INTEGER NOT NULL DEFAULT 60,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_weathers_gathering_multiplier CHECK (gathering_multiplier >= 0),
    CONSTRAINT chk_weathers_crafting_multiplier CHECK (crafting_multiplier >= 0),
    CONSTRAINT chk_weathers_duration CHECK (duration_minutes > 0)
);

DROP TABLE IF EXISTS seasons CASCADE;
CREATE TABLE seasons (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    gathering_multiplier NUMERIC(5,2) NOT NULL DEFAULT 1.00,
    crafting_multiplier NUMERIC(5,2) NOT NULL DEFAULT 1.00,
    start_month INTEGER NOT NULL,
    end_month INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_seasons_gathering_multiplier CHECK (gathering_multiplier >= 0),
    CONSTRAINT chk_seasons_crafting_multiplier CHECK (crafting_multiplier >= 0),
    CONSTRAINT chk_seasons_start_month CHECK (start_month >= 1 AND start_month <= 12),
    CONSTRAINT chk_seasons_end_month CHECK (end_month >= 1 AND end_month <= 12)
);

DROP TABLE IF EXISTS biomes CASCADE;
CREATE TABLE biomes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    gathering_multiplier NUMERIC(5,2) NOT NULL DEFAULT 1.00,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_biomes_gathering_multiplier CHECK (gathering_multiplier >= 0)
);

-- =====================================================
-- TABLES PROFESSIONS (4)
-- =====================================================

DROP TABLE IF EXISTS subclasses CASCADE;
CREATE TABLE subclasses (
    id SERIAL PRIMARY KEY,
    profession_id INTEGER NOT NULL REFERENCES professions(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    unlock_level INTEGER NOT NULL DEFAULT 25,
    bonus_type VARCHAR(50) NOT NULL,
    bonus_value NUMERIC(5,2) NOT NULL DEFAULT 0.00,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_subclasses_unlock_level CHECK (unlock_level >= 1),
    CONSTRAINT chk_subclasses_bonus_value CHECK (bonus_value >= 0)
);
CREATE INDEX idx_subclasses_profession ON subclasses(profession_id);

DROP TABLE IF EXISTS mastery_rank CASCADE;
CREATE TABLE mastery_rank (
    id SERIAL PRIMARY KEY,
    rank_name VARCHAR(50) NOT NULL UNIQUE,
    min_level INTEGER NOT NULL,
    bonus_multiplier NUMERIC(5,2) NOT NULL DEFAULT 1.00,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_mastery_rank_min_level CHECK (min_level >= 1),
    CONSTRAINT chk_mastery_rank_bonus_multiplier CHECK (bonus_multiplier >= 1.00)
);

DROP TABLE IF EXISTS users_professions CASCADE;
CREATE TABLE users_professions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    profession_id INTEGER NOT NULL REFERENCES professions(id) ON DELETE CASCADE,
    level INTEGER NOT NULL DEFAULT 1,
    experience INTEGER NOT NULL DEFAULT 0,
    mastery_rank_id INTEGER NOT NULL DEFAULT 1 REFERENCES mastery_rank(id) ON DELETE RESTRICT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_users_professions_level CHECK (level >= 1),
    CONSTRAINT chk_users_professions_experience CHECK (experience >= 0),
    CONSTRAINT uq_users_professions UNIQUE (user_id, profession_id)
);
CREATE INDEX idx_users_professions_user ON users_professions(user_id);
CREATE INDEX idx_users_professions_profession ON users_professions(profession_id);
CREATE INDEX idx_users_professions_mastery ON users_professions(mastery_rank_id);

DROP TABLE IF EXISTS users_subclasses CASCADE;
CREATE TABLE users_subclasses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subclass_id INTEGER NOT NULL REFERENCES subclasses(id) ON DELETE CASCADE,
    unlocked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_users_subclasses UNIQUE (user_id, subclass_id)
);
CREATE INDEX idx_users_subclasses_user ON users_subclasses(user_id);
CREATE INDEX idx_users_subclasses_subclass ON users_subclasses(subclass_id);

-- =====================================================
-- TABLES RESSOURCES (6)
-- =====================================================

DROP TABLE IF EXISTS resources_types CASCADE;
CREATE TABLE resources_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS resources_professions CASCADE;
CREATE TABLE resources_professions (
    id SERIAL PRIMARY KEY,
    resource_id INTEGER NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    profession_id INTEGER NOT NULL REFERENCES professions(id) ON DELETE CASCADE,
    drop_rate NUMERIC(5,2) NOT NULL DEFAULT 100.00,
    CONSTRAINT chk_resources_professions_drop_rate CHECK (drop_rate >= 0 AND drop_rate <= 100),
    CONSTRAINT uq_resources_professions UNIQUE (resource_id, profession_id)
);
CREATE INDEX idx_resources_professions_resource ON resources_professions(resource_id);
CREATE INDEX idx_resources_professions_profession ON resources_professions(profession_id);

DROP TABLE IF EXISTS resources_biomes CASCADE;
CREATE TABLE resources_biomes (
    id SERIAL PRIMARY KEY,
    resource_id INTEGER NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    biome_id INTEGER NOT NULL REFERENCES biomes(id) ON DELETE CASCADE,
    spawn_chance NUMERIC(5,2) NOT NULL DEFAULT 100.00,
    CONSTRAINT chk_resources_biomes_spawn_chance CHECK (spawn_chance >= 0 AND spawn_chance <= 100),
    CONSTRAINT uq_resources_biomes UNIQUE (resource_id, biome_id)
);
CREATE INDEX idx_resources_biomes_resource ON resources_biomes(resource_id);
CREATE INDEX idx_resources_biomes_biome ON resources_biomes(biome_id);

DROP TABLE IF EXISTS resources_weathers CASCADE;
CREATE TABLE resources_weathers (
    id SERIAL PRIMARY KEY,
    resource_id INTEGER NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    weather_id INTEGER NOT NULL REFERENCES weathers(id) ON DELETE CASCADE,
    drop_multiplier NUMERIC(5,2) NOT NULL DEFAULT 1.00,
    CONSTRAINT chk_resources_weathers_drop_multiplier CHECK (drop_multiplier >= 0),
    CONSTRAINT uq_resources_weathers UNIQUE (resource_id, weather_id)
);
CREATE INDEX idx_resources_weathers_resource ON resources_weathers(resource_id);
CREATE INDEX idx_resources_weathers_weather ON resources_weathers(weather_id);

DROP TABLE IF EXISTS resources_seasons CASCADE;
CREATE TABLE resources_seasons (
    id SERIAL PRIMARY KEY,
    resource_id INTEGER NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    season_id INTEGER NOT NULL REFERENCES seasons(id) ON DELETE CASCADE,
    availability_multiplier NUMERIC(5,2) NOT NULL DEFAULT 1.00,
    CONSTRAINT chk_resources_seasons_availability CHECK (availability_multiplier >= 0),
    CONSTRAINT uq_resources_seasons UNIQUE (resource_id, season_id)
);
CREATE INDEX idx_resources_seasons_resource ON resources_seasons(resource_id);
CREATE INDEX idx_resources_seasons_season ON resources_seasons(season_id);

DROP TABLE IF EXISTS recipes_resources CASCADE;
CREATE TABLE recipes_resources (
    id SERIAL PRIMARY KEY,
    recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    resource_id INTEGER NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT chk_recipes_resources_quantity CHECK (quantity > 0)
);
CREATE INDEX idx_recipes_resources_recipe ON recipes_resources(recipe_id);
CREATE INDEX idx_recipes_resources_resource ON recipes_resources(resource_id);

-- =====================================================
-- TABLES WORKSHOPS (3)
-- =====================================================

DROP TABLE IF EXISTS workshops CASCADE;
CREATE TABLE workshops (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    profession_id INTEGER NOT NULL REFERENCES professions(id) ON DELETE CASCADE,
    required_level INTEGER NOT NULL DEFAULT 1,
    base_cost NUMERIC(10,2) NOT NULL DEFAULT 100.00,
    durability INTEGER NOT NULL DEFAULT 100,
    max_durability INTEGER NOT NULL DEFAULT 100,
    efficiency_bonus NUMERIC(5,2) NOT NULL DEFAULT 1.00,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_workshops_required_level CHECK (required_level >= 1),
    CONSTRAINT chk_workshops_base_cost CHECK (base_cost >= 0),
    CONSTRAINT chk_workshops_durability CHECK (durability >= 0 AND durability <= max_durability),
    CONSTRAINT chk_workshops_max_durability CHECK (max_durability > 0),
    CONSTRAINT chk_workshops_efficiency_bonus CHECK (efficiency_bonus >= 0)
);
CREATE INDEX idx_workshops_profession ON workshops(profession_id);

DROP TABLE IF EXISTS workshops_resources CASCADE;
CREATE TABLE workshops_resources (
    id SERIAL PRIMARY KEY,
    workshop_id INTEGER NOT NULL REFERENCES workshops(id) ON DELETE CASCADE,
    resource_id INTEGER NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT chk_workshops_resources_quantity CHECK (quantity > 0),
    CONSTRAINT uq_workshops_resources UNIQUE (workshop_id, resource_id)
);
CREATE INDEX idx_workshops_resources_workshop ON workshops_resources(workshop_id);
CREATE INDEX idx_workshops_resources_resource ON workshops_resources(resource_id);

DROP TABLE IF EXISTS workshops_biomes CASCADE;
CREATE TABLE workshops_biomes (
    id SERIAL PRIMARY KEY,
    workshop_id INTEGER NOT NULL REFERENCES workshops(id) ON DELETE CASCADE,
    biome_id INTEGER NOT NULL REFERENCES biomes(id) ON DELETE CASCADE,
    CONSTRAINT uq_workshops_biomes UNIQUE (workshop_id, biome_id)
);
CREATE INDEX idx_workshops_biomes_workshop ON workshops_biomes(workshop_id);
CREATE INDEX idx_workshops_biomes_biome ON workshops_biomes(biome_id);

-- =====================================================
-- TABLES MARCHÉ (2 + partitioning)
-- =====================================================

DROP TABLE IF EXISTS market_status CASCADE;
CREATE TABLE market_status (
    id SERIAL PRIMARY KEY,
    status_name market_status_type NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS markets CASCADE;
CREATE TABLE markets (
    id SERIAL,
    seller_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    buyer_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    resource_id INTEGER NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL,
    total_price NUMERIC(10,2) NOT NULL,
    status_id INTEGER NOT NULL DEFAULT 1 REFERENCES market_status(id) ON DELETE RESTRICT,
    expires_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    CONSTRAINT chk_markets_quantity CHECK (quantity > 0),
    CONSTRAINT chk_markets_unit_price CHECK (unit_price > 0),
    CONSTRAINT chk_markets_total_price CHECK (total_price > 0),
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

CREATE TABLE markets_2024 PARTITION OF markets FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
CREATE TABLE markets_2025 PARTITION OF markets FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
CREATE TABLE markets_2026 PARTITION OF markets FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
CREATE TABLE markets_future PARTITION OF markets FOR VALUES FROM ('2027-01-01') TO (MAXVALUE);

CREATE INDEX idx_markets_seller ON markets(seller_id);
CREATE INDEX idx_markets_buyer ON markets(buyer_id);
CREATE INDEX idx_markets_resource ON markets(resource_id);
CREATE INDEX idx_markets_status ON markets(status_id);
CREATE INDEX idx_markets_search ON markets(resource_id, status_id, created_at DESC) WHERE status_id = 1;
CREATE INDEX idx_markets_expires ON markets(expires_at) WHERE expires_at IS NOT NULL;

-- =====================================================
-- TABLES AUTRES (2)
-- =====================================================

DROP TABLE IF EXISTS devices CASCADE;
CREATE TABLE devices (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_name VARCHAR(100) NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    last_used TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_devices_user ON devices(user_id);

DROP TABLE IF EXISTS user_statistics CASCADE;
CREATE TABLE user_statistics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    total_items_sold INTEGER NOT NULL DEFAULT 0,
    total_items_bought INTEGER NOT NULL DEFAULT 0,
    total_items_crafted INTEGER NOT NULL DEFAULT 0,
    total_sales_value NUMERIC(15,2) NOT NULL DEFAULT 0.00,
    total_purchases_value NUMERIC(15,2) NOT NULL DEFAULT 0.00,
    total_resources_gathered INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_user_statistics_totals CHECK (
        total_items_sold >= 0 AND total_items_bought >= 0 AND 
        total_items_crafted >= 0 AND total_sales_value >= 0 AND 
        total_purchases_value >= 0 AND total_resources_gathered >= 0
    )
);
CREATE INDEX idx_user_statistics_user ON user_statistics(user_id);

-- =====================================================
-- DONNÉES INITIALES
-- =====================================================

INSERT INTO rarities (name, color, multiplier, drop_chance) VALUES
('Commun', '#CCCCCC', 1.0, 100.0), ('Rare', '#4A90E2', 2.0, 25.0),
('Épique', '#9B59B6', 4.0, 5.0), ('Légendaire', '#F39C12', 7.0, 1.0),
('Mythique', '#E74C3C', 10.0, 0.1);

INSERT INTO weathers (name, description, gathering_multiplier, crafting_multiplier, duration_minutes) VALUES
('Ensoleillé', 'Temps clair et ensoleillé', 1.0, 1.0, 120),
('Pluvieux', 'Pluie légère', 0.8, 1.2, 90),
('Orageux', 'Orages violents', 0.5, 0.8, 60),
('Neigeux', 'Chute de neige', 0.7, 1.1, 100),
('Venteux', 'Vent fort', 1.2, 0.9, 80);

INSERT INTO seasons (name, description, gathering_multiplier, crafting_multiplier, start_month, end_month) VALUES
('Printemps', 'Saison de la renaissance', 1.2, 1.0, 3, 5),
('Été', 'Saison chaude et ensoleillée', 1.0, 1.0, 6, 8),
('Automne', 'Saison des récoltes', 1.1, 1.2, 9, 11),
('Hiver', 'Saison froide', 0.8, 1.3, 12, 2);

INSERT INTO biomes (name, description, gathering_multiplier) VALUES
('Forêt', 'Forêt dense et sombre', 1.2), ('Montagne', 'Montagnes rocheuses', 1.0),
('Plaine', 'Vastes plaines herbeuses', 1.1), ('Rivière', 'Cours d eau douce', 1.3),
('Marais', 'Zones marécageuses', 0.9), ('Côte', 'Littoral marin', 1.4);

INSERT INTO mastery_rank (rank_name, min_level, bonus_multiplier) VALUES
('Débutant', 1, 1.00), ('Apprenti', 15, 1.10), ('Compagnon', 30, 1.25),
('Expert', 50, 1.50), ('Maître', 75, 2.00);

INSERT INTO resources_types (name, description) VALUES
('Minerai', 'Ressources minérales'), ('Bois', 'Ressources forestières'),
('Plante', 'Ressources végétales'), ('Animal', 'Ressources animales'),
('Alimentaire', 'Ressources consommables'), ('Outil', 'Outils et équipements'),
('Matériau', 'Matériaux de construction');

INSERT INTO market_status (status_name, description) VALUES
('active', 'Offre active sur le marché'), ('sold', 'Offre vendue'),
('cancelled', 'Offre annulée par le vendeur'), ('expired', 'Offre expirée'),
('reserved', 'Offre réservée (en attente de paiement)');

ALTER TABLE resources ADD CONSTRAINT fk_resources_rarity FOREIGN KEY (rarity_id) REFERENCES rarities(id);
ALTER TABLE resources ADD CONSTRAINT fk_resources_type FOREIGN KEY (type_id) REFERENCES resources_types(id);

-- =====================================================
-- TRIGGERS (11)
-- =====================================================

CREATE OR REPLACE FUNCTION fn_check_max_professions() RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT COUNT(*) FROM users_professions WHERE user_id = NEW.user_id) >= 3 THEN
        RAISE EXCEPTION 'Un utilisateur ne peut pas avoir plus de 3 professions actives';
    END IF;
    RETURN NEW;
END; $$ LANGUAGE plpgsql;
CREATE TRIGGER trg_check_max_professions BEFORE INSERT ON users_professions FOR EACH ROW EXECUTE FUNCTION fn_check_max_professions();

CREATE OR REPLACE FUNCTION fn_update_mastery_rank() RETURNS TRIGGER AS $$
DECLARE new_rank_id INTEGER;
BEGIN
    IF NEW.level >= OLD.level THEN
        SELECT id INTO new_rank_id FROM mastery_rank WHERE min_level <= NEW.level ORDER BY min_level DESC LIMIT 1;
        NEW.mastery_rank_id := new_rank_id;
    END IF;
    RETURN NEW;
END; $$ LANGUAGE plpgsql;
CREATE TRIGGER trg_update_mastery_rank BEFORE UPDATE ON users_professions FOR EACH ROW EXECUTE FUNCTION fn_update_mastery_rank();

CREATE OR REPLACE FUNCTION fn_prevent_self_trading() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.buyer_id IS NOT NULL AND NEW.buyer_id = NEW.seller_id THEN
        RAISE EXCEPTION 'Un utilisateur ne peut pas acheter ses propres offres';
    END IF;
    RETURN NEW;
END; $$ LANGUAGE plpgsql;
CREATE TRIGGER trg_prevent_self_trading BEFORE UPDATE ON markets FOR EACH ROW EXECUTE FUNCTION fn_prevent_self_trading();

CREATE OR REPLACE FUNCTION fn_validate_email() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.email !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' THEN
        RAISE EXCEPTION 'Format d email invalide';
    END IF;
    RETURN NEW;
END; $$ LANGUAGE plpgsql;
CREATE TRIGGER trg_validate_email BEFORE INSERT OR UPDATE ON users FOR EACH ROW EXECUTE FUNCTION fn_validate_email();

CREATE OR REPLACE FUNCTION fn_workshop_usage() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.durability < OLD.durability THEN NEW.updated_at = CURRENT_TIMESTAMP; END IF;
    RETURN NEW;
END; $$ LANGUAGE plpgsql;
CREATE TRIGGER trg_workshop_usage BEFORE UPDATE ON workshops FOR EACH ROW EXECUTE FUNCTION fn_workshop_usage();

CREATE OR REPLACE FUNCTION fn_check_inventory_quantity() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.quantity < 0 THEN RAISE EXCEPTION 'La quantité en inventaire ne peut pas être négative'; END IF;
    RETURN NEW;
END; $$ LANGUAGE plpgsql;
CREATE TRIGGER trg_check_inventory_quantity BEFORE INSERT OR UPDATE ON inventory FOR EACH ROW EXECUTE FUNCTION fn_check_inventory_quantity();

CREATE OR REPLACE FUNCTION fn_check_stack_limit() RETURNS TRIGGER AS $$
DECLARE max_stack INTEGER;
BEGIN
    SELECT stack_size INTO max_stack FROM resources WHERE id = NEW.resource_id;
    IF NEW.quantity > max_stack THEN RAISE EXCEPTION 'La quantité dépasse la limite de stack pour cette ressource'; END IF;
    RETURN NEW;
END; $$ LANGUAGE plpgsql;
CREATE TRIGGER trg_check_stack_limit BEFORE INSERT OR UPDATE ON inventory FOR EACH ROW EXECUTE FUNCTION fn_check_stack_limit();

CREATE OR REPLACE FUNCTION fn_transfer_to_market() RETURNS TRIGGER AS $$
BEGIN
    UPDATE inventory SET quantity = quantity - NEW.quantity WHERE user_id = NEW.seller_id AND resource_id = NEW.resource_id;
    DELETE FROM inventory WHERE user_id = NEW.seller_id AND resource_id = NEW.resource_id AND quantity <= 0;
    RETURN NEW;
END; $$ LANGUAGE plpgsql;
CREATE TRIGGER trg_transfer_to_market AFTER INSERT ON markets FOR EACH ROW EXECUTE FUNCTION fn_transfer_to_market();

CREATE OR REPLACE FUNCTION fn_complete_market_transaction() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status_id = 2 AND OLD.status_id != 2 AND NEW.buyer_id IS NOT NULL THEN
        UPDATE users SET coins = coins + NEW.total_price WHERE id = NEW.seller_id;
        UPDATE users SET coins = coins - NEW.total_price WHERE id = NEW.buyer_id;
        INSERT INTO inventory (user_id, resource_id, quantity) VALUES (NEW.buyer_id, NEW.resource_id, NEW.quantity)
        ON CONFLICT (user_id, resource_id) DO UPDATE SET quantity = inventory.quantity + EXCLUDED.quantity;
        UPDATE user_statistics SET total_items_sold = total_items_sold + NEW.quantity, total_sales_value = total_sales_value + NEW.total_price WHERE user_id = NEW.seller_id;
        UPDATE user_statistics SET total_items_bought = total_items_bought + NEW.quantity, total_purchases_value = total_purchases_value + NEW.total_price WHERE user_id = NEW.buyer_id;
    END IF;
    RETURN NEW;
END; $$ LANGUAGE plpgsql;
CREATE TRIGGER trg_complete_market_transaction AFTER UPDATE ON markets FOR EACH ROW EXECUTE FUNCTION fn_complete_market_transaction();

CREATE OR REPLACE FUNCTION fn_auto_expire_listings() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.expires_at IS NOT NULL AND NEW.expires_at <= CURRENT_TIMESTAMP AND OLD.status_id = 1 THEN
        NEW.status_id = 4;
        INSERT INTO inventory (user_id, resource_id, quantity) VALUES (NEW.seller_id, NEW.resource_id, NEW.quantity)
        ON CONFLICT (user_id, resource_id) DO UPDATE SET quantity = inventory.quantity + EXCLUDED.quantity;
    END IF;
    RETURN NEW;
END; $$ LANGUAGE plpgsql;
CREATE TRIGGER trg_auto_expire_listings BEFORE UPDATE ON markets FOR EACH ROW EXECUTE FUNCTION fn_auto_expire_listings();

CREATE OR REPLACE FUNCTION fn_auto_level_up() RETURNS TRIGGER AS $$
DECLARE required_xp INTEGER;
BEGIN
    IF NEW.experience >= OLD.experience THEN
        required_xp := NEW.level * 100;
        WHILE NEW.experience >= required_xp AND NEW.level < 100 LOOP
            NEW.level := NEW.level + 1;
            NEW.experience := NEW.experience - required_xp;
            required_xp := NEW.level * 100;
        END LOOP;
    END IF;
    RETURN NEW;
END; $$ LANGUAGE plpgsql;
CREATE TRIGGER trg_auto_level_up BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION fn_auto_level_up();

-- =====================================================
-- VUES STANDARDS (4)
-- =====================================================

DROP VIEW IF EXISTS v_resources_details CASCADE;
CREATE VIEW v_resources_details AS
SELECT r.id, r.name, r.description, rt.name AS type_name, rar.name AS rarity_name, rar.color AS rarity_color,
       rar.multiplier AS rarity_multiplier, r.base_value, r.base_value * rar.multiplier AS adjusted_value,
       r.stack_size, r.is_tradeable, r.is_craftable, r.created_at
FROM resources r JOIN resources_types rt ON r.type_id = rt.id JOIN rarities rar ON r.rarity_id = rar.id;

DROP VIEW IF EXISTS v_user_progression CASCADE;
CREATE VIEW v_user_progression AS
SELECT u.id AS user_id, u.login, u.level AS character_level, u.experience AS character_xp, u.coins,
       p.name AS profession_name, up.level AS profession_level, up.experience AS profession_xp,
       mr.rank_name AS mastery_rank, mr.bonus_multiplier, us.total_items_crafted, us.total_resources_gathered, us.total_items_sold
FROM users u
LEFT JOIN users_professions up ON u.id = up.user_id
LEFT JOIN professions p ON up.profession_id = p.id
LEFT JOIN mastery_rank mr ON up.mastery_rank_id = mr.id
LEFT JOIN user_statistics us ON u.id = us.user_id;

DROP VIEW IF EXISTS v_workshops_status CASCADE;
CREATE VIEW v_workshops_status AS
SELECT w.id, w.name, p.name AS profession_name, w.durability, w.max_durability,
       ROUND((w.durability * 100.0 / w.max_durability), 2) AS durability_percent, w.efficiency_bonus,
       CASE WHEN w.durability = 0 THEN 'Cassé'
            WHEN w.durability < w.max_durability * 0.25 THEN 'Critique'
            WHEN w.durability < w.max_durability * 0.50 THEN 'Faible'
            WHEN w.durability < w.max_durability * 0.75 THEN 'Moyen'
            ELSE 'Excellent' END AS status,
       w.base_cost * (1 - (w.durability * 1.0 / w.max_durability)) AS estimated_repair_cost
FROM workshops w JOIN professions p ON w.profession_id = p.id;

DROP VIEW IF EXISTS v_inventory_value CASCADE;
CREATE VIEW v_inventory_value AS
SELECT i.user_id, u.login, r.name AS resource_name, i.quantity, r.base_value, rar.multiplier AS rarity_multiplier,
       i.quantity * r.base_value * rar.multiplier AS total_value
FROM inventory i
JOIN users u ON i.user_id = u.id
JOIN resources r ON i.resource_id = r.id
JOIN rarities rar ON r.rarity_id = rar.id
WHERE i.quantity > 0;

-- =====================================================
-- VUES MATÉRIALISÉES (5)
-- =====================================================

DROP MATERIALIZED VIEW IF EXISTS mv_economy_overview CASCADE;
CREATE MATERIALIZED VIEW mv_economy_overview AS
SELECT COUNT(DISTINCT m.seller_id) AS active_sellers, COUNT(DISTINCT m.buyer_id) AS active_buyers,
       COUNT(*) FILTER (WHERE m.status_id = 1) AS active_listings, COUNT(*) FILTER (WHERE m.status_id = 2) AS completed_sales,
       COALESCE(SUM(m.total_price) FILTER (WHERE m.status_id = 1), 0) AS total_active_value,
       COALESCE(SUM(m.total_price) FILTER (WHERE m.status_id = 2 AND m.completed_at >= NOW() - INTERVAL '24 hours'), 0) AS sales_last_24h,
       COALESCE(SUM(m.total_price) FILTER (WHERE m.status_id = 2 AND m.completed_at >= NOW() - INTERVAL '7 days'), 0) AS sales_last_7days,
       COALESCE(SUM(m.total_price) FILTER (WHERE m.status_id = 2 AND m.completed_at >= NOW() - INTERVAL '30 days'), 0) AS sales_last_30days,
       COUNT(DISTINCT m.resource_id) AS unique_resources_traded,
       (SELECT COUNT(*) FROM users WHERE is_active = true) AS total_active_users,
       (SELECT SUM(coins) FROM users WHERE is_active = true) AS total_economy_coins,
       (SELECT AVG(coins) FROM users WHERE is_active = true) AS avg_user_coins,
       (SELECT SUM(total_items_crafted) FROM user_statistics) AS total_items_crafted_global,
       (SELECT SUM(total_resources_gathered) FROM user_statistics) AS total_resources_gathered_global,
       NOW() AS last_refresh
FROM markets m;
CREATE INDEX idx_mv_economy_last_refresh ON mv_economy_overview(last_refresh);

DROP MATERIALIZED VIEW IF EXISTS mv_top_traded_resources CASCADE;
CREATE MATERIALIZED VIEW mv_top_traded_resources AS
SELECT r.id AS resource_id, r.name AS resource_name, rt.name AS resource_type, rar.name AS rarity, rar.color AS rarity_color,
       COUNT(*) FILTER (WHERE m.status_id = 2 AND m.completed_at >= NOW() - INTERVAL '24 hours') AS sales_count_24h,
       COALESCE(SUM(m.quantity) FILTER (WHERE m.status_id = 2 AND m.completed_at >= NOW() - INTERVAL '24 hours'), 0) AS volume_24h,
       COALESCE(SUM(m.total_price) FILTER (WHERE m.status_id = 2 AND m.completed_at >= NOW() - INTERVAL '24 hours'), 0) AS revenue_24h,
       COUNT(*) FILTER (WHERE m.status_id = 2 AND m.completed_at >= NOW() - INTERVAL '7 days') AS sales_count_7d,
       COALESCE(SUM(m.quantity) FILTER (WHERE m.status_id = 2 AND m.completed_at >= NOW() - INTERVAL '7 days'), 0) AS volume_7d,
       COALESCE(SUM(m.total_price) FILTER (WHERE m.status_id = 2 AND m.completed_at >= NOW() - INTERVAL '7 days'), 0) AS revenue_7d,
       COALESCE(AVG(m.unit_price) FILTER (WHERE m.status_id = 2 AND m.completed_at >= NOW() - INTERVAL '24 hours'), 0) AS avg_price_24h,
       COALESCE(AVG(m.unit_price) FILTER (WHERE m.status_id = 2 AND m.completed_at >= NOW() - INTERVAL '7 days'), 0) AS avg_price_7d,
       COUNT(*) FILTER (WHERE m.status_id = 1) AS active_listings,
       COALESCE(MIN(m.unit_price) FILTER (WHERE m.status_id = 1), 0) AS lowest_active_price, NOW() AS last_refresh
FROM resources r JOIN resources_types rt ON r.type_id = rt.id JOIN rarities rar ON r.rarity_id = rar.id LEFT JOIN markets m ON r.id = m.resource_id
GROUP BY r.id, r.name, rt.name, rar.name, rar.color
HAVING COUNT(*) FILTER (WHERE m.status_id = 2 AND m.completed_at >= NOW() - INTERVAL '7 days') > 0
ORDER BY sales_count_7d DESC, revenue_7d DESC LIMIT 10;
CREATE INDEX idx_mv_top_resources_sales ON mv_top_traded_resources(sales_count_7d DESC, revenue_7d DESC);
CREATE INDEX idx_mv_top_resources_resource ON mv_top_traded_resources(resource_id);

DROP MATERIALIZED VIEW IF EXISTS mv_leaderboard CASCADE;
CREATE MATERIALIZED VIEW mv_leaderboard AS
WITH user_scores AS (
    SELECT u.id AS user_id, u.login, u.level, u.experience, u.coins, COUNT(DISTINCT up.profession_id) AS profession_count,
           COALESCE(SUM(up.level), 0) AS total_profession_levels, COALESCE(AVG(up.level), 0) AS avg_profession_level,
           COUNT(*) FILTER (WHERE mr.rank_name = 'Maître') AS master_professions,
           COUNT(*) FILTER (WHERE mr.rank_name = 'Expert') AS expert_professions,
           COALESCE(us.total_items_sold, 0) AS total_items_sold, COALESCE(us.total_items_bought, 0) AS total_items_bought,
           COALESCE(us.total_items_crafted, 0) AS total_items_crafted, COALESCE(us.total_sales_value, 0) AS total_sales_value,
           (u.level * 10) + (COALESCE(SUM(up.level), 0) * 5) + (COUNT(*) FILTER (WHERE mr.rank_name = 'Maître') * 500) +
           (COUNT(*) FILTER (WHERE mr.rank_name = 'Expert') * 250) + (COALESCE(us.total_items_crafted, 0) * 0.1) +
           (COALESCE(us.total_sales_value, 0) * 0.01) AS global_score
    FROM users u LEFT JOIN users_professions up ON u.id = up.user_id LEFT JOIN mastery_rank mr ON up.mastery_rank_id = mr.id
    LEFT JOIN user_statistics us ON u.id = us.user_id WHERE u.is_active = true
    GROUP BY u.id, u.login, u.level, u.experience, u.coins, us.total_items_sold, us.total_items_bought, us.total_items_crafted, us.total_sales_value
)
SELECT ROW_NUMBER() OVER (ORDER BY global_score DESC) AS rank, user_id, login, level, experience, coins, profession_count,
       total_profession_levels, avg_profession_level, master_professions, expert_professions, total_items_crafted, total_sales_value,
       ROUND(global_score, 2) AS global_score,
       CASE WHEN ROW_NUMBER() OVER (ORDER BY global_score DESC) = 1 THEN '🥇 Champion'
            WHEN ROW_NUMBER() OVER (ORDER BY global_score DESC) = 2 THEN '🥈 Vice-Champion'
            WHEN ROW_NUMBER() OVER (ORDER BY global_score DESC) = 3 THEN '🥉 Médaille de Bronze'
            WHEN ROW_NUMBER() OVER (ORDER BY global_score DESC) <= 10 THEN '⭐ Top 10'
            WHEN ROW_NUMBER() OVER (ORDER BY global_score DESC) <= 50 THEN '🌟 Top 50'
            ELSE '💎 Top 100' END AS badge, NOW() AS last_refresh
FROM user_scores ORDER BY global_score DESC LIMIT 100;
CREATE INDEX idx_mv_leaderboard_rank ON mv_leaderboard(rank);
CREATE INDEX idx_mv_leaderboard_user ON mv_leaderboard(user_id);
CREATE INDEX idx_mv_leaderboard_score ON mv_leaderboard(global_score DESC);

DROP MATERIALIZED VIEW IF EXISTS mv_rare_resources_by_biome CASCADE;
CREATE MATERIALIZED VIEW mv_rare_resources_by_biome AS
SELECT b.id AS biome_id, b.name AS biome_name, b.description AS biome_description, b.gathering_multiplier AS biome_multiplier,
       r.id AS resource_id, r.name AS resource_name, rt.name AS resource_type, rar.name AS rarity, rar.color AS rarity_color,
       rar.multiplier AS rarity_multiplier, rar.drop_chance AS base_drop_chance, rb.spawn_chance,
       ROUND((rb.spawn_chance * rar.drop_chance / 100), 4) AS effective_drop_chance,
       ROUND(r.base_value * rar.multiplier * b.gathering_multiplier, 2) AS effective_value,
       ARRAY_AGG(DISTINCT p.name ORDER BY p.name) FILTER (WHERE p.name IS NOT NULL) AS required_professions,
       ARRAY_AGG(DISTINCT w.name ORDER BY w.name) FILTER (WHERE rw.drop_multiplier > 1.0) AS favorable_weathers,
       ARRAY_AGG(DISTINCT s.name ORDER BY s.name) FILTER (WHERE rs.availability_multiplier > 1.0) AS favorable_seasons, NOW() AS last_refresh
FROM biomes b JOIN resources_biomes rb ON b.id = rb.biome_id JOIN resources r ON rb.resource_id = r.id
JOIN resources_types rt ON r.type_id = rt.id JOIN rarities rar ON r.rarity_id = rar.id
LEFT JOIN resources_professions rp ON r.id = rp.resource_id LEFT JOIN professions p ON rp.profession_id = p.id
LEFT JOIN resources_weathers rw ON r.id = rw.resource_id LEFT JOIN weathers w ON rw.weather_id = w.id
LEFT JOIN resources_seasons rs ON r.id = rs.resource_id LEFT JOIN seasons s ON rs.season_id = s.id
WHERE rar.name IN ('Rare', 'Épique', 'Légendaire', 'Mythique')
GROUP BY b.id, b.name, b.description, b.gathering_multiplier, r.id, r.name, r.base_value, rt.name, rar.name, rar.color, rar.multiplier, rar.drop_chance, rb.spawn_chance
ORDER BY rar.multiplier DESC, effective_value DESC, b.name;
CREATE INDEX idx_mv_rare_resources_biome ON mv_rare_resources_by_biome(biome_id);
CREATE INDEX idx_mv_rare_resources_resource ON mv_rare_resources_by_biome(resource_id);
CREATE INDEX idx_mv_rare_resources_rarity ON mv_rare_resources_by_biome(rarity);
CREATE INDEX idx_mv_rare_resources_value ON mv_rare_resources_by_biome(effective_value DESC);

DROP MATERIALIZED VIEW IF EXISTS mv_resource_price_history CASCADE;
CREATE MATERIALIZED VIEW mv_resource_price_history AS
WITH daily_prices AS (
    SELECT r.id AS resource_id, r.name AS resource_name, rt.name AS resource_type, rar.name AS rarity, DATE(m.completed_at) AS trade_date,
           COUNT(*) AS trades_count, SUM(m.quantity) AS total_volume, AVG(m.unit_price) AS avg_price,
           MIN(m.unit_price) AS min_price, MAX(m.unit_price) AS max_price, STDDEV(m.unit_price) AS price_volatility,
           LAG(AVG(m.unit_price)) OVER (PARTITION BY r.id ORDER BY DATE(m.completed_at)) AS prev_day_avg_price
    FROM resources r JOIN resources_types rt ON r.type_id = rt.id JOIN rarities rar ON r.rarity_id = rar.id
    JOIN markets m ON r.id = m.resource_id WHERE m.status_id = 2 AND m.completed_at >= NOW() - INTERVAL '30 days'
    GROUP BY r.id, r.name, rt.name, rar.name, DATE(m.completed_at)
)
SELECT resource_id, resource_name, resource_type, rarity, trade_date, trades_count, total_volume,
       ROUND(avg_price, 2) AS avg_price, ROUND(min_price, 2) AS min_price, ROUND(max_price, 2) AS max_price,
       ROUND(price_volatility, 2) AS price_volatility, ROUND(prev_day_avg_price, 2) AS prev_day_avg_price,
       CASE WHEN prev_day_avg_price IS NOT NULL AND prev_day_avg_price > 0
            THEN ROUND(((avg_price - prev_day_avg_price) / prev_day_avg_price * 100), 2) ELSE NULL END AS price_change_percent,
       CASE WHEN prev_day_avg_price IS NULL THEN 'NEW'
            WHEN avg_price > prev_day_avg_price * 1.05 THEN 'HAUSSE'
            WHEN avg_price < prev_day_avg_price * 0.95 THEN 'BAISSE'
            ELSE 'STABLE' END AS trend, NOW() AS last_refresh
FROM daily_prices ORDER BY resource_id, trade_date DESC;
CREATE INDEX idx_mv_price_history_resource ON mv_resource_price_history(resource_id, trade_date DESC);
CREATE INDEX idx_mv_price_history_date ON mv_resource_price_history(trade_date DESC);
CREATE INDEX idx_mv_price_history_trend ON mv_resource_price_history(trend);

-- =====================================================
-- FONCTIONS DE REFRESH (6)
-- =====================================================

CREATE OR REPLACE FUNCTION refresh_all_materialized_views() RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_economy_overview;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_top_traded_resources;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_leaderboard;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_rare_resources_by_biome;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_resource_price_history;
    RAISE NOTICE 'Toutes les vues matérialisées ont été rafraîchies à %', NOW();
END; $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION refresh_economy_view() RETURNS void AS $$ BEGIN REFRESH MATERIALIZED VIEW CONCURRENTLY mv_economy_overview; END; $$ LANGUAGE plpgsql;
CREATE OR REPLACE FUNCTION refresh_top_resources_view() RETURNS void AS $$ BEGIN REFRESH MATERIALIZED VIEW CONCURRENTLY mv_top_traded_resources; END; $$ LANGUAGE plpgsql;
CREATE OR REPLACE FUNCTION refresh_leaderboard_view() RETURNS void AS $$ BEGIN REFRESH MATERIALIZED VIEW CONCURRENTLY mv_leaderboard; END; $$ LANGUAGE plpgsql;
CREATE OR REPLACE FUNCTION refresh_rare_resources_view() RETURNS void AS $$ BEGIN REFRESH MATERIALIZED VIEW CONCURRENTLY mv_rare_resources_by_biome; END; $$ LANGUAGE plpgsql;
CREATE OR REPLACE FUNCTION refresh_price_history_view() RETURNS void AS $$ BEGIN REFRESH MATERIALIZED VIEW CONCURRENTLY mv_resource_price_history; END; $$ LANGUAGE plpgsql;

-- Initial refresh
REFRESH MATERIALIZED VIEW mv_economy_overview;
REFRESH MATERIALIZED VIEW mv_top_traded_resources;
REFRESH MATERIALIZED VIEW mv_leaderboard;
REFRESH MATERIALIZED VIEW mv_rare_resources_by_biome;
REFRESH MATERIALIZED VIEW mv_resource_price_history;

-- =====================================================
-- FIN POSTGRESQL v3.0 COMPLET
-- =====================================================

SELECT 'B-CraftD PostgreSQL v3.0 - Installation réussie' AS message,
       '27 tables, 11 triggers, 40+ index, 4 vues, 5 vues matérialisées' AS features;