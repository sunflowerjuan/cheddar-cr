from datetime import datetime

class Logger:
    @staticmethod
    def info(mensaje):
        print(f"[ℹ️ ] {mensaje}")

    @staticmethod
    def success(mensaje):
        print(f"[✅] {mensaje}")

    @staticmethod
    def error(mensaje):
        print(f"[❌] {mensaje}")

    @staticmethod
    def warning(mensaje):
        print(f"[⚠️ ] {mensaje}")

    @staticmethod
    def debug(mensaje):
        print(f"[🔍] {mensaje}")
