import logging

FORMAT = "[%(levelname)s] %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger("intel_logger")
logger.setLevel(logging.DEBUG)
