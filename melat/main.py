"""
Copyright 2019 Javier Caballero Lloris

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
# import asyncio
import sys
from urllib.request import urlopen

from ping3 import ping

from tqdm import tqdm


HEADER = (
    "<-. (`-')   (`-')  _  _(`-')      _       (`-')  _  <-. (`-')_    ("
    "`-')               \n   \\(OO )_  ( OO).-/ ( (OO ).->  (_)      (OO"
    " ).-/     \\( OO) )   (OO )_.->    <-.    \n,--./  ,-.)(,------.  "
    "\\    .'_   ,-(`-')  / ,---.   ,--./ ,--/    (_| \\_)--. ,--. )   "
    "\n|   `.'   | |  .---'  '`'-..__)  | ( OO)  | \\ /`.\\  |   \\ |  |"
    "    \\  `.'  /  |  (`-') \n|  |'.'|  |(|  '--.   |  |  ' |  |  |  )"
    "  '-'|_.' | |  . '|  |)    \\    .')  |  |OO ) \n|  |   |  | |  .--"
    "'   |  |  / : (|  |_/  (|  .-.  | |  |\\    |     .'    \\  (|  '__"
    " | \n|  |   |  | |  `---.  |  '-'  /  |  |'->  |  | |  | |  | \\   "
    "|    /  .'.  \\  |     |' \n`--'   `--' `------'  `------'   `--'  "
    "   `--' `--' `--'  `--'   `--'   '--' `-----' \n ______    __     _"
    "_____      __    __      _____    \n/ ____/\\  /\\_\\   /_/\\___\\ "
    "   /_/\\  /\\_\\    /\\___/\\   \n) ) __\\/  \\/_/   ) ) ___/    ) "
    ") \\/ ( (   / / _ \\ \\  \n \\ \\ \\     /\\_\\ /_/ /  ___  /_/ \\ "
    " / \\_\\  \\ \\(_)/ /  \n _\\ \\ \\   / / / \\ \\ \\_/\\__\\ \\ \\ "
    "\\\\// / /  / / _ \\ \\  \n)____) ) ( (_(   )_)  \\/ _/  )_) )( (_("
    "  ( (_( )_) ) \n\\____\\/   \\/_/   \\_\\____/    \\_\\/  \\/_/   "
    "\\/_/ \\_\\/ "
)

MIN = 1
MAX = 10


def pprint_table(data: list):
    """Pretty print the results table

    Arguments:
        data {list} -- Ordered list to be printed
    """

    print("\n*** Best game servers ***")
    print("-------------------------")
    print("|  Name  |               Location               | milis |")
    print("| ------ | ------------------------------------ | ----- |")
    for gs in data:
        name = gs["name"].center(6, " ")
        loc = gs["location"].center(36, " ")
        avg = str(gs["avg"]).center(5, " ")
        print(f"| {name} | {loc} | {avg} |")
        print("| ------ | ------------------------------------ | ----- |")


def ask_user():
    """Ask the user about how many 'pings' we should do

    Returns:
        int -- Number of 'pings' to do
    """

    try:
        question = f"How many checks to do? ({MIN} to {MAX}). Recomended: 4\n"
        checks = input(question)
        if not checks.isdigit():
            raise ValueError("Incorrect value provided")
        checks = int(checks)
    except (EOFError, ValueError):
        sys.exit("Incorrect value provided")
    else:
        if MIN <= checks <= MAX:
            return checks
        else:
            sys.exit("Out of range value")


def ping_server(checks: int, server_info: list):
    """Measure latency against a server

    Keyword Arguments:
        checks {int} -- Quantity of 'pings' to do
        server_info {list} -- List with [0]=name, [1]=location and [2]=IP

    Returns:
        int -- Average miliseconds that takes a package to travel to server
    """

    avg = None
    if server_info:
        latencies = []
        for _ in range(checks):
            timeout = ping(server_info[2], timeout=1, unit="ms")
            if timeout:
                latencies.append(timeout)
            else:
                # Server unstable or down
                return None
        # Compute an average
        avg = int(round(sum(latencies) / checks))
    return {"name": server_info[0], "location": server_info[1], "avg": avg}


def process(checks: int):
    """Main process to ping servers

    Arguments:
        checks {int} -- Number of pings to do
    """

    # Download server list
    url = ""
    with open("data/gs_url.txt", "r") as file:
        url = file.readline()
    if not url:
        sys.exit("There is no URL configured for servers list")
    response = urlopen(url)
    if response.getcode() != 200:
        sys.exit("The server list cannot be retrieved")
    # Convert downloaded file to dict
    server_list = response.read().decode().split("\n")
    gsdata = []
    for line in server_list:
        data = []
        line = line.strip()
        for val in line.split("\t"):
            if val:
                data.append(val)
        if data and len(data) == 3:
            gsdata.append(data)
    # Store results to dict
    timeouts = []
    # With Async/await
    # futures = []
    # loop = asyncio.get_event_loop()
    # for gs in gsdata:
    #     futures.append(
    #         asyncio.ensure_future(ping_server(checks, gs_info)))
    # done, _ = loop.run_until_complete(asyncio.wait(futures))
    # for future in done:
    #     result = future.result()
    #     if result:
    #         timeouts.append(result)
    # Linear execution
    for gs_info in tqdm(gsdata):
        result = ping_server(checks, gs_info)
        if result:
            timeouts.append(result)
    # Print better servers
    best = sorted(timeouts, key=lambda x: x["avg"])[:5]  # best five
    pprint_table(best)


if __name__ == "__main__":
    print(HEADER)
    print("\n\nWill find out the best GS for this Internet connection")
    checks = ask_user()
    process(checks)
    print("*** Have fun ***")
