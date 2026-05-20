
--  SCRIPT COMPLETO - Sistema de control de barreras y sensores
--  Smart Residencial — Sistema de Peaje Automatizado



-- SECCIÓN 0: ELIMINAR Y CREAR BASE DE DATOS


DROP DATABASE IF EXISTS `smart_residencial`;
CREATE DATABASE `smart_residencial`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_spanish_ci;

USE `smart_residencial`;


-- SECCIÓN 1: CREACIÓN DE TABLAS


-- Tabla de Roles
DROP TABLE IF EXISTS `Roles`;
CREATE TABLE `Roles` (
  `Id_Rol`   INT          NOT NULL AUTO_INCREMENT,
  `Nombre`   VARCHAR(100) NOT NULL,
  `Activo`   TINYINT(1)   NOT NULL DEFAULT 1,
  PRIMARY KEY (`Id_Rol`)
);

-- Tabla de Usuarios
DROP TABLE IF EXISTS `Usuarios`;
CREATE TABLE `Usuarios` (
  `Id_User`    INT          NOT NULL AUTO_INCREMENT,
  `Nombre`     VARCHAR(100) NOT NULL,
  `Email`      VARCHAR(150) NOT NULL UNIQUE,
  `Contrasena` VARCHAR(255) NOT NULL,
  `Foto`       MEDIUMBLOB   DEFAULT NULL,
  `Id_Rol`     INT          NOT NULL,
  `Activo`     TINYINT(1)   NOT NULL DEFAULT 1,
  `Fecha_Alta` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Id_User`)
);

-- Tabla de Tipos de sensor
-- Define la naturaleza de cada sensor y ayuda a interpretar sus lecturas.
DROP TABLE IF EXISTS `Tipos`;
CREATE TABLE `Tipos` (
  `Id_Tipos`   INT          NOT NULL AUTO_INCREMENT,
  `Nombre`     VARCHAR(100) NOT NULL,
  `Unidad`     VARCHAR(30)  DEFAULT NULL,
  `Tipo_Dato`  ENUM('NUMERICO','ALFANUMERICO','MIXTO') NOT NULL DEFAULT 'MIXTO',
  `Descripcion` VARCHAR(255) DEFAULT NULL,
  `Activo`     TINYINT(1)   NOT NULL DEFAULT 1,
  PRIMARY KEY (`Id_Tipos`),
  UNIQUE KEY `uk_Tipos_Nombre` (`Nombre`)
);

-- Tabla de Sensores
-- Cada fila es una lectura histórica.
-- Se adapta al método Arduino databaseInsert(id_tipo, valorNumerico, valorAlfanumerico).
-- Valor guarda la parte numérica y Valor_Alfanumerico guarda el estado, etiqueta o texto asociado.
DROP TABLE IF EXISTS `Sensores`;
CREATE TABLE `Sensores` (
  `Id_Sensor`           INT          NOT NULL AUTO_INCREMENT,
  `Valor`               FLOAT        DEFAULT NULL,
  `Valor_Alfanumerico`  VARCHAR(100) DEFAULT NULL,
  `Fecha`               DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Id_Tipo`             INT          NOT NULL,
  `Origen`              VARCHAR(50)  NOT NULL DEFAULT 'ESP32',
  `Activo`              TINYINT(1)   NOT NULL DEFAULT 1,
  PRIMARY KEY (`Id_Sensor`),
  KEY `idx_Sensores_Tipo_Fecha` (`Id_Tipo`, `Fecha`),
  KEY `idx_Sensores_Fecha` (`Fecha`),
  CONSTRAINT `chk_Sensores_Valor_NoVacio`
    CHECK (`Valor` IS NOT NULL OR `Valor_Alfanumerico` IS NOT NULL)
);

-- Tabla de Notificaciones generadas por sensores
-- Mantiene el dato numérico y permite guardar también el estado alfanumérico que provocó la alerta.
DROP TABLE IF EXISTS `Notificaciones`;
CREATE TABLE `Notificaciones` (
  `Id`                  INT          NOT NULL AUTO_INCREMENT,
  `Fecha`               DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Dato`                FLOAT        DEFAULT NULL,
  `Dato_Alfanumerico`   VARCHAR(100) DEFAULT NULL,
  `Titulo`              VARCHAR(100) NOT NULL,
  `Id_Sensor`           INT          NOT NULL,
  `Activo`              TINYINT(1)   NOT NULL DEFAULT 1,
  PRIMARY KEY (`Id`),
  KEY `idx_Notificaciones_Fecha` (`Fecha`),
  KEY `idx_Notificaciones_Sensor` (`Id_Sensor`)
);

-- Tabla de Barreras
DROP TABLE IF EXISTS `Barreras`;
CREATE TABLE `Barreras` (
  `id_Barrera` INT         NOT NULL AUTO_INCREMENT,
  `Estado`     ENUM('abierta','cerrada','error') NOT NULL DEFAULT 'cerrada',
  `Control`    ENUM('automatico','manual')       NOT NULL DEFAULT 'automatico',
  `Ubicacion`  VARCHAR(150) NOT NULL,
  `Activo`     TINYINT(1)  NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_Barrera`)
);

