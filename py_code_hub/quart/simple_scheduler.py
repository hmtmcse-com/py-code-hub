from quart import Quart
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import os

app = Quart(__name__)
scheduler = AsyncIOScheduler()

# --- Async job ---
async def async_job(name):
    print(f"Hello {name}! Time: {datetime.now().strftime('%H:%M:%S')}")

# --- Add jobs ---
def add_jobs():
    scheduler.add_job(
        async_job,  # Pass the async function directly
        trigger=IntervalTrigger(seconds=5),
        args=["Touhid"],
        id="say_hello",
        replace_existing=True
    )

@app.before_serving
async def startup():
    # Only start scheduler in main process (safe for dev auto-reload)
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or os.environ.get("WERKZEUG_RUN_MAIN") is None:
        add_jobs()
        scheduler.start()
        print("AsyncIOScheduler started!")

@app.after_serving
async def shutdown():
    scheduler.shutdown()
    print("Scheduler stopped!")

@app.route('/')
async def hello():
    return {"message": "Scheduler is running"}

if __name__ == '__main__':
    app.run(debug=True)
