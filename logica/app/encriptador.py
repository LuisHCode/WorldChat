from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib
import base64

passphrase = 'ClaveSimetrica'

# Derivar clave AES-256 desde la passphrase
def derivar_clave(passphrase):
    return hashlib.sha256(passphrase.encode("utf-8")).digest()  # 32 bytes

# Encriptar texto plano → binario (guardar en VARBINARY)
def encriptar(texto, passphrase):
    clave = derivar_clave(passphrase)
    cipher = AES.new(clave, AES.MODE_CBC)
    iv = cipher.iv
    cifrado = cipher.encrypt(pad(texto.encode("utf-8"), AES.block_size))
    return iv + cifrado  # concatenamos IV + contenido

# Desencriptar binario (VARBINARY) → texto plano
def desencriptar(binario, passphrase):
    clave = derivar_clave(passphrase)
    iv = binario[:16]
    cifrado = binario[16:]
    cipher = AES.new(clave, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(cifrado), AES.block_size).decode("utf-8")

# --- Solo para pruebas ---
if __name__ == "__main__":
    secreto = "Hola desde WorldChat"
    clave = "MiLlaveSecreta"

    cifrado = encriptar(secreto, clave)
    print("🔐 Encriptado (base64):", base64.b64encode(cifrado).decode())

    descifrado = desencriptar(cifrado, clave)
    print("🔓 Desencriptado:", descifrado)
