-- ============================================================
-- SECCIÓN 1: CREACIÓN DE TABLAS
-- ============================================================

-- Tabla de Roles (sin dependencias, se crea primero)
CREATE TABLE `Roles` (
  `Id_Rol`   INT          NOT NULL AUTO_INCREMENT,
  `Nombre`   VARCHAR(100) NOT NULL,
  `Activo`   TINYINT(1)   NOT NULL DEFAULT 1,   -- baja lógica
  PRIMARY KEY (`Id_Rol`)
);

-- Tabla de Usuarios con contraseña encriptada (SHA2/bcrypt en la app, aquí VARCHAR(255))
-- La columna Contrasena almacena el hash, nunca texto plano
CREATE TABLE `Usuarios` (
  `Id_User`    INT          NOT NULL AUTO_INCREMENT,
  `Nombre`     VARCHAR(100) NOT NULL,
  `Email`      VARCHAR(150) NOT NULL UNIQUE,
  `Contrasena` VARCHAR(255) NOT NULL,            -- hash SHA2-256 o bcrypt
  `Foto`       MEDIUMBLOB   DEFAULT NULL,        -- dato binario: foto de perfil
  `Id_Rol`     INT          NOT NULL,
  `Activo`     TINYINT(1)   NOT NULL DEFAULT 1,  -- baja lógica
  `Fecha_Alta` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Id_User`)
);

-- Tabla de Tipos de sensor
CREATE TABLE `Tipos` (
  `Id_Tipos` INT          NOT NULL AUTO_INCREMENT,
  `Nombre`   VARCHAR(100) NOT NULL,
  `Activo`   TINYINT(1)   NOT NULL DEFAULT 1,
  PRIMARY KEY (`Id_Tipos`)
);

-- Tabla de Sensores
CREATE TABLE `Sensores` (
  `Id_Sensor` INT      NOT NULL AUTO_INCREMENT,
  `Valor`     FLOAT    NOT NULL DEFAULT 0,
  `Fecha`     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Id_Tipo`   INT      NOT NULL,
  `Activo`    TINYINT(1) NOT NULL DEFAULT 1,     -- baja lógica
  PRIMARY KEY (`Id_Sensor`)
);

-- Sensor biordinario: valor numérico + carácter alfanumérico en cada lectura
CREATE TABLE `Sensores_Biordinarios` (
  `Id_Registro`        INT          NOT NULL AUTO_INCREMENT,
  `ValorNumerico`      INT          NOT NULL,
  `ValorAlfanumerico`  CHAR(1)      NOT NULL,
  `Fecha`              DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Activo`             TINYINT(1)   NOT NULL DEFAULT 1,
  PRIMARY KEY (`Id_Registro`)
);

-- Tabla de Notificaciones generadas por sensores
CREATE TABLE `Notificaciones` (
  `Id`       INT          NOT NULL AUTO_INCREMENT,
  `Fecha`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Dato`     FLOAT        NOT NULL DEFAULT 0,
  `Titulo`   VARCHAR(100) NOT NULL,
  `Id_Sensor` INT         NOT NULL,
  `Activo`   TINYINT(1)   NOT NULL DEFAULT 1,    -- baja lógica
  PRIMARY KEY (`Id`)
);

-- Tabla de Barreras (ENUM con valores válidos)
CREATE TABLE `Barreras` (
  `id_Barrera` INT         NOT NULL AUTO_INCREMENT,
  `Estado`     ENUM('abierta','cerrada','error') NOT NULL DEFAULT 'cerrada',
  `Control`    ENUM('automatico','manual')       NOT NULL DEFAULT 'automatico',
  `Ubicacion`  VARCHAR(150) NOT NULL,
  `Activo`     TINYINT(1)  NOT NULL DEFAULT 1,   -- baja lógica
  PRIMARY KEY (`id_Barrera`)
);

