#!/usr/bin/env python3


# SECTION: Import libraries
import datetime
from colorama import Fore, Style
import argparse
from sys import argv
from ipaddress import ip_address
from subprocess import run, Popen, call, PIPE, DEVNULL
import re
from ftplib import FTP
import os
import getpass
from telnetlib import Telnet

# SECTION: Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-H", "--host", help="target host ip address", required="true")
parser.add_argument("-P", "--prompt", help="prompt for each test before continuing", action="store_true")
args = parser.parse_args()


# SECTION: Colorama and format definitions
def output_blue():
    print(Fore.CYAN + '[*]', end="")
    print(Style.RESET_ALL, end=" ")


def output_green():
    print(Fore.GREEN + '[+]', end="")
    print(Style.RESET_ALL, end=" ")


def output_red():
    print(Fore.RED + '[-]', end="")
    print(Style.RESET_ALL, end=" ")


def output_yellow():
    print(Fore.YELLOW + '[?]', end="")
    print(Style.RESET_ALL, end=" ")


def indent():
    print("    ", end='')


# SECTION: Safety net
def safetynet():
    print("CRITICAL: This error should never occur.")
    quit()


# SECTION: Define host and generic lists and wordlists
host = args.host

portlist_tcp = [21, 22, 80, 111, 443, 445, 1433, 2049, 3306, 5432, 8000, 8080, 8443, 9090, 9443]
openports_tcp = []
portlist_udp = []
openports_udp = []

list_users_main = ['', 'root', 'foobar', 'guest', 'admin', 'administrator', 'sysadmin', 'user', 'marketing', 'test']
list_passwords_main = ['', 'toor', '123', '1234', '12345', '123456', '1234567', '12345678', '111111', '123123',
                       'abc123', 'qwerty', 'password', 'password1', 'password123']

share_list_full = [
    'a$', 'b$', 'c$', 'd$', 'e$', 'f$', 'g$', 'h$', 'i$', 'j$', 'k$', 'l$', 'm$', 'n$', 'o$', 'p$', 'q$', 'r$', 's$',
    't$', 'u$', 'v$', 'w$', 'x$', 'y$', 'z$', 'logon', 'admin$', 'home', 'tools', 'share', 'admin', 'data', 'dfs$',
    'raid', 'ipc$', 'public', 'private', 'temp', 'files',
    'tmp', 'code', 'lp', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
    't', 'u', 'v', 'w',
    'x', 'y', 'z', 'images'
]

# SECTION: Create unique file suffix based on date for saving
now = datetime.datetime.now()
suffix = now.strftime("%Y-%m-%d")

# SECTION: Welcome splash
print("\nWelcome to:\n".format(argv[0]))
print("""
  /$$$$$$                                /$$      /$$                    
 /$$__  $$                              | $$$    /$$$                    
| $$  \__/  /$$$$$$   /$$$$$$   /$$$$$$ | $$$$  /$$$$  /$$$$$$   /$$$$$$ 
| $$ /$$$$ /$$__  $$ /$$__  $$ /$$__  $$| $$ $$/$$ $$ |____  $$ /$$__  $$
| $$|_  $$| $$  \__/| $$$$$$$$| $$  \ $$| $$  $$$| $$  /$$$$$$$| $$  \ $$
| $$  \ $$| $$      | $$_____/| $$  | $$| $$\  $ | $$ /$$__  $$| $$  | $$
|  $$$$$$/| $$      |  $$$$$$$|  $$$$$$$| $$ \/  | $$|  $$$$$$$| $$$$$$$/
 \______/ |__/       \_______/ \____  $$|__/     |__/ \_______/| $$____/ 
                               /$$  \ $$                       | $$      
                              |  $$$$$$/                       | $$         
                               \______/                        |__/      
    Powered by Greg
    #MKOfficeBestOffice
""")
output_blue()
print("Information")
output_green()
print("Success")
output_red()
print("Failure")
output_yellow()
print("Prompt")

# SECTION: Command-line arguments
prompt = 0
guess = 0
login = 0
thorough = 0

print()
try:
    ip_address(args.host)
    output_blue()
    print("Target host: {}".format(args.host))
except Exception as e:
    output_red()
    print("Exception: {e}".format(e=e))
    exit()
if args.prompt:
    prompt = 1
    output_blue()
    print("Prompt enabled: TRUE")
else:
    output_blue()
    print("Prompt enabled: FALSE")

# SECTION: Scanner (QUICK)
print()
output_blue()
print("Beginning port scanner...")
for p in portlist_tcp:
    results = run(['nc', '-vnz', '-w1', host, str(p)], stderr=PIPE, stdout=DEVNULL, encoding="ASCII")
    if "open" in results.stderr.rstrip():
        openports_tcp.append(results.stderr.rstrip())
    else:
        pass

# SECTION: Create port list from scanner (quick) (from regex101.com)
regex = r"] (\d+) \("

test_str = str(openports_tcp)

matches = re.finditer(regex, test_str, re.MULTILINE)
openports_tcp = []

for matchNum, match in enumerate(matches, start=1):
    for groupNum in range(0, len(match.groups())):
        groupNum = groupNum + 1
        openports_tcp.append(match.group(groupNum))

for p in openports_tcp:
    output_green()
    print("[OPEN] Port {port} TCP".format(port=p))

output_blue()
print("Port scanner complete.")

# SECTION: Loot directory function
loot_dir_exists = 2
loot_dir = ''
dir_label = ''


