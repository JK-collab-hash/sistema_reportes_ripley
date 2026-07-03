-- ============================================
--  SISTEMA DE REPORTES DE GARITA
--  Script de creación de base de datos MySQL
-- ============================================

CREATE DATABASE IF NOT EXISTS sistema_reportes
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_spanish_ci;

USE sistema_reportes;

-- --------------------------------------------
-- TABLA: usuarios
-- --------------------------------------------
CREATE TABLE usuarios (
    id          INT(10)         NOT NULL AUTO_INCREMENT,
    nombre      VARCHAR(200)    NOT NULL,
    apellido_p  VARCHAR(200)    NOT NULL,
    apellido_m  VARCHAR(200)    NOT NULL,
    contrasena  VARCHAR(50)     NOT NULL,
    rol         ENUM('admin', 'logistica', 'garita') NOT NULL DEFAULT 'garita',
    creado_en   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

-- --------------------------------------------
-- TABLA: camiones
-- --------------------------------------------
CREATE TABLE camiones (
    id          INT             NOT NULL AUTO_INCREMENT,
    placa       VARCHAR(20)     NOT NULL UNIQUE,
    nombre      VARCHAR(100)    NOT NULL,
    conductor   VARCHAR(200),
    marca       VARCHAR(100),
    activo      TINYINT(1)      NOT NULL DEFAULT 1
                    COMMENT '1=Activo, 0=Inactivo',
    PRIMARY KEY (id)
);

-- --------------------------------------------
-- TABLA: categorias
-- Solo el admin puede crear/editar
-- --------------------------------------------
CREATE TABLE categorias (
    id          INT             NOT NULL AUTO_INCREMENT,
    nombre      VARCHAR(100)    NOT NULL,
    creado_por  INT(10)         NOT NULL,
    creado_en   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (creado_por) REFERENCES usuarios(id)
);

-- --------------------------------------------
-- TABLA: reportes
-- Un reporte por camión por ingreso
-- --------------------------------------------
CREATE TABLE reportes (
    id              INT         NOT NULL AUTO_INCREMENT,
    codigo          VARCHAR(50) NOT NULL UNIQUE,
    camion_id       INT         NOT NULL,
    usuario_id      INT(10)     NOT NULL,
    comentarios     TEXT,
    incidencias     TEXT,
    fecha_registro  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (camion_id)  REFERENCES camiones(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- --------------------------------------------
-- TABLA: detalle_reporte
-- Cada fila = un producto dentro del reporte
-- --------------------------------------------
CREATE TABLE detalle_reporte (
    id              INT          NOT NULL AUTO_INCREMENT,
    reporte_id      INT          NOT NULL,
    categoria_id    INT          NOT NULL,
    nombre_producto VARCHAR(300) NOT NULL,
    cantidad        INT          NOT NULL DEFAULT 1,
    observacion     TEXT,
    PRIMARY KEY (id),
    FOREIGN KEY (reporte_id)   REFERENCES reportes(id),
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

-- ============================================
--  DATOS INICIALES
-- ============================================

INSERT INTO usuarios (nombre, apellido_p, apellido_m, contrasena, rol) VALUES
    ('Admin', 'Sistema', '', 'admin123', 'admin'),
    ('Jose', 'Manuel', 'Alguay', '123456', 'garita');

INSERT INTO categorias (nombre, creado_por) VALUES
    ('Ropa',             1),
    ('Electrodoméstico', 1),
    ('Tecnología',       1),
    ('Alimentos',        1),
    ('Muebles',          1);

INSERT INTO camiones (placa, nombre, conductor, marca) VALUES
    ('ABC-123', 'Camión 01', 'Juan Pérez', 'Volvo'),
    ('DEF-456', 'Camión 03', 'Luis Ramos', 'Mercedes-Benz'),
    ('GHI-789', 'Camión 05', 'Pedro Salas', 'Scania'),
    ('JKL-321', 'Camión 06', 'Carlos Vega', 'Volvo');
