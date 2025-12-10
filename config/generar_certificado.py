#!/usr/bin/env python3
"""
Generador de certificados SSL/TLS self-signed para SpecsNet.

Crea un certificado X.509 personalizado para la institución.
Válido por 10 años, algoritmo RSA 4096 bits.

Uso:
    python generar_certificado.py

Genera:
    - config/server.crt  (certificado público - distribuir a clientes)
    - config/server.key  (clave privada - mantener en servidor)
"""

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta
from pathlib import Path

def generar_certificado(
    organization="TuOrganización",
    country="ES",
    state="Madrid",
    city="Madrid",
    unit="Departamento IT",
    common_name="servidor.local",
    email="admin@tuorganizacion.local",
    days_valid=3650,
):
    """
    Genera un certificado SSL/TLS self-signed personalizado.

    Args:
        organization (str): Nombre de la organización/institución
        country (str): País (código ISO 2 letras)
        state (str): Provincia/Estado
        city (str): Ciudad/Localidad
        unit (str): Unidad/Departamento
        common_name (str): Nombre del servidor (CN)
        email (str): Email de contacto
        days_valid (int): Días de validez (default: 3650 = 10 años)
    """
    print("[*] Generando certificado SSL/TLS personalizado para SpecsNet...")
    print()

    # Ruta donde guardar los certificados
    config_dir = Path(__file__).parent / "config"
    config_dir.mkdir(exist_ok=True)

    cert_path = config_dir / "server.crt"
    key_path = config_dir / "server.key"

    # Verificar si ya existen
    if cert_path.exists() and key_path.exists():
        print("⚠️  Los certificados ya existen en config/")
        response = input("¿Deseas regenerarlos? (s/n): ").lower()
        if response != "s":
            print("❌ Operación cancelada")
            return False

    # Paso 1: Generar clave privada RSA 4096
    print("[1/4] Generando clave privada RSA 4096...")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )
    print("     ✅ Clave privada generada")

    # Paso 2: Crear datos del certificado
    print("[2/4] Creando datos del certificado...")
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, country),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state),
            x509.NameAttribute(NameOID.LOCALITY_NAME, city),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, unit),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ]
    )
    print("     ✅ Datos de identificación configurados")

    # Paso 3: Crear y firmar certificado
    print("[3/4] Creando certificado self-signed...")
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=days_valid))
        .add_extension(
            x509.SubjectAlternativeName(
                [
                    x509.DNSName("servidor.local"),
                    x509.DNSName("localhost"),
                    x509.DNSName("127.0.0.1"),
                ]
            ),
            critical=False,
        )
        .add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        )
        .sign(private_key, hashes.SHA256())
    )
    print("     ✅ Certificado firmado con SHA256")

    # Paso 4: Guardar archivos
    print("[4/4] Guardando archivos...")

    # Guardar clave privada
    with open(key_path, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
    print(f"     ✅ Clave privada guardada: {key_path}")

    # Guardar certificado
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    print(f"     ✅ Certificado guardado: {cert_path}")

    # Mostrar resumen
    print()
    print("=" * 70)
    print("✅ CERTIFICADO GENERADO EXITOSAMENTE")
    print("=" * 70)
    print()
    print("📋 INFORMACIÓN DEL CERTIFICADO:")
    print(f"   • Organización: {organization}")
    print(f"   • País: {country}")
    print(f"   • Localidad: {city}")
    print(f"   • Departamento: {unit}")
    print(f"   • Servidor: {common_name}")
    print(f"   • Email: {email}")
    print()
    print(f"📅 VALIDEZ:")
    print(f"   • Válido desde: {datetime.utcnow().strftime('%Y-%m-%d')}")
    print(f"   • Válido hasta: {(datetime.utcnow() + timedelta(days=days_valid)).strftime('%Y-%m-%d')}")
    print(f"   • Duración: {days_valid} días ({days_valid // 365} años)")
    print()
    print(f"🔐 ARCHIVOS:")
    print(f"   • Certificado (público): {cert_path}")
    print(f"   • Clave privada (secreto): {key_path}")
    print()
    print("⚠️  INSTRUCCIONES IMPORTANTES:")
    print()
    print("1️⃣  EN EL SERVIDOR:")
    print(f"   • Los archivos server.crt y server.key ya están en {config_dir}/")
    print("   • El servidor usará estos archivos automáticamente")
    print()
    print("2️⃣  EN CADA CLIENTE:")
    print(f"   • Copiar 'server.crt' a: config/server.crt")
    print("   • El cliente lo usará para verificar la identidad del servidor")
    print()
    print("3️⃣  SEGURIDAD:")
    print(f"   • 🔒 NUNCA compartir server.key públicamente")
    print(f"   • 📄 server.crt es seguro compartir (es público)")
    print(f"   • ✅ Agregar server.key a .gitignore")
    print()
    print("4️⃣  VERIFICAR CERTIFICADO:")
    print(f"   python -m cryptography.hazmat.backends.openssl.backend")
    print(f"   openssl x509 -in config/server.crt -text -noout  (si tienes openssl)")
    print()
    print("=" * 70)

    return True


if __name__ == "__main__":
    try:
        # Generar certificado con valores por defecto
        # Puedes cambiar estos valores según tu institución
        generar_certificado(
            organization="SpecsNet",
            country="ES",
            state="Madrid",
            city="Madrid",
            unit="Departamento IT",
            common_name="servidor.local",
            email="admin@specsnet.local",
            days_valid=3650,  # 10 años
        )
    except Exception as e:
        print()
        print(f"❌ ERROR al generar certificado: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