def create_loot_dir():
    global loot_dir
    loot_dir = 'loot_' + host + '_' + suffix + '/'
    try:
        run(['mkdir', loot_dir], stderr=DEVNULL, stdout=PIPE, encoding="ASCII")
        global dir_label
        dir_label = './' + loot_dir
        dir_check = os.path.isdir(dir_label)
        global loot_dir_exists
        if dir_check:
            loot_dir_exists = 1
            output_green()
            print("Loot directory created/exists.")
        else:
            loot_dir_exists = 0
            output_red()
            print("Something went wrong. Could not locate loot directory.")
            safetynet()
    except Exception as x:
        print("Exception: {x}".format(x=x))


# SECTION: Create loot directory
print()
if len(openports_tcp) > 0:
    if loot_dir_exists != 1:
        output_blue()
        print("Creating/checking for loot directory...")
        create_loot_dir()

# STATE AND FUNCTION DEFINITIONS #####################################################################


# SECTION: Preliminary definitions
preliminary_skip_tests = 0

whois_label = ''
whois_Popen_check = ''
whois_was_run = 0


def preliminary_prompt_recall():
    preliminary_prompt()


def preliminary_prompt():
    global preliminary_skip_tests
    output_yellow()
    preliminary_prompt_input = input("Run preliminary tests? (whois) (Y/n) ")
    if preliminary_prompt_input not in ["y", "Y", "n", "N", ""]:
        output_red()
        print("Invalid input.\n")
        preliminary_prompt_recall()
    else:
        if preliminary_prompt_input in ["y", "Y", ""]:
            output_blue()
            print("Running preliminary tests...")
            # all basic preliminary tests here
            whois()
        else:
            output_blue()
            print("Skipping preliminary tests!")
            preliminary_skip_tests = 1


def whois():
    global host, whois_label, dir_label, whois_Popen_check, whois_was_run
    whois_label = dir_label + "whois"
    try:
        with open(whois_label, "w") as whois_file:
            run(["whois", host], stderr=DEVNULL, stdout=whois_file)
            output_green()
            print("Writing whois output to file {f}".format(f=whois_label))
    except Exception as x:
        output_red()
        print("Exception: {x}".format(x=x))


# SECTION: FTP (21): Define FTP test states and variables
ftp_skip_tests = 0
ftp_can_connect = 2
ftp_can_auth = 2
ftp_can_list = 2
ftp_can_read = 2
ftp_can_write = 2

ftp = ''
ftp_host = ''
ftp_user = ''
ftp_pass = ''
ftp_user_success = ''
ftp_pass_success = ''
ftp_dir_label = ''

list_ftp_anon_user = ['anonymous', 'ftp', '']
list_ftp_anon_pass = ['anonymous', 'guest', 'anonymous@email.com', '']
list_ftp = ['ftp', 'ftp@', 'ftp123', 'ftpuser', 'ftp@email.com']
guessable_ftp_users = list_ftp + list_users_main
guessable_ftp_passwords = list_ftp + list_passwords_main


# SECTION: FTP (21): Port 21 check
def ftp_check():
    global ftp_can_connect
    if '21' in openports_tcp:
        ftp_can_connect = 1
        print()
    else:
        ftp_can_connect = 0


# SECTION: FTP (21): Authenticate
def ftp_auth_prompt_recall():
    ftp_auth_prompt()


def ftp_auth_prompt():
    global ftp_skip_tests
    output_yellow()
    ftp_auth_prompt_input = input("Attempt to authenticate to FTP server (anonymous)? (Y/n) ")
    if ftp_auth_prompt_input not in ["y", "Y", "n", "N", ""]:
        output_red()
        print("Invalid input.\n")
        ftp_auth_prompt_recall()
    else:
        if ftp_auth_prompt_input in ["y", "Y", ""]:
            output_blue()
            print("Attempting to authenticate to FTP server (anonymous)...")
            ftp_auth_guess(list_ftp_anon_user, list_ftp_anon_pass)
            if ftp_can_auth != 1:
                output_red()
                print("Could not anonymously authenticate to FTP server.")
                ftp_auth_prompt2()
        else:
            output_blue()
            print("Skipping FTP tests!")
            ftp_skip_tests = 1


def ftp_auth_prompt_recall2():
    ftp_auth_prompt2()


def ftp_auth_prompt2():
    global ftp_skip_tests
    output_yellow()
    ftp_auth_prompt2_input = input("Attempt to authenticate to FTP server (FTP-based guessable)? (Y/n) ")
    if ftp_auth_prompt2_input not in ["y", "Y", "n", "N", ""]:
        output_red()
        print("Invalid input.\n")
        ftp_auth_prompt2_recall()
    else:
        if ftp_auth_prompt2_input in ["y", "Y", ""]:
            output_blue()
            print("Attempting to authenticate to FTP server (FTP-based guessable)...")
            ftp_auth_guess(list_ftp, list_ftp)
            if ftp_can_auth != 1:
                output_red()
                print("Could not authenticate to FTP server using FTP-based weak credentials.")
                ftp_auth_prompt3()
        else:
            output_blue()
            print("Skipping FTP tests!")
            ftp_skip_tests = 1


def ftp_auth_prompt_recall3():
    ftp_auth_prompt3()


