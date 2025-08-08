from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pyk.kast.pretty import PrettyPrinter, indent

_LOGGER: logging.Logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from pyk.kore.syntax import Definition


class KMIRPrettyPrinter(PrettyPrinter):
    """
    Custom Pretty Printer for improved ListItem display formatting.
    Formats ListItem elements with line breaks for better readability.
    """

    def __init__(self, definition: Definition) -> None:
        """
        Initialize KMIR Pretty Printer

        Args:
            definition: K definition
        """
        super().__init__(definition)
        self.symbol_table['ListItem'] = lambda *args: 'ListItem (' + (indent(', '.join(args))).strip() + ')\n'
