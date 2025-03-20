from dataclasses import dataclass, field

@dataclass
class Subject:
    name: str
    code: str
    url_extension: str
    url_link: str = ""
    year_range: list[int] = field(default_factory=list)
    variants : list[int] = field(default_factory=list)
    papers : list[int] = field(default_factory=list)