def ftp_auth_prompt3():
    global ftp_skip_tests
    output_yellow()
    ftp_auth_prompt3_input = input("Attempt to authenticate to FTP server (general guessable) [LENGTHY]? (Y/n) ")
    if ftp_auth_prompt3_input not in ["y", "Y", "n", "N", ""]:
        output_red()
        print("Invalid input.\n")
        ftp_auth_prompt3_recall()
    else:
        if ftp_auth_prompt3_input in ["y", "Y", ""]:
            output_blue()
            print("Attempting to authenticate to FTP server (general guessable)...")
            ftp_auth_guess(guessable_ftp_users, guessable_ftp_passwords)
            if ftp_can_auth != 1:
                output_red()
                print("Could not authenticate to FTP server using general guessable credentials. Giving up!")
                output_blue()
                print("Skipping FTP tests!")
                ftp_skip_tests = 1
        else:
            output_blue()
            print("Skipping FTP tests!")
            ftp_skip_tests = 1


def ftp_auth():
    try:
        global ftp_user, ftp_pass, ftp_can_auth, ftp_user_success, ftp_pass_success
        ftp.login(ftp_user, ftp_pass)
        output_green()
        print("FTP authentication successful. (with credentials {u}:{p})".format(u=ftp_user, p=ftp_pass))
        ftp_can_auth = 1
        ftp_user_success = ftp_user
        ftp_pass_success = ftp_pass
    except Exception as x:
        ftp_can_auth = 0
        output_red()
        print("Exception: {x} (with credentials {u}:{p})".format(x=x, u=ftp_user, p=ftp_pass))


def ftp_auth_guess(user_list, pass_list):
    global ftp, ftp_pass, ftp_user
    for x in pass_list:
        ftp_pass = x
        for y in user_list:
            ftp_user = y
            if ftp_can_auth != 1:
                ftp = FTP(host)
                ftp_auth()


# SECTION: FTP (21): List permissions
def ftp_list_prompt_recall():
    ftp_list_prompt()


def ftp_list_prompt():
    output_yellow()
    ftp_list_prompt_input = input("Attempt to list directory of FTP server? (Y/n) ")
    if ftp_list_prompt_input not in ["y", "Y", "n", "N", ""]:
        output_red()
        print("Invalid input.\n")
        ftp_list_prompt_recall()
    else:
        if ftp_list_prompt_input in ["y", "Y", ""]:
            output_blue()
            print("Attempting to list directory of FTP server...")
            ftp_list()
        else:
            output_blue()
            print("Skipping FTP test!")


def ftp_list():
    global ftp_can_list
    try:
        ftp.retrlines('LIST')
        ftp_can_list = 1
        output_green()
        print("FTP directory listing successful.")
    except Exception as x:
        print("Exception: {x}".format(x=x))
        ftp_can_list = 0


# SECTION: FTP (21): Read permissions
def ftp_read_prompt_recall():
    ftp_read_prompt()


def ftp_read_prompt():
    output_yellow()
    ftp_read_prompt_input = input("Attempt to download contents of FTP server? (Y/n) ")
    if ftp_read_prompt_input not in ["y", "Y", "n", "N", ""]:
        output_red()
        print("Invalid input.\n")
        ftp_read_prompt_recall()
    else:
        if ftp_read_prompt_input in ["y", "Y", ""]:
            output_blue()
            print("Attempting to download contents of FTP server...")
            ftp_read()
        else:
            output_blue()
            print("Skipping FTP tests!")


def ftp_read():
    global ftp_can_read
    try:
        global ftp_host, host
        ftp_host = "ftp://" + host
        global ftp_dir_label, dir_label
        ftp_dir_label = dir_label + 'ftp_file_download'
        ftp_wget_user = "--ftp-user=" + ftp_user_success
        ftp_wget_pass = "--ftp-password=" + ftp_pass_success
        cmd = run(['wget', ftp_wget_user, ftp_wget_pass, '-m', '-nH', '-r', '-P', ftp_dir_label, ftp_host],
                  stderr=DEVNULL, stdout=DEVNULL, encoding="ASCII")
        if cmd.returncode == 0:
            output_green()
            print("Download complete. Files saved to {}".format(ftp_dir_label))
            ftp_can_read = 1
        else:
            output_red()
            print(
                "Exception: Received return code {r} when attempting to wget from FTP server.".format(r=cmd.returncode))
            ftp_can_read = 0
    except Exception as x:
        print("Exception: {x}".format(x=x))
        ftp_can_read = 0


# SECTION: FTP (21): Write permissions
def ftp_write_prompt_recall():
    ftp_write_prompt()


def ftp_write_prompt():
    output_yellow()
    ftp_write_prompt_input = input("Attempt to write content to FTP server? (Y/n) ")
    if ftp_write_prompt_input not in ["y", "Y", "n", "N", ""]:
        output_red()
        print("Invalid input.\n")
        ftp_write_prompt_recall()
    else:
        if ftp_write_prompt_input in ["y", "Y", ""]:
            output_blue()
            print("Attempting to write content to FTP server...")
            ftp_write()
        else:
            output_blue()
            print("Skipping FTP test!")


def ftp_write():
    global ftp_can_write
    try:
        global suffix
        ftp_write_test = 'ftp_write_test_' + suffix
        ftp.mkd(ftp_write_test)
        ftp_can_write = 1
        output_green()
        print("Test directory created.")
        try:
            output_blue()
            print("Removing test directory...")
            ftp.rmd(ftp_write_test)
            output_blue()
            print("Test directory has been removed.")
        except Exception as x:
            output_red()
            print("Exception: {x}".format(x=x))
            output_blue()
            print("Manual cleanup possibly required.")
    except Exception as x:
        output_red()
        print("Exception: {x}".format(x=x))
        ftp_can_write = 0


