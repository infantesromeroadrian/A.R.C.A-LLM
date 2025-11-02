#!/usr/bin/env python3
"""
Script para ejecutar tests de A.R.C.A-LLM.

Uso:
    python run_tests.py              # Ejecutar todos los tests
    python run_tests.py --unit       # Solo tests unitarios
    python run_tests.py --integration  # Solo tests de integración
    python run_tests.py --coverage   # Con reporte de cobertura
    python run_tests.py --html       # Generar reporte HTML
    python run_tests.py --fast       # Skip tests lentos
"""

import sys
import subprocess
from pathlib import Path
from typing import List


class TestRunner:
    """Ejecutor de tests con diferentes configuraciones."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.base_cmd = [sys.executable, "-m", "pytest"]
    
    def run(self, args: List[str]) -> int:
        """Ejecutar pytest con los argumentos dados."""
        cmd = self.base_cmd + args
        print(f"\n🧪 Ejecutando: {' '.join(cmd)}\n")
        result = subprocess.run(cmd, cwd=self.project_root)
        return result.returncode
    
    def all_tests(self, coverage: bool = False, html: bool = False) -> int:
        """Ejecutar todos los tests."""
        args = ["tests/", "-v"]
        
        if coverage:
            args.extend(["--cov=src", "--cov-report=term-missing"])
        
        if html:
            args.extend(["--cov-report=html", "--html=reports/test_report.html", "--self-contained-html"])
        
        return self.run(args)
    
    def unit_tests(self, coverage: bool = False) -> int:
        """Ejecutar solo tests unitarios."""
        args = ["tests/unit/", "-v", "-m", "unit"]
        
        if coverage:
            args.extend(["--cov=src", "--cov-report=term-missing"])
        
        return self.run(args)
    
    def integration_tests(self) -> int:
        """Ejecutar solo tests de integración."""
        args = ["tests/integration/", "-v", "-m", "integration"]
        return self.run(args)
    
    def domain_tests(self) -> int:
        """Ejecutar solo tests del dominio."""
        args = ["tests/unit/domain/", "-v"]
        return self.run(args)
    
    def application_tests(self) -> int:
        """Ejecutar solo tests de la capa de aplicación."""
        args = ["tests/unit/application/", "-v"]
        return self.run(args)
    
    def fast_tests(self) -> int:
        """Ejecutar tests rápidos (sin E2E ni lentos)."""
        args = ["tests/", "-v", "-m", "not slow"]
        return self.run(args)
    
    def failed_tests(self) -> int:
        """Re-ejecutar tests que fallaron en la última ejecución."""
        args = ["--lf", "-v"]
        return self.run(args)
    
    def watch_mode(self) -> int:
        """Ejecutar tests en modo watch (requiere pytest-watch)."""
        try:
            cmd = ["ptw", "--", "-v"]
            print(f"\n👀 Modo watch: {' '.join(cmd)}\n")
            result = subprocess.run(cmd, cwd=self.project_root)
            return result.returncode
        except FileNotFoundError:
            print("❌ pytest-watch no instalado. Instalar con: pip install pytest-watch")
            return 1


def print_help():
    """Imprimir ayuda."""
    help_text = """
🧪 A.R.C.A-LLM Test Runner

COMANDOS:
    python run_tests.py                    Ejecutar todos los tests
    python run_tests.py --unit             Solo tests unitarios
    python run_tests.py --integration      Solo tests de integración
    python run_tests.py --domain           Solo tests del dominio
    python run_tests.py --application      Solo tests de aplicación
    python run_tests.py --fast             Tests rápidos (sin E2E)
    python run_tests.py --failed           Re-ejecutar tests que fallaron
    python run_tests.py --watch            Modo watch (auto-reload)
    
OPCIONES:
    --coverage, -c                         Generar reporte de cobertura
    --html, -h                            Generar reporte HTML
    --help                                Mostrar esta ayuda

EJEMPLOS:
    python run_tests.py --unit --coverage      # Tests unitarios con cobertura
    python run_tests.py --integration          # Tests de integración
    python run_tests.py --domain              # Tests del dominio
    python run_tests.py --html                # Todos los tests + HTML report

ESTRUCTURA DE TESTS:
    tests/
    ├── unit/               Tests unitarios (rápidos, sin I/O)
    │   ├── domain/        Tests de Value Objects y Aggregates
    │   ├── application/   Tests de servicios de aplicación
    │   └── infrastructure/  Tests de clientes (mocked)
    ├── integration/       Tests de API (con mocks)
    └── e2e/              Tests end-to-end (con servicios reales)

COBERTURA ACTUAL:
    ✅ Domain Layer:        97-100% coverage (40 tests)
    ✅ Application Layer:   98% coverage (22 tests)
    ✅ Integration Tests:   14 tests (2 skipped)
    📊 Total:              76 tests ejecutables
    """
    print(help_text)


def main():
    """Punto de entrada principal."""
    if len(sys.argv) == 1:
        # Sin argumentos: ejecutar todos los tests
        runner = TestRunner()
        return runner.all_tests()
    
    runner = TestRunner()
    command = sys.argv[1]
    
    # Flags
    coverage = "--coverage" in sys.argv or "-c" in sys.argv
    html = "--html" in sys.argv or "-h" in sys.argv
    
    # Comandos
    if command == "--help":
        print_help()
        return 0
    elif command == "--unit":
        return runner.unit_tests(coverage=coverage)
    elif command == "--integration":
        return runner.integration_tests()
    elif command == "--domain":
        return runner.domain_tests()
    elif command == "--application":
        return runner.application_tests()
    elif command == "--fast":
        return runner.fast_tests()
    elif command == "--failed":
        return runner.failed_tests()
    elif command == "--watch":
        return runner.watch_mode()
    elif command == "--coverage" or command == "-c":
        return runner.all_tests(coverage=True)
    elif command == "--html" or command == "-h":
        return runner.all_tests(coverage=True, html=True)
    else:
        print(f"❌ Comando desconocido: {command}")
        print("Usa '--help' para ver comandos disponibles.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