-- Historial de cambios en barreras
-- Cada apertura/cierre genera un INSERT nuevo (historial completo)
DROP TABLE IF EXISTS `Historial_Barreras`;
CREATE TABLE `Historial_Barreras` (
  `id_Historial` INT          NOT NULL AUTO_INCREMENT,
  `Fecha`        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Control`      VARCHAR(100) NOT NULL,
  `Estado`       ENUM('abierta','cerrada','error') NOT NULL DEFAULT 'cerrada',
  `id_Barrera`   INT          NOT NULL,
  PRIMARY KEY (`id_Historial`)
);

-- Configuración de luminosidad
DROP TABLE IF EXISTS `Conf_Luminosidad`;
CREATE TABLE `Conf_Luminosidad` (
  `id`             INT        NOT NULL AUTO_INCREMENT,
  `Control`        ENUM('encendido','apagado','automatico') NOT NULL DEFAULT 'automatico',
  `Umbral`         FLOAT      NOT NULL DEFAULT 0,
  `Hora_Inicial`   TINYINT    NOT NULL DEFAULT 0,
  `Hora_Final`     TINYINT    NOT NULL DEFAULT 23,
  `Minuto_Inicial` TINYINT    NOT NULL DEFAULT 0,
  `Minuto_Final`   TINYINT    NOT NULL DEFAULT 59,
  `Activo`         TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`)
);

-- Configuración de alertas por tipo de sensor
DROP TABLE IF EXISTS `Conf_Alertas`;
CREATE TABLE `Conf_Alertas` (
  `id`      INT        NOT NULL AUTO_INCREMENT,
  `Valor`   FLOAT      NOT NULL,
  `Id_Tipo` INT        NOT NULL,
  `Activo`  TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`)
);

-- Conversaciones del chat
DROP TABLE IF EXISTS `Conversacion`;
CREATE TABLE `Conversacion` (
  `Id_Conversacion` INT          NOT NULL AUTO_INCREMENT,
  `Titulo`          VARCHAR(150) NOT NULL DEFAULT 'Sin título',
  `Fecha`           DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Activo`          TINYINT(1)   NOT NULL DEFAULT 1,
  PRIMARY KEY (`Id_Conversacion`)
);

-- Participantes de una conversación
DROP TABLE IF EXISTS `Participantes`;
CREATE TABLE `Participantes` (
  `Id_Participantes` INT      NOT NULL AUTO_INCREMENT,
  `Id_User`          INT      NOT NULL,
  `Id_Conversacion`  INT      NOT NULL,
  `Fecha_Union`      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Activo`           TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`Id_Participantes`)
);

-- Mensajes del chat
DROP TABLE IF EXISTS `Mensajes`;
CREATE TABLE `Mensajes` (
  `Id`              INT        NOT NULL AUTO_INCREMENT,
  `Id_User`         INT        NOT NULL,
  `Descripcion`     TEXT       NOT NULL,
  `Adjunto`         MEDIUMBLOB DEFAULT NULL,
  `Fecha`           DATETIME   NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Id_Conversacion` INT        NOT NULL,
  `Activo`          TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`Id`)
);

-- ============================================================
-- SECCIÓN 2: CLAVES FORÁNEAS
-- ============================================================

