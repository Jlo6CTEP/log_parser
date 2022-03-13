import logging

FORMAT = "[%(levelname)s] [%(asctime)s] %(message)s"
logging.basicConfig(format=FORMAT, datefmt='%d-%b-%Y %H%M:%S')
logger = logging.getLogger("intel_logger")
logger.setLevel(logging.DEBUG)
