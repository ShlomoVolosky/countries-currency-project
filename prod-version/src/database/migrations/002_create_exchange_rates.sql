-- Migration: 002_create_exchange_rates.sql
-- Description: Create currency rates table with enhanced structure
-- Created: 2024-01-01
-- Author: Countries Currency Project

-- Create currency rates table
CREATE TABLE IF NOT EXISTS currency_rates (
    id SERIAL PRIMARY KEY,
    country_name VARCHAR(255) NOT NULL,
    currency_code VARCHAR(10) NOT NULL,
    shekel_rate DECIMAL(15, 8) NOT NULL,
    rate_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(country_name, currency_code, rate_date)
);

-- Add updated_at column if it doesn't exist (for existing tables)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'currency_rates' AND column_name = 'updated_at') THEN
        ALTER TABLE currency_rates ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
    END IF;
END $$;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_currency_rates_country ON currency_rates(country_name);
CREATE INDEX IF NOT EXISTS idx_currency_rates_currency ON currency_rates(currency_code);
CREATE INDEX IF NOT EXISTS idx_currency_rates_date ON currency_rates(rate_date);
CREATE INDEX IF NOT EXISTS idx_currency_rates_country_currency ON currency_rates(country_name, currency_code);
CREATE INDEX IF NOT EXISTS idx_currency_rates_country_date ON currency_rates(country_name, rate_date);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_currency_rates_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_currency_rates_updated_at 
    BEFORE UPDATE ON currency_rates 
    FOR EACH ROW 
    EXECUTE FUNCTION update_currency_rates_updated_at_column();

-- Add foreign key constraint to countries table (optional, for data integrity)
-- ALTER TABLE currency_rates 
-- ADD CONSTRAINT fk_currency_rates_country 
-- FOREIGN KEY (country_name) REFERENCES countries(country_name) 
-- ON DELETE CASCADE;

-- Add check constraints for data validation
ALTER TABLE currency_rates 
ADD CONSTRAINT chk_shekel_rate_positive 
CHECK (shekel_rate > 0);

ALTER TABLE currency_rates 
ADD CONSTRAINT chk_currency_code_format 
CHECK (currency_code ~ '^[A-Z]{3}$');

-- Add comments for documentation
COMMENT ON TABLE currency_rates IS 'Stores currency exchange rates to ILS (Israeli Shekel)';
COMMENT ON COLUMN currency_rates.country_name IS 'Country name (references countries table)';
COMMENT ON COLUMN currency_rates.currency_code IS 'ISO 4217 currency code (3 letters)';
COMMENT ON COLUMN currency_rates.shekel_rate IS 'Exchange rate: how much of this currency equals 1 ILS';
COMMENT ON COLUMN currency_rates.rate_date IS 'Date when this rate was valid';
COMMENT ON COLUMN currency_rates.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN currency_rates.updated_at IS 'Record last update timestamp';

-- Create view for latest rates
CREATE OR REPLACE VIEW latest_currency_rates AS
SELECT DISTINCT ON (country_name, currency_code)
    country_name,
    currency_code,
    shekel_rate,
    rate_date,
    created_at,
    updated_at
FROM currency_rates
ORDER BY country_name, currency_code, rate_date DESC;

COMMENT ON VIEW latest_currency_rates IS 'View showing the latest exchange rate for each country-currency pair';

-- Create view for rate statistics
CREATE OR REPLACE VIEW currency_rate_stats AS
SELECT 
    currency_code,
    COUNT(*) as total_rates,
    MIN(rate_date) as first_rate_date,
    MAX(rate_date) as last_rate_date,
    AVG(shekel_rate) as avg_rate,
    MIN(shekel_rate) as min_rate,
    MAX(shekel_rate) as max_rate,
    STDDEV(shekel_rate) as rate_stddev
FROM currency_rates
GROUP BY currency_code
ORDER BY currency_code;

COMMENT ON VIEW currency_rate_stats IS 'Statistical summary of currency rates by currency code';
