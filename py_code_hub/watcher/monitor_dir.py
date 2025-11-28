import fnmatch
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# ----------------------------
# Configuration
# ----------------------------
IGNORE_PATTERNS = ["*~", "*.swp", ".#*", "*.tmp"]
DEBOUNCE_DELAY = 0.5  # seconds

# Dictionary to track last modification times
_last_event_time = {}

# ----------------------------
# Event Handler
# ----------------------------
class MyHandler(FileSystemEventHandler):
    def _should_ignore(self, path):
        """Return True if the file matches any ignore pattern."""
        return any(fnmatch.fnmatch(path, pattern) for pattern in IGNORE_PATTERNS)

    def _should_process(self, path):
        """Debounce multiple events for the same file."""
        now = time.time()
        last_time = _last_event_time.get(path, 0)
        if now - last_time < DEBOUNCE_DELAY:
            return False
        _last_event_time[path] = now
        return True

    def _process_event(self, event, action):
        """Generalized event processor for created, modified, deleted."""
        if event.is_directory:  # Ignore directories
            return
        if self._should_ignore(event.src_path):
            return
        if not self._should_process(event.src_path):
            return
        print(f"{action}: {event.src_path}")

    def on_created(self, event):
        self._process_event(event, "File created")

    def on_modified(self, event):
        self._process_event(event, "File modified")

    def on_deleted(self, event):
        self._process_event(event, "File deleted")


# Step 2: Set the directory to watch
path_to_watch = "./my_folder"  # Change this to your folder path

# Step 3: Create an Observer
observer = Observer()
observer.schedule(MyHandler(), path=path_to_watch, recursive=True)

# Step 4: Start observing
observer.start()
print(f"Watching directory: {path_to_watch}")

try:
    while True:
        time.sleep(1)  # Keep the script running
except KeyboardInterrupt:
    observer.stop()
observer.join()
