USE `smart_residencial`;

CREATE TABLE IF NOT EXISTS `Pulsometro` (
  `Id_Pulsometro` INT NOT NULL AUTO_INCREMENT,
  `Frecuencia_Cardiaca` INT NOT NULL,
  `Presion_Sistolica` INT NOT NULL,
  `Presion_Diastolica` INT NOT NULL,
  `Fecha` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Activo` TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`Id_Pulsometro`)
);

INSERT INTO `Pulsometro`
  (`Frecuencia_Cardiaca`, `Presion_Sistolica`, `Presion_Diastolica`, `Fecha`, `Activo`)
VALUES (72, 120, 80, NOW(), 1);

SELECT `Id_Pulsometro`, `Frecuencia_Cardiaca`, `Presion_Sistolica`,
       `Presion_Diastolica`, `Fecha`
FROM `Pulsometro`
WHERE `Activo` = 1
ORDER BY `Fecha` DESC;

UPDATE `Pulsometro`
SET `Frecuencia_Cardiaca` = 74,
    `Presion_Sistolica` = 121,
    `Presion_Diastolica` = 81
WHERE `Id_Pulsometro` = 1;
