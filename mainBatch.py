import os
import subprocess
import time
import random
import shutil

def run_main_script():
    subprocess.run(["python", "main.py"], check=True)

def route_generator(run):
    ROADNETWORK = "CN10EVEN"
    SUMO_TOOLS = r"C:\Program Files (x86)\Eclipse\Sumo\tools"
    NET_FILE = r"C:\Users\bobbi\Documents\YEAR 3\sumo3\TESTS\CN10EVEN.net.xml"
    OUTPUT_DIR_TRIPS = r"C:\Users\bobbi\Documents\YEAR 3\sumo3\TESTS"
    OUTPUT_DIR = r"C:\Users\bobbi\Documents\YEAR 3\sumo3"


    os.makedirs(OUTPUT_DIR, exist_ok=True)

    trips_file = os.path.join(OUTPUT_DIR_TRIPS, f"{ROADNETWORK}.trips.xml")
    rou_file   = os.path.join(OUTPUT_DIR, f"{ROADNETWORK}.rou.xml")
    seed = random.randint(0, 1000000)

    random_trips_cmd = [
        "python", os.path.join(SUMO_TOOLS, "randomTrips.py"),
        "-n", NET_FILE,
        "-o", trips_file,
        "--begin", "0",
        "--end", "300",
        "--fringe-factor", "0.1",
        "--period", "1",
        "--validate",
        "--seed", str(seed),
        
    ]

    subprocess.run(random_trips_cmd, check=True)

    duarouter_cmd = [
        "duarouter",
        "-n", NET_FILE,
        "-t", trips_file,
        "-o", rou_file,
        "--ignore-errors"
    ]

    subprocess.run(duarouter_cmd, check=True)

def copy_summary_file(run_index):
    src = r"C:\Users\bobbi\Documents\YEAR 3\sumo3\summary.xml"
    dest_folder = r"C:\Users\bobbi\Documents\YEAR 3\sumo3\results\CNSBPSHORT"
    os.makedirs(dest_folder, exist_ok=True)

    dest = os.path.join(dest_folder, f"summary_{run_index}.xml")
    shutil.copy(src, dest)

def copy_queue_file(run_index):
    src = r"C:\Users\bobbi\Documents\YEAR 3\sumo3\queue_output.xml"
    dest_folder = r"C:\Users\bobbi\Documents\YEAR 3\sumo3\results\CNSBPSHORT"
    os.makedirs(dest_folder, exist_ok=True)

    dest = os.path.join(dest_folder, f"queue_{run_index}.xml")
    shutil.copy(src, dest)
    

def main():
    for i in range(50,100):
        # Run the main script
        route_generator(i)
        run_main_script()

        # Check if the script has finished running
        if os.path.exists("main.py"):
            print("main.py has finished running.")
        else:
            print("main.py is still running.")

        copy_summary_file(i)
        copy_queue_file(i)
        # Wait for a while before running again (optional)
        #time.sleep(1)


if __name__ == "__main__":
    # Run the main script
    main()