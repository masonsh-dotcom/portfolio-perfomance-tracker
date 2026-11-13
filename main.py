"""Portfolio Performance Tracker, a CISC106 web app built with Drafter."""

from dataclasses import dataclass
from math import isfinite

from drafter import (
    Button, Div, Header, Label, Link, Page, Paragraph, TextBox,
    add_website_css, hide_debug_information, route, set_site_information,
    set_website_framed, set_website_title, start_server,
)


@dataclass
class Stock:
    """A holding with a manually entered current price, in USD."""

    symbol: str
    shares: float
    purchase_price: float
    current_price: float


@dataclass
class State:
    """Holdings and settings for the current browser session."""

    stocks: list[Stock]
    portfolio_name: str
    investment_goal: float
    cash_balance: float


def initial_state() -> State:
    """Start with an empty portfolio, no goal, and no cash."""
    return State([], "My Portfolio", 0.0, 0.0)


def totals(stocks: list[Stock]) -> tuple[float, float]:
    """Return the total cost basis and current market value of the holdings."""
    cost = 0.0
    value = 0.0
    for stock in stocks:
        cost += stock.shares * stock.purchase_price
        value += stock.shares * stock.current_price
    return cost, value


def stock_return(stock: Stock) -> float:
    """Calculate the holding's percent return from its per-share prices."""
    return 100 * (stock.current_price - stock.purchase_price) / stock.purchase_price


def read_number(raw: str, minimum: float) -> float | None:
    """Read a finite decimal between the requested minimum and one billion."""
    try:
        value = float(raw)
    except ValueError:
        return None
    if not isfinite(value) or not minimum <= value <= 1_000_000_000:
        return None
    return value


def money(value: float) -> str:
    """Format a dollar amount with its sign before the currency symbol."""
    if round(value, 2) < 0:
        return f"-${abs(value):,.2f}"
    return f"${abs(value):,.2f}"


def performance(cost: float, value: float) -> str:
    """Describe the dollar and percentage change in the tracked holdings."""
    if cost == 0:
        return "Stock return unavailable until you add a holding."
    change = value - cost
    percent = 100 * change / cost
    if change > 0:
        return f"Gain {money(change)} ({percent:+.2f}%)"
    if change < 0:
        return f"Loss {money(change)} ({percent:+.2f}%)"
    return "No change ($0.00, 0.00%)"


def field(label: str, name: str, value: str = "") -> Div:
    """Create a labeled input with an optional prefilled value."""
    box = TextBox(name, value, id=name)
    return Div(Label(label, name), box, classes="tracker-field")


def notice(message: str) -> Div:
    """Show a result or validation message when one is present."""
    return Div(message, classes="tracker-notice", role="status")


def screen(state: State, title: str, content: list) -> Page:
    """Build a page with common navigation and the route's content."""
    navigation = Div(
        Link("Home", "home"),
        Link("Add Stock", "add_stock"),
        Link("Holdings", "holdings"),
        Link("Summary", "summary"),
        Link("Settings", "settings"),
        classes="tracker-nav", role="navigation", aria_label="Portfolio",
    )
    return Page(state, [Div(
        Paragraph("Portfolio Performance Tracker", classes="tracker-brand"),
        navigation, Header(title), *content, classes="tracker",
    )])


def metric(label: str, value: str) -> Div:
    """Display a labeled portfolio figure."""
    return Div(Paragraph(label), Header(value, 2), classes="tracker-metric")


@route
def index(state: State) -> Page:
    """Open Home at the site's root address."""
    return home(state)


@route
def home(state: State, message: str = "") -> Page:
    """Show the portfolio dashboard and links to the main tasks."""
    cost, value = totals(state.stocks)
    return screen(state, state.portfolio_name, [
        notice(message),
        Div(
            metric("Portfolio value", money(value + state.cash_balance)),
            metric("Stock value", money(value)),
            metric("Cash balance", money(state.cash_balance)),
            classes="tracker-metrics",
        ),
        Paragraph(performance(cost, value)),
        Paragraph("Enter prices manually. Your portfolio resets when you reload the site."),
        Link("Add a holding", "add_stock", classes="tracker-primary"),
    ])


@route
def add_stock(state: State, message: str = "", symbol: str = "", shares: str = "",
              purchase_price: str = "", current_price: str = "") -> Page:
    """Show the Add Stock form, preserving entries after a validation error."""
    return screen(state, "Add Stock", [
        notice(message),
        Paragraph("Record one purchase. Use plain numbers in USD and enter the latest price yourself."),
        Div(
            field("Ticker symbol (e.g. AAPL)", "symbol", symbol),
            field("Shares owned", "shares", shares),
            field("Purchase price per share ($)", "purchase_price", purchase_price),
            field("Current price per share ($)", "current_price", current_price),
            Button("Save stock", "save_stock"), classes="tracker-form",
        ),
    ])


