"""
Utilidades generales para el sistema de tickets
"""
import hashlib
import os
from django.core.files.storage import default_storage
from django.conf import settings


def calcular_checksum(archivo):
    """
    Calcula el checksum SHA-256 de un archivo
    """
    hash_sha256 = hashlib.sha256()
    for chunk in archivo.chunks():
        hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def validar_tamaño_archivo(archivo, max_size_mb=25):
    """
    Valida que el archivo no exceda el tamaño máximo permitido
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    return archivo.size <= max_size_bytes


def obtener_tipo_mime(archivo):
    """
    Obtiene el tipo MIME de un archivo basado en su extensión
    """
    extension = os.path.splitext(archivo.name)[1].lower()
    tipos_mime = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.webp': 'image/webp',
        '.mp4': 'video/mp4',
        '.mov': 'video/quicktime',
        '.pdf': 'application/pdf',
    }
    return tipos_mime.get(extension, 'application/octet-stream')


def generar_nombre_unico(archivo):
    """
    Genera un nombre único para un archivo manteniendo la extensión original
    """
    import uuid
    extension = os.path.splitext(archivo.name)[1]
    return f"{uuid.uuid4()}{extension}"


def formatear_tamaño_archivo(bytes_size):
    """
    Convierte bytes a formato legible (KB, MB, GB)
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def es_imagen(archivo):
    """
    Verifica si un archivo es una imagen
    """
    extension = os.path.splitext(archivo.name)[1].lower()
    return extension in ['.jpg', '.jpeg', '.png', '.webp']


def es_video(archivo):
    """
    Verifica si un archivo es un video
    """
    extension = os.path.splitext(archivo.name)[1].lower()
    return extension in ['.mp4', '.mov']


def es_documento(archivo):
    """
    Verifica si un archivo es un documento
    """
    extension = os.path.splitext(archivo.name)[1].lower()
    return extension in ['.pdf']