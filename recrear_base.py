import sqlite3
import os

# Eliminar base existente si aún existe
if os.path.exists('restaurante.db'):
    os.remove('restaurante.db')
    print("✓ Base de datos eliminada")

# Conectar a la base (se creará automáticamente)
conn = sqlite3.connect('restaurante.db')
cursor = conn.cursor()

# Habilitar foreign keys
cursor.execute("PRAGMA foreign_keys = ON")

print("✓ Creando tablas...")

# Crear tabla mesas
cursor.execute('''
CREATE TABLE mesas (
    id INTEGER PRIMARY KEY,
    numero INTEGER NOT NULL,
    capacidad INTEGER NOT NULL,
    estado VARCHAR(9),
    fecha_creacion DATETIME,
    observaciones TEXT
)
''')

# Crear tabla empleados
cursor.execute('''
CREATE TABLE empleados (
    id INTEGER PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    puesto VARCHAR(8) NOT NULL,
    estado VARCHAR(8),
    telefono VARCHAR(20),
    email VARCHAR(100),
    fecha_ingreso DATETIME,
    salario FLOAT
)
''')

# Crear tabla ingredientes
cursor.execute('''
CREATE TABLE ingredientes (
    id INTEGER PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    cantidad FLOAT,
    unidad VARCHAR(50) NOT NULL,
    precio_unitario FLOAT NOT NULL,
    estado VARCHAR(10),
    cantidad_minima FLOAT,
    proveedor VARCHAR(100),
    fecha_ultimo_ingreso DATETIME
)
''')

# Crear tabla platos
cursor.execute('''
CREATE TABLE platos (
    id INTEGER PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio FLOAT NOT NULL,
    categoria VARCHAR(14) NOT NULL,
    estado VARCHAR(13),
    tiempo_preparacion INTEGER,
    fecha_creacion DATETIME,
    imagen_url VARCHAR(500)
)
''')

# Crear tabla plato_ingrediente
cursor.execute('''
CREATE TABLE plato_ingrediente (
    plato_id INTEGER NOT NULL,
    ingrediente_id INTEGER NOT NULL,
    cantidad_requerida FLOAT,
    unidad VARCHAR(50),
    PRIMARY KEY (plato_id, ingrediente_id),
    FOREIGN KEY(plato_id) REFERENCES platos (id),
    FOREIGN KEY(ingrediente_id) REFERENCES ingredientes (id)
)
''')

# Crear tabla clientes
cursor.execute('''
CREATE TABLE clientes (
    id INTEGER PRIMARY KEY,
    cedula VARCHAR(20) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    correo VARCHAR(100),
    telefono VARCHAR(20),
    direccion VARCHAR(255),
    mesa_id INTEGER,
    estado VARCHAR(9),
    fecha_llegada DATETIME,
    FOREIGN KEY(mesa_id) REFERENCES mesas (id)
)
''')

# Crear tabla turnos
cursor.execute('''
CREATE TABLE turnos (
    id INTEGER PRIMARY KEY,
    empleado_id INTEGER NOT NULL,
    fecha_inicio DATETIME NOT NULL,
    fecha_fin DATETIME,
    FOREIGN KEY(empleado_id) REFERENCES empleados (id)
)
''')

# Crear tabla pedidos
cursor.execute('''
CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY,
    cliente_id INTEGER NOT NULL,
    mesa_id INTEGER NOT NULL,
    empleado_id INTEGER,
    estado VARCHAR(10),
    fecha_creacion DATETIME,
    fecha_entrega DATETIME,
    observaciones TEXT,
    descuento FLOAT,
    FOREIGN KEY(cliente_id) REFERENCES clientes (id),
    FOREIGN KEY(mesa_id) REFERENCES mesas (id),
    FOREIGN KEY(empleado_id) REFERENCES empleados (id)
)
''')

# Crear tabla detalles_pedido
cursor.execute('''
CREATE TABLE detalles_pedido (
    id INTEGER PRIMARY KEY,
    pedido_id INTEGER NOT NULL,
    plato_id INTEGER NOT NULL,
    cantidad INTEGER,
    precio_unitario FLOAT NOT NULL,
    subtotal FLOAT NOT NULL,
    FOREIGN KEY(pedido_id) REFERENCES pedidos (id),
    FOREIGN KEY(plato_id) REFERENCES platos (id)
)
''')

