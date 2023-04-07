import concurrent.futures
import subprocess
import time
import os
import sys

def pull_and_save_image(image, index, total):
    try:
        print(f"[{index + 1}/{total}] Pulling {image}...")
        result = subprocess.run(["docker", "pull", image], capture_output=True, text=True, check=True)
        print(f"[{index + 1}/{total}] Successfully pulled {image}")
        
        save_path = f"harness-airgapped/{image.replace('/', '_')}.tar"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        result = subprocess.run(["docker", "save", "-o", save_path, image], capture_output=True, text=True, check=True)
        print(f"[{index + 1}/{total}] Successfully saved {image} to {save_path}")
        
        return (image, True)
    except subprocess.CalledProcessError as e:
        print(f"[{index + 1}/{total}] Failed to pull and save {image}: {e}")
        return (image, False)

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]

    with open(filename, "r") as f:
        images = [line.strip() for line in f.readlines()]

    print("Downloading all container images required for air gapped installation, this can take little more than an hour")
    start_time = time.time()

    success_count = 0
    failure_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(pull_and_save_image, image, index, len(images)): image for index, image in enumerate(images)}
        for future in concurrent.futures.as_completed(futures):
            _, success = future.result()
            if success:
                success_count += 1
            else:
                failure_count += 1

    end_time = time.time()

    print(f"Total time: {end_time - start_time:.2f} seconds")
    print(f"Total images: {len(images)}")
    print(f"Succeeded: {success_count}")
    print(f"Failed: {failure_count}")

if __name__ == "__main__":
    main()
