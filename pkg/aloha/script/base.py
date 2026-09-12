import argparse
import importlib
import sys


def main():
    if "" not in sys.path:  # if start from script, cwd is not include in sys.path
        sys.path.insert(0, "")

    parser = argparse.ArgumentParser()
    parser.add_argument("cmd")
    args, _ = parser.parse_known_args()

    cmd = args.cmd
    module = f"{__package__}.{cmd}"
    try:
        module = importlib.import_module(module)
    except ImportError as e:
        print(f"Invalid sub-command: {cmd}\n\tFailed to import: {module}")
        print(str(e))
        sys.exit(-1)

    sys.argv.pop(0)
    print("aloha command options: {}".format("".join(sys.argv)))
    func_main = module.main

    sys.exit(func_main())


if __name__ == "__main__":
    main()
