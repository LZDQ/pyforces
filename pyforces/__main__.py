from pyforces.cmd.main import main as cmd_main

def main():
    try:
        cmd_main()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
