import configparser

from dataclasses import dataclass


@dataclass
class Sections:
    raw_sections: dict

    def __post_init__(self):
        for section_key, section_value in self.raw_sections.items():
            setattr(self, section_key, SectionContent(section_value.items()))


@dataclass
class SectionContent:
    raw_section_content: dict

    def __post_init__(self):
        for section_content_k, section_content_v in self.raw_section_content:
            setattr(self, section_content_k, section_content_v)


class Config(Sections):
    def __init__(self, raw_config_parser):
        Sections.__init__(self, raw_config_parser)

raw_config = configparser.ConfigParser()
raw_config.read('ab_project/config/config.ini')
app_config = Config(raw_config)
