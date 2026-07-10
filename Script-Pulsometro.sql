-- ============================================================================
--  Script-Pulsometro.sql
--  Integración de un nuevo sensor: PULSÓMETRO
--
--  El pulsómetro registra en cada lectura tres valores correlacionados:
--    * Frecuencia_Cardiaca   -> pulsaciones por minuto (ppm)
--    * Presion_Sistolica     -> presión máxima al latir el corazón, en mm Hg
--    * Presion_Diastolica    -> presión entre latido y latido, en mm Hg
CREATE TABLE IF NOT EXISTS Pulsometro (
    Id_Pulsometro       INT           NOT NULL AUTO_INCREMENT,
    Frecuencia_Cardiaca INT           NOT NULL,                    -- ppm (pulsaciones por minuto)
    Presion_Sistolica   INT           NOT NULL,                    -- mm Hg (presión máxima)
    Presion_Diastolica  INT           NOT NULL,                    -- mm Hg (presión mínima)
    Fecha               DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Activo              TINYINT(1)    NOT NULL DEFAULT 1,
    PRIMARY KEY (Id_Pulsometro),
    -- Índice para acelerar las consultas por fecha (últimas lecturas).
    KEY idx_pulsometro_fecha (Fecha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Registro del tipo de sensor en el catálogo `Tipos`, por consistencia con el
-- resto del sistema (no crea dependencia: la tabla Pulsometro es autocontenida).
INSERT INTO Tipos (Nombre, Activo)
SELECT 'Pulsómetro', 1
WHERE NOT EXISTS (SELECT 1 FROM Tipos WHERE Nombre = 'Pulsómetro');
