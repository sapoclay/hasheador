# Generador de Hashes PHPass para WordPress

Esto es un pequeño programa en Python que genera hashes de contraseñas compatibles con WordPress utilizando el algoritmo PHPass. Este tipo de hash es el que WordPress utiliza para almacenar contraseñas de forma segura en su base de datos.

El código original lo ha colocado Jairo en https://gist.github.com/jairochapela/3c9b0de04267a94f7875bdf4fcb17137

## Descripción

Este programa implementa el algoritmo de hashing PHPass que WordPress utiliza para proteger las contraseñas de los usuarios. El hash generado puede ser utilizado directamente en bases de datos de WordPress o sistemas compatibles como qdpm, que es lo que nos interesa en este caso.

## ¿Qué es un Hash? (explicación de andar por casa)

Un **hash** es como una versión encriptada de una contraseña que **no se puede revertir**. Es una función matemática de un solo sentido que convierte cualquier texto (como una contraseña) en una cadena de caracteres única. Aunque dos personas tengan la misma contraseña, si se usa un "salt" diferente, los hashes serán completamente distintos (ahí está la gracia)

## Estructura del Hash generado

El programa genera un hash de **34 caracteres** con la siguiente estructura:

```
$P$CjF.jd1bB6t9fxwFbhNgIZhp0RozS1/
└┬┘└┬┘└──┬───┘└────────┬──────────┘
 │  │    │             └─ Hash codificado (22 caracteres)
 │  │    └─────────────── Salt aleatorio (8 caracteres)
 │  └──────────────────── Carácter de iteración (1 carácter)
 └─────────────────────── Prefijo PHPass (3 caracteres)
```

### Componentes del Hash:

| Posición | Componente | Longitud | Ejemplo | Descripción |
|----------|------------|----------|---------|-------------|
| 1-3 | Prefijo | 3 chars | `$P$` | Identifica que es un hash PHPass |
| 4 | Iteración | 1 char | `C` | Nivel de seguridad (14 = 16,384 repeticiones) |
| 5-12 | Salt | 8 chars | `jF.jd1bB` | Cadena aleatoria única |
| 13-34 | Hash | 22 chars | `6t9fx...S1/` | Hash codificado de la contraseña |

**Total: 3 + 1 + 8 + 22 = 34 caracteres**

## ¿Qué es el carácter de iteración?

El **carácter de iteración** (posición 4) es un código que indica cuántas veces se repite el proceso de hasheo. Cuantas más veces se repita, más seguro es el hash, pero también va a ser más lento de generar.

## Uso del programa

### Ejecución básica:

```bash
python3 hashWordpress.py
```

El programa te pedirá que introduzcas una contraseña y justo después te mostrará el hash generado.

```
Introduce la contraseña: chanchunai123

Hash PHPass generado:
$P$CjF.jd1bB6t9fxwFbhNgIZhp0RozS1/
```

## Uso con base de datos

Para hacer esto, evidentemente, necesitamos tener acceso a la base de datos en la que queramos utilizar este hash generado

### Actualizar contraseña en WordPress/qdpm:

```sql
UPDATE configuration 
SET value = '$P$CjF.jd1bB6t9fxwFbhNgIZhp0RozS1/' 
WHERE `key` = 'app_administrator_password';
```

**Nota:** Usa backticks (`) alrededor de `key` porque es una palabra reservada en MySQL.

## Notas

1. **Cada ejecución genera un hash diferente** debido al salt aleatorio, incluso con la misma contraseña
2. **No es posible revertir el hash** para obtener la contraseña original
3. **El nivel 14 es el estándar de WordPress** aun que de esto no estoy seguro
4. **Niveles más altos** (>14) son más seguros pero significativamente más lentos

## Referencias

- [PHPass - Portable PHP password hashing framework](https://www.openwall.com/phpass/)
- [WordPress Password Hashing](https://developer.wordpress.org/reference/functions/wp_hash_password/)
- [Documentación MD5](https://docs.python.org/3/library/hashlib.html)

## Licencia

Este código es de uso educativo y puede ser utilizado libremente para proyectos personales o profesionales.

---
