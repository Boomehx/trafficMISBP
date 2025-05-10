import os
import subprocess
import time
import random
import shutil

def run_main_script():
    subprocess.run(["python", "mainStatic.py"], check=True)

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

    cmd = [
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

    subprocess.run(cmd, check=True)

    duaroutercmd = [
        "duarouter",
        "-n", NET_FILE,
        "-t", trips_file,
        "-o", rou_file,
        "--ignore-errors"
    ]

    subprocess.run(duaroutercmd, check=True)

def copy_summary_file(runIndex):
    src = r"C:\Users\bobbi\Documents\YEAR 3\sumo3\summary.xml"
    dest = r"C:\Users\bobbi\Documents\YEAR 3\sumo3\results\STSHORT"
    os.makedirs(dest, exist_ok=True)

    dest = os.path.join(dest, f"summary_{runIndex}.xml")
    shutil.copy(src, dest)

def copy_queue_file(runIndex):
    src = r"C:\Users\bobbi\Documents\YEAR 3\sumo3\queue_output.xml"
    dest = r"C:\Users\bobbi\Documents\YEAR 3\sumo3\results\STSHORT"
    os.makedirs(dest, exist_ok=True)

    dest = os.path.join(dest, f"queue_{runIndex}.xml")
    shutil.copy(src, dest)
    

def main():
    for i in range(0, 50):
        route_generator(i)
        run_main_script()
        copy_summary_file(i)
        copy_queue_file(i)



if __name__ == "__main__":

    main()