# SECTION: HTTP (80/443/8000/8080/8443/9090/9443): Define HTTP test states and variables
http_can_connect = 2
http_skip_tests = 0
dirb_was_run = 0

http_ports = [80, 443, 8000, 8080, 8443, 9090, 9443]
http_ports_open = []
http_web_server_confirmed = []
http_web_server_200ok_received = []
http_method_options_supported = []
http_method_options_unsupported = []
http_method_put_supported = []
http_method_put_unsupported = []
http_method_put_success = []
http_method_put_failure = []

curl_target = ''
curl_dir_label = ''
curl_dir_label_port = ''
curl_options_dir_label = ''
curl_options_dir_label_port = ''
curl_options_grep = ''
curl_put_targets = ['/']
curl_put_target = ''
curl_put_dir_label = ''
curl_put_dir_label_port = ''
dirb_target = ''
dirb_dir_label = ''
dirb_dir_label_port = ''


# SECTION: HTTP (80/443/8000/8080/8443/9090/9443): Port and web server checks
def http_check():
    global http_can_connect, http_ports, http_ports_open, openports_tcp
    for port in http_ports:
        if str(port) in openports_tcp:
            http_ports_open.append(port)
    if len(http_ports_open) > 0:
        http_can_connect = 1
    else:
        http_can_connect = 0


def http_web_server_check():
    global host, http_ports_open, curl_target, dir_label, curl_dir_label, curl_dir_label_port, http_web_server_confirmed, http_web_server_200ok_received
    curl_dir_label = dir_label + "curl/"
    run(["mkdir", curl_dir_label], stderr=DEVNULL, stdout=DEVNULL)
    for port in http_ports_open:
        curl_dir_label_port = curl_dir_label + "curl" + str(port)
        curl_target = host + ':' + str(port)
        try:
            with open(curl_dir_label_port, "w") as curl_file:
                cmd = run(["curl", "-v", curl_target], stderr=curl_file, stdout=curl_file, timeout=3)
            if cmd.returncode == 0:
                with open(curl_dir_label_port, "r") as curl_file2:
                    if '<' in curl_file2.read():
                        http_web_server_confirmed.append(port)
                        with open(curl_dir_label_port, "r") as curl_file3:
                            if '200 OK' in curl_file3.read():
                                http_web_server_200ok_received.append(port)
                    else:
                        output_red()
                        print(
                            "Exception: Web server did not respond to cURL request when testing web server on port {p}".format(
                                p=port))
            else:
                output_red()
                print("Exception: Received return code {r} from cURL when testing web server on port {p}".format(
                    r=cmd.returncode, p=port))
        except Exception as x:
            output_red()
            print("Exception: {x}".format(x=x))


# SECTION: HTTP (80/443/8000/8080/8443/9090/9443): HTTP cURL tests (dirb + options, put method tests)
def http_tests_prompt_recall():
    http_tests_prompt()


def http_tests_prompt():
    global http_skip_tests
    output_yellow()
    http_tests_prompt_input = input("Run tests against web server(s)? (Y/n) ")
    if http_tests_prompt_input not in ["y", "Y", "n", "N", ""]:
        output_red()
        print("Invalid input.\n")
        http_tests_prompt_recall()
    else:
        if http_tests_prompt_input in ["y", "Y", ""]:
            output_blue()
            print("Running tests against web server(s)...")
            http_web_server_check()
            curl_methods()
        else:
            output_blue()
            print("Skipping HTTP tests!")
            http_skip_tests = 1


def curl_methods():
    global host, curl_options_dir_label, curl_options_dir_label_port, dir_label, http_web_server_200ok_received, curl_options_grep, \
        http_method_options_supported, http_method_options_unsupported, http_method_put_supported, http_method_put_unsupported, \
        http_method_put_success, http_method_put_failure, curl_put_dir_label, curl_put_dir_label_port, curl_put_target, curl_put_targets
    for port in http_web_server_200ok_received:
        output_blue()
        print("Web server running on port {p}".format(p=port))
        curl_options_dir_label_port = curl_dir_label + "curl_options" + str(port)
        curl_options_target = host + ':' + str(port)
        try:
            with open(curl_options_dir_label_port, "w") as curl_file:
                cmd = run(["curl", "-v", "-X", "OPTIONS", curl_options_target], stderr=curl_file, stdout=curl_file)
            if cmd.returncode == 0:
                http_method_options_supported.append(port)
                with open(curl_options_dir_label_port, "r") as curl_file2:
                    if '<' in curl_file2.read():
                        curl_file2.seek(0, 0)
                        for line in curl_file2:
                            if '< Allow: ' in line:
                                output_green()
                                print("Web server running on port {p} supports OPTIONS method".format(p=port))
                                output_blue()
                                print("Methods supported by web server running on port {p}".format(p=port))
                                replace1 = line.replace("< Allow: ", "")
                                replace2 = replace1.replace(" ", "")
                                replace3 = replace2.replace("\n", "")
                                methods = replace3.split(',')
                                for m in methods:
                                    output_green()
                                    print(m)
                                    if m == 'PUT':
                                        http_method_put_supported.append(port)
                    else:
                        output_red()
                        print(
                            "Exception: Web server did not respond to cURL request when testing web server on port {p}".format(
                                p=port))
            else:
                output_red()
                print("Exception: Received return code {r} from cURL when testing web server on port {p}".format(
                    r=cmd.returncode, p=port))
        except Exception as x:
            output_red()
            print("Exception: {x}".format(x=x))
    for port in http_method_put_supported:
        curl_put_dir_label_port = curl_dir_label + "curl_put" + str(port)
        curl_put_target = host + ':' + str(port)
        try:
            with open(curl_put_dir_label_port, "w") as curl_file:
                cmd = run(["curl", "-v", "-X", "PUT", "-d", "test_put", curl_options_target], stderr=curl_file,
                          stdout=curl_file)
            if cmd.returncode == 0:
                with open(curl_put_dir_label_port, "r") as curl_file2:
                    if '<' in curl_file2.read():
                        curl_file2.seek(0, 0)
                        for line in curl_file2:
                            if '200 OK' in line:
                                http_method_put_success.append(port)
                                output_green()
                                print("Successful PUT request for web server running on port {p}".format(p=port))
                        if port not in http_method_put_success:
                            output_red()
                            print(
                                "PUT method supported but could not upload data for web server running on port {p}".format(
                                    p=port))
                    else:
                        output_red()
                        print(
                            "Exception: Web server did not respond to cURL request when testing web server on port {p}".format(
                                p=port))
            else:
                output_red()
                print("Exception: Received return code {r} from cURL when testing web server on port {p}".format(
                    r=cmd.returncode, p=port))
        except Exception as x:
            output_red()
            print("Exception: {x}".format(x=x))


