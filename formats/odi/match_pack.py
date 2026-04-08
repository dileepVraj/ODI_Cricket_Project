"""Backward compatibility shim for ODI match pack generation."""
from formats.odi.match_pack._assembler import MatchPackAssembler
from formats.odi.match_pack._orchestrator import MatchPackOrchestrator
from formats.odi.match_pack._persister import MatchPackPersister

MatchPackGenerator = MatchPackOrchestrator

__all__ = [
    "MatchPackAssembler",
    "MatchPackGenerator",
    "MatchPackOrchestrator",
    "MatchPackPersister",
]
