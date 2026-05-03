"""BaseStrategy — what strategy authors implement.

Stateless: run(data, ctx) -> (output, ctx). The framework owns ctx
persistence (Redis); the strategy just reads/writes it.

DataBundle (which carries pandas DataFrames) lives in gaemini-core to
keep this contracts package pandas-free. Type checkers resolve DataBundle
via the TYPE_CHECKING gate when both packages are installed.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from gaemini_contracts.types.context import StrategyContext
from gaemini_contracts.types.output import OUTPUT_TYPE_NAMES, OutputType

if TYPE_CHECKING:
    # Imported only by type checkers; runtime never touches pandas.
    from gaemini_core.domain.types import DataBundle  # type: ignore[import-not-found]


@runtime_checkable
class BaseStrategy(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def output_type(self) -> OUTPUT_TYPE_NAMES: ...

    @property
    def data_config(self) -> dict[str, Any]: ...

    def run(
        self, data: "DataBundle", ctx: StrategyContext
    ) -> tuple[OutputType, StrategyContext]: ...

    def on_params_changed(
        self,
        old_params: dict[str, Any],
        new_params: dict[str, Any],
        ctx: StrategyContext,
    ) -> StrategyContext:
        """Default no-op; override to invalidate caches when params change."""
        return ctx