def dirb_prompt_recall():
    dirb_prompt()


def dirb_prompt():
    output_yellow()
    dirb_prompt_input = input("Run DIRB against web server(s) (as background process)? (Y/n) ")
    if dirb_prompt_input not in ["y", "Y", "n", "N", ""]:
        output_red()
        print("Invalid input.\n")
        dirb_prompt_recall()
    else:
        if dirb_prompt_input in ["y", "Y", ""]:
            output_blue()
            print("Running DIRB against web server(s)...")
            dirb()
        else:
            output_blue()
            print("Skipping DIRB!")


def dirb():
    global dirb_dir_label, dirb_dir_label_port, dir_label, dirb_was_run, host, dirb_target
    dirb_dir_label = dir_label + 'dirb/'
    run(["mkdir", dirb_dir_label], stderr=DEVNULL, stdout=DEVNULL)
    for port in http_web_server_confirmed:
        dirb_dir_label_port = dirb_dir_label + "dirb" + str(port)
        dirb_target = "http://" + host + ":" + str(port)
        try:
            with open(dirb_dir_label_port, "w") as dirb_output:
                Popen(['dirb', dirb_target], stderr=DEVNULL, stdout=dirb_output)
            dirb_was_run = 1

        except Exception as x:
            output_red()
            print("Exception: {x}".format(x=x))


# SECTION: RPC (111): Define RPC test states and variables
rpc_can_connect = 2
rpc_confirmed = 2
rpc_rpcinfo = 2
rpc_showmount = 2

rpc_label = ''
showmount_file = ''

rpc_service_list = []


# SECTION: RPC (111): Port 111 check
def rpc_check():
    global rpc_can_connect
    if '111' in openports_tcp:
        rpc_can_connect = 1
        print()
    else:
        rpc_can_connect = 0


# SECTION: RPC (111): rpcinfo + showmount (mount protocol)
def rpcinfo_prompt_recall():
    rpcinfo_prompt()


def rpcinfo_prompt():
    output_yellow()
    rpcinfo_prompt_input = input("Run tests against the RPC service? (Y/n) ")
    if rpcinfo_prompt_input not in ["y", "Y", "n", "N", ""]:
        output_red()
        print("Invalid input.\n")
        rpcinfo_prompt_recall()
    else:
        if rpcinfo_prompt_input in ["y", "Y", ""]:
            output_blue()
            print("Running rpcinfo against the RPC service...")
            rpcinfo()
            rpcinfo_services()
        else:
            output_blue()
            print("Skipping RPC test!")


def rpcinfo():
    try:
        global host
        global rpc_rpcinfo
        rpc_rpcinfo = 1
        global rpc_label, dir_label
        rpc_label = dir_label + "rpcinfo"
        with open(rpc_label, "w") as r:
            run(["rpcinfo", "-p", host], stderr=DEVNULL, stdout=r)
    except Exception as x:
        print("Exception: {x}".format(x=x))


def rpcinfo_services():
    global rpc_service_list
    with open(rpc_label, "r") as f:
        for line in f.readlines():
            service = line.split()[-1]
            try:
                int(service)
            except:
                if service not in rpc_service_list and service != "tcp" and service != "udp":
                    rpc_service_list.append(service)
    if len(rpc_service_list) > 0:
        output_blue()
        print("Services running according to rpcinfo...")
        for unique in rpc_service_list:
            output_green()
            print(unique)
    if len(rpc_service_list) == 0:
        output_red()
        print("No services were returned when querying the RPC service. This is weird and should never happen?")


def showmount_prompt_recall():
    showmount_prompt()


def showmount_prompt():
    output_yellow()
    showmount_prompt_input = input("Run showmount against the RPC service? (Y/n) ")
    if showmount_prompt_input not in ["y", "Y", "n", "N", ""]:
        output_red()
        print("Invalid input.\n")
        showmount_prompt_recall()
    else:
        if showmount_prompt_input in ["y", "Y", ""]:
            output_blue()
            print("Running showmount against the RPC service...")
            showmount()
            showmount_output()
        else:
            output_blue()
            print("Skipping RPC test!")
            global rpc_showmount
            rpc_showmount = 0


