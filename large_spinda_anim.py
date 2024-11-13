from glob import glob
from pathlib import Path
from argparse import ArgumentParser
from large_spinda import to_spindas
import json
import multiprocessing as mp
from time import time

GENERATIONS = 10
POPULATION = 100

# OUTPUT_DIR = "badspinda-fast"

def spindafy_frame(n, filename, overwrite=False, dump_json=False, n_inputs=0, output_dir="badspinda-fast"):

    if not overwrite and len(glob(output_dir + f"/frame{n:0>4}*")) > 0:
        # print("frame already found! skipping.")
        return
    
    if n % 100 == 0:
        print(f"Starting frame {n}")

    (img, pids) = to_spindas(filename, POPULATION, GENERATIONS, invert=True)

    output_filename = output_dir + f"/frame{n:0>4}.png"
    img.save(output_filename)

    # write PIDs to JSON files:
    if dump_json:
        with open(output_dir + f"/pids/frame{n:0>4}.json", "w") as f:
            json.dump(pids, f)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("input_directory")
    parser.add_argument("output_directory")
    # parser.add_argument("output_directory")
    # parser.add_argument("skip", type=int, default=0, nargs="?")
    # parser.add_argument("--skip-even", action="store_true")
    # parser.add_argument("--skip-odd", action="store_true")
    parser.add_argument('--overwrite', action="store_true")
    parser.add_argument('--dump-json', action="store_true")

    args = parser.parse_args()

    # find all input images
    inputs = [str(i) for i in glob(args.input_directory + "/*")]
        
    # create output directories if they don't exist
    Path(args.output_directory).mkdir(parents=True, exist_ok=True)

    if args.dump_json:
        Path(args.output_directory + "/pids").mkdir(parents=True, exist_ok=True)
    
    input_params = [(ind, f, args.overwrite, args.dump_json, len(inputs), args.output_directory)
                    for ind, f in enumerate(inputs)]
    
    cpu_count = -1
    try:
        cpu_count = mp.cpu_count()
    except NotImplementedError:
        cpu_count = 1
    
    start = time()

    with mp.Pool(cpu_count) as pool:
        pool.starmap(spindafy_frame, input_params, chunksize=1)

    print(time() - start)
        

