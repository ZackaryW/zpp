from importlib.resources import files

from zpp.utils.authored_layers import collect_authored_layer
from zpp.utils.models import AuthoredLayerSnapshot


def load_packaged_default_profile() -> AuthoredLayerSnapshot:
    root = files("zpp.artifacts").joinpath("profiles", "default")
    return collect_authored_layer(root)