ALTER TABLE `Usuarios`
  ADD CONSTRAINT `fk_Usuarios_Roles`
    FOREIGN KEY (`Id_Rol`) REFERENCES `Roles` (`Id_Rol`)
    ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE `Sensores`
  ADD CONSTRAINT `fk_Sensores_Tipos`
    FOREIGN KEY (`Id_Tipo`) REFERENCES `Tipos` (`Id_Tipos`)
    ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE `Notificaciones`
  ADD CONSTRAINT `fk_Notificaciones_Sensores`
    FOREIGN KEY (`Id_Sensor`) REFERENCES `Sensores` (`Id_Sensor`)
    ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `Historial_Barreras`
  ADD CONSTRAINT `fk_Historial_Barreras`
    FOREIGN KEY (`id_Barrera`) REFERENCES `Barreras` (`id_Barrera`)
    ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `Conf_Alertas`
  ADD CONSTRAINT `fk_Conf_Alertas_Tipos`
    FOREIGN KEY (`Id_Tipo`) REFERENCES `Tipos` (`Id_Tipos`)
    ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE `Participantes`
  ADD CONSTRAINT `fk_Participantes_Usuarios`
    FOREIGN KEY (`Id_User`) REFERENCES `Usuarios` (`Id_User`)
    ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `Participantes`
  ADD CONSTRAINT `fk_Participantes_Conversacion`
    FOREIGN KEY (`Id_Conversacion`) REFERENCES `Conversacion` (`Id_Conversacion`)
    ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `Mensajes`
  ADD CONSTRAINT `fk_Mensajes_Usuarios`
    FOREIGN KEY (`Id_User`) REFERENCES `Usuarios` (`Id_User`)
    ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `Mensajes`
  ADD CONSTRAINT `fk_Mensajes_Conversacion`
    FOREIGN KEY (`Id_Conversacion`) REFERENCES `Conversacion` (`Id_Conversacion`)
    ON DELETE CASCADE ON UPDATE CASCADE;

-- Vista útil para consultar lecturas con su tipo, unidad y estado textual
DROP VIEW IF EXISTS `Vista_Lecturas_Sensores`;
CREATE VIEW `Vista_Lecturas_Sensores` AS
SELECT
  s.`Id_Sensor`,
  t.`Nombre` AS `Tipo`,
  t.`Unidad`,
  s.`Valor`,
  s.`Valor_Alfanumerico`,
  s.`Fecha`,
  s.`Origen`,
  s.`Activo`
FROM `Sensores` s
JOIN `Tipos` t ON s.`Id_Tipo` = t.`Id_Tipos`;


--  3: DATOS DE PRUEBA


-- Roles
INSERT INTO `Roles` (`Id_Rol`, `Nombre`, `Activo`) VALUES
  (1, 'Administrador', 1),
  (2, 'Operador',      1),
  (3, 'Invitado',      1);

-- Usuarios (contraseña hasheada SHA2-256)
INSERT INTO `Usuarios` (`Id_User`, `Nombre`, `Email`, `Contrasena`, `Id_Rol`, `Activo`, `Fecha_Alta`) VALUES
  (1, 'Ana García',    'ana@sistema.com',    SHA2('password123', 256), 1, 1, '2024-01-10 09:00:00'),
  (2, 'Luis Martínez', 'luis@sistema.com',   SHA2('operador456', 256), 2, 1, '2024-02-15 10:30:00'),
  (3, 'Carlos Ruiz',   'carlos@sistema.com', SHA2('invitado789', 256), 3, 0, '2024-03-01 08:00:00');

-- Tipos de sensor
INSERT INTO `Tipos` (`Id_Tipos`, `Nombre`, `Unidad`, `Tipo_Dato`, `Descripcion`, `Activo`) VALUES
  (1, 'Temperatura', 'ºC',      'MIXTO', 'Temperatura ambiental medida por DHT11', 1),
  (2, 'Humedad',     '%',       'MIXTO', 'Humedad relativa medida por DHT11', 1),
  (3, 'Luminosidad', '0-1000',  'MIXTO', 'Nivel de luz calculado desde LDR', 1),
  (4, 'Gas',         'ADC',     'MIXTO', 'Lectura analógica del sensor de gas', 1),
  (5, 'Viento',      'km/h',    'MIXTO', 'Velocidad estimada del viento', 1),
  (6, 'Flujo de Agua','L/min',  'MIXTO', 'Caudal o flujo de agua del sistema', 1),
  (7, 'Potencia',    'W',       'MIXTO', 'Potencia eléctrica estimada', 1);

