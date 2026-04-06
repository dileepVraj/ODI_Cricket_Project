from core.services.builder._data_builder import ReportDataBuilder
from core.services.builder._form_assembler import FormDataAssembler
from core.services.builder._matrix_generator import MatrixReportGenerator


class ReportBuilder(ReportDataBuilder, FormDataAssembler, MatrixReportGenerator):
    """Hub -- MRO: ReportBuilder -> ReportDataBuilder -> FormDataAssembler -> MatrixReportGenerator."""

    pass


__all__ = ["ReportBuilder"]