def showmount():
    try:
        global showmount_file, dir_label, host, rpc_showmount
        showmount_file = dir_label + "showmount"
        with open(showmount_file, "w") as s:
            shwmnt = run(["showmount", "-e", host], stderr=DEVNULL, stdout=s)
            if shwmnt.returncode == 0:
                rpc_showmount = 1
            else:
                rpc_showmount = 0
                print("Exception: showmount didn't return a 0.")
    except Exception as x:
        print("Exception: {x}".format(x=x))


def showmount_output():
    global showmount_file
    with open(showmount_file, "r") as infile:
        count = len(infile.readlines())
    showmount_list = []
    mount_targets = []
    with open(showmount_file, "r") as infile:
        i = 0
        while i < count:
            showmount_line = infile.readline()
            i = i + 1
            showmount_list.append(showmount_line)
    showmount_list_exports = showmount_list[1:]
    for line in showmount_list_exports:
        mount_targets.append(line.split()[0])
    for m in mount_targets:
        output_green()
        print(m)


# SECTION: NFS (2049): Define NFS test states and variables
nfs_skip_tests = 0
nfs_can_connect = 2
nfs_can_showmount = 2
nfs_export_exists = 2
nfs_can_mount = 2
nfs_can_read = 2
nfs_can_write = 2

nfs_mount_successes = 0
nfs_mount_failures = 0

nfs = ''
nfs_host = ''
nfs_dir_label = ''
nfs_mount_label = ''


# SECTION: NFS (2049): Port 2049 check
def nfs_check():
    global nfs_can_connect
    if '2049' in openports_tcp:
        nfs_can_connect = 1
    else:
        nfs_can_connect = 0


# SECTION: NFS (2049): Mount exported shares
def nfs_shares_check():
    global showmount_file, nfs_export_exists
    with open(showmount_file, "r") as infile:
        count = len(infile.readlines())
    if count > 1:
        nfs_export_exists = 1
    else:
        nfs_export_exists = 0


def nfs_mount_prompt_recall():
    nfs_mount_prompt()


def nfs_mount_prompt():
    output_yellow()
    nfs_mount_prompt_input = input("Attempt to mount exported shares? (Y/n) ")
    if nfs_mount_prompt_input not in ["y", "Y", "n", "N", ""]:
        output_red()
        print("Invalid input.\n")
        nfs_mount_prompt_recall()
    else:
        if nfs_mount_prompt_input in ["y", "Y", ""]:
            output_blue()
            print("Attempting to mount exported shares...")
            nfs_mount()
        else:
            output_blue()
            print("Skipping mount!")
            global nfs_can_mount
            nfs_can_mount = 0


def nfs_mount():
    try:
        global showmount_file
        with open(showmount_file, "r") as infile:
            count = len(infile.readlines())
        showmount_list = []
        mount_targets = []
        with open(showmount_file, "r") as infile:
            i = 0
            while i < count:
                showmount_line = infile.readline()
                i = i + 1
                showmount_list.append(showmount_line)
        showmount_list_exports = showmount_list[1:]
        for line in showmount_list_exports:
            mount_targets.append(line.split()[0])
        global dir_label, nfs_mount_label, host
        m = 1
        nfs_mount_label = dir_label + "mount/"
        run(["mkdir", nfs_mount_label], stderr=DEVNULL, stdout=DEVNULL)
        for line in mount_targets:
            nfs_mount_label_int = nfs_mount_label + str(m)
            run(["mkdir", nfs_mount_label_int], stderr=DEVNULL, stdout=DEVNULL)
            mount_target_label = host + ":" + line
            mount = run(["mount", "-t", "nfs", mount_target_label, nfs_mount_label_int, "-o",
                         "nolock,vers=2"])  # stderr=DEVNULL, stdout=DEVNULL)
            m = m + 1
            global nfs_mount_successes, nfs_mount_failures
            if mount.returncode == 0:
                nfs_mount_successes = nfs_mount_successes + 1
            if mount.returncode != 0:
                nfs_mount_failures = nfs_mount_failures + 1
        global nfs_can_mount
        if nfs_mount_successes > 0:
            nfs_can_mount = 1
            if count == 2:
                output_green()
                print(
                    "Successfully mounted {s} exported share to {l}.".format(s=nfs_mount_successes, l=nfs_mount_label))
            if count > 2:
                output_green()
                print(
                    "Successfully mounted {s} exported shares to {l}.".format(s=nfs_mount_successes, l=nfs_mount_label))
            if count < 2:
                safetynet()
        expected_successes = count - 1
        if nfs_mount_successes != expected_successes:
            output_red()
            print("There were problems mount {f} of the {e} exported shares.".format(f=nfs_mount_failures,
                                                                                     e=expected_successes))
    except Exception as x:
        print("Exception: {x}".format(x=x))


# SECTION: SMB: Define SMB test states and variables
smb_skip_tests = 0
smb_can_connect = 2
smb_can_null_auth = 2
smb_can_list = 2
smb_can_read = 2
smb_can_write = 2

smb = ''
smb_host = ''
smb_dir_label = ''
smb_target_share = ''
smb_null_auth_share_success = ''

share_list_smb = ['ipc$', 'ipc', 'admin$', 'admin', 'c$', 'c']
smb_share_null_auth_success = []