-- Sensores — historial de lecturas de ejemplo
-- Cada fila es una lectura independiente, nunca se actualiza.
-- Valor guarda el número y Valor_Alfanumerico guarda el estado o etiqueta descriptiva.
INSERT INTO `Sensores` (`Id_Sensor`, `Valor`, `Valor_Alfanumerico`, `Fecha`, `Id_Tipo`, `Activo`) VALUES
  -- Temperatura
  (1,  22.5, 'TEMPERATURA_NORMAL', '2024-06-01 08:00:00', 1, 1),
  (2,  23.1, 'TEMPERATURA_NORMAL', '2024-06-01 08:10:00', 1, 1),
  (3,  24.8, 'TEMPERATURA_NORMAL', '2024-06-01 08:20:00', 1, 1),
  (4,  36.2, 'TEMPERATURA_ALTA',   '2024-06-01 08:30:00', 1, 1),
  -- Humedad
  (5,  55.0, 'HUMEDAD_NORMAL',     '2024-06-01 08:00:00', 2, 1),
  (6,  60.5, 'HUMEDAD_NORMAL',     '2024-06-01 08:10:00', 2, 1),
  (7,  82.3, 'HUMEDAD_CRITICA',    '2024-06-01 08:20:00', 2, 1),
  -- Luminosidad (escala 0-1000)
  (8,  800.0, 'LUCES_OFF',         '2024-06-01 08:00:00', 3, 1),
  (9,  650.0, 'LUCES_OFF',         '2024-06-01 08:10:00', 3, 1),
  (10,  80.0, 'LUCES_ON',          '2024-06-01 08:20:00', 3, 1),
  -- Gas (valor ADC 0-4095)
  (11, 900.0, 'GAS_NORMAL',        '2024-06-01 08:00:00', 4, 1),
  (12,1200.0, 'GAS_NORMAL',        '2024-06-01 08:10:00', 4, 1),
  (13,2300.0, 'GAS_ALTO',          '2024-06-01 08:20:00', 4, 1),
  -- Viento
  (14,  12.0, 'VIENTO_NORMAL',     '2024-06-01 08:00:00', 5, 1),
  (15,  58.0, 'VIENTO_ALTO',       '2024-06-01 08:20:00', 5, 1);

-- Barreras (4 barreras del peaje)
INSERT INTO `Barreras` (`id_Barrera`, `Estado`, `Control`, `Ubicacion`, `Activo`) VALUES
  (1, 'cerrada', 'automatico', 'Norte-Entrada', 1),
  (2, 'cerrada', 'automatico', 'Norte-Salida',  1),
  (3, 'cerrada', 'automatico', 'Sur-Entrada',   1),
  (4, 'cerrada', 'automatico', 'Sur-Salida',    1);

-- Historial de barreras — cada apertura/cierre es un registro nuevo
INSERT INTO `Historial_Barreras` (`id_Historial`, `Fecha`, `Control`, `Estado`, `id_Barrera`) VALUES
  (1,  '2024-06-01 08:05:00', 'Apertura automatica: vehiculo detectado en Norte-Entrada', 'abierta',  1),
  (2,  '2024-06-01 08:05:03', 'Cierre automatico tras 3 segundos en Norte-Entrada',       'cerrada',  1),
  (3,  '2024-06-01 08:12:00', 'Apertura automatica: vehiculo detectado en Norte-Salida',  'abierta',  2),
  (4,  '2024-06-01 08:12:03', 'Cierre automatico tras 3 segundos en Norte-Salida',        'cerrada',  2),
  (5,  '2024-06-01 08:18:00', 'Apertura automatica: vehiculo detectado en Sur-Entrada',   'abierta',  3),
  (6,  '2024-06-01 08:18:03', 'Cierre automatico tras 3 segundos en Sur-Entrada',         'cerrada',  3),
  (7,  '2024-06-01 08:25:00', 'Apertura automatica: vehiculo detectado en Sur-Salida',    'abierta',  4),
  (8,  '2024-06-01 08:25:03', 'Cierre automatico tras 3 segundos en Sur-Salida',          'cerrada',  4);

-- Notificaciones generadas al superar umbrales
INSERT INTO `Notificaciones` (`Id`, `Fecha`, `Dato`, `Dato_Alfanumerico`, `Titulo`, `Id_Sensor`, `Activo`) VALUES
  (1, '2024-06-01 08:30:00', 36.2, 'TEMPERATURA_ALTA', 'Temperatura alta',       4,  1),
  (2, '2024-06-01 08:20:00', 82.3, 'HUMEDAD_CRITICA',  'Humedad critica',        7,  1),
  (3, '2024-06-01 08:20:00', 80.0, 'LUCES_ON',         'Luminosidad baja',       10, 1),
  (4, '2024-06-01 08:20:00',2300,  'GAS_ALTO',         'Gas elevado detectado',  13, 1),
  (5, '2024-06-01 08:20:00', 58.0, 'VIENTO_ALTO',      'Viento peligroso',       15, 1);

