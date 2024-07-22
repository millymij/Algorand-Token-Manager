import sys
from pathlib import Path

# declare path of root of the project, src folder and config folder
root_dir = Path(__file__).parent.parent
src_dir = root_dir / 'src'
config_dir = root_dir / 'config'
sys.path.append(str(src_dir))
sys.path.append(str(config_dir))