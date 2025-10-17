-- Migration: Add arbitrage_score column to properties table
-- Date: October 17, 2025
-- Purpose: Enable Arbitrage Score filtering (0-100 range)
-- Pattern: Cloned from flip_score implementation

-- Add arbitrage_score column (INTEGER, nullable, 0-100 range)
ALTER TABLE properties 
ADD COLUMN IF NOT EXISTS arbitrage_score INTEGER;

-- Add CHECK constraint to ensure valid range (0-100)
ALTER TABLE properties 
ADD CONSTRAINT arbitrage_score_range 
CHECK (arbitrage_score IS NULL OR (arbitrage_score >= 0 AND arbitrage_score <= 100));

-- Create index for performance (filtering queries)
CREATE INDEX IF NOT EXISTS idx_properties_arbitrage_score 
ON properties(arbitrage_score);

-- Verify the column was added
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'properties' 
  AND column_name = 'arbitrage_score';

-- Expected output:
-- column_name      | data_type | is_nullable
-- arbitrage_score  | integer   | YES
