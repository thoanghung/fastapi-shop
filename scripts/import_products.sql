-- Import products.csv into PostgreSQL (with pgvector).
-- Run with:  psql "$DATABASE_URL" -f import_products.sql
-- (products.csv must be in the directory where you run psql)

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS products (
    id           BIGSERIAL PRIMARY KEY,
    sku          TEXT UNIQUE NOT NULL,
    name         TEXT NOT NULL,
    category     TEXT NOT NULL,
    product_type TEXT NOT NULL,
    brand        TEXT NOT NULL,
    price        INTEGER NOT NULL,          -- VND
    stock        INTEGER NOT NULL DEFAULT 0,
    rating       NUMERIC(2,1),
    description  TEXT,
    attributes   JSONB NOT NULL DEFAULT '{}',
    embedding    vector(1024),              -- set to your embedding model's dimension
    created_at   TIMESTAMP NOT NULL DEFAULT now()
);

-- Fast bulk load (client-side, so no superuser needed)
\copy products (sku, name, category, product_type, brand, price, stock, rating, description, attributes, created_at) FROM 'products.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')

-- Indexes for filters (create AFTER loading: much faster)
CREATE INDEX IF NOT EXISTS idx_products_category ON products (category);
CREATE INDEX IF NOT EXISTS idx_products_price    ON products (price);
CREATE INDEX IF NOT EXISTS idx_products_brand    ON products (brand);
CREATE INDEX IF NOT EXISTS idx_products_attrs    ON products USING GIN (attributes);

-- Create the vector index later, after embeddings are filled in:
-- CREATE INDEX idx_products_embedding ON products USING hnsw (embedding vector_cosine_ops);

ANALYZE products;
SELECT count(*) AS total, count(DISTINCT name) AS distinct_names FROM products;
