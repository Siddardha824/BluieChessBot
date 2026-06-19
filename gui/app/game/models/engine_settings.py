from dataclasses import dataclass

@dataclass
class EngineSettings:
    constraint_mode: str = "Depth"
    max_depth: int = 3
    max_time_ms: int = 1000
    max_nodes: int = 10000
    engine_path: str = ""
