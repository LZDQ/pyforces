from pathlib import Path
from pyforces.config import Config
from logging import getLogger

logger = getLogger(__name__)


def do_gen(cfg: Config, name: str | None = None):
    if name:
        templates = {t.name: t for t in cfg.templates}
        if name not in templates:
            print(f"{name} not found, choices are: {' '.join(templates.keys())}")
            return
        template = templates[name]
    elif cfg.default_template != -1:
        template = cfg.templates[cfg.default_template]
    else:
        logger.error("No default template, aborting")
        return
    # get the filename like a.cpp
    f = Path.cwd().parts[-1] + template.path.suffix
    template.generate(f)
