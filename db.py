import psycopg2
from psycopg2 import pool

#Crear un pool de conexiones
connection_pool = pool.SimpleConnectionPool(
    1,20,
    database="bar_la_catrina",
    user="postgres",
    password="tVE4QgrFP9rnEb",
    host="localhost",
    port="5432"
)

def conectar():
    return connection_pool.getconn()

def desconectar(conn):
    connection_pool.putconn(conn)