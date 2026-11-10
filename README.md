# Off-Piste — Field Notes

Code for the [Off-Piste](https://www.youtube.com/@goingoffpiste) YouTube channel.

Each video traces an equation back to the real-world problem that forced it into existence, then shows the math, the code, and the systems where it still lives today. Every folder here is the runnable code behind one episode, so you can reproduce what you saw on screen and change the inputs yourself.

## Episodes

| # | Episode | Folder | Video |
|---|---|---|---|
| 01 | The Math That Lets a Tower Catch a Rocket | [`01-rocket-landing`](01-rocket-landing) | coming soon |

## Running an episode

Each folder is self-contained with its own `requirements.txt`. Python 3.10 or newer:

```bash
cd 01-rocket-landing
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python lander.py
```

The episode's README lists the output you should see.

## A note on honesty

These are teaching models. They use the published math behind real systems, simplified so it fits in a screen of code. When a company hasn't published how its system works, the episode README says so and explains which public research the code follows.

Found a mistake in the math or the code? Open an issue. This audience checks the math, and corrections are welcome.

## License

[MIT](LICENSE)
