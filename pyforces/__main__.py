from pyforces.cmd.main import main
import logging
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
