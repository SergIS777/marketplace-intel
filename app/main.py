import asyncio, logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
log = logging.getLogger("intel")

async def main():
    log.info("marketplace-intel: skeleton started, waiting for modules")
    while True:
        await asyncio.sleep(3600)

asyncio.run(main())
