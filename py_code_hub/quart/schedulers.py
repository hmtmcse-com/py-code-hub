from quart import Quart
from datetime import datetime

from py_code_hub.quart.mweb_scheduler import mweb_scheduler

app = Quart(__name__)

# --- Async job ---
async def async_job(name):
    print(f"Hello {name}! Time: {datetime.now().strftime('%H:%M:%S')}")

@app.before_serving
async def startup():
    print("AsyncIOScheduler started!")

@app.after_serving
async def shutdown():
    # scheduler.shutdown()
    print("Scheduler stopped!")

@app.route('/')
async def hello():
    mweb_scheduler.start()
    mweb_scheduler.add_interval_job(async_job, job_id="say_hello", seconds=5, args=["Goru Go"])
    return {"message": "Scheduler is running"}

if __name__ == '__main__':
    app.run(debug=True)
