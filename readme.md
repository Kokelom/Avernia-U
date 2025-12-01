# Construcción

Para construir se debe utilizar el siguiente comando:

```bash
    docker build -t avernia-rest .
```

# Ejecución

Para correrlo se utiliza:

```bash
    docker run -d -p 8000:8000 --name mi-api avernia-rest
```

# Verificación

```bash
    curl localhost:8000
```

es posible que no tengan descargado curl, so, su

```bash
    sudo apt install curl
```

confirman con la contraseña y ya, proceso estándar.