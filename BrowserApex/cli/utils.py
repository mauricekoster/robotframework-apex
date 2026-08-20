from pathlib import Path
import tomllib
from jinja2 import FileSystemLoader, Environment, ChoiceLoader, PackageLoader, TemplateNotFound, TemplateSyntaxError

def get_config_path():
    path = Path().cwd()
    root = path.drive + path.root
    while str(path) != str(root):
        if (path / "rfapex.toml").exists():
            return path
        path = path.parent

    return None

def get_config(path=None):
    if path is None:
        path = get_config_path()

    with open(path / "rfapex.toml", "rb") as f:
        cnf = tomllib.load(f)
    return cnf


def get_template(template_name, template_path: Path):
    default_loader = ChoiceLoader(
        [FileSystemLoader(template_path / "templates"), PackageLoader(__package__, "templates")]
    )
    env = Environment(loader=default_loader)
    if not template_name.endswith(".template") and not template_name.endswith(".sample"):
        template_name += ".template"
    try:
        template = env.get_template(template_name)
        return template
    except TemplateNotFound:
        print("Template not found")
        return None

    except TemplateSyntaxError:
        print("Template has syntax error")
        return None
    