import asyncio
import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
log = logging.getLogger("intel")

async def run_telegram_bot():
    try:
        from telegram_bot import main as bot_main
        log.info("Starting Telegram bot...")
        await bot_main()
    except Exception as e:
        log.error(f"Telegram bot failed: {e}")

async def run_scheduler():
    try:
        from scheduler import main as scheduler_main
        log.info("Starting scheduler...")
        await scheduler_main()
    except Exception as e:
        log.error(f"Scheduler failed: {e}")

def run_dashboard():
    try:
        log.info("Starting Streamlit dashboard on port 8501...")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            str(Path(__file__).parent / "dashboard.py"),
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--server.headless=true"
        ])
    except Exception as e:
        log.error(f"Dashboard failed: {e}")

async def main():
    log.info("marketplace-intel: starting all modules")
    loop = asyncio.get_event_loop()
    dashboard_task = loop.run_in_executor(None, run_dashboard)
    bot_task = asyncio.create_task(run_telegram_bot())
    scheduler_task = asyncio.create_task(run_scheduler())
    log.info("All modules started, waiting for completion")
    await asyncio.gather(bot_task, scheduler_task, dashboard_task)

if __name__ == "__main__":
    asyncio.run(main())
