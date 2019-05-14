from modules.bbox_hierarchy import *
from modules.parser import *

ROOT_DIR = ''
DEFAULT_OID_DIR = os.path.join(ROOT_DIR, 'OID')

if __name__ == '__main__':
    args = parser_arguments()
    bbox_images(args, DEFAULT_OID_DIR)
