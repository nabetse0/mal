import os
import sys
import re
import argparse
import atexit
import signal
import subprocess


# ;; Message to be printed out
# ;;; Just a comment
# ;>>> A command for configuring the test
# ;  This is unexpected.  Need to error out for some reason
# else  This is a form to be fed into the mal implementation

# ;=> A return value
# ;/ Program output (not a return value but more like an error message)

TEST_FILE = r"C:\Users\schang2\dev\fun\mal\impls\tests\step1_read_print.mal"

RE_TEST_COMMAND = re.compile("([a-zA-Z0-9_.]+)\s*=\s*([a-zA-Z0-9_.]+)")
RE_REPL_REPLY = re.compile("(user> )?(.*)")

def parse_test_command(line):
    results = {}
    matching = RE_TEST_COMMAND.findall(line)
    for key, val in matching:
        results[key] = val.lower() == "true"
    return results

def read_test(test_fname):
    re_blankline = re.compile("^\s*$")
    re_msg = re.compile("^;;\s*(.*)")
    re_cmd = re.compile("^;>>>\s*(.*)")
    re_ret = re.compile("^;=>(.*)")
    re_out = re.compile("^;/(.*)")

    line_num = 0

    settings = {
        "soft": False,
        "deferrable": False,
        "optional": False,
        "out": "",
        "ret": "",
    }

    read_output = False
    test = None

    with open(test_fname) as fobj:

        test = dict(settings)

        for line in fobj:
            # print("LINE:{} read_output:{}".format(line.strip(), read_output))
            if read_output:
                m = re_out.match(line)
                if m:
                    test["out"] = m.group(1)
                    line_num += 1
                    continue

                m = re_ret.match(line)
                if m:
                    test["ret"] = m.group(1)
                    line_num += 1
                    test["line_number"] = line_num
                    yield test
                    # Switch to scanning for an input
                    read_output = False
                    test = dict(settings)
                    continue
                else:
                    # We've encountered a line that does not match an
                    # output, so assume it's an input.  We still need
                    # to continue processing this line below--hence,
                    # no 'continue' here.
                    test["ret"] = ""
                    test["line_number"] = line_num
                    yield test
                    # Switch to scanning for an input
                    read_output = False
                    test = dict(settings)

            if not read_output:
                if re_blankline.match(line):
                    line_num += 1
                    continue  # Ignore blank lines

                if line.startswith(";;;"):
                    line_num += 1
                    continue  # ';;;' is a comment.  Ignore.

                m = re_msg.match(line)  # ';;' is a message to be printed out
                if m:
                    test["msg"] = m.group(1)
                    line_num += 1
                    continue

                cmds = parse_test_command(line)
                for k in cmds:
                    if k in settings:
                        settings[k] = cmds[k]

                if cmds:
                    line_num += 1
                    continue

                if line.startswith(";"):
                    raise RuntimeError("Unrecognized input (line {}): {}".format(line_num, line))

                # If none of the above are caught, assume it's the mal input
                test["form"] = line.rstrip()
                line_num += 1

                # On the next line, scan for an output
                read_output = True  


def send_recv(proc, data):
    proc.stdin.write(bytes("{}\n".format(data), "utf-8"))

    output = proc.stdout.readline().decode("utf-8")

    m = RE_REPL_REPLY.match(output)
    if m:
        return m.group(2)
    else:
        raise RuntimeError("Failed to parse, {}".format(output))

                
def run_test(test_fname, mal_cmd):
    proc = subprocess.Popen(mal_cmd,
                            bufsize=0,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)

    count_test = 0
    count_pass = 0
    count_fail = 0
    count_fail_soft = 0
    failures = []

    for test in read_test(test_fname):
        if "msg" in test:
            print()
            print("-" * 80)
            print(test["msg"])
            print("-" * 80)

        print("Test {}: '{}' --> '{}', '{}'".format(
            count_test,
            test["form"],
            test["ret"],
            test["out"] if "out" in test else "",
        ))
        print("    Deferrable:{} Optional:{} Soft:{}".format(
            test["deferrable"],
            test["optional"],
            test["soft"],
        ))

        count_test += 1

        result = send_recv(proc, test["form"])
        print("    Result >>> {}".format(result))

        if not (test["ret"] or test["out"]):
            print("    SUCCESS (result ignored)")
            count_pass += 1

        elif test["ret"] and re.search(re.escape(test["ret"]), result):
            print("    SUCCESS (result matches expectation)")
            count_pass += 1

        elif test["out"] and re.search(re.escape(test["out"]), result):
            print("    SUCCESS (output matches expectation)")
            count_pass += 1

        else:
            if test["soft"]:
                print("    SOFT FAIL (line {})".format(test["line_number"]))
                count_fail_soft += 1
                fail_str = "SOFT FAILED"
            else:
                print("    FAIL (line {})".format(test["line_number"]))
                count_fail += 1
                fail_str = "FAILED"

            input_output_str = "Test {}: '{}' --> '{}', '{}'".format(
                count_test,
                test["form"],
                test["ret"],
                test["out"] if "out" in test else "",
            )

            failures.append(
                "{} {}\n"
                "    Expected: {}\n"
                "         Got: {}\n".format(fail_str, input_output_str, test["ret"], result)
            )

    proc.terminate()

    if failures:
        print()
        print("=" * 79)
        print("Failures")
        print("=" * 79)
        for f in failures:
            print(f)

    print()
    print("=" * 79)
    print("Test Results (for {}):".format(test_fname))
    print("    {:3d} soft fails".format(count_fail_soft))
    print("    {:3d} fails".format(count_fail))
    print("    {:3d} passes".format(count_pass))
    print("    {:3d} total".format(count_test))
    print("=" * 79)
    print()
    return
        

run_test(TEST_FILE, r"python C:\Users\schang2\dev\fun\mal\impls\lithp\step1_read_print.py")

# for x in read_test(TEST_FILE):
#     if "msg" in x:
#         print(x["msg"])
#     print(x)
