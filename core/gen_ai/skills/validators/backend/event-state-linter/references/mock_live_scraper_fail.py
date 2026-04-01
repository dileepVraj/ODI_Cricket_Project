

class LiveState:
    def __init__(self) -> None:
        self.last_tick = None


class LiveScraper:
    async def stream(self) -> None:
        while True:
            payload = self.fetch_live()  # missing await + hot loop
            print(payload)

    def fetch_live(self):
        return {"ok": True}
