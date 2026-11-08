"""Gestor de internacionalización (i18n) para el sistema clínico.

El módulo mantiene una única instancia compartida de :class:`LanguageManager`
que carga los catálogos JSON de ``assets/locales`` y expone una API simple para
traducir claves planas (por ejemplo ``"pacientes.title"``).

Características principales:

* Idioma por defecto: español (``es``).
* Fallback en cascada: idioma actual -> español -> valor por defecto -> clave.
* Notificación a las vistas mediante callbacks cuando cambia el idioma.
* Sin dependencias externas y sin acoplarse a la ontología ni a los controladores.

El catálogo se guarda como UTF-8 para conservar tildes, eñes y emojis.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Self

logger = logging.getLogger(__name__)

#: Ruta absoluta a la carpeta de catálogos de idioma.
LOCALES_DIR = Path(__file__).resolve().parent.parent / "assets" / "locales"

#: Idioma base y de respaldo.
DEFAULT_LANGUAGE = "es"

#: Idiomas soportados por la aplicación.
SUPPORTED_LANGUAGES = ("es", "en")


class LanguageError(Exception):
    """Error al cargar o validar un catálogo de idioma."""


class LanguageManager:
    """Instancia compartida (Singleton) para resolver traducciones.

    Uso típico::

        from logica.language_manager import language_manager

        language_manager.get("pacientes.title")
        language_manager.t("common.no_patient")
        language_manager.set_language("en")
    """

    _instance: LanguageManager | None = None

    def __new__(cls, *args, **kwargs) -> Self:
        if cls._instance is None:
            instance = super().__new__(cls)
            instance._initialized = False
            cls._instance = instance
        return cls._instance

    def __init__(
        self,
        default_language: str = DEFAULT_LANGUAGE,
        locales_dir: str | Path | None = None,
    ) -> None:
        """Inicializa el gestor cargando el idioma por defecto.

        Solo la primera construcción tiene efecto; las siguientes devuelven la
        misma instancia para que todas las vistas compartan el estado.
        """
        if getattr(self, "_initialized", False):
            return

        self._locales_dir = Path(locales_dir) if locales_dir else LOCALES_DIR
        self._default_language = self._normalize(default_language)
        if self._default_language not in SUPPORTED_LANGUAGES:
            self._default_language = DEFAULT_LANGUAGE

        self._language = self._default_language
        self._translations: dict[str, dict[str, str]] = {}
        self._listeners: list[Callable[[str], None]] = []

        try:
            self._load_language(self._default_language)
        except LanguageError as exc:
            # La aplicación puede seguir arrancando mostrando las claves.
            logger.error("No se pudo cargar el idioma por defecto: %s", exc)

        self._initialized = True

    # ------------------------------------------------------------------
    # Propiedades
    # ------------------------------------------------------------------
    @property
    def current_language(self) -> str:
        """Código del idioma activo (``es`` o ``en``)."""
        return self._language

    @property
    def default_language(self) -> str:
        """Código del idioma base usado como respaldo."""
        return self._default_language

    @property
    def available_languages(self) -> tuple[str, ...]:
        """Idiomas disponibles para la interfaz."""
        return SUPPORTED_LANGUAGES

    @property
    def locales_dir(self) -> Path:
        """Carpeta donde se leen los catálogos JSON."""
        return self._locales_dir

    # ------------------------------------------------------------------
    # Cambio e identificación de idioma
    # ------------------------------------------------------------------
    def set_language(self, lang_code: str) -> bool:
        """Cambia el idioma activo y notifica a los listeners.

        Devuelve ``True`` si el idioma es válido y pudo cargarse. Si el archivo
        no existe o es inválido, conserva el idioma actual y devuelve ``False``.
        """
        code = self._normalize(lang_code)
        if code not in SUPPORTED_LANGUAGES:
            logger.warning("Idioma no soportado: %r", lang_code)
            return False

        if code not in self._translations:
            try:
                self._load_language(code)
            except LanguageError as exc:
                logger.error("No se pudo cambiar al idioma %r: %s", code, exc)
                return False

        if code == self._language:
            return True

        self._language = code
        self._notify_listeners()
        return True

    def toggle_language(self) -> str:
        """Alterna entre español e inglés y devuelve el idioma resultante."""
        target = "en" if self._language == "es" else "es"
        self.set_language(target)
        return self._language

    def reload(self) -> bool:
        """Recarga desde disco el catálogo del idioma activo."""
        try:
            self._translations.pop(self._language, None)
            self._load_language(self._language)
        except LanguageError as exc:
            logger.error("No se pudo recargar el idioma %r: %s", self._language, exc)
            return False
        self._notify_listeners()
        return True

    # ------------------------------------------------------------------
    # Traducción
    # ------------------------------------------------------------------
    def get(self, key: str, default: str = "") -> str:
        """Devuelve la traducción de ``key``.

        Orden de búsqueda: idioma actual -> idioma por defecto -> ``default``
        -> la propia clave. Así una clave sin traducir en inglés muestra el
        texto en español en lugar de un identificador técnico.
        """
        if not isinstance(key, str):
            return default

        value = self._translations.get(self._language, {}).get(key)
        if value is not None:
            return value

        if self._language != self._default_language:
            value = self._translations.get(self._default_language, {}).get(key)
            if value is not None:
                return value

        return default if default else key

    def t(self, key: str, default: str = "") -> str:
        """Alias corto de :meth:`get`."""
        return self.get(key, default)

    def format(self, key: str, default: str = "", **kwargs: object) -> str:
        """Devuelve la traducción aplicando ``str.format`` con ``kwargs``.

        Si faltan parámetros o la plantilla es inválida, devuelve el texto sin
        formatear para no romper la interfaz.
        """
        template = self.get(key, default)
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            logger.warning("No se pudo formatear la clave %r: %r", key, template)
            return template

    def has_key(self, key: str, language: str | None = None) -> bool:
        """Indica si una clave existe en el catálogo indicado."""
        code = self._normalize(language) if language else self._language
        return key in self._translations.get(code, {})

    # ------------------------------------------------------------------
    # Listeners
    # ------------------------------------------------------------------
    def add_listener(self, callback: Callable[[str], None]) -> None:
        """Registra un callback que recibirá el nuevo código de idioma."""
        if not callable(callback):
            raise TypeError("El listener debe ser invocable")
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[str], None]) -> bool:
        """Elimina un callback registrado. Devuelve ``True`` si existía."""
        try:
            self._listeners.remove(callback)
            return True
        except ValueError:
            return False

    def clear_listeners(self) -> None:
        """Elimina todos los listeners registrados."""
        self._listeners.clear()

    @property
    def listener_count(self) -> int:
        """Número de callbacks registrados."""
        return len(self._listeners)

    def _notify_listeners(self) -> None:
        for callback in list(self._listeners):
            try:
                callback(self._language)
            except Exception:
                logger.exception("Error en listener de idioma")

    # ------------------------------------------------------------------
    # Carga de catálogos
    # ------------------------------------------------------------------
    def _load_language(self, lang_code: str) -> None:
        """Lee ``<lang_code>.json`` y lo guarda en la caché de traducciones."""
        path = self._locales_dir / f"{lang_code}.json"
        if not path.is_file():
            raise LanguageError(f"No existe el catálogo de idioma: {path}")

        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except (OSError, UnicodeDecodeError) as exc:
            raise LanguageError(f"No se pudo leer {path}: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise LanguageError(f"JSON inválido en {path}: {exc}") from exc

        if not isinstance(data, dict):
            raise LanguageError(f"El catálogo {path} debe ser un objeto JSON")

        catalog: dict[str, str] = {}
        for key, value in data.items():
            if isinstance(key, str) and isinstance(value, str):
                catalog[key] = value
            else:
                logger.warning("Entrada ignorada en %s: %r", path.name, key)

        self._translations[lang_code] = catalog

    @staticmethod
    def _normalize(lang_code: str) -> str:
        """Normaliza variantes como ``es-ES`` o ``en_US`` a ``es``/``en``."""
        if not isinstance(lang_code, str):
            return ""
        return lang_code.strip().replace("-", "_").split("_", 1)[0].lower()

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    @classmethod
    def instance(cls) -> Self:
        """Devuelve la instancia compartida, creándola si es necesario."""
        return cls()

    def __repr__(self) -> str:
        return (
            f"LanguageManager(language={self._language!r}, "
            f"default={self._default_language!r}, "
            f"keys={len(self._translations.get(self._language, {}))})"
        )


#: Instancia compartida que deben importar las vistas.
language_manager = LanguageManager()


def t(key: str, default: str = "") -> str:
    """Atajo funcional para traducir una clave."""
    return language_manager.t(key, default)


def set_language(lang_code: str) -> bool:
    """Atajo funcional para cambiar el idioma activo."""
    return language_manager.set_language(lang_code)


# ----------------------------------------------------------------------
# Prueba integrada: ``python -m logica.language_manager``
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    manager = LanguageManager.instance()
    errors: list[str] = []

    print("Directorio de locales:", manager.locales_dir)
    print("Idioma por defecto:", manager.default_language)
    print("Idioma activo:", manager.current_language)

    catalogs: dict[str, dict[str, str]] = {}
    for code in SUPPORTED_LANGUAGES:
        path = manager.locales_dir / f"{code}.json"
        try:
            catalogs[code] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"No se pudo leer {path}: {exc}")
            catalogs[code] = {}
        else:
            print(f"OK  {path.name}: {len(catalogs[code])} claves")

    es_keys = set(catalogs.get("es", {}))
    en_keys = set(catalogs.get("en", {}))
    if es_keys - en_keys:
        errors.append(f"Claves ausentes en en.json: {sorted(es_keys - en_keys)}")
    if en_keys - es_keys:
        errors.append(f"Claves extra en en.json: {sorted(en_keys - es_keys)}")
    if not es_keys:
        errors.append("es.json no contiene claves")
    if not en_keys:
        errors.append("en.json no contiene claves")

    # Comprobación de lectura desde el manager
    if "app.window_title" not in catalogs["es"]:
        errors.append("No se encontró 'app.window_title' en es.json")
    if "app.window_title" not in catalogs["en"]:
        errors.append("No se encontró 'app.window_title' en en.json")

    # Cambio de idioma y notificación de listeners
    notifications: list[str] = []
    manager.add_listener(notifications.append)

    if not manager.set_language("en"):
        errors.append("No se pudo cambiar el idioma a 'en'")
    if manager.current_language != "en":
        errors.append("El idioma activo no es 'en'")
    if notifications != ["en"]:
        errors.append(f"Notificaciones inesperadas al cambiar a 'en': {notifications}")
    if manager.get("common.no_patient") != catalogs["en"].get("common.no_patient"):
        errors.append("La traducción en inglés de 'common.no_patient' no coincide")

    # Fallback: una clave inexistente en el idioma actual usa el valor por defecto
    if manager.get("clave.inexistente", "fallback") != "fallback":
        errors.append("El fallback de get() no funciona")

    # Regreso al español
    if not manager.set_language("es"):
        errors.append("No se pudo volver al idioma 'es'")
    if manager.current_language != "es":
        errors.append("El idioma activo no es 'es'")
    if notifications != ["en", "es"]:
        errors.append(f"Notificaciones inesperadas al volver a 'es': {notifications}")

    manager.remove_listener(notifications.append)

    if errors:
        print("\nFALLÓ LA PRUEBA:")
        for error in errors:
            print(" -", error)
        sys.exit(1)

    print("\nOK: catálogos leídos, claves alineadas y cambio de idioma verificado.")