@route
def save_stock(state: State, symbol: str, shares: str,
               purchase_price: str, current_price: str) -> Page:
    """Validate and add a holding, or show the form with an error."""
    ticker = symbol.strip().upper()
    quantity = read_number(shares, 0.000001)
    purchase = read_number(purchase_price, 0.000001)
    current = read_number(current_price, 0.0)
    if not 1 <= len(ticker) <= 12 or any(
        char not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-" for char in ticker
    ) or not any(char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" for char in ticker):
        return add_stock(state, "Enter a ticker of up to 12 letters, digits, periods, or hyphens.",
                         symbol, shares, purchase_price, current_price)
    if quantity is None or purchase is None or current is None:
        return add_stock(
            state, "Shares and purchase price must be at least 0.000001. "
            "Current price can be zero. Each amount must be at most 1 billion.",
            symbol, shares, purchase_price, current_price,
        )
    state.stocks.append(Stock(ticker, quantity, purchase, current))
    return holdings(state, f"Added {ticker}.")


@route
def holdings(state: State, message: str = "") -> Page:
    """List holdings with values, returns, and actions for each position."""
    content = [notice(message), Link("Add a holding", "add_stock", classes="tracker-primary")]
    if not state.stocks:
        content.append(Paragraph("Your portfolio has no holdings yet."))
    for stock_index, stock in enumerate(state.stocks):
        cost = stock.shares * stock.purchase_price
        value = stock.shares * stock.current_price
        arguments = [("stock_index", stock_index)]
        content.append(Div(
            Header(stock.symbol, 2),
            Paragraph(f"{stock.shares:,.6f}".rstrip("0").rstrip(".") + " shares"),
            Paragraph(f"Cost basis {money(cost)} · Current value {money(value)}"),
            Paragraph(f"Purchase price {money(stock.purchase_price)} · Current price {money(stock.current_price)}"),
            Paragraph(performance(cost, value)),
            Div(
                Link(f"Edit {stock.symbol} price", "edit_stock", arguments),
                Button(f"Remove {stock.symbol}", "remove_stock", arguments, classes="tracker-remove"),
                classes="tracker-actions",
            ),
            classes="tracker-holding",
        ))
    return screen(state, "My Holdings", content)


@route
def edit_stock(state: State, stock_index: int, message: str = "", new_price: str = "") -> Page:
    """Open the current-price form for the selected holding."""
    if not 0 <= stock_index < len(state.stocks):
        return holdings(state, "That holding is no longer available.")
    stock = state.stocks[stock_index]
    return screen(state, f"Edit {stock.symbol}", [
        notice(message),
        Paragraph(f"Recorded price per share: {money(stock.current_price)}"),
        Div(
            field("New current price per share ($)", "new_price",
                  new_price if message else str(stock.current_price)),
            Button("Save new price", "save_price", [("stock_index", stock_index)]),
            classes="tracker-form",
        ),
    ])


@route
def save_price(state: State, stock_index: int, new_price: str) -> Page:
    """Update a holding's current price after validating the selection and price."""
    if not 0 <= stock_index < len(state.stocks):
        return holdings(state, "That holding is no longer available.")
    price = read_number(new_price, 0.0)
    if price is None:
        return edit_stock(state, stock_index, "Enter a price from zero to 1 billion.", new_price)
    stock = state.stocks[stock_index]
    stock.current_price = price
    return holdings(state, f"Updated {stock.symbol}.")


@route
def remove_stock(state: State, stock_index: int) -> Page:
    """Remove the selected record from the list of tracked holdings."""
    if not 0 <= stock_index < len(state.stocks):
        return holdings(state, "That holding is no longer available.")
    stock = state.stocks.pop(stock_index)
    return holdings(state, f"Removed {stock.symbol}.")


@route
def summary(state: State) -> Page:
    """Show stock performance, the best holding, and progress toward the goal."""
    cost, value = totals(state.stocks)
    portfolio_value = value + state.cash_balance
    best_holding = "Add a holding to see your top performer."
    if state.stocks:
        best = max(state.stocks, key=stock_return)
        best_holding = f"Top performer by percent return: {best.symbol} ({stock_return(best):+.2f}%)"
    goal_text = "Set an investment goal in Settings to track your progress."
    if state.investment_goal > 0:
        progress = 100 * portfolio_value / state.investment_goal
        goal_text = f"{progress:.1f}% of your {money(state.investment_goal)} goal"
        if portfolio_value >= state.investment_goal:
            goal_text += " · Goal reached"
    return screen(state, "Portfolio Summary", [
        Div(
            metric("Cost basis", money(cost)),
            metric("Stock value", money(value)),
            metric("Cash balance", money(state.cash_balance)),
            metric("Portfolio value", money(portfolio_value)),
            classes="tracker-metrics",
        ),
        Header("Stock performance", 2), Paragraph(performance(cost, value)),
        Paragraph(best_holding),
        Header("Investment goal", 2), Paragraph(goal_text),
        Paragraph("Goal progress includes cash. Stock returns use the cost basis of the holdings."),
    ])


@route
def settings(state: State, message: str = "", name: str = "", goal: str = "",
             cash_deposit: str = "") -> Page:
    """Show the portfolio name, goal, and cash deposit form."""
    if not message:
        name = state.portfolio_name
        goal = str(state.investment_goal)
        cash_deposit = "0"
    return screen(state, "Settings", [
        notice(message),
        Paragraph(f"Cash balance: {money(state.cash_balance)}. Deposits add to this balance."),
        Div(
            field("Portfolio name", "name", name),
            field("Investment goal ($, zero clears the goal)", "goal", goal),
            field("Cash deposit ($)", "cash_deposit", cash_deposit),
            Button("Save settings", "save_settings"), classes="tracker-form",
        ),
    ])


@route
def save_settings(state: State, name: str, goal: str, cash_deposit: str) -> Page:
    """Update the name, goal, and accumulated cash after validating all inputs."""
    clean_name = name.strip()
    new_goal = read_number(goal, 0.0)
    deposit = read_number(cash_deposit, 0.0)
    if not 1 <= len(clean_name) <= 60:
        return settings(state, "Enter a portfolio name from 1 to 60 characters.", name, goal, cash_deposit)
    if new_goal is None or deposit is None:
        return settings(state, "Enter goal and deposit amounts from zero to 1 billion.",
                        name, goal, cash_deposit)
    state.portfolio_name = clean_name
    state.investment_goal = new_goal
    state.cash_balance += deposit
    return home(state, "Settings saved.")


def configure_site() -> None:
    """Set the site title, assignment credits, and responsive presentation."""
    set_website_title("Portfolio Performance Tracker")
    set_site_information(
        author="Mason Shimp",
        description="A CISC106 tracker for manually priced stocks, cash, returns, and an investment goal.",
        sources="Drafter documentation and ChatGPT. See the repository's AI conversation file.",
        planning="See the brainstorming and design documents in the repository's worksheets folder.",
        links=["https://drafter-edu.github.io/drafter/"],
    )
    hide_debug_information()
    set_website_framed(False)
    add_website_css("""
        body { background: #f2f6f5; }
        .tracker { max-width: 58rem; margin: 0 auto; padding: 1.75rem 1rem 3rem;
                   color: #172d2b; font-family: "DM Sans", system-ui, sans-serif; }
        .tracker h1 { margin: 1.45rem 0 1rem; font-size: clamp(2rem, 5vw, 3.1rem); }
        .tracker h2 { margin: .5rem 0; font-size: 1.3rem; }
        .tracker p { margin: .55rem 0; }
        .tracker .tracker-brand { font-weight: 750; color: #1b574d; }
        .tracker-nav, .tracker-actions { display: flex; flex-wrap: wrap; gap: .6rem 1rem; align-items: center; }
        .tracker-nav { border-bottom: 1px solid #c7d8d4; padding: .65rem 0 .9rem; }
        .tracker a { color: #185749; text-underline-offset: .16em; }
        .tracker button, .tracker .tracker-primary { display: inline-block; padding: .55rem .9rem;
            border: 1px solid #185749; border-radius: .45rem; background: #185749; color: white;
            font: inherit; font-weight: 650; text-decoration: none; cursor: pointer; }
        .tracker .tracker-remove { color: #8a2f28; background: white; border-color: #e1b5af; }
        .tracker button:hover, .tracker .tracker-primary:hover { filter: brightness(.9); }
        .tracker :focus-visible { outline: 3px solid #388e7c; outline-offset: 3px; }
        .tracker-metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 12rem), 1fr));
            gap: .7rem; margin: 1rem 0; }
        .tracker-metric, .tracker-holding, .tracker-form { background: white; padding: 1rem;
            border: 1px solid #cdded9; border-radius: .65rem; }
        .tracker-metric h2 { overflow-wrap: anywhere; font-variant-numeric: tabular-nums; }
        .tracker-holding, .tracker-form { margin: 1rem 0; }
        .tracker-form { max-width: 28rem; }
        .tracker-field { margin-bottom: 1rem; }
        .tracker-field label { display: block; font-weight: 650; margin-bottom: .35rem; }
        .tracker-field input { box-sizing: border-box; width: 100%; padding: .55rem .65rem;
            border: 1px solid #758e87; border-radius: .35rem; font: inherit; }
        .tracker-notice:not(:empty) { background: #e2efec; border-left: 4px solid #287667;
            padding: .7rem .9rem; margin: .75rem 0; }
        .tracker-actions { margin-top: .8rem; }
        .tracker .tracker-primary { margin: .65rem 0 .25rem; }
    """)


if __name__ == "__main__":
    configure_site()
    start_server(initial_state())
