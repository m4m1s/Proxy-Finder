from concurrent.futures import ThreadPoolExecutor
from requests import get
from time import sleep, time
import re

TIMEOUT = 3

success_count = 0
failure_count = 0

def check_proxy(proxy: str):
    global success_count, failure_count
    try:
        start_time = time()
        response = get("https://twitch.tv/", proxies={"http": proxy, "https": proxy}, timeout=TIMEOUT)
        end_time = time()

        if response.status_code == 200:
            with open("results.txt", "a") as f:
                f.write(proxy + "\n")
            print(f"{proxy} ({response.elapsed.total_seconds() * 1000} ms) | Kalan Proxy: {len(ips) - (success_count + failure_count)}")
            success_count += 1
        else:
            failure_count += 1
    except:
        failure_count += 1

if __name__ == "__main__":
    try:
        with open("results.txt", 'w') as file:
            file.truncate(0)
    except:
        pass
        
    print("\n[1] -> Get from proxies.txt\n[2] -> Get from API\n")

    selection = 0
    while not selection:
        try:
            temp = int(input("Select an option: "))
            if not (1 <= temp <= 2):
                raise ValueError()

            selection = temp
        except ValueError:
            print("You must select a number between 1 and 2.")

    ips = []

    if selection == 2:
        API_ENDPOINT = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"

        try:
            res = get(API_ENDPOINT)
            if res.status_code != 200:
                print("There is a problem with the API.\nTerminating...")
                sleep(3)
                exit()
        except:
            print("Couldn't connect to the API.\nTerminating...")
            sleep(3)
            exit()

        print("Made a request to the endpoint.")

        ips = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+)', str(res.content).split("\n")[0])

    elif selection == 1:
        try:
            with open("proxies.txt", "r") as f:
                ips = f.read().splitlines()
        except:
            print("Couldn't find proxies.txt\nTerminating...")
            sleep(3)
            exit()

    print("Parsed all IP(s)")

    MAX_WORKERS = 80

    tasks = [item for item in range(len(ips))]

    print(f"{MAX_WORKERS} Worker(s) running.\nLooping through all IP(s)...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(check_proxy, ip) for ip in ips]

        for future in futures:
            future.result()

    print("Finito!\n")
    print(f"\nSuccessful Proxies: {success_count}")
    print(f"Failed Proxies: {failure_count}")
    print(f"Kapatmak için enter'a bas.")
    input()
