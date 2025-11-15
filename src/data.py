import os
import glob
from dataclasses import dataclass, field
from typing import List


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REFSPEC_DIR = os.path.join(BASE_DIR, "..", "refspec")


def load_styles() -> List[str]:
    """
    Reads refspec/*.html and returns a list of filenames without extension.
    """
    pattern = os.path.join(REFSPEC_DIR, "*.html")
    files = glob.glob(pattern)

    return [
        os.path.splitext(os.path.basename(f))[0]
        for f in files
    ]


@dataclass
class UIData:
    """
    Stores all values needed to populate the web interface.
    """
    styles: List[str] = field(default_factory=load_styles)
    order_options: List[str] = field(default_factory=lambda: ["asc", "desc"])
    group_options: List[str] = field(default_factory=lambda: ["year", "month", "author"])
