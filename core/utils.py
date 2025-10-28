"""
Utilidades generales para el sistema de tickets
"""
import hashlib
import os
from django.core.files.storage import default_storage
from django.conf import settings

import uuid

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


def generar_nombre_unico(archivo):
    """
    Genera un nombre único para un archivo manteniendo la extensión original
    Args:
        archivo: Puede ser un string (nombre/ruta) o un objeto archivo
    """
    # Si es un objeto archivo, obtener el nombre
    if hasattr(archivo, 'name'):
        nombre = archivo.name
    else:
        # Si es un string, usarlo directamente
        nombre = str(archivo)
    
    extension = os.path.splitext(nombre)[1]
    return f"{uuid.uuid4()}{extension}"



def es_imagen(archivo):
    """
    Verifica si un archivo es una imagen basándose en su extensión
    Args:
        archivo: Puede ser un string (nombre/ruta) o un objeto archivo
    """
    # Si es un objeto archivo, obtener el nombre
    if hasattr(archivo, 'name'):
        nombre = archivo.name
    else:
        # Si es un string, usarlo directamente
        nombre = str(archivo)
    
    extension = os.path.splitext(nombre)[1].lower()
    extensiones_imagen = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
    return extension in extensiones_imagen


def es_video(archivo):
    """
    Verifica si un archivo es un video basándose en su extensión
    Args:
        archivo: Puede ser un string (nombre/ruta) o un objeto archivo
    """
    # Si es un objeto archivo, obtener el nombre
    if hasattr(archivo, 'name'):
        nombre = archivo.name
    else:
        # Si es un string, usarlo directamente
        nombre = str(archivo)
    
    extension = os.path.splitext(nombre)[1].lower()
    extensiones_video = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v']
    return extension in extensiones_video


def es_documento(archivo):
    """
    Verifica si un archivo es un documento basándose en su extensión
    Args:
        archivo: Puede ser un string (nombre/ruta) o un objeto archivo
    """
    # Si es un objeto archivo, obtener el nombre
    if hasattr(archivo, 'name'):
        nombre = archivo.name
    else:
        # Si es un string, usarlo directamente
        nombre = str(archivo)
    
    extension = os.path.splitext(nombre)[1].lower()
    extensiones_documento = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.odt', '.ods', '.ppt', '.pptx']
    return extension in extensiones_documento


def obtener_tipo_mime(archivo):
    """
    Obtiene el tipo MIME de un archivo
    Args:
        archivo: Puede ser un string (nombre/ruta) o un objeto archivo
    """
    import mimetypes
    
    # Si es un objeto archivo, obtener el nombre
    if hasattr(archivo, 'name'):
        nombre = archivo.name
    else:
        # Si es un string, usarlo directamente
        nombre = str(archivo)
    
    tipo_mime, _ = mimetypes.guess_type(nombre)
    return tipo_mime or 'application/octet-stream'


def formatear_tamaño_archivo(tamaño_bytes):
    """
    Convierte el tamaño en bytes a un formato legible
    Args:
        tamaño_bytes: Tamaño en bytes (int)
    Returns:
        String con el tamaño formateado (ej: "1.5 MB")
    """
    if tamaño_bytes < 1024:
        return f"{tamaño_bytes} B"
    elif tamaño_bytes < 1024 * 1024:
        return f"{tamaño_bytes / 1024:.2f} KB"
    elif tamaño_bytes < 1024 * 1024 * 1024:
        return f"{tamaño_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{tamaño_bytes / (1024 * 1024 * 1024):.2f} GB"