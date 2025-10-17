from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .kmir import KMIR

if TYPE_CHECKING:
    from pathlib import Path


class KompiledSMIR(ABC):
    @abstractmethod
    def create_kmir(self, *, bug_report_file: Path | None = None) -> KMIR: ...


@dataclass
class KompiledSymbolic(KompiledSMIR):
    haskell_dir: Path
    llvm_lib_dir: Path

    def create_kmir(self, *, bug_report_file: Path | None = None) -> KMIR:
        return KMIR(
            definition_dir=self.haskell_dir,
            llvm_library_dir=self.llvm_lib_dir,
            bug_report=bug_report_file,
        )


@dataclass
class KompiledConcrete(KompiledSMIR):
    llvm_dir: Path

    def create_kmir(self, *, bug_report_file: Path | None = None) -> KMIR:
        return KMIR(
            definition_dir=self.llvm_dir,
            bug_report=bug_report_file,
        )
