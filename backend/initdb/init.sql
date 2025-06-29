-- Ajouter la colonne condition_value si elle n'existe pas déjà
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'actuators' AND column_name = 'condition_value'
    ) THEN
        ALTER TABLE actuators ADD COLUMN condition_value FLOAT NOT NULL DEFAULT 0.0;
        ALTER TABLE actuators ALTER COLUMN condition_value DROP DEFAULT;
    END IF;
END $$;

-- Supprimer la colonne low si elle existe
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'actuators' AND column_name = 'low'
    ) THEN
        ALTER TABLE actuators DROP COLUMN low;
    END IF;
END $$;

-- Supprimer la colonne high si elle existe
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'actuators' AND column_name = 'high'
    ) THEN
        ALTER TABLE actuators DROP COLUMN high;
    END IF;
END $$;