-- Historial de cambios en barreras (registra evento con fecha)
CREATE TABLE `Historial_Barreras` (
  `id_Historial` INT         NOT NULL AUTO_INCREMENT,
  `Fecha`        DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Control`      VARCHAR(100) NOT NULL,
  `id_Barrera`   INT         NOT NULL,
  PRIMARY KEY (`id_Historial`)
);

-- Configuración de luminosidad
CREATE TABLE `Conf_Luminosidad` (
  `id`             INT        NOT NULL AUTO_INCREMENT,
  `Control`        ENUM('encendido','apagado','automatico') NOT NULL DEFAULT 'automatico',
  `Umbral`         FLOAT      NOT NULL DEFAULT 0,
  `Hora_Inicial`   TINYINT    NOT NULL DEFAULT 0,   -- 0-23
  `Hora_Final`     TINYINT    NOT NULL DEFAULT 23,
  `Minuto_Inicial` TINYINT    NOT NULL DEFAULT 0,   -- 0-59
  `Minuto_Final`   TINYINT    NOT NULL DEFAULT 59,
  `Activo`         TINYINT(1) NOT NULL DEFAULT 1,   -- baja lógica
  PRIMARY KEY (`id`)
);

-- Configuración de alertas (PK simple, Valor no forma parte de la PK)
CREATE TABLE `Conf_Alertas` (
  `id`       INT   NOT NULL AUTO_INCREMENT,
  `Valor`    FLOAT NOT NULL,
  `Id_Tipo`  INT   NOT NULL,
  `Activo`   TINYINT(1) NOT NULL DEFAULT 1,         -- baja lógica
  PRIMARY KEY (`id`)
);

-- Conversaciones
INSERT INTO `Conversacion` (`Id_Conversacion`, `Titulo`, `Fecha`, `Activo`) VALUES
  (1, 'Incidencia barrera 3',  '2024-06-01 10:35:00', 1),
  (2, 'Revisión sensores',     '2024-06-02 09:00:00', 1),
  (3, 'Chat eliminado',        '2024-05-01 08:00:00', 0),
  (4, 'Relación Operador 2', '2024-06-03 10:00:00', 1),
  (5, 'Relación Operador 8', '2024-06-03 10:00:00', 1),
  (6, 'Relación Operador 9', '2024-06-03 10:00:00', 1),
  (7, 'Relación Operador 10', '2024-06-03 10:00:00', 1),
  (8, 'Relación Operador 11', '2024-06-03 10:00:00', 1),
  (9, 'Relación Operador 12', '2024-06-03 10:00:00', 1),
  (10, 'Relación Operador 13', '2024-06-03 10:00:00', 1),
  (11, 'Relación Operador 14', '2024-06-03 10:00:00', 1),
  (12, 'Relación Operador 15', '2024-06-03 10:00:00', 1);

-- Participantes de una conversación (tabla relación con fecha de unión)
CREATE TABLE `Participantes` (
  `Id_Participantes` INT      NOT NULL AUTO_INCREMENT,
  `Id_User`          INT      NOT NULL,
  `Id_Conversacion`  INT      NOT NULL,
  `Fecha_Union`      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- fecha en relación
  `Activo`           TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`Id_Participantes`)
);

-- Mensajes
INSERT INTO `Mensajes` (`Id`, `Id_User`, `Descripcion`, `Fecha`, `Id_Conversacion`, `Activo`) VALUES
  (1, 1, 'La barrera 3 sigue dando error, revisar sensor.',   '2024-06-01 10:36:00', 1, 1),
  (2, 2, 'Confirmado, voy a revisarlo ahora mismo.',          '2024-06-01 10:40:00', 1, 1),
  (3, 1, 'Los sensores de humedad están por encima del umbral.','2024-06-02 09:01:00', 2, 1),
  (4, 2, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 4, 1),
  (5, 8, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 5, 1),
  (6, 9, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 6, 1),
  (7, 10, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 7, 1),
  (8, 11, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 8, 1),
  (9, 12, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 9, 1),
  (10, 13, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 10, 1),
  (11, 14, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 11, 1),
  (12, 15, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 12, 1);


-- ============================================================
-- SECCIÓN 2: CLAVES FORÁNEAS CON CRITERIO DE BORRADO/ACTUALIZACIÓN
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


-- ============================================================
-- SECCIÓN 3: DATOS DE PRUEBA REPRESENTATIVOS
-- ============================================================

-- Roles
INSERT INTO `Roles` (`Id_Rol`, `Nombre`, `Activo`) VALUES
  (1, 'Administrador', 1),
  (2, 'Operador',      1),
  (3, 'Invitado',      1);

-- Usuarios (contraseña hasheada con SHA2-256: 'password123' → hash)
INSERT INTO `Usuarios` (`Id_User`, `Nombre`, `Email`, `Contrasena`, `Id_Rol`, `Activo`, `Fecha_Alta`) VALUES
  (1, 'Ana García',   'ana@sistema.com',   SHA2('password123', 256), 1, 1, '2024-01-10 09:00:00'),
  (4, 'Admin Dos',    'admin2@sistema.com',SHA2('password123', 256), 1, 1, '2024-01-11 09:00:00'),
  (5, 'Admin Tres',   'admin3@sistema.com',SHA2('password123', 256), 1, 1, '2024-01-12 09:00:00'),
  (6, 'Admin Cuatro', 'admin4@sistema.com',SHA2('password123', 256), 1, 1, '2024-01-13 09:00:00'),
  (7, 'Admin Cinco',  'admin5@sistema.com',SHA2('password123', 256), 1, 1, '2024-01-14 09:00:00'),
  (2, 'Luis Martínez','luis@sistema.com',  SHA2('operador456', 256), 2, 1, '2024-02-15 10:30:00'),
  (8, 'Operador Dos', 'op2@sistema.com',   SHA2('password123', 256), 2, 1, '2024-02-16 10:30:00'),
  (9, 'Operador Tres','op3@sistema.com',   SHA2('password123', 256), 2, 1, '2024-02-17 10:30:00'),
  (10,'Operador Cua', 'op4@sistema.com',   SHA2('password123', 256), 2, 1, '2024-02-18 10:30:00'),
  (11,'Operador Cin', 'op5@sistema.com',   SHA2('password123', 256), 2, 1, '2024-02-19 10:30:00'),
  (12,'Operador Sei', 'op6@sistema.com',   SHA2('password123', 256), 2, 1, '2024-02-20 10:30:00'),
  (13,'Operador Sie', 'op7@sistema.com',   SHA2('password123', 256), 2, 1, '2024-02-21 10:30:00'),
  (14,'Operador Och', 'op8@sistema.com',   SHA2('password123', 256), 2, 1, '2024-02-22 10:30:00'),
  (15,'Operador Nue', 'op9@sistema.com',   SHA2('password123', 256), 2, 1, '2024-02-23 10:30:00'),
  (3, 'Carlos Ruiz',  'carlos@sistema.com',SHA2('invitado789', 256), 3, 1, '2024-03-01 08:00:00'),
  (16,'Invitado Dos', 'inv2@sistema.com',  SHA2('password123', 256), 3, 1, '2024-03-02 08:00:00'),
  (17,'Invitado Tre', 'inv3@sistema.com',  SHA2('password123', 256), 3, 1, '2024-03-03 08:00:00'),
  (18,'Invitado Cua', 'inv4@sistema.com',  SHA2('password123', 256), 3, 1, '2024-03-04 08:00:00'),
  (19,'Invitado Cin', 'inv5@sistema.com',  SHA2('password123', 256), 3, 1, '2024-03-05 08:00:00');

-- Sensores
INSERT INTO `Sensores` (`Id_Sensor`, `Valor`, `Fecha`, `Id_Tipo`, `Activo`) VALUES
  (1, 22.5,  '2024-06-01 08:00:00', 1, 1),
  (2, 65.0,  '2024-06-01 08:00:00', 2, 1),
  (3, 300.0, '2024-06-01 08:00:00', 3, 1),
  (4, 0.0,   '2024-06-01 08:00:00', 4, 0),
  (5, 21, '2024-06-01 08:10:00', 1, 1),
  (6, 22, '2024-06-01 08:20:00', 1, 1),
  (7, 23, '2024-06-01 08:30:00', 1, 1),
  (8, 24, '2024-06-01 08:40:00', 1, 1),
  (9, 20, '2024-06-01 08:50:00', 1, 1),
  (10, 21, '2024-06-01 09:00:00', 1, 1),
  (11, 22, '2024-06-01 09:10:00', 1, 1),
  (12, 23, '2024-06-01 09:20:00', 1, 1),
  (13, 24, '2024-06-01 09:30:00', 1, 1),
  (14, 20, '2024-06-01 09:40:00', 1, 1),
  (15, 21, '2024-06-01 09:50:00', 1, 1),
  (16, 22, '2024-06-01 10:00:00', 1, 1),
  (17, 23, '2024-06-01 10:10:00', 1, 1),
  (18, 24, '2024-06-01 10:20:00', 1, 1),
  (19, 20, '2024-06-01 10:30:00', 1, 1),
  (20, 21, '2024-06-01 10:40:00', 1, 1),
  (21, 22, '2024-06-01 10:50:00', 1, 1),
  (22, 23, '2024-06-01 11:00:00', 1, 1),
  (23, 24, '2024-06-01 11:10:00', 1, 1),
  (24, 20, '2024-06-01 11:20:00', 1, 1),
  (25, 21, '2024-06-01 11:30:00', 1, 1),
  (26, 22, '2024-06-01 11:40:00', 1, 1),
  (27, 23, '2024-06-01 11:50:00', 1, 1),
  (28, 24, '2024-06-01 12:00:00', 1, 1),
  (29, 20, '2024-06-01 12:10:00', 1, 1),
  (30, 21, '2024-06-01 12:20:00', 1, 1),
  (31, 22, '2024-06-01 12:30:00', 1, 1),
  (32, 23, '2024-06-01 12:40:00', 1, 1),
  (33, 24, '2024-06-01 12:50:00', 1, 1),
  (34, 20, '2024-06-01 13:00:00', 1, 1),
  (35, 21, '2024-06-01 13:10:00', 1, 1),
  (36, 22, '2024-06-01 13:20:00', 1, 1),
  (37, 23, '2024-06-01 13:30:00', 1, 1),
  (38, 24, '2024-06-01 13:40:00', 1, 1),
  (39, 20, '2024-06-01 13:50:00', 1, 1),
  (40, 21, '2024-06-01 14:00:00', 1, 1),
  (41, 22, '2024-06-01 14:10:00', 1, 1),
  (42, 23, '2024-06-01 14:20:00', 1, 1),
  (43, 24, '2024-06-01 14:30:00', 1, 1),
  (44, 20, '2024-06-01 14:40:00', 1, 1),
  (45, 21, '2024-06-01 14:50:00', 1, 1),
  (46, 22, '2024-06-01 15:00:00', 1, 1),
  (47, 23, '2024-06-01 15:10:00', 1, 1),
  (48, 24, '2024-06-01 15:20:00', 1, 1),
  (49, 20, '2024-06-01 15:30:00', 1, 1),
  (50, 21, '2024-06-01 15:40:00', 1, 1),
  (51, 22, '2024-06-01 15:50:00', 1, 1),
  (52, 23, '2024-06-01 16:00:00', 1, 1),
  (53, 24, '2024-06-01 16:10:00', 1, 1),
  (54, 20, '2024-06-01 16:20:00', 1, 1),
  (55, 21, '2024-06-01 16:30:00', 1, 1),
  (56, 22, '2024-06-01 16:40:00', 1, 1),
  (57, 23, '2024-06-01 16:50:00', 1, 1),
  (58, 24, '2024-06-01 17:00:00', 1, 1),
  (59, 20, '2024-06-01 17:10:00', 1, 1),
  (60, 21, '2024-06-01 17:20:00', 1, 1),
  (61, 22, '2024-06-01 17:30:00', 1, 1),
  (62, 23, '2024-06-01 17:40:00', 1, 1),
  (63, 24, '2024-06-01 17:50:00', 1, 1),
  (64, 51, '2024-06-01 08:15:00', 2, 1),
  (65, 52, '2024-06-01 08:30:00', 2, 1),
  (66, 53, '2024-06-01 08:45:00', 2, 1),
  (67, 54, '2024-06-01 09:00:00', 2, 1),
  (68, 55, '2024-06-01 09:15:00', 2, 1),
  (69, 56, '2024-06-01 09:30:00', 2, 1),
  (70, 57, '2024-06-01 09:45:00', 2, 1),
  (71, 58, '2024-06-01 10:00:00', 2, 1),
  (72, 59, '2024-06-01 10:15:00', 2, 1),
  (73, 60, '2024-06-01 10:30:00', 2, 1),
  (74, 61, '2024-06-01 10:45:00', 2, 1),
  (75, 62, '2024-06-01 11:00:00', 2, 1),
  (76, 63, '2024-06-01 11:15:00', 2, 1),
  (77, 64, '2024-06-01 11:30:00', 2, 1),
  (78, 65, '2024-06-01 11:45:00', 2, 1),
  (79, 66, '2024-06-01 12:00:00', 2, 1),
  (80, 67, '2024-06-01 12:15:00', 2, 1),
  (81, 68, '2024-06-01 12:30:00', 2, 1),
  (82, 69, '2024-06-01 12:45:00', 2, 1),
  (83, 210, '2024-06-01 08:20:00', 3, 1),
  (84, 220, '2024-06-01 08:40:00', 3, 1),
  (85, 230, '2024-06-01 09:00:00', 3, 1),
  (86, 240, '2024-06-01 09:20:00', 3, 1),
  (87, 250, '2024-06-01 09:40:00', 3, 1),
  (88, 260, '2024-06-01 10:00:00', 3, 1),
  (89, 270, '2024-06-01 10:20:00', 3, 1),
  (90, 280, '2024-06-01 10:40:00', 3, 1),
  (91, 290, '2024-06-01 11:00:00', 3, 1),
  (92, 300, '2024-06-01 11:20:00', 3, 1),
  (93, 310, '2024-06-01 11:40:00', 3, 1),
  (94, 320, '2024-06-01 12:00:00', 3, 1),
  (95, 330, '2024-06-01 12:20:00', 3, 1),
  (96, 340, '2024-06-01 12:40:00', 3, 1),
  (97, 350, '2024-06-01 13:00:00', 3, 1),
  (98, 360, '2024-06-01 13:20:00', 3, 1),
  (99, 370, '2024-06-01 13:40:00', 3, 1),
  (100, 380, '2024-06-01 14:00:00', 3, 1),
  (101, 390, '2024-06-01 14:20:00', 3, 1);

-- Historial de barreras
INSERT INTO `Historial_Barreras` (`id_Historial`, `Fecha`, `Control`, `id_Barrera`) VALUES
  (1, '2024-06-01 07:55:00', 'Apertura automática mañana', 1),
  (2, '2024-06-01 09:00:00', 'Cierre manual operador',     2),
  (3, '2024-06-01 10:30:00', 'Error detectado en sensor',  3);

-- Notificaciones
INSERT INTO `Notificaciones` (`Id`, `Fecha`, `Dato`, `Titulo`, `Id_Sensor`, `Activo`) VALUES
  (1, '2024-06-01 08:15:00', 35.2, 'Temperatura alta',    1, 1),
  (2, '2024-06-01 08:20:00', 80.0, 'Humedad crítica',     2, 1),
  (3, '2024-06-01 08:45:00', 50.0, 'Luminosidad baja',    3, 1);

-- Configuración de luminosidad
INSERT INTO `Conf_Luminosidad` (`id`, `Control`, `Umbral`, `Hora_Inicial`, `Hora_Final`, `Minuto_Inicial`, `Minuto_Final`, `Activo`) VALUES
  (1, 'automatico', 150.0, 7, 22, 0, 0, 1),
  (2, 'encendido',  0.0,   0,  6, 0, 59, 1);

-- Configuración de alertas
INSERT INTO `Conf_Alertas` (`id`, `Valor`, `Id_Tipo`, `Activo`) VALUES
  (1, 35.0, 1, 1),  -- alerta temperatura > 35
  (2, 80.0, 2, 1),  -- alerta humedad > 80
  (3, 100.0, 3, 1), -- alerta luminosidad < 100
  (4, 1.0,  4, 1);  -- alerta movimiento detectado

-- Conversaciones
INSERT INTO `Conversacion` (`Id_Conversacion`, `Titulo`, `Fecha`, `Activo`) VALUES
  (1, 'Incidencia barrera 3',  '2024-06-01 10:35:00', 1),
  (2, 'Revisión sensores',     '2024-06-02 09:00:00', 1),
  (3, 'Chat eliminado',        '2024-05-01 08:00:00', 0),
  (4, 'Relación Operador 2', '2024-06-03 10:00:00', 1),
  (5, 'Relación Operador 8', '2024-06-03 10:00:00', 1),
  (6, 'Relación Operador 9', '2024-06-03 10:00:00', 1),
  (7, 'Relación Operador 10', '2024-06-03 10:00:00', 1),
  (8, 'Relación Operador 11', '2024-06-03 10:00:00', 1),
  (9, 'Relación Operador 12', '2024-06-03 10:00:00', 1),
  (10, 'Relación Operador 13', '2024-06-03 10:00:00', 1),
  (11, 'Relación Operador 14', '2024-06-03 10:00:00', 1),
  (12, 'Relación Operador 15', '2024-06-03 10:00:00', 1);

-- Mensajes
INSERT INTO `Mensajes` (`Id`, `Id_User`, `Descripcion`, `Fecha`, `Id_Conversacion`, `Activo`) VALUES
  (1, 1, 'La barrera 3 sigue dando error, revisar sensor.',   '2024-06-01 10:36:00', 1, 1),
  (2, 2, 'Confirmado, voy a revisarlo ahora mismo.',          '2024-06-01 10:40:00', 1, 1),
  (3, 1, 'Los sensores de humedad están por encima del umbral.','2024-06-02 09:01:00', 2, 1),
  (4, 2, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 4, 1),
  (5, 8, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 5, 1),
  (6, 9, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 6, 1),
  (7, 10, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 7, 1),
  (8, 11, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 8, 1),
  (9, 12, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 9, 1),
  (10, 13, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 10, 1),
  (11, 14, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 11, 1),
  (12, 15, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 12, 1);


-- ============================================================
-- SECCIÓN 4: CONSULTAS DE EJEMPLO
-- ============================================================

-- Login: una sola consulta con WHERE sobre email + hash de contraseña
SELECT `Id_User`, `Nombre`, `Id_Rol`
  FROM `Usuarios`
 WHERE `Email` = 'ana@sistema.com'
   AND `Contrasena` = SHA2('password123', 256)
   AND `Activo` = 1;

-- Listado de sensores activos con su tipo, ordenados por tipo
SELECT s.`Id_Sensor`, t.`Nombre` AS Tipo, s.`Valor`, s.`Fecha`
  FROM `Sensores` s
  JOIN `Tipos` t ON s.`Id_Tipo` = t.`Id_Tipos`
 WHERE s.`Activo` = 1
 ORDER BY t.`Nombre`, s.`Fecha` DESC;

-- Notificaciones recientes de un sensor concreto
SELECT n.`Id`, n.`Titulo`, n.`Dato`, n.`Fecha`
  FROM `Notificaciones` n
 WHERE n.`Id_Sensor` = 1
   AND n.`Activo` = 1
 ORDER BY n.`Fecha` DESC;

-- Historial de una barrera ordenado cronológicamente
SELECT h.`id_Historial`, h.`Fecha`, h.`Control`
  FROM `Historial_Barreras` h
 WHERE h.`id_Barrera` = 1
 ORDER BY h.`Fecha` DESC;

-- Mensajes
INSERT INTO `Mensajes` (`Id`, `Id_User`, `Descripcion`, `Fecha`, `Id_Conversacion`, `Activo`) VALUES
  (1, 1, 'La barrera 3 sigue dando error, revisar sensor.',   '2024-06-01 10:36:00', 1, 1),
  (2, 2, 'Confirmado, voy a revisarlo ahora mismo.',          '2024-06-01 10:40:00', 1, 1),
  (3, 1, 'Los sensores de humedad están por encima del umbral.','2024-06-02 09:01:00', 2, 1),
  (4, 2, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 4, 1),
  (5, 8, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 5, 1),
  (6, 9, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 6, 1),
  (7, 10, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 7, 1),
  (8, 11, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 8, 1),
  (9, 12, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 9, 1),
  (10, 13, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 10, 1),
  (11, 14, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 11, 1),
  (12, 15, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', 12, 1);

-- Usuarios (contraseña hasheada con SHA2-256: 'password123' → hash)
INSERT INTO `Usuarios` (`Id_User`, `Nombre`, `Email`, `Contrasena`, `Id_Rol`, `Activo`, `Fecha_Alta`) VALUES
  (1, 'Ana García',   'ana@sistema.com',   SHA2('password123', 256), 1, 1, '2024-01-10 09:00:00'),
  (4, 'Admin Dos',    'admin2@sistema.com',SHA2('password123', 256), 1, 1, '2024-01-11 09:00:00'),
  (5, 'Admin Tres',   'admin3@sistema.com',SHA2('password123', 256), 1, 1, '2024-01-12 09:00:00'),
  (6, 'Admin Cuatro', 'admin4@sistema.com',SHA2('password123', 256), 1, 1, '2024-01-13 09:00:00'),
  (7, 'Admin Cinco',  'admin5@sistema.com',SHA2('password123', 256), 1, 1, '2024-01-14 09:00:00'),
  (2, 'Luis Martínez','luis@sistema.com',  SHA2('operador456', 256), 2, 1, '2024-02-15 10:30:00'),
  (8, 'Operador Dos', 'op2@sistema.com',   SHA2('password123', 256), 2, 1, '2024-02-16 10:30:00'),
  (9, 'Operador Tres','op3@sistema.com',   SHA2('password123', 256), 2, 1, '2024-02-17 10:30:00'),
  (10,'Operador Cua', 'op4@sistema.com',   SHA2('password123', 256), 2, 1, '2024-02-18 10:30:00'),
  (11,'Operador Cin', 'op5@sistema.com',   SHA2('password123', 256), 2, 1, '2024-02-19 10:30:00'),
  (12,'Operador Sei', 'op6@sistema.com',   SHA2('password123', 256), 2, 1, '2024-02-20 10:30:00'),
  (13,'Operador Sie', 'op7@sistema.com',   SHA2('password123', 256), 2, 1, '2024-02-21 10:30:00'),
  (14,'Operador Och', 'op8@sistema.com',   SHA2('password123', 256), 2, 1, '2024-02-22 10:30:00'),
  (15,'Operador Nue', 'op9@sistema.com',   SHA2('password123', 256), 2, 1, '2024-02-23 10:30:00'),
  (3, 'Carlos Ruiz',  'carlos@sistema.com',SHA2('invitado789', 256), 3, 1, '2024-03-01 08:00:00'),
  (16,'Invitado Dos', 'inv2@sistema.com',  SHA2('password123', 256), 3, 1, '2024-03-02 08:00:00'),
  (17,'Invitado Tre', 'inv3@sistema.com',  SHA2('password123', 256), 3, 1, '2024-03-03 08:00:00'),
  (18,'Invitado Cua', 'inv4@sistema.com',  SHA2('password123', 256), 3, 1, '2024-03-04 08:00:00'),
  (19,'Invitado Cin', 'inv5@sistema.com',  SHA2('password123', 256), 3, 1, '2024-03-05 08:00:00');


-- ============================================================
-- SECCIÓN 5: INSERT, UPDATE CON WHERE SOBRE PK
-- ============================================================

-- Nuevo mensaje en una conversación
INSERT INTO `Mensajes` (`Id_User`, `Descripcion`, `Fecha`, `Id_Conversacion`, `Activo`)
VALUES (2, 'Sensor de humedad reemplazado, niveles normales.', NOW(), 2, 1);

-- Actualizar estado de una barrera (WHERE sobre PK)
UPDATE `Barreras`
   SET `Estado` = 'cerrada', `Control` = 'automatico'
 WHERE `id_Barrera` = 3;

-- Actualizar valor de un sensor (WHERE sobre PK)
UPDATE `Sensores`
   SET `Valor` = 24.3, `Fecha` = NOW()
 WHERE `Id_Sensor` = 1;

-- Cambiar contraseña de un usuario (WHERE sobre PK)
UPDATE `Usuarios`
   SET `Contrasena` = SHA2('nuevaPassword!99', 256)
 WHERE `Id_User` = 2;


-- ============================================================
-- SECCIÓN 6: BAJA LÓGICA (nunca se borran datos)
-- ============================================================

-- Dar de baja un sensor (no se elimina)
UPDATE `Sensores`   SET `Activo` = 0 WHERE `Id_Sensor` = 4;

-- Dar de baja un usuario (no se elimina)
UPDATE `Usuarios`   SET `Activo` = 0 WHERE `Id_User` = 3;

-- Dar de baja una conversación (no se elimina)
UPDATE `Conversacion` SET `Activo` = 0 WHERE `Id_Conversacion` = 3;

-- Dar de baja un participante de una conversación
UPDATE `Participantes` SET `Activo` = 0 WHERE `Id_Participantes` = 4;