enum4linux_is_running = 0
enum4linux_dir_label = ''
enum4linux_was_run = 0


# SECTION: SMB: Port 445 check
def smb_check():
    global smb_can_connect
    if "445" in openports_tcp:
        smb_can_connect = 1
        print()
    else:
        smb_can_connect = 0


# SECTION: SMB: SMB IPC null auth
def smb_null_auth_prompt_recall():
    smb_null_auth_prompt()


def smb_null_auth_prompt():
    output_yellow()
    smb_null_auth_prompt_input = input("Attempt to authenticate to SMB service using null session? (Y/n) ")
    if smb_null_auth_prompt_input not in ["y", "Y", "n", "N", ""]:
        output_red()
        print("Invalid input.\n")
        smb_null_auth_prompt_recall()
    else:
        if smb_null_auth_prompt_input in ["y", "Y", ""]:
            output_blue()
            print("Attempting to authenticate to {s} share using null session...".format(s=smb_target_share))
            smb_null_auth()
        else:
            output_blue()
            print("Skipping null auth test!")


def smb_null_auth():
    global host, smb_can_null_auth, smb_null_auth_share_success, smb_null_auth_share_success
    for share in share_list_smb:
        smbhost = '//' + host + '/' + share
        user = '-U%'
        command = run(["smbclient", smbhost, user, "-c", "help", "2>&1"], stderr=DEVNULL, stdout=DEVNULL)
        if command.returncode == 0:
            output_green()
            print("Successfully authenticated to {s} share using null session.".format(s=share))
            smb_can_null_auth = 1
            smb_null_auth_share_success = share
            smb_share_null_auth_success.append(share)
    if smb_null_auth_share_success == '':
        output_red()
        print("Could not authenticate to any shares using a null session.")
        smb_can_null_auth = 0
    # add listing successful shares
    # for share_sucess in smb_share_null_auth_success:
    #    smbhost = '//' + host + '/' + share_sucess
    #    user = '-U%'
    #    command2 = run(["smbclient", ])


def enum4linux_prompt_recall():
    enum4linux_prompt()


def enum4linux_prompt():
    output_yellow()
    enum4linux_prompt_input = input("Run enum4linux against SMB service (as background process)? (Y/n) ")
    if enum4linux_prompt_input not in ["y", "Y", "n", "N", ""]:
        output_red()
        print("Invalid input.\n")
        enum4linux_prompt_recall()
    else:
        if enum4linux_prompt_input in ["y", "Y", ""]:
            output_blue()
            print("Running enum4linux...")
            enum4linux()
        else:
            output_blue()
            print("Skipping enum4linux!")


def enum4linux():
    global enum4linux_dir_label, dir_label, enum4linux_is_running, enum4linux_was_run, host
    enum4linux_dir_label = dir_label + 'enum4linux'
    try:
        with open(enum4linux_dir_label, "w") as enum:
            Popen(['enum4linux', host], stderr=DEVNULL, stdout=enum)
            enum4linux_was_run = 1
    except Exception as x:
        output_red()
        print("Exception: {x}".format(x=x))


# TESTING AND REPORTING ##############################################################################


# SECTION: Preliminary tests
print()
if prompt == 0:
    output_blue()
    print("Running preliminary tests...")
    whois()
if prompt == 1:
    preliminary_prompt()

# SECTION: FTP tests
ftp_check()
if ftp_can_connect == 1:
    if prompt == 0:
        output_blue()
        print("Attempting to authenticate to FTP server...")
        ftp_auth_guess(list_ftp_anon_user, list_ftp_anon_pass)
    if prompt == 1:
        ftp_auth_prompt()

    if ftp_skip_tests == 0:
        if ftp_can_auth == 1:
            if prompt == 0:
                output_blue()
                print("Attempting to list directory of FTP server...")
                ftp_list()
            if prompt == 1:
                ftp_list_prompt()

        if ftp_can_auth == 1:
            if prompt == 0:
                output_blue()
                print("Attempting to download files from FTP server...")
                ftp_read()
            if prompt == 1:
                ftp_read_prompt()

        if ftp_can_auth == 1:
            if prompt == 0:
                output_blue()
                print("Attempting to write to FTP server...")
                ftp_write()
            if prompt == 1:
                ftp_write_prompt()

# SECTION: RPC tests
rpc_check()

if rpc_can_connect == 1:
    if prompt == 0:
        output_blue()
        print("Running tests against RPC service...")
        rpcinfo()
        rpcinfo_services()
    if prompt == 1:
        rpcinfo_prompt()

if "mountd" in rpc_service_list:
    if prompt == 0:
        output_blue()
        print("Running showmount against RPC service...")
        showmount()
        if rpc_showmount == 1:
            showmount_output()
    if prompt == 1:
        showmount_prompt()

if "nfs" in rpc_service_list:
    nfs_check()

if rpc_showmount == 1 and "nfs" in rpc_service_list:
    nfs_shares_check()
    if nfs_can_connect == 1 and nfs_export_exists == 1:
        if prompt == 0:
            output_blue()
            print("Attempting to mount exported directories...")
            nfs_mount()
        if prompt == 1:
            nfs_mount_prompt()

if rpc_showmount == 2 and nfs_can_connect == 1:
    output_blue()
    print("RPC showmount test skipped. Cannot attempt to mount exported drives.")

# SECTION: SMB tests
smb_check()

