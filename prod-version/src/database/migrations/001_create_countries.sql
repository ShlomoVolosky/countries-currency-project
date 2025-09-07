-- Migration: 001_create_countries.sql
-- Description: Create countries table with enhanced structure
-- Created: 2024-01-01
-- Author: Countries Currency Project

-- Create countries table
CREATE TABLE IF NOT EXISTS countries (
    id SERIAL PRIMARY KEY,
    country_name VARCHAR(255) NOT NULL UNIQUE,
    capitals TEXT[],
    continent VARCHAR(255),
    currencies TEXT[],
    is_un_member BOOLEAN DEFAULT FALSE,
    population BIGINT DEFAULT 0,
    timezone_info JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_countries_name ON countries(country_name);
CREATE INDEX IF NOT EXISTS idx_countries_continent ON countries(continent);
CREATE INDEX IF NOT EXISTS idx_countries_un_member ON countries(is_un_member);
CREATE INDEX IF NOT EXISTS idx_countries_population ON countries(population);
CREATE INDEX IF NOT EXISTS idx_countries_currencies ON countries USING GIN(currencies);
CREATE INDEX IF NOT EXISTS idx_countries_timezone_info ON countries USING GIN(timezone_info);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_countries_updated_at 
    BEFORE UPDATE ON countries 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE countries IS 'Stores country information including capitals, currencies, and timezone data';
COMMENT ON COLUMN countries.country_name IS 'Official country name';
COMMENT ON COLUMN countries.capitals IS 'Array of capital cities';
COMMENT ON COLUMN countries.continent IS 'Continent where country is located';
COMMENT ON COLUMN countries.currencies IS 'Array of currency codes used by the country';
COMMENT ON COLUMN countries.is_un_member IS 'Whether the country is a UN member';
COMMENT ON COLUMN countries.population IS 'Country population count';
COMMENT ON COLUMN countries.timezone_info IS 'JSON object containing timezone information with current times';
COMMENT ON COLUMN countries.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN countries.updated_at IS 'Record last update timestamp';