# Crear tabla pagos
cursor.execute('''
CREATE TABLE pagos (
    id INTEGER PRIMARY KEY,
    pedido_id INTEGER NOT NULL,
    monto FLOAT NOT NULL,
    metodo VARCHAR(13) NOT NULL,
    estado VARCHAR(9),
    fecha_pago DATETIME,
    referencia VARCHAR(100),
    cambio FLOAT,
    observaciones TEXT,
    UNIQUE(pedido_id),
    FOREIGN KEY(pedido_id) REFERENCES pedidos (id)
)
''')

# Crear tabla usos_ingredientes
cursor.execute('''
CREATE TABLE usos_ingredientes (
    id INTEGER PRIMARY KEY,
    ingrediente_id INTEGER NOT NULL,
    pedido_id INTEGER,
    cantidad_usada FLOAT NOT NULL,
    fecha DATETIME,
    notas TEXT,
    FOREIGN KEY(ingrediente_id) REFERENCES ingredientes (id),
    FOREIGN KEY(pedido_id) REFERENCES pedidos (id)
)
''')

print("✓ Creando índices...")
cursor.execute('CREATE INDEX ix_mesas_id ON mesas (id)')
cursor.execute('CREATE UNIQUE INDEX ix_mesas_numero ON mesas (numero)')
cursor.execute('CREATE INDEX ix_empleados_id ON empleados (id)')
cursor.execute('CREATE INDEX ix_ingredientes_id ON ingredientes (id)')
cursor.execute('CREATE UNIQUE INDEX ix_ingredientes_nombre ON ingredientes (nombre)')
cursor.execute('CREATE UNIQUE INDEX ix_platos_nombre ON platos (nombre)')
cursor.execute('CREATE INDEX ix_platos_id ON platos (id)')
cursor.execute('CREATE UNIQUE INDEX ix_clientes_cedula ON clientes (cedula)')
cursor.execute('CREATE INDEX ix_clientes_id ON clientes (id)')
cursor.execute('CREATE INDEX ix_turnos_id ON turnos (id)')
cursor.execute('CREATE INDEX ix_pedidos_id ON pedidos (id)')
cursor.execute('CREATE INDEX ix_pedidos_fecha_creacion ON pedidos (fecha_creacion)')
cursor.execute('CREATE INDEX ix_detalles_pedido_id ON detalles_pedido (id)')
cursor.execute('CREATE INDEX ix_pagos_id ON pagos (id)')
cursor.execute('CREATE INDEX ix_usos_ingredientes_id ON usos_ingredientes (id)')
cursor.execute('CREATE INDEX ix_usos_ingredientes_fecha ON usos_ingredientes (fecha)')

print("✓ Insertando mesas...")
cursor.executemany('INSERT INTO mesas (id, numero, capacidad, estado, fecha_creacion, observaciones) VALUES (?,?,?,?,?,?)', [
    (1, 1, 2, 'LIBRE', '2026-03-23 00:33:47.323418', None),
    (2, 2, 4, 'LIBRE', '2026-03-23 00:34:04.645669', None),
    (3, 3, 6, 'LIBRE', '2026-03-23 00:34:13.958711', None),
    (4, 4, 4, 'LIBRE', '2026-03-23 00:34:25.433222', None)
])

print("✓ Insertando empleados...")
cursor.executemany('INSERT INTO empleados (id, nombre, puesto, estado, telefono, email, fecha_ingreso, salario) VALUES (?,?,?,?,?,?,?,?)', [
    (1, 'Juan Perez', 'CAMARERO', 'ACTIVO', '0986754321', 'jueanperez@gmail.com', '2026-03-23 00:35:39.648613', 241.0),
    (2, 'Miguel', 'CAMARERO', 'ACTIVO', '0987654321', 'miguel@gmail.com', '2026-03-23 00:36:24.275419', 482.0)
])

