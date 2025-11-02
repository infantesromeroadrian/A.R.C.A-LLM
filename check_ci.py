#!/usr/bin/env python3
"""
Script para validar CI localmente antes de push.

Ejecuta las mismas validaciones que el CI:
- Tests unitarios
- Coverage mínimo
- Linting (opcional)

Uso:
    python check_ci.py              # Validación completa
    python check_ci.py --quick      # Solo tests
    python check_ci.py --no-lint    # Skip linting
"""

import sys
import subprocess
from pathlib import Path


class CIChecker:
    """Validador de CI local."""
    
    def __init__(self, quick: bool = False, no_lint: bool = False):
        self.quick = quick
        self.no_lint = no_lint
        self.project_root = Path(__file__).parent
        self.failed = []
    
    def run_command(self, cmd: list, check_name: str) -> bool:
        """Ejecutar comando y reportar resultado."""
        print(f"\n{'='*60}")
        print(f"🔍 Running: {check_name}")
        print(f"{'='*60}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=False,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ {check_name}: PASSED")
                return True
            else:
                print(f"❌ {check_name}: FAILED")
                self.failed.append(check_name)
                return False
        except Exception as e:
            print(f"❌ {check_name}: ERROR - {e}")
            self.failed.append(check_name)
            return False
    
    def check_tests(self) -> bool:
        """Ejecutar tests."""
        if self.quick:
            # Ejecutar solo tests unitarios (sin integration)
            return self.run_command(
                [sys.executable, "-m", "pytest", "tests/unit/", "-v"],
                "Unit Tests (Quick)"
            )
        else:
            return self.run_command(
                [sys.executable, "run_tests.py", "--coverage"],
                "Full Test Suite with Coverage"
            )
    
    def check_coverage(self) -> bool:
        """Validar coverage mínimo."""
        if self.quick:
            return True  # Skip en modo quick
        
        return self.run_command(
            [sys.executable, "-m", "coverage", "report", "--fail-under=60"],
            "Coverage Check (minimum 60%)"
        )
    
    def check_lint(self) -> bool:
        """Ejecutar linting."""
        if self.no_lint:
            print("\n⏭️  Skipping linting (--no-lint)")
            return True
        
        try:
            # Intentar ruff
            result = subprocess.run(
                [sys.executable, "-m", "ruff", "check", "src/"],
                cwd=self.project_root,
                capture_output=True
            )
            
            if result.returncode != 0:
                print("\n⚠️  Ruff found issues (non-blocking)")
                return True  # No-blocking
            else:
                print("\n✅ Linting: PASSED")
                return True
        except FileNotFoundError:
            print("\n⏭️  Ruff not installed, skipping lint")
            return True
    
    def run_all_checks(self) -> bool:
        """Ejecutar todas las validaciones."""
        print("\n" + "="*60)
        print("🚀 A.R.C.A-LLM CI Checker")
        print("="*60)
        
        if self.quick:
            print("⚡ Quick mode: Running fast checks only")
        
        checks = [
            ("Tests", self.check_tests),
            ("Coverage", self.check_coverage),
            ("Linting", self.check_lint),
        ]
        
        for name, check_func in checks:
            check_func()
        
        # Resumen final
        print("\n" + "="*60)
        print("📊 CI CHECK SUMMARY")
        print("="*60)
        
        if not self.failed:
            print("✅ All checks PASSED! Ready to push.")
            print("\nYou can now:")
            print("  git add .")
            print("  git commit -m 'your message'")
            print("  git push origin main")
            return True
        else:
            print("❌ Some checks FAILED:")
            for check in self.failed:
                print(f"   - {check}")
            print("\nPlease fix the issues before pushing.")
            return False


def main():
    """Punto de entrada."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate CI locally before push")
    parser.add_argument("--quick", action="store_true", help="Quick check (unit tests only)")
    parser.add_argument("--no-lint", action="store_true", help="Skip linting")
    
    args = parser.parse_args()
    
    checker = CIChecker(quick=args.quick, no_lint=args.no_lint)
    success = checker.run_all_checks()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

