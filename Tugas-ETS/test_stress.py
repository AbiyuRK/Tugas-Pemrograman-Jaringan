import os
import subprocess
import sys
import time
import csv
import shutil
import argparse
from file_manage_server import startServer, stopServer

SERVER = "127.0.0.1"
PORT = 6667
OPERATIONS = ["upload", "get"]
VOLUMES = [10*1024*1024, 50*1024*1024, 100*1024*1024]
CLIENT_WORKERS = [1, 5, 50]
SERVER_WORKERS = [1, 5, 50]
RESULTS_CSV = "stress_test_results.csv"

def make_file(fileName, size):
    with open(fileName, "wb") as fp:
        fp.write(os.urandom(size))

def client_worker(op, filename):
    try:
        if op == "upload":
            result = subprocess.run(
                [sys.executable, "file_client_cli.py", "--server", SERVER, "--port", str(PORT), "upload", filename],
                capture_output=True, text=True, timeout=300
            )
        elif op == "get":
            result = subprocess.run(
                [sys.executable, "file_client_cli.py", "--server", SERVER, "--port", str(PORT), "get", filename],
                capture_output=True, text=True, timeout=300
            )
        else:
            return False
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        success = ("Sukses" in result.stdout)
        return success
    except Exception as e:
        print(f"[ERROR] Exception in client_worker: {str(e)}")
        return False
    
def client_stress(op, size, client_workers):
    file = f"file_{size//1024//1024}MB.bin"
    if op == "upload" and not os.path.exists(file):
        make_file(file, size)
    succes = 0
    fails = 0
    time_start = time.time()
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    def worker_func(i):
        fname = file
        if op == "upload":
            worker_file = f"worker_{i}_{file}"
            shutil.copy(fname, worker_file)
            s = client_worker(op, worker_file)
            if os.path.exists(worker_file):
                os.remove(worker_file)
            return s
        else:
            s = client_worker(op, fname)
            return s
        
    with ThreadPoolExecutor(max_workers=client_workers) as executor:
        futures = [executor.submit(worker_func, i) for i in range(client_workers)]
        for future in as_completed(futures):
            if future.result():
                succes += 1
            else:
                fails += 1
    
    time_end = time.time()
    total_time = time_end - time_start
    
    throughput = (size * succes) / total_time if total_time > 0 else 0
    return total_time, throughput, succes, fails

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=1, help="Mulai dari kombinasi ke-berapa (1-based)")
    parser.add_argument("--end", type=int, default=None, help="Sampai kombinasi ke-berapa (1-based, opsional)")
    args = parser.parse_args()

    fieldnames = [
        "No", "Operasi", "Volume (MB)", "Client Worker Pool",
        "Server Worker Pool", "Waktu Total per Client (s)",
        "Throughput per Client (B/s)", "Worker Client Sukses",
        "Worker Client Gagal"
    ]
    nomor = 1
    if not os.path.exists(RESULTS_CSV) or args.start == 1:
        with open(RESULTS_CSV, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
    # Loop kombinasi
    for op in OPERATIONS:
        for size in VOLUMES:
            for clients in CLIENT_WORKERS:
                for servers in SERVER_WORKERS:
                    if nomor < args.start:
                        nomor += 1
                        continue
                    if args.end is not None and nomor > args.end:
                        print(f"Selesai (kombinasi terakhir: {nomor-1})")
                        return
                    print(f"\n--- Kombinasi ke-{nomor} ---")
                    print(f"Operasi: {op}, Volume: {size//1024//1024} MB, Client Worker Pool: {clients}, Server Worker Pool: {servers}")
                    proc = startServer(servers)
                    time.sleep(2)
                    file = f"file_{size//1024//1024}MB.bin"
                    if op == "upload":
                        if not os.path.exists(file):
                            make_file(file, size)
                    total_time, throughput, n_success, n_fail = client_stress(op, size, clients)
                    print(f"Total waktu per client: {total_time:.2f}s, Throughput: {throughput:.2f} B/s, Sukses: {n_success}, Gagal: {n_fail}")
                    row = {
                        "No": nomor,
                        "Operasi": op,
                        "Volume (MB)": size//1024//1024,
                        "Client Worker Pool": clients,
                        "Server Worker Pool": servers,
                        "Waktu Total per Client (s)": f"{total_time:.2f}",
                        "Throughput per Client (B/s)": f"{throughput:.2f}",
                        "Worker Client Sukses": n_success,
                        "Worker Client Gagal": n_fail,
                    }
                    
                    with open(RESULTS_CSV, "a", newline="") as f:
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writerow(row)
                    nomor += 1
                    stopServer(proc)
                    time.sleep(2)
    print(f"\nHasil rekap kombinasi sudah disimpan ke {RESULTS_CSV}")

if __name__ == "__main__":
    main()

        