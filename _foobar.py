import sys
import os
import subprocess
import argparse

def send_and_print(proc, data):
    # try:
    #     outputs, errors = proc.communicate(input=b"(+ 1 2 3)", timeout=1)
    # except subprocess.TimeoutExpired:
    #     proc.kill()
    #     outputs, errors = proc.communicate()

    proc.stdin.write(bytes("{}\n".format(data), "utf-8"))

    outputs = proc.stdout.readline()

    print(" Outputs")
    print("=======================")
    print(outputs.decode("utf-8"))
    print()
    return outputs

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", type=str,
                        help="Command to execute")
    args = parser.parse_args(argv[1:]) 

    proc = subprocess.Popen(args.cmd,
                            bufsize=0,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)

    send_and_print(proc, "(+ 1 2 3)")
    send_and_print(proc, "(* a b c)")
    send_and_print(proc, "foobar")
    send_and_print(proc, "[1 2]")


    proc.terminate()

    return 


if __name__ == "__main__":
    main(sys.argv)