-- Configuración de luminosidad
-- Umbral: valor ADC por debajo del cual se encienden los LEDs (escala 0-4095)
INSERT INTO `Conf_Luminosidad` (`id`, `Control`, `Umbral`, `Hora_Inicial`, `Hora_Final`, `Minuto_Inicial`, `Minuto_Final`, `Activo`) VALUES
  (1, 'automatico', 1500, 7, 22, 0, 0, 1),  -- modo auto: usa umbral ADC
  (2, 'encendido',     0, 0,  6, 0, 59, 1); -- forzado ON de 00:00 a 06:59

-- Configuración de alertas por tipo
INSERT INTO `Conf_Alertas` (`id`, `Valor`, `Id_Tipo`, `Activo`) VALUES
  (1,   35.0, 1, 1),   -- Temperatura °C: alerta si supera 35
  (2,   80.0, 2, 1),   -- Humedad %: alerta si supera 80
  (3,  100.0, 3, 1),   -- Luminosidad (0-1000): alerta si baja de 100
  (4, 2000.0, 4, 1),   -- Gas (ADC 0-4095): alerta si supera 2000
  (5,   50.0, 5, 1);   -- Viento km/h: alerta si supera 50

-- Conversaciones del chat
INSERT INTO `Conversacion` (`Id_Conversacion`, `Titulo`, `Fecha`, `Activo`) VALUES
  (1, 'Incidencia barrera Norte-Entrada', '2024-06-01 08:35:00', 1),
  (2, 'Revisión sensor de gas',           '2024-06-01 08:40:00', 1),
  (3, 'Chat eliminado',                   '2024-05-01 08:00:00', 0);

-- Participantes
INSERT INTO `Participantes` (`Id_Participantes`, `Id_User`, `Id_Conversacion`, `Fecha_Union`, `Activo`) VALUES
  (1, 1, 1, '2024-06-01 08:35:00', 1),
  (2, 2, 1, '2024-06-01 08:36:00', 1),
  (3, 1, 2, '2024-06-01 08:40:00', 1),
  (4, 2, 2, '2024-06-01 08:41:00', 1);

-- Mensajes
INSERT INTO `Mensajes` (`Id`, `Id_User`, `Descripcion`, `Fecha`, `Id_Conversacion`, `Activo`) VALUES
  (1, 1, 'La barrera Norte-Entrada ha abierto varias veces seguidas, revisar sensor.', '2024-06-01 08:36:00', 1, 1),
  (2, 2, 'Confirmado, voy a revisar el HC-SR04.',                                      '2024-06-01 08:38:00', 1, 1),
  (3, 1, 'El sensor de gas supera el umbral, posible fallo o gas real.',               '2024-06-01 08:41:00', 2, 1),
  (4, 2, 'Revisado, era un pico puntual. Niveles vuelven a la normalidad.',            '2024-06-01 08:45:00', 2, 1);


--  4: CONSULTAS DE EJEMPLO


-- Login
SELECT `Id_User`, `Nombre`, `Id_Rol`
  FROM `Usuarios`
 WHERE `Email` = 'ana@sistema.com'
   AND `Contrasena` = SHA2('password123', 256)
   AND `Activo` = 1;

-- Historial de lecturas de temperatura ordenado cronológicamente
SELECT s.`Id_Sensor`, s.`Valor`, s.`Valor_Alfanumerico`, s.`Fecha`
  FROM `Sensores` s
  JOIN `Tipos` t ON s.`Id_Tipo` = t.`Id_Tipos`
 WHERE t.`Nombre` = 'Temperatura'
   AND s.`Activo` = 1
 ORDER BY s.`Fecha` ASC;

-- Última lectura de cada tipo de sensor
SELECT t.`Nombre` AS Tipo, s.`Valor`, s.`Valor_Alfanumerico`, s.`Fecha`
  FROM `Sensores` s
  JOIN `Tipos` t ON s.`Id_Tipo` = t.`Id_Tipos`
 WHERE s.`Activo` = 1
   AND s.`Fecha` = (
     SELECT MAX(s2.`Fecha`)
       FROM `Sensores` s2
      WHERE s2.`Id_Tipo` = s.`Id_Tipo`
        AND s2.`Activo` = 1
   )
 ORDER BY t.`Nombre`;

