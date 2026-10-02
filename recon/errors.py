class ReadError(ValueError):
    """Input cannot be represented as a rectangular table."""


class ReconError(ValueError):
    """Base class for user-facing recon-helper errors."""


class RuleConfigError(ReconError):
    """Rule configuration is invalid."""


class ReportError(ReconError):
    """Report cannot be generated or validated."""


class BenchmarkError(ReconError):
    """Benchmark configuration or execution failed."""
