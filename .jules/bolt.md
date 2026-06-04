## Issue: Redundant mkdir calls in loop

- **Problem:** `core.process_images` calls `out_path.parent.mkdir(parents=True, exist_ok=True)` inside the loop for every file, leading to redundant syscalls even when the directory exists.
- **Impact:** About 5% overhead in pure Python benchmarking (5000 files processing drop from ~0.90s to ~0.85s). The impact scales heavily with filesystem latency and depth of directory tree.
- **Solution:** Maintain a `created_dirs` set inside `core.process_images` and check it before attempting to create the directory. This reduces the number of `mkdir` attempts from $O(N)$ (where $N$ is total files) to $O(D)$ (where $D$ is the number of directories).

## 2024-06-04 - Parallelize subprocess execution
**Learning:** In a pure Python script that orchestrates external command line processes (like `magick` ImageMagick calls), doing `subprocess.run` sequentially in a loop is a significant performance bottleneck. IO bounds and external tool processing times dominate execution.
**Action:** Use `concurrent.futures.ThreadPoolExecutor` to execute multiple `subprocess.run` processes in parallel, which greatly reduces total wait time without adding concurrency complexity, as the OS handles the actual multi-processing workload. Results from the threads can be safely collected into a stats dictionary sequentially using `executor.map`.
