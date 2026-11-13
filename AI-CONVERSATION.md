**You**

I have four boxes on my Add Stock page. How do I get Drafter to send those values to my `save_stock` function?

**ChatGPT**

Give each `TextBox` the same name as its matching route parameter. For example, `TextBox("shares")` matches `shares: str` in `save_stock`. Point the Save Stock button at that route. Then convert the numeric inputs, validate them, and append a `Stock` to `state.stocks` once all four inputs are valid.

**You**

What happens if someone types `abc` for the number of shares?

**ChatGPT**

Catch the conversion error and show the Add Stock page again with an error message and the values they already entered. Validate all four inputs before changing `state.stocks` so a failed submission leaves the portfolio as it was.

**You**

How can I check that the summary is right after I update a price and add cash?

**ChatGPT**

Use numbers you can check by hand. Add 10 shares bought at $150 each, then update the current price to $180. The cost basis should be $1,500 and the stock value should be $1,800. That gives you a $300 gain and a 20% return. Deposit $100 in Settings and check that the portfolio value rises to $1,900 while the stock return stays at 20%.

**You**

What should I check after removing the stock?

**ChatGPT**

Check that the holdings list is empty, the $100 cash balance is still there, and the summary says stock return is unavailable. That covers the case where the cost basis is zero.

**You**

GitHub Actions found the built site, but the deploy job failed with a 404. What should I check?

**ChatGPT**

Open **Settings → Pages** using the link in the error message. Set the publishing source to **GitHub Actions**, then rerun the failed deployment. The workflow already built the site files, so this error points to the Pages setup.

**You**

How do I know the site is ready to submit?

**ChatGPT**

Once the deployment has a green check, open **Settings → Pages → Visit site** in an incognito window. Add a stock, update its price, and check that the summary reflects the change. Then submit the live website URL in Canvas.

# Fictional example — Setting up the Drafter app

**You**

I have the idea for my portfolio tracker, but how do I set up `main.py` so Drafter opens a homepage?

**ChatGPT**

Start with a `State` dataclass, one route, and a call to `start_server`. For this project, define `Stock` first so `State` can use `list[Stock]`. Then write an `index` route. Drafter calls `index` when someone opens the site’s main address. In the finished project, `index` calls `home(state)` so both routes show the same dashboard.

**You**

What values should I start with in `State`?

**ChatGPT**

Start with an empty list of stocks, `"My Portfolio"` as the name, and `0.0` for both the investment goal and cash balance. Put those values in an `initial_state()` function that returns `State([], "My Portfolio", 0.0, 0.0)`. Each call creates a fresh list, which keeps separate test runs from sharing holdings.

**You**

How do I connect the homepage to another page?

**ChatGPT**

Define the second page as a function with `@route`, such as `holdings(state: State) -> Page`. Then add `Link("Holdings", "holdings")` to the homepage. The first `"Holdings"` is the text visitors see. The second `"holdings"` is the route Drafter opens. Return `Page(state, [...])` from both routes so the portfolio carries across pages.

**You**

Why does `start_server` go inside `if __name__ == "__main__":`?

**ChatGPT**

That lets you run `main.py` in Thonny to start the website and import the route functions in `test_tracker.py` without launching the server. In the same block, call `configure_site()` before `start_server(initial_state())` so the site title and `set_site_information(...)` credits are in place when the app starts.
