# conexion, configuracion base de datos
class DevelopmentConfig():
    DEBUG=True
    MYSQL_HOST='localhost'
    MYSQL_USER='root'
    MYSQL_PASSWORD=''
    # MYSQL_DB='api_utl'
    MYSQL_DB='pizzeria'
    # ssl_disabled=True

config={
    'development':DevelopmentConfig
}