-- Historial completo de una barrera
SELECT h.`id_Historial`, h.`Fecha`, h.`Estado`, h.`Control`
  FROM `Historial_Barreras` h
 WHERE h.`id_Barrera` = 1
 ORDER BY h.`Fecha` DESC;

-- Notificaciones activas con el tipo de sensor
SELECT n.`Id`, n.`Titulo`, n.`Dato`, n.`Dato_Alfanumerico`, n.`Fecha`, t.`Nombre` AS Tipo
  FROM `Notificaciones` n
  JOIN `Sensores` s ON n.`Id_Sensor` = s.`Id_Sensor`
  JOIN `Tipos`   t ON s.`Id_Tipo`   = t.`Id_Tipos`
 WHERE n.`Activo` = 1
 ORDER BY n.`Fecha` DESC;

-- Mensajes de una conversación con nombre de usuario
SELECT m.`Id`, u.`Nombre`, m.`Descripcion`, m.`Fecha`
  FROM `Mensajes` m
  JOIN `Usuarios` u ON m.`Id_User` = u.`Id_User`
 WHERE m.`Id_Conversacion` = 1
   AND m.`Activo` = 1
 ORDER BY m.`Fecha` ASC;

-- Usuarios activos con su rol
SELECT u.`Id_User`, u.`Nombre`, u.`Email`, r.`Nombre` AS Rol
  FROM `Usuarios` u
  JOIN `Roles` r ON u.`Id_Rol` = r.`Id_Rol`
 WHERE u.`Activo` = 1
 ORDER BY r.`Nombre`, u.`Nombre`;


-- SECCIÓN 5: INSERTS Y UPDATES DE EJEMPLO


-- Nueva lectura de sensor desde Arduino databaseInsert(id_tipo, valorNumerico, valorAlfanumerico)
INSERT INTO `Sensores` (`Valor`, `Valor_Alfanumerico`, `Fecha`, `Id_Tipo`, `Activo`)
VALUES (25.3, 'TEMPERATURA_DHT11', NOW(), 1, 1);

-- Nueva apertura de barrera (INSERT en historial + UPDATE estado actual)
INSERT INTO `Historial_Barreras` (`Fecha`, `Control`, `Estado`, `id_Barrera`)
VALUES (NOW(), 'Apertura automatica: vehiculo detectado en Norte-Entrada', 'abierta', 1);

UPDATE `Barreras`
   SET `Estado` = 'abierta'
 WHERE `id_Barrera` = 1;

-- Nueva notificación de alerta asociada a una lectura mixta
INSERT INTO `Notificaciones` (`Fecha`, `Dato`, `Dato_Alfanumerico`, `Titulo`, `Id_Sensor`, `Activo`)
VALUES (NOW(), 36.5, 'TEMPERATURA_ALTA', 'Temperatura alta', 14, 1);

-- Nuevo mensaje en conversación
INSERT INTO `Mensajes` (`Id_User`, `Descripcion`, `Fecha`, `Id_Conversacion`, `Activo`)
VALUES (2, 'Sensor de temperatura revisado, funcionando correctamente.', NOW(), 2, 1);

-- Cambiar contraseña de usuario
UPDATE `Usuarios`
   SET `Contrasena` = SHA2('nuevaPassword!99', 256)
 WHERE `Id_User` = 2;

-- Cambiar configuración de luminosidad
UPDATE `Conf_Luminosidad`
   SET `Control` = 'encendido'
 WHERE `id` = 1 AND `Activo` = 1;

-- Cambiar umbral de alerta de temperatura
UPDATE `Conf_Alertas`
   SET `Valor` = 38.0
 WHERE `Id_Tipo` = 1 AND `Activo` = 1;

-- ============================================================
-- SECCIÓN 6: BAJA LÓGICA
-- ============================================================

-- Dar de baja un sensor (no se elimina, deja de mostrarse)
UPDATE `Sensores` SET `Activo` = 0 WHERE `Id_Sensor` = 1;

-- Dar de baja un usuario
UPDATE `Usuarios` SET `Activo` = 0 WHERE `Id_User` = 3;

-- Dar de baja una conversación
UPDATE `Conversacion` SET `Activo` = 0 WHERE `Id_Conversacion` = 3;

-- Dar de baja un participante
UPDATE `Participantes` SET `Activo` = 0 WHERE `Id_Participantes` = 4;

-- Dar de baja una notificación (marcarla como leída/resuelta)
UPDATE `Notificaciones` SET `Activo` = 0 WHERE `Id` = 1;
