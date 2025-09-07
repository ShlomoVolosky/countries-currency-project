-- Create countries table
CREATE TABLE IF NOT EXISTS countries (
    id SERIAL PRIMARY KEY,
    country_name VARCHAR(255) NOT NULL,
    capitals TEXT[],
    continent VARCHAR(255),
    currencies TEXT[],
    is_un_member BOOLEAN,
    population BIGINT,
    timezone_info JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create currency rates table for part 2
CREATE TABLE IF NOT EXISTS currency_rates (
    id SERIAL PRIMARY KEY,
    country_name VARCHAR(255) NOT NULL,
    currency_code VARCHAR(10) NOT NULL,
    shekel_rate DECIMAL(10, 4),
    rate_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(country_name, currency_code, rate_date)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_countries_name ON countries(country_name);
CREATE INDEX IF NOT EXISTS idx_currency_rates_country ON currency_rates(country_name);
CREATE INDEX IF NOT EXISTS idx_currency_rates_date ON currency_rates(rate_date);