print("✓ Insertando ingredientes...")
ingredientes = [
    (1, 'Tomate', 190.0, 'Gramos', 1.80, 'DISPONIBLE', 2.0, 'Juan', None),
    (2, 'Queso mozzarella', 4850.0, 'Kilogramos', 8.5, 'DISPONIBLE', 200.0, 'El mercado', None),
    (3, 'Albahaca', 40.0, 'Kilogramos', 0.80, 'DISPONIBLE', 1.0, 'El mercado', None),
    (4, 'Pechuga de pollo', 300.0, 'Kilogramos', 5.5, 'DISPONIBLE', 200.0, 'Carniceria', None),
    (5, 'Papa', 21.0, 'Kilogramos', 1.0, 'DISPONIBLE', 5.0, 'El mercado', None),
    (6, 'Naranja', 44.0, 'Kilogramos', 0.80, 'DISPONIBLE', 2.0, 'El mercado', None),
    (7, 'Aceite de oliva', 9970.0, 'Mililitros', 7.0, 'DISPONIBLE', 500.0, 'Distribuidora Gourmet', None),
    (8, 'Vinagre balsamico', 4985.0, 'Mililitros', 9.0, 'DISPONIBLE', 250.0, 'Distribuidora Gourmet', None),
    (9, 'Sal de mar', 1995.0, 'Gramos', 2.0, 'DISPONIBLE', 100.0, 'Salinera Nacional', None),
    (10, 'Pimienta negra', 998.0, 'Gramos', 12.0, 'DISPONIBLE', 50.0, 'Especieria Central', None),
    (11, 'Mantequilla', 200.0, 'Gramos', 5.0, 'AGOTADO', 200.0, 'Lacteos Andinos', None),
    (12, 'Leche entera', 2.0, 'Mililitros', 1.10, 'AGOTADO', 1000.0, 'Lacteos Andinos', None),
    (13, 'Lechuga', 3.0, 'Gramos', 1.5, 'AGOTADO', 100.0, 'Huerta Organica', None),
    (14, 'Zanahoria', 0.0, 'Gramos', 1.0, 'DISPONIBLE', 150.0, 'Huerta Organica', None),
    (15, 'Limon', 4.0, 'Gramos', 1.40, 'AGOTADO', 100.0, 'Citricultores del Sur', None),
    (16, 'Azucar', 1.0, 'Gramos', 1.0, 'AGOTADO', 200.0, 'Ingenio Azucarero', None)
]
cursor.executemany('INSERT INTO ingredientes (id, nombre, cantidad, unidad, precio_unitario, estado, cantidad_minima, proveedor, fecha_ultimo_ingreso) VALUES (?,?,?,?,?,?,?,?,?)', ingredientes)

print("✓ Insertando platos...")
platos = [
    (1, 'Pechuga de pollo a la plancha con pure de papa y ensalada', 'Pechuga de pollo a la plancha, acompanada de pure de papa casero y ensalada fresca', 2.70, 'PLATO_FUERTE', 'DISPONIBLE', 15, '2026-03-23 00:43:59.576931', None),
    (2, 'Ensalada Caprese', 'Fresca ensalada con tomate, mozzarella fresca, albahaca, aceite de oliva y vinagre balsamico', 1.95, 'ENTRADA', 'DISPONIBLE', 10, '2026-03-23 05:52:47', None),
    (3, 'Jugo de naranja natural', 'Jugo fresco de naranjas recien exprimidas, endulzado al gusto', 0.75, 'BEBIDA', 'DISPONIBLE', 5, '2026-03-23 05:52:47', None)
]
cursor.executemany('INSERT INTO platos (id, nombre, descripcion, precio, categoria, estado, tiempo_preparacion, fecha_creacion, imagen_url) VALUES (?,?,?,?,?,?,?,?,?)', platos)

print("✓ Insertando recetas...")
recetas = [
    (1, 4, 200.0, 'Gramos'),
    (1, 5, 200.0, 'Gramos'),
    (1, 11, 30.0, 'Gramos'),
    (1, 12, 50.0, 'Mililitros'),
    (1, 9, 5.0, 'Gramos'),
    (1, 13, 50.0, 'Gramos'),
    (1, 14, 30.0, 'Gramos'),
    (1, 15, 20.0, 'Gramos'),
    (2, 1, 200.0, 'Gramos'),
    (2, 2, 150.0, 'Gramos'),
    (2, 3, 10.0, 'Gramos'),
    (2, 7, 30.0, 'Mililitros'),
    (2, 8, 15.0, 'Mililitros'),
    (2, 9, 5.0, 'Gramos'),
    (2, 10, 2.0, 'Gramos'),
    (3, 6, 400.0, 'Gramos'),
    (3, 16, 10.0, 'Gramos')
]
cursor.executemany('INSERT INTO plato_ingrediente (plato_id, ingrediente_id, cantidad_requerida, unidad) VALUES (?,?,?,?)', recetas)

