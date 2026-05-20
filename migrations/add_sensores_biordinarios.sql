-- Migración: sensor biordinario (dato numérico + alfanumérico)
-- Ejecutar en smart_residencial si la BD ya existe.

USE `smart_residencial`;

CREATE TABLE IF NOT EXISTS `Sensores_Biordinarios` (
  `Id_Registro`        INT          NOT NULL AUTO_INCREMENT,
  `ValorNumerico`      INT          NOT NULL,
  `ValorAlfanumerico`  CHAR(1)      NOT NULL,
  `Fecha`              DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Activo`             TINYINT(1)   NOT NULL DEFAULT 1,
  PRIMARY KEY (`Id_Registro`)
);
