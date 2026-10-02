from pathlib import Path
import sys
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



def _get_export_and_type(cnf):
    if 'export' not in cnf:
        raise RuntimeWarning(f"No config for exported application. Section: '[export]'")

    folder  = cnf['export'].get('folder', None)
    if folder is None:
        raise RuntimeWarning(f"No config for 'folder' in section [export]")

    folder = Path(folder)
    if not folder.exists():
        raise RuntimeWarning(f"Configure 'folder' in section [export] does not exist.")

    app_type = cnf['export'].get('type', 'apx')

    if app_type not in ['yaml', 'apx']:
        raise RuntimeWarning(f"Unsupported file format {app_type}. Use 'apx' or 'yaml'")
                    
    return folder, app_type


def get_page_file(cnf, page_id) -> Path:
    
    try:
        folder, app_type = _get_export_and_type(cnf)
    except RuntimeWarning as e:
        print(e)
        sys.exit(2)
    

    match app_type:
        case "apx":
            p = folder / "pages"
            page_fn = list(p.glob(f"p{page_id:05d}*.apx"))
            print(page_fn)
            if page_fn:
                p = folder / "pages" / page_fn[-1]
            else:
                print(f"File {p} does not exists.")
                sys.exit(2)
        case "yaml":
            page_fn = f"p{page_id:05d}.yaml"
            p = folder / "pages" / page_fn
            if not p.exists():
                print(f"File {p} does not exists.")
                sys.exit(2)

    return p


def get_breadcrumb_file(cnf) -> Path:

    try:
        folder, app_type = _get_export_and_type(cnf)
    except RuntimeWarning as e:
        print(e)
        sys.exit(2)

    match app_type:
        case "apx":
            p = folder / "shared-components" / "breadcrumbs.apx"
        case "yaml":
            p = folder / "shared_components" / "breadcrumbs.yaml"

    if not p.exists():
        print(f"File {p} does not exists.")
        return None

    return p