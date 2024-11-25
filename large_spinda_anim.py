from glob import glob
from pathlib import Path
from argparse import ArgumentParser
from large_spinda import to_spindas
import json
import multiprocessing as mp
from time import time
import os
from PIL import UnidentifiedImageError

GENERATIONS = 10
POPULATION = 100

# OUTPUT_DIR = "badspinda-fast"

def spindafy_frame(n, filename, overwrite=False, dump_json=False, n_inputs=0, output_dir="badspinda-fast", scale=1, edges=False):

    if not overwrite and len(glob(output_dir + f"/frame{n:0>7}*")) > 0:
        # print("frame already found! skipping.")
        if n % 100 == 0:
            print(f"Skipping frame {n}")
        return
    
    if n % 100 == 0:
        print(f"Starting frame {n}")

    (img, pids) = to_spindas(filename, POPULATION, GENERATIONS, invert=True, scale=scale, edges=edges)

    output_filename = output_dir + f"/frame{n:0>7}.png"
    img.save(output_filename)

    # write PIDs to JSON files:
    if dump_json:
        with open(output_dir + f"/pids/frame{n:0>7}.json", "w") as f:
            json.dump(pids, f)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("input", help="Input directory or image path.")
    parser.add_argument("output", help="Output directory or image path.")
    parser.add_argument("-s", "--start", type=int, default=0,
                        help="Frame to start from in the lexigraphical ordering, inclusive. "
                             "Defaults to 0.")
    parser.add_argument("-e", "--end", type=int, default=-1,
                        help="Frame to end on in lexigraphical ordering, exclusive. " 
                             "Make sure this is at least 1 more than start."
                             "Defaults to -1 (the last file).")
    parser.add_argument("-S", "--scale", type=float, default=1,
                        help="Float to multiply width and height of input images by. "
                             "Scales < 1 generate less spindas. Defaults to 1.0.")
    parser.add_argument("-E", '--edges', action="store_true",
                        help="Convert input image to its edges before rendering.")
    parser.add_argument("-c", "--ncores", type=int, default=-1,
                        help="How many CPU cores you want the program to use. -1 for auto-detect. "
                             "Default is -1.")
    parser.add_argument("-O", '--overwrite', action="store_true",
                        help="Overwrite existing files in output directory when generating")
    parser.add_argument("-J", '--dump-json', action="store_true",
                        help="Dumps the 2D JSON array of the PID's of the spindas for each frame.")

    args = parser.parse_args()

    if args.output.find(".") > 0 or args.input.find(".") > 0:
        if args.output.find(".") <= 0:
            print("Output directory must also be a file")
            exit(1)
        if args.input.find(".") <= 0:
            print("Input directory must also be a file")
            exit(1)

        if not os.path.exists(args.input):
            print(f"Could not find input file {args.input}")
            exit(1)
        
        try:
            img_out, _ = to_spindas(args.input, 0, 0, invert=True, edges=args.edges, scale=args.scale)
            img_out.save(args.output)
        except UnidentifiedImageError:
            print(f"Could not parse input file {args.input} as an image")
            exit(1)
        
        exit(0)
        
        
        

    # find all input images
    inputs = [str(i) for i in glob(args.input + "/*")]
        
    # create output directories if they don't exist
    Path(args.output).mkdir(parents=True, exist_ok=True)

    if args.dump_json:
        Path(args.output + "/pids").mkdir(parents=True, exist_ok=True)
    
    input_params = [(ind, f, args.overwrite, args.dump_json, len(inputs), args.output, args.scale, args.edges)
                    for ind, f in enumerate(inputs)][args.start:args.end]
    
    cpu_count = args.ncores
    if cpu_count == -1:
        try:
            cpu_count = mp.cpu_count()
        except NotImplementedError:
            cpu_count = 1
    
    start = time()

    with mp.Pool(cpu_count) as pool:
        pool.starmap(spindafy_frame, input_params, chunksize=1)

    run_time = time() - start
    if run_time > 60:
        print(f"Finished in {int(run_time // 60)}m {run_time % 60:.4f}s")
    else:
        print(f"Finished in {run_time:.4f}s")
        