if smb_can_connect == 1:
    if prompt == 0:
        output_blue()
        print("Running tests against SMB service...")
        smb_null_auth()
    if prompt == 1:
        smb_null_auth_prompt()

if smb_can_connect == 1:
    if prompt == 0:
        output_blue()
        print("Running enum4linux against SMB service (as background process)...")
        enum4linux()
        output_green()
        print("Writing to file {f}".format(f=enum4linux_dir_label))
    if prompt == 1:
        enum4linux_prompt()

# SECTION: HTTP tests
print()
http_check()
if http_can_connect == 1:
    if prompt == 0:
        output_blue()
        print("Running tests against web server(s)...")
        http_web_server_check()
        curl_methods()
    if prompt == 1:
        http_tests_prompt()
if http_web_server_confirmed:
    if prompt == 0:
        output_blue()
        print("Running DIRB against web server(s) (as background process)...")
        dirb()
    if prompt == 1:
        dirb_prompt()


# http web server notes:

# SECTION: Report
print("\n================ BEGIN REPORT ================\n")
if ftp_can_connect == 0:
    output_red()
    print("FTP service not running.")
if ftp_can_connect == 1:
    output_green()
    print("FTP service running.")
    if ftp_can_auth == 0:
        output_red()
        print("Could not authenticate to FTP service.")
    if ftp_can_auth == 1:
        output_green()
        print("FTP valid credentials: user={u}, pass={p}".format(u=ftp_user_success, p=ftp_pass_success))
        if ftp_can_list == 0:
            output_red()
            print("FTP list permissions")
        if ftp_can_list == 1:
            output_green()
            print("FTP list permissions")
        if ftp_can_list == 2:
            output_blue()
            print("FTP list permissions not tested")

        if ftp_can_read == 0:
            output_red()
            print("FTP read permissions")
        if ftp_can_read == 1:
            output_green()
            print("FTP read permissions")
        if ftp_can_read == 2:
            output_blue()
            print("FTP read permissions not tested")

        if ftp_can_write == 0:
            output_red()
            print("FTP write permissions")
        if ftp_can_write == 1:
            output_green()
            print("FTP write permissions")
        if ftp_can_write == 2:
            output_blue()
            print("FTP write permissions not tested")
    if ftp_can_auth == 2:
        output_blue()
        print("Did not attempt to authenticate to FTP server")
if ftp_can_connect == 2:
    output_red()
    print("ftp_check() did not run for some reason. This should never happen")

print()
if rpc_can_connect == 0:
    output_red()
    print("RPC service not running")
if rpc_can_connect == 1:
    output_green()
    print("RPC service running")
    if nfs_can_connect == 0:
        output_red()
        print("NFS service not running")
    if nfs_can_connect == 1:
        output_green()
        print("NFS service running")
        if nfs_can_mount == 0:
            output_red()
            print("Could not mount NFS shares")
        if nfs_can_mount == 1:
            output_green()
            print("Successfully mounted NFS shares")
        if nfs_can_mount == 2:
            output_blue()
            print("Did not attempt to mount NFS shares")
    if nfs_can_connect == 2:
        output_blue()
        print("NFS service not tested")
if rpc_can_connect == 2:
    output_blue()
    print("rpc_check() did not run for some reason. This should never happen")

print()
if smb_can_connect == 0:
    output_red()
    print("SMB service not running")
if smb_can_connect == 1:
    output_green()
    print("SMB service running")
    if smb_can_null_auth == 0:
        output_red()
        print("Could not authenticate to SMB server using a null session")
    if smb_can_null_auth == 1:
        output_green()
        print("Successfully authenticated to the {s} share using a null session".format(s=smb_null_auth_share_success))
    if smb_can_null_auth == 2:
        output_blue()
        print("Did not attempt to authenticate to the SMB server using a null session")
if smb_can_connect == 2:
    output_red()
    print("smb_check() did not run for some reason. This should never happen")

print()
if http_can_connect == 0:
    output_red()
    print("HTTP service not running")
if http_can_connect == 1:
    if http_web_server_confirmed:
        output_green()
        print("HTTP service running on ports: ", end='')
        for port in http_web_server_confirmed:
            print("{p} ".format(p=port), end='')
        print()
        if http_method_options_supported:
            output_green()
            print("OPTIONS method supported on ports: ", end='')
            for port in http_method_options_supported:
                print("{p} ".format(p=port), end='')
            print()
        else:
            output_red()
            print("OPTIONS method not allowed ")
        if http_method_put_supported:
            output_green()
            print("PUT method supported on ports: ", end='')
            for port in http_method_put_supported:
                print("{p} ".format(p=port), end='')
            print()
        else:
            output_red()
            print("PUT method not supported")
        if http_method_put_success:
            output_green()
            print("PUT method upload successful on ports: ", end='')
            for port in http_method_put_success:
                print("{p} ".format(p=port), end='')
            print()
        else:
            output_red()
            print("PUT method upload failed on tested URLs")
    else:
        output_red()
        print("HTTP common ports used, but no web service detected")


if http_can_connect == 2:
    output_red()
    print("http_check() did not run for some reason. This should never happen")

# SECTION: Popen processes warnings
print()
if enum4linux_was_run == 1:
    output_blue()
    print("Warning: enum4linux process may still be writing to file.")
if dirb_was_run == 1:
    output_blue()
    print("Warning: dirb process may still be writing to file.")

# SECTION: dev tests

# SECTION: END
print()
output_blue()
print("Testing complete. Nice work! I'm proud of you.\n")


