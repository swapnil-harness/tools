import concurrent.futures
import subprocess
import time
import os
import sys
import tarfile
import tempfile
import json

def check_image_exists_locally(image):
    try:
        result = subprocess.run(["docker", "inspect", "--type=image", image], capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def pull_image(image, index, total):
    if check_image_exists_locally(image):
        print(f"[{index + 1}/{total}] {image} already exists locally, skipping pull.")
        return (image, True)

    try:
        print(f"[{index + 1}/{total}] Pulling {image}...")
        subprocess.run(["docker", "pull", image], capture_output=True, text=True, check=True)
        print(f"[{index + 1}/{total}] Successfully pulled {image}")
        return (image, True)
    except subprocess.CalledProcessError as e:
        print(f"[{index + 1}/{total}] Failed to pull {image}: {e}")
        return (image, False)

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <filename> <service_account_key>")
        sys.exit(1)

    filename = sys.argv[1]
    service_account_key = sys.argv[2]

    with open(filename, "r") as f:
        images = [line.strip() for line in f.readlines()]

    start_time = time.time()
    success_count = 0
    failure_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(pull_image, image, i, len(images)): image for i, image in enumerate(images)}
        for future in concurrent.futures.as_completed(futures):
            _, success = future.result()
            if success:
                success_count += 1
            else:
                failure_count += 1

    end_time = time.time()
    total_time = end_time - start_time

    with tempfile.TemporaryDirectory() as tempdir:
        archive_path = os.path.join(tempdir, "images.tgz")
        with tarfile.open(archive_path, "w:gz") as tar:
            for image in images:
                image_name = image.replace("/", "_")
                subprocess.run(["docker", "save", image, "-o", f"{tempdir}/{image_name}.tar"])
                tar.add(f"{tempdir}/{image_name}.tar", arcname=f"{image_name}.tar")

        with open(service_account_key) as f:
            key_contents = json.load(f)

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_key
        bucket_path = "gs://smp-airgap-bundles"
        subprocess.run(["gsutil", "cp", archive_path, f"{bucket_path}/images.tgz"])

        with open(os.path.join(tempdir, "result.txt"), "w") as result_file:
            result_file.write(f"Total time: {total_time:.2f} seconds\n")
            result_file.write(f"Total images: {len(images)}\n")
            result_file.write(f"Succeeded: {success_count}\n")
            result_file.write(f"Failed: {failure_count}\n")

        subprocess.run(["gsutil", "cp", os.path.join(tempdir, "result.txt"), f"{bucket_path}/result.txt"])

if __name__ == "__main__":
    main()
