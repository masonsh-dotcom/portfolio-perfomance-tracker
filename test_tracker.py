"""Unit tests for every route in the portfolio tracker."""

from unittest import TestCase

from drafter import Button, Header, Link, Paragraph, TextBox, assert_has

from main import (
    State, Stock, add_stock, edit_stock, holdings, home, index, initial_state,
    remove_stock, save_price, save_settings, save_stock, settings, summary,
)


class TrackerTests(TestCase):
    """Check route results, calculations, and changes to portfolio state."""

    def test_index_and_home(self) -> None:
        """The root opens Home and Home shows the name and empty return."""
        state = initial_state()
        self.assertEqual(index(state), home(state))
        self.assertTrue(assert_has(home(state), Header("My Portfolio"), quiet=True))
        self.assertTrue(assert_has(home(state), Link("Holdings", "holdings"), quiet=True))

    def test_add_stock(self) -> None:
        """The Add Stock page contains the four inputs and save action."""
        page = add_stock(initial_state())
        for name in ("symbol", "shares", "purchase_price", "current_price"):
            self.assertTrue(assert_has(page, TextBox(name, "", id=name), quiet=True))
        self.assertTrue(assert_has(page, Button("Save stock", "save_stock"), quiet=True))

    def test_save_stock(self) -> None:
        """Saving a valid holding normalizes its ticker and allows fractions."""
        state = initial_state()
        page = save_stock(state, " brk.b ", "2.5", "100", "110")
        self.assertEqual(page.state.stocks, [Stock("BRK.B", 2.5, 100.0, 110.0)])
        self.assertTrue(assert_has(page, Header("My Holdings"), quiet=True))

    def test_save_stock_invalid(self) -> None:
        """Invalid tickers, quantities, and prices return the populated form."""
        state = initial_state()
        for inputs in [("<bad>", "2", "10", "20"), ("ABC", "0", "10", "20"),
                       ("ABC", "2", "nan", "20"), ("ABC", "2", "10", "-1")]:
            with self.subTest(inputs=inputs):
                page = save_stock(state, *inputs)
                self.assertEqual(page.state, initial_state())
                self.assertTrue(assert_has(page, Header("Add Stock"), quiet=True))
                self.assertTrue(assert_has(page, TextBox("symbol", inputs[0], id="symbol"), quiet=True))

    def test_holdings(self) -> None:
        """Holdings describes an empty list and shows a loss for a losing stock."""
        state = initial_state()
        self.assertTrue(assert_has(holdings(state), Paragraph("Your portfolio has no holdings yet."), quiet=True))
        state.stocks.append(Stock("ABC", 2, 100, 75))
        self.assertTrue(assert_has(holdings(state), Paragraph("Loss -$50.00 (-25.00%)"), quiet=True))

    def test_edit_stock(self) -> None:
        """The selected stock's price is prefilled and invalid indices are rejected."""
        state = State([Stock("ABC", 2.0, 100.0, 75.0)], "Demo", 0.0, 0.0)
        page = edit_stock(state, 0)
        self.assertTrue(assert_has(page, Header("Edit ABC"), quiet=True))
        self.assertTrue(assert_has(page, TextBox("new_price", "75.0", id="new_price"), quiet=True))
        self.assertTrue(assert_has(edit_stock(state, -1), Header("My Holdings"), quiet=True))

    def test_save_price(self) -> None:
        """Bad prices preserve state and a zero price updates only the selected holding."""
        state = State([Stock("ABC", 2, 100, 75), Stock("XYZ", 3, 8, 9)], "Demo", 0, 0)
        self.assertTrue(assert_has(save_price(state, 1, "inf"), Header("Edit XYZ"), quiet=True))
        self.assertEqual(state.stocks[1].current_price, 9)
        self.assertTrue(assert_has(save_price(state, 1, "0"), Header("My Holdings"), quiet=True))
        self.assertEqual(state.stocks, [Stock("ABC", 2, 100, 75), Stock("XYZ", 3, 8, 0)])

    def test_remove_stock(self) -> None:
        """Remove the chosen holding and ignore out-of-range selections."""
        state = State([Stock("ABC", 2, 100, 75), Stock("XYZ", 3, 8, 9)], "Demo", 0, 0)
        self.assertEqual(len(remove_stock(state, 4).state.stocks), 2)
        self.assertEqual(remove_stock(state, 0).state.stocks, [Stock("XYZ", 3, 8, 9)])

    def test_summary(self) -> None:
        """Show weighted stock performance, the top return, and goal progress including cash."""
        state = State([Stock("ABC", 2, 100, 150), Stock("XYZ", 10, 20, 15)], "Demo", 500, 50)
        page = summary(state)
        for line in (
            "Gain $50.00 (+12.50%)",
            "Top performer by percent return: ABC (+50.00%)",
            "100.0% of your $500.00 goal · Goal reached",
        ):
            self.assertTrue(assert_has(page, Paragraph(line), quiet=True))
        empty = summary(initial_state())
        self.assertTrue(assert_has(empty, Paragraph("Add a holding to see your top performer."), quiet=True))

    def test_settings(self) -> None:
        """Settings shows existing values and defaults the next deposit to zero."""
        page = settings(State([], "Demo", 500.0, 50.0))
        for name, value in [("name", "Demo"), ("goal", "500.0"), ("cash_deposit", "0")]:
            self.assertTrue(assert_has(page, TextBox(name, value, id=name), quiet=True))

    def test_save_settings(self) -> None:
        """Validate the whole form, then update all three settings and accumulate cash."""
        state = State([], "Demo", 500, 50)
        invalid = save_settings(state, "New name", "1000", "-1")
        self.assertEqual(invalid.state, State([], "Demo", 500, 50))
        self.assertTrue(assert_has(invalid, Header("Settings"), quiet=True))
        saved = save_settings(state, " New name ", "1000", "25")
        self.assertEqual(saved.state, State([], "New name", 1000, 75))
        self.assertTrue(assert_has(saved, Header("New name"), quiet=True))
        self.assertEqual(save_settings(state, "New name", "0", "25").state, State([], "New name", 0, 100))
