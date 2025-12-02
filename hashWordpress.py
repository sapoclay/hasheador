"""
Programa para generar hashes de contraseñas de WordPress.
Un hash es como una versión encriptada de una contraseña que no se puede revertir.

ESTRUCTURA DEL HASH GENERADO (34 caracteres en total):

(los espacios mostrados son solo para la claridad)

$P$ C  jF.jd1bB  6t9fxwFbhNgIZhp0RozS1/
└┬┘└┬┘└──┬─────┘└────────┬─────────────┘
 │  │    │             └─ 22 caracteres del hash
 │  │    └─────────────── 8 caracteres del salt
 │  └──────────────────── 'C' = nivel 14 = 16,384 repeticiones
 └─────────────────────── Prefijo $P$ (3 caracteres)

¿QUÉ SIGNIFICA EL CARÁCTER DE ITERACIÓN? (el 4º carácter)
Este carácter indica cuántas veces se repite el proceso de hasheo.
Cuantas más veces se repita, más difícil es romper el hash (pero más lento de crear).

Ejemplos de conversión del número al carácter:
  - iteration_log2 = 7  → carácter '7'  → se repite 2^7  = 128 veces
  - iteration_log2 = 10 → carácter 'A'  → se repite 2^10 = 1,024 veces
  - iteration_log2 = 14 → carácter 'C'  → se repite 2^14 = 16,384 veces (estándar)
  - iteration_log2 = 20 → carácter 'K'  → se repite 2^20 = 1,048,576 veces

El carácter se obtiene del alfabeto ITOA64 en la posición del número.
Por ejemplo: ITOA64[14] = 'C', ITOA64[10] = 'A', etc...
"""

import random
import hashlib

# Lista de caracteres especiales que WordPress usa para crear los hashes
# Es como un alfabeto personalizado con 64 caracteres diferentes
ITOA64 = "./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def get_random_salt(length=8):
    """
    Crea una cadena aleatoria de 8 caracteres.
    Esta cadena se llama "salt" y se usa para hacer el hash más seguro.
    
    LONGITUD: Siempre 8 caracteres
    EJEMPLO: "jF.jd1bB" o "Dwa6I9Oe"
    
    Parámetros:
        length: cuántos caracteres queremos (en este caso 8)
    
    Devuelve:
        Una cadena de texto aleatoria de 8 caracteres usando el alfabeto ITOA64
    """
    return ''.join(random.choice(ITOA64) for _ in range(length))


def encode64(input_bytes, count):
    """
    Convierte datos binarios en texto usando el alfabeto especial de WordPress.
    Es como traducir números a letras usando un código secreto.
    
    LONGITUD DE SALIDA: Variable, pero en este programa siempre genera más de 22 caracteres
                        (luego se recorta a 22 para el hash final)
    
    Parámetros:
        input_bytes: los datos que queremos convertir (16 bytes del hash MD5)
        count: cuántos datos vamos a procesar (siempre 16 en este caso)
    
    Devuelve:
        Un texto codificado de aproximadamente 22 caracteres que forma parte del hash final
    """
    output = []
    i = 0

    while i < count:
        value = input_bytes[i]
        i += 1
        output.append(ITOA64[value & 0x3f])

        if i < count:
            value |= input_bytes[i] << 8
            i += 1
        output.append(ITOA64[(value >> 6) & 0x3f])

        if i >= count:
            break

        if i < count:
            value |= input_bytes[i] << 16
            i += 1
        output.append(ITOA64[(value >> 12) & 0x3f])

        if i >= count:
            break

        output.append(ITOA64[(value >> 18) & 0x3f])

    return ''.join(output)


def phpass_hash(password, iteration_log2=14):
    """
    Convierte una contraseña en un hash de WordPress listo para guardarlo en la base de datos qdpm (que es lo que nos ocupa)

    Parámetros:
        password: la contraseña que queremos convertir en hash
        iteration_log2: número que controla cuántas veces se repite el proceso (entre 7 y 30) Más alto es más seguro pero más lento (14 me parece que es el estándar de WordPress)
                       Con 14: se repite 2^14 = 16,384 veces
    
    Devuelve:
        El hash completo de 34 caracteres (ejemplo: $P$CjF.jd1bB6t9fxwFbhNgIZhp0RozS1/)
    
    Errores:
        Si el número de iteraciones no está entre 7 y 30, muestra un error
    """
    if not 7 <= iteration_log2 <= 30:
        raise ValueError(f"iteration_log2 debe estar entre 7 y 30, recibido: {iteration_log2}")

    salt = get_random_salt(8)
    setting = f'$P${ITOA64[iteration_log2]}{salt}'

    # Convertir la contraseña a formato binario una sola vez
    password_bytes = password.encode('utf-8')
    count = 1 << iteration_log2
    
    # Primer paso: mezclar el salt con la contraseña y crear el hash inicial
    hash_val = hashlib.md5(salt.encode('utf-8') + password_bytes).digest()

    # Repetir el proceso muchas veces para hacer el hash más difícil de romper
    # Con iteration_log2=14, esto se repite 16,384 veces
    for _ in range(count):
        hash_val = hashlib.md5(hash_val + password_bytes).digest()

    encoded = encode64(hash_val, 16)
    return setting + encoded[:22]


def main():
    """Función principal que se ejecuta cuando inicias el programa."""
    try:
        password = input("Introduce la contraseña: ").strip()
        if not password:
            print("Error: Debes escribir una contraseña. Esto no puede estar vacío, por que no tiene sentido. Vuelve a ejecutarlo")
            return
        
        print("\nHash PHPass generado:")
        print(phpass_hash(password))
    except KeyboardInterrupt:
        print("\n\nOperación cancelada por el usuario")
    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()