print("✓ Insertando clientes...")
clientes = [
    (1, '0107881450', 'Jhonny', 'Mendez', 'jhony@gmail.com', '0987654321', 'cuenca', None, 'COMIENDO', '2026-03-23 00:31:46.301733'),
    (2, '0150342459', 'Adriana', 'Cornejo', 'adriana@gmail.com', '0987654321', 'cuenca', None, 'PAGADO', '2026-03-23 00:32:59.860461'),
    (3, '0106018815', 'Ismael', 'Loja', 'isma@gmail.com', '0987654321', 'cuenca', None, 'COMIENDO', '2026-03-23 00:33:35.295310'),
    (4, '9999999999', 'CLIENTE_GENERICO', 'Sistema', 'sistema@restaurante.com', '0000000000', 'Pedidos sin cliente', None, 'COMIENDO', '2026-03-23 00:33:41.856706')
]
cursor.executemany('INSERT INTO clientes (id, cedula, nombre, apellido, correo, telefono, direccion, mesa_id, estado, fecha_llegada) VALUES (?,?,?,?,?,?,?,?,?,?)', clientes)

print("✓ Insertando turnos...")
cursor.executemany('INSERT INTO turnos (id, empleado_id, fecha_inicio, fecha_fin) VALUES (?,?,?,?)', [
    (1, 1, '2026-03-23 00:36:30.719743', None),
    (2, 2, '2026-03-23 00:36:34.366491', None)
])

print("✓ Insertando pedidos...")
pedidos = [
    (1, 2, 1, 1, 'ENTREGADO', '2026-03-23 00:44:21.675952', '2026-03-23 00:44:44.964727', None, 0.0),
    (2, 1, 2, 1, 'ENTREGADO', '2026-03-23 04:52:47', '2026-03-23 05:22:47', None, 0.0)
]
cursor.executemany('INSERT INTO pedidos (id, cliente_id, mesa_id, empleado_id, estado, fecha_creacion, fecha_entrega, observaciones, descuento) VALUES (?,?,?,?,?,?,?,?,?)', pedidos)

print("✓ Insertando detalles de pedido...")
detalles = [
    (1, 1, 1, 2, 2.70, 5.40),
    (2, 2, 2, 1, 1.95, 1.95)
]
cursor.executemany('INSERT INTO detalles_pedido (id, pedido_id, plato_id, cantidad, precio_unitario, subtotal) VALUES (?,?,?,?,?,?)', detalles)

print("✓ Insertando pagos...")
cursor.executemany('INSERT INTO pagos (id, pedido_id, monto, metodo, estado, fecha_pago, referencia, cambio, observaciones) VALUES (?,?,?,?,?,?,?,?,?)', [
    (1, 1, 5.40, 'EFECTIVO', 'PAGADO', '2026-03-23 00:45:08.907930', None, 0.54, None)
])

print("✓ Insertando usos de ingredientes...")
usos = [
    (1, 1, 2, 200.0, '2026-03-23 05:52:47', None),
    (2, 2, 2, 150.0, '2026-03-23 05:52:47', None),
    (3, 3, 2, 10.0, '2026-03-23 05:52:47', None),
    (4, 7, 2, 30.0, '2026-03-23 05:52:47', None),
    (5, 8, 2, 15.0, '2026-03-23 05:52:47', None),
    (6, 9, 2, 5.0, '2026-03-23 05:52:47', None),
    (7, 10, 2, 2.0, '2026-03-23 05:52:47', None)
]
cursor.executemany('INSERT INTO usos_ingredientes (id, ingrediente_id, pedido_id, cantidad_usada, fecha, notas) VALUES (?,?,?,?,?,?)', usos)

# Confirmar cambios
conn.commit()

# Verificar datos
print("\n✓ Verificando datos...")
cursor.execute("SELECT COUNT(*) FROM platos")
print(f"  - Platos: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM ingredientes")
print(f"  - Ingredientes: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM ingredientes WHERE cantidad IS NULL")
print(f"  - Ingredientes con cantidad NULL: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM ingredientes WHERE cantidad = 0")
print(f"  - Ingredientes con cantidad 0: {cursor.fetchone()[0]}")

# Mostrar platos
print("\n📋 PLATOS REGISTRADOS:")
cursor.execute("SELECT id, nombre, categoria, precio FROM platos")
for row in cursor.fetchall():
    print(f"  {row[0]}. {row[1]} - {row[2]} - ${row[3]:.2f}")

conn.close()
print("\n✅ Base de datos recreada exitosamente!")