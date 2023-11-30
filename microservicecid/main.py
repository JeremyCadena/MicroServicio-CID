from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from cryptography.fernet import Fernet
import mysql.connector

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configura la conexión a la base de datos
database_config = {
    "host": "localhost",
    "user": "root",
    "password": "Jejocad1218",
    "database": "practica_patrones",
}

conn = mysql.connector.connect(**database_config)
cursor = conn.cursor(dictionary=True)

# Genera una clave única para cifrar y descifrar datos
clave_secreta = Fernet.generate_key()
fernet = Fernet(clave_secreta)

# Ruta para obtener todos los clientes
@app.get("/clientes/", response_model=list[dict])
async def obtener_clientes():
    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()

    # Cifra solo los valores específicos del cliente
    clientes_cifrados = [
        {
            key: fernet.encrypt(str(value).encode()).decode() if key != "ID" else value
            for key, value in cliente.items()
        }
        for cliente in clientes
    ]

    return clientes_cifrados

# Ruta para obtener un cliente por ID
@app.get("/clientes/{cliente_id}", response_model=dict)
async def obtener_cliente(cliente_id: int):
    cursor.execute("SELECT * FROM clientes WHERE ID = %s", (cliente_id,))
    cliente = cursor.fetchone()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Descifra solo los valores específicos del cliente
    cliente_descifrado = {
        key: fernet.decrypt(str(value).encode()).decode() if key != "ID" else value
        for key, value in cliente.items()
    }

    return cliente_descifrado