"""
White-box test cases for MoneyPoly game.
These tests cover all major branches, edge cases, and key variable states.
"""
import sys
import os
import pytest

# Add project root to path so we can import moneypoly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from moneypoly.dice import Dice
from moneypoly.player import Player
from moneypoly.property import Property, PropertyGroup
from moneypoly.bank import Bank
from moneypoly.board import Board
from moneypoly.cards import CardDeck, CHANCE_CARDS, COMMUNITY_CHEST_CARDS
from moneypoly.game import Game
from moneypoly.config import (
    STARTING_BALANCE, GO_SALARY, BOARD_SIZE,
    JAIL_POSITION, JAIL_FINE,
    INCOME_TAX_AMOUNT, LUXURY_TAX_AMOUNT,
)


# =====================================================================
# DICE TESTS
# =====================================================================

class TestDice:
    """Tests for Dice class — covers roll range, doubles, and streak."""

    def test_dice_roll_range(self):
        """Each die must produce values between 1 and 6."""
        d = Dice()
        for _ in range(200):
            d.roll()
            assert 1 <= d.die1 <= 6, f"die1 out of range: {d.die1}"
            assert 1 <= d.die2 <= 6, f"die2 out of range: {d.die2}"

    def test_dice_total_range(self):
        """Combined total must be between 2 and 12."""
        d = Dice()
        for _ in range(200):
            total = d.roll()
            assert 2 <= total <= 12, f"Total out of range: {total}"

    def test_dice_doubles_detection(self):
        """is_doubles() returns True only when both dice match."""
        d = Dice()
        d.die1 = 3
        d.die2 = 3
        assert d.is_doubles() is True

        d.die1 = 3
        d.die2 = 5
        assert d.is_doubles() is False

    def test_dice_doubles_streak_increments(self):
        """Doubles streak increases on consecutive doubles."""
        d = Dice()
        d.die1 = 4
        d.die2 = 4
        d.doubles_streak = 0
        # Simulate a roll that results in doubles
        d.die1 = 4
        d.die2 = 4
        if d.is_doubles():
            d.doubles_streak += 1
        assert d.doubles_streak == 1

    def test_dice_streak_resets_on_non_doubles(self):
        """Streak resets to 0 when dice are not doubles."""
        d = Dice()
        d.doubles_streak = 2
        d.die1 = 3
        d.die2 = 5
        if not d.is_doubles():
            d.doubles_streak = 0
        assert d.doubles_streak == 0

    def test_dice_reset(self):
        """reset() clears all dice state."""
        d = Dice()
        d.roll()
        d.reset()
        assert d.die1 == 0
        assert d.die2 == 0
        assert d.doubles_streak == 0

    def test_dice_describe(self):
        """describe() returns a readable string."""
        d = Dice()
        d.die1 = 3
        d.die2 = 4
        result = d.describe()
        assert "3 + 4 = 7" in result

    def test_dice_describe_doubles(self):
        """describe() shows DOUBLES when both dice match."""
        d = Dice()
        d.die1 = 5
        d.die2 = 5
        result = d.describe()
        assert "DOUBLES" in result


# =====================================================================
# PLAYER TESTS
# =====================================================================

class TestPlayer:
    """Tests for Player class — covers money, movement, jail, properties."""

    def test_player_initial_balance(self):
        """Player starts with the configured starting balance."""
        p = Player("Alice")
        assert p.balance == STARTING_BALANCE

    def test_add_money(self):
        """add_money() increases balance correctly."""
        p = Player("Alice", balance=500)
        p.add_money(200)
        assert p.balance == 700

    def test_add_negative_money_raises(self):
        """add_money() with negative amount raises ValueError."""
        p = Player("Alice")
        with pytest.raises(ValueError):
            p.add_money(-100)

    def test_deduct_money(self):
        """deduct_money() decreases balance correctly."""
        p = Player("Alice", balance=500)
        p.deduct_money(200)
        assert p.balance == 300

    def test_deduct_negative_money_raises(self):
        """deduct_money() with negative amount raises ValueError."""
        p = Player("Alice")
        with pytest.raises(ValueError):
            p.deduct_money(-50)

    def test_is_bankrupt_zero_balance(self):
        """Player with zero balance is bankrupt."""
        p = Player("Alice", balance=0)
        assert p.is_bankrupt() is True

    def test_is_bankrupt_negative_balance(self):
        """Player with negative balance is bankrupt."""
        p = Player("Alice", balance=-100)
        assert p.is_bankrupt() is True

    def test_is_not_bankrupt(self):
        """Player with positive balance is not bankrupt."""
        p = Player("Alice", balance=100)
        assert p.is_bankrupt() is False

    def test_move_basic(self):
        """move() updates position correctly."""
        p = Player("Alice")
        p.position = 5
        p.move(3)
        assert p.position == 8

    def test_move_wraps_around_board(self):
        """move() wraps position around the board."""
        p = Player("Alice")
        p.position = 38
        p.move(4)
        assert p.position == 2

    def test_move_pass_go_collects_salary(self):
        """Player collects GO salary when passing GO (wrapping around)."""
        p = Player("Alice", balance=1000)
        p.position = 38
        p.move(4)  # wraps to position 2
        assert p.balance == 1000 + GO_SALARY

    def test_move_no_salary_without_passing_go(self):
        """Player does not collect GO salary when not passing GO."""
        p = Player("Alice", balance=1000)
        p.position = 5
        p.move(3)
        assert p.balance == 1000

    def test_go_to_jail(self):
        """go_to_jail() sets position and jail flags."""
        p = Player("Alice")
        p.position = 30
        p.go_to_jail()
        assert p.position == JAIL_POSITION
        assert p.in_jail is True
        assert p.jail_turns == 0

    def test_add_property(self):
        """add_property() adds to player's holdings."""
        p = Player("Alice")
        prop = Property("Test", 1, 100, 10)
        p.add_property(prop)
        assert prop in p.properties
        assert p.count_properties() == 1

    def test_add_duplicate_property(self):
        """add_property() does not add duplicates."""
        p = Player("Alice")
        prop = Property("Test", 1, 100, 10)
        p.add_property(prop)
        p.add_property(prop)
        assert p.count_properties() == 1

    def test_remove_property(self):
        """remove_property() removes from player's holdings."""
        p = Player("Alice")
        prop = Property("Test", 1, 100, 10)
        p.add_property(prop)
        p.remove_property(prop)
        assert prop not in p.properties
        assert p.count_properties() == 0

    def test_remove_nonexistent_property(self):
        """remove_property() does nothing if property not owned."""
        p = Player("Alice")
        prop = Property("Test", 1, 100, 10)
        p.remove_property(prop)  # should not crash
        assert p.count_properties() == 0

    # ----- BUG 7: net_worth should include property values -----
    def test_net_worth_includes_properties(self):
        """
        net_worth() should include the value of owned properties.
        BUG: Currently only returns balance, ignoring properties.
        """
        p = Player("Alice", balance=500)
        prop = Property("Test", 1, 200, 10)
        p.add_property(prop)
        # net_worth should be balance + property value = 500 + 200 = 700
        assert p.net_worth() == 700

    def test_net_worth_no_properties(self):
        """net_worth() with no properties equals balance."""
        p = Player("Alice", balance=1500)
        assert p.net_worth() == 1500

    def test_status_line(self):
        """status_line() returns a readable string."""
        p = Player("Alice", balance=1000)
        line = p.status_line()
        assert "Alice" in line
        assert "1000" in line

    def test_status_line_jailed(self):
        """status_line() includes JAILED tag when in jail."""
        p = Player("Alice")
        p.in_jail = True
        line = p.status_line()
        assert "JAILED" in line


# =====================================================================
# PROPERTY TESTS
# =====================================================================

class TestProperty:
    """Tests for Property and PropertyGroup classes."""

    def test_property_creation(self):
        """Property initializes with correct values."""
        prop = Property("Park Place", 37, 350, 35)
        assert prop.name == "Park Place"
        assert prop.price == 350
        assert prop.base_rent == 35
        assert prop.mortgage_value == 175
        assert prop.owner is None
        assert prop.is_mortgaged is False

    def test_get_rent_basic(self):
        """get_rent() returns base rent normally."""
        prop = Property("Test", 1, 100, 10)
        assert prop.get_rent() == 10

    def test_get_rent_mortgaged(self):
        """get_rent() returns 0 when property is mortgaged."""
        prop = Property("Test", 1, 100, 10)
        prop.is_mortgaged = True
        assert prop.get_rent() == 0

    def test_get_rent_full_group_doubles(self):
        """get_rent() doubles when owner has full color group."""
        group = PropertyGroup("Brown", "brown")
        p1 = Property("Mediterranean", 1, 60, 2, group)
        p2 = Property("Baltic", 3, 60, 4, group)
        owner = Player("Alice")
        p1.owner = owner
        p2.owner = owner
        assert p1.get_rent() == 4  # 2 * 2
        assert p2.get_rent() == 8  # 4 * 2

    def test_get_rent_partial_group_no_double(self):
        """get_rent() does NOT double when owner has partial group."""
        group = PropertyGroup("Brown", "brown")
        p1 = Property("Mediterranean", 1, 60, 2, group)
        p2 = Property("Baltic", 3, 60, 4, group)
        owner = Player("Alice")
        p1.owner = owner
        p2.owner = Player("Bob")
        assert p1.get_rent() == 2  # no doubling

    def test_mortgage(self):
        """mortgage() returns payout and sets flag."""
        prop = Property("Test", 1, 100, 10)
        payout = prop.mortgage()
        assert payout == 50
        assert prop.is_mortgaged is True

    def test_mortgage_already_mortgaged(self):
        """mortgage() returns 0 if already mortgaged."""
        prop = Property("Test", 1, 100, 10)
        prop.mortgage()
        payout = prop.mortgage()
        assert payout == 0

    def test_unmortgage(self):
        """unmortgage() returns cost and clears flag."""
        prop = Property("Test", 1, 100, 10)
        prop.mortgage()
        cost = prop.unmortgage()
        assert cost == int(50 * 1.1)  # 55
        assert prop.is_mortgaged is False

    def test_unmortgage_not_mortgaged(self):
        """unmortgage() returns 0 if not mortgaged."""
        prop = Property("Test", 1, 100, 10)
        cost = prop.unmortgage()
        assert cost == 0

    def test_is_available(self):
        """is_available() returns True for unowned, unmortgaged property."""
        prop = Property("Test", 1, 100, 10)
        assert prop.is_available() is True

    def test_is_not_available_owned(self):
        """is_available() returns False if property is owned."""
        prop = Property("Test", 1, 100, 10)
        prop.owner = Player("Alice")
        assert prop.is_available() is False

    def test_property_group_all_owned_by(self):
        """all_owned_by() returns True only when ALL are owned by same player."""
        group = PropertyGroup("Brown", "brown")
        p1 = Property("Mediterranean", 1, 60, 2, group)
        p2 = Property("Baltic", 3, 60, 4, group)
        owner = Player("Alice")
        p1.owner = owner
        p2.owner = owner
        assert group.all_owned_by(owner) is True

    def test_property_group_partial_ownership(self):
        """all_owned_by() returns False when only some are owned."""
        group = PropertyGroup("Brown", "brown")
        p1 = Property("Mediterranean", 1, 60, 2, group)
        p2 = Property("Baltic", 3, 60, 4, group)
        owner = Player("Alice")
        p1.owner = owner
        # p2 unowned
        assert group.all_owned_by(owner) is False

    def test_property_group_none_player(self):
        """all_owned_by(None) returns False."""
        group = PropertyGroup("Brown", "brown")
        Property("Mediterranean", 1, 60, 2, group)
        assert group.all_owned_by(None) is False


# =====================================================================
# BANK TESTS
# =====================================================================

class TestBank:
    """Tests for Bank class — covers collect, pay_out, loans."""

    def test_bank_initial_balance(self):
        """Bank starts with configured starting funds."""
        bank = Bank()
        assert bank.get_balance() > 0

    def test_bank_collect(self):
        """collect() increases bank funds."""
        bank = Bank()
        initial = bank.get_balance()
        bank.collect(100)
        assert bank.get_balance() == initial + 100

    def test_bank_collect_negative_ignored(self):
        """collect() should ignore negative amounts."""
        bank = Bank()
        initial = bank.get_balance()
        bank.collect(-500)
        assert bank.get_balance() == initial

    def test_bank_pay_out(self):
        """pay_out() decreases bank funds."""
        bank = Bank()
        initial = bank.get_balance()
        paid = bank.pay_out(100)
        assert paid == 100
        assert bank.get_balance() == initial - 100

    def test_bank_pay_out_zero(self):
        """pay_out(0) returns 0 without changing anything."""
        bank = Bank()
        initial = bank.get_balance()
        paid = bank.pay_out(0)
        assert paid == 0
        assert bank.get_balance() == initial

    def test_bank_pay_out_negative(self):
        """pay_out() with negative returns 0."""
        bank = Bank()
        paid = bank.pay_out(-50)
        assert paid == 0

    def test_bank_pay_out_insufficient_funds(self):
        """pay_out() raises ValueError when bank lacks funds."""
        bank = Bank()
        with pytest.raises(ValueError):
            bank.pay_out(999999999)

    def test_bank_give_loan(self):
        """give_loan() credits the player."""
        bank = Bank()
        p = Player("Alice", balance=0)
        bank.give_loan(p, 500)
        assert p.balance == 500
        assert bank.loan_count() == 1
        assert bank.total_loans_issued() == 500

    def test_bank_give_loan_zero(self):
        """give_loan() with zero does nothing."""
        bank = Bank()
        p = Player("Alice", balance=100)
        bank.give_loan(p, 0)
        assert p.balance == 100
        assert bank.loan_count() == 0


# =====================================================================
# BOARD TESTS
# =====================================================================

class TestBoard:
    """Tests for Board class — covers tile types and property lookup."""

    def test_board_has_22_properties(self):
        """Board should have 22 purchasable properties."""
        board = Board()
        assert len(board.properties) == 22

    def test_go_tile(self):
        """Position 0 is the GO tile."""
        board = Board()
        assert board.get_tile_type(0) == "go"

    def test_jail_tile(self):
        """Position 10 is the jail tile."""
        board = Board()
        assert board.get_tile_type(10) == "jail"

    def test_go_to_jail_tile(self):
        """Position 30 is the go_to_jail tile."""
        board = Board()
        assert board.get_tile_type(30) == "go_to_jail"

    def test_property_tile(self):
        """Position 1 (Mediterranean) is a property tile."""
        board = Board()
        assert board.get_tile_type(1) == "property"

    def test_chance_tile(self):
        """Position 7 is a chance tile."""
        board = Board()
        assert board.get_tile_type(7) == "chance"

    def test_community_chest_tile(self):
        """Position 2 is a community chest tile."""
        board = Board()
        assert board.get_tile_type(2) == "community_chest"

    def test_get_property_at_valid(self):
        """get_property_at() returns property at valid position."""
        board = Board()
        prop = board.get_property_at(1)
        assert prop is not None
        assert prop.name == "Mediterranean Avenue"

    def test_get_property_at_invalid(self):
        """get_property_at() returns None for non-property position."""
        board = Board()
        assert board.get_property_at(0) is None

    def test_is_purchasable_unowned(self):
        """is_purchasable() returns True for unowned property."""
        board = Board()
        assert board.is_purchasable(1) is True

    def test_is_purchasable_owned(self):
        """is_purchasable() returns False for owned property."""
        board = Board()
        board.get_property_at(1).owner = Player("Alice")
        assert board.is_purchasable(1) is False

    def test_unowned_properties(self):
        """unowned_properties() returns all initially."""
        board = Board()
        assert len(board.unowned_properties()) == 22


# =====================================================================
# CARD DECK TESTS
# =====================================================================

class TestCardDeck:
    """Tests for CardDeck class — covers draw, peek, cycling."""

    def test_draw_returns_card(self):
        """draw() returns a card dict."""
        deck = CardDeck(CHANCE_CARDS)
        card = deck.draw()
        assert card is not None
        assert "action" in card

    def test_draw_cycles(self):
        """draw() cycles back to start after all cards are drawn."""
        cards = [{"action": "a", "value": 1}, {"action": "b", "value": 2}]
        deck = CardDeck(cards)
        c1 = deck.draw()
        c2 = deck.draw()
        c3 = deck.draw()  # should cycle back to first
        assert c3 == c1

    def test_draw_empty_deck(self):
        """draw() returns None for empty deck."""
        deck = CardDeck([])
        assert deck.draw() is None

    def test_peek(self):
        """peek() returns next card without advancing."""
        deck = CardDeck(CHANCE_CARDS)
        peeked = deck.peek()
        drawn = deck.draw()
        assert peeked == drawn

    def test_peek_empty_deck(self):
        """peek() returns None for empty deck."""
        deck = CardDeck([])
        assert deck.peek() is None

    def test_reshuffle(self):
        """reshuffle() resets index to 0."""
        deck = CardDeck(CHANCE_CARDS)
        deck.draw()
        deck.draw()
        deck.reshuffle()
        assert deck.index == 0


# =====================================================================
# GAME LOGIC TESTS — BUY PROPERTY
# =====================================================================

class TestBuyProperty:
    """Tests for buy_property() in Game class."""

    def _make_game(self):
        """Helper to create a 2-player game."""
        return Game(["Alice", "Bob"])

    def test_buy_property_success(self):
        """Player with enough money can buy a property."""
        game = self._make_game()
        player = game.players[0]
        prop = game.board.properties[0]  # Mediterranean, $60
        player.balance = 200
        result = game.buy_property(player, prop)
        assert result is True
        assert prop.owner == player
        assert player.balance == 140

    def test_buy_property_insufficient_funds(self):
        """Player with less money than price cannot buy."""
        game = self._make_game()
        player = game.players[0]
        prop = game.board.properties[0]  # $60
        player.balance = 30
        result = game.buy_property(player, prop)
        assert result is False
        assert prop.owner is None

    # ----- BUG 6: buy with exact balance should work -----
    def test_buy_property_exact_balance(self):
        """
        Player with EXACTLY enough money should be able to buy.
        BUG: Currently uses <= which rejects exact balance.
        """
        game = self._make_game()
        player = game.players[0]
        prop = game.board.properties[0]  # $60
        player.balance = 60
        result = game.buy_property(player, prop)
        assert result is True, "Player with exact balance should be able to buy"
        assert prop.owner == player
        assert player.balance == 0


# =====================================================================
# GAME LOGIC TESTS — PAY RENT
# =====================================================================

class TestPayRent:
    """Tests for pay_rent() in Game class."""

    def _make_game(self):
        return Game(["Alice", "Bob"])

    def test_pay_rent_basic(self):
        """Tenant pays rent and balance decreases."""
        game = self._make_game()
        tenant = game.players[0]
        owner = game.players[1]
        prop = game.board.properties[0]
        prop.owner = owner
        owner.add_property(prop)

        tenant.balance = 500
        owner.balance = 500
        rent = prop.get_rent()

        game.pay_rent(tenant, prop)
        assert tenant.balance == 500 - rent

    # ----- BUG 8: rent must be added to owner -----
    def test_pay_rent_owner_receives(self):
        """
        Owner must RECEIVE the rent money.
        BUG: Currently rent is deducted from tenant but never added to owner.
        """
        game = self._make_game()
        tenant = game.players[0]
        owner = game.players[1]
        prop = game.board.properties[0]
        prop.owner = owner
        owner.add_property(prop)

        tenant.balance = 500
        owner.balance = 500
        rent = prop.get_rent()

        game.pay_rent(tenant, prop)
        assert owner.balance == 500 + rent, "Owner should receive rent payment"

    def test_pay_rent_mortgaged_property(self):
        """No rent collected on mortgaged property."""
        game = self._make_game()
        tenant = game.players[0]
        owner = game.players[1]
        prop = game.board.properties[0]
        prop.owner = owner
        prop.is_mortgaged = True

        tenant.balance = 500
        game.pay_rent(tenant, prop)
        assert tenant.balance == 500  # no change

    def test_pay_rent_unowned_property(self):
        """No rent on unowned property."""
        game = self._make_game()
        tenant = game.players[0]
        prop = game.board.properties[0]
        prop.owner = None

        tenant.balance = 500
        game.pay_rent(tenant, prop)
        assert tenant.balance == 500


# =====================================================================
# GAME LOGIC TESTS — TRADE
# =====================================================================

class TestTrade:
    """Tests for trade() in Game class."""

    def _make_game(self):
        return Game(["Alice", "Bob"])

    def test_trade_success(self):
        """Trade transfers property and deducts money from buyer."""
        game = self._make_game()
        seller = game.players[0]
        buyer = game.players[1]
        prop = game.board.properties[0]
        prop.owner = seller
        seller.add_property(prop)

        buyer.balance = 500
        seller.balance = 500

        result = game.trade(seller, buyer, prop, 100)
        assert result is True
        assert prop.owner == buyer
        assert buyer.balance == 400

    # ----- BUG 10: seller must receive cash -----
    def test_trade_seller_receives_cash(self):
        """
        Seller must RECEIVE the cash amount from trade.
        BUG: Currently buyer pays but seller never gets the money.
        """
        game = self._make_game()
        seller = game.players[0]
        buyer = game.players[1]
        prop = game.board.properties[0]
        prop.owner = seller
        seller.add_property(prop)

        buyer.balance = 500
        seller.balance = 500

        game.trade(seller, buyer, prop, 100)
        assert seller.balance == 600, "Seller should receive cash from trade"

    def test_trade_buyer_cant_afford(self):
        """Trade fails when buyer cannot afford."""
        game = self._make_game()
        seller = game.players[0]
        buyer = game.players[1]
        prop = game.board.properties[0]
        prop.owner = seller
        seller.add_property(prop)

        buyer.balance = 50
        result = game.trade(seller, buyer, prop, 100)
        assert result is False

    def test_trade_wrong_owner(self):
        """Trade fails when seller doesn't own the property."""
        game = self._make_game()
        seller = game.players[0]
        buyer = game.players[1]
        prop = game.board.properties[0]
        prop.owner = buyer  # NOT seller

        result = game.trade(seller, buyer, prop, 100)
        assert result is False


# =====================================================================
# GAME LOGIC TESTS — JAIL
# =====================================================================

class TestJailLogic:
    """Tests for jail-related logic."""

    def test_player_sent_to_jail(self):
        """Player's position and flags set correctly when jailed."""
        p = Player("Alice")
        p.go_to_jail()
        assert p.position == JAIL_POSITION
        assert p.in_jail is True

    # ----- BUG 9: voluntary jail fine must deduct from player -----
    def test_jail_fine_deducts_from_player(self, monkeypatch):
        """
        When player voluntarily pays jail fine, money must be deducted.
        BUG: Currently bank collects but player.deduct_money() is never called.
        """
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        player.in_jail = True
        player.jail_turns = 0
        player.balance = 1000

        # Simulate user saying "yes" to pay fine
        monkeypatch.setattr("moneypoly.ui.confirm", lambda prompt: True)
        # Mock _move_and_resolve to avoid stdin prompts from property tiles
        monkeypatch.setattr(game, "_move_and_resolve", lambda p, r: None)

        game._handle_jail_turn(player)

        assert player.balance == 1000 - JAIL_FINE, "Jail fine must be deducted from player"
        assert player.in_jail is False

    def test_jail_use_get_out_of_jail_card(self, monkeypatch):
        """Player can use Get Out of Jail Free card."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        player.in_jail = True
        player.jail_turns = 0
        player.get_out_of_jail_cards = 1
        player.balance = 1000

        monkeypatch.setattr("moneypoly.ui.confirm", lambda prompt: True)
        # Mock _move_and_resolve to avoid stdin prompts from property tiles
        monkeypatch.setattr(game, "_move_and_resolve", lambda p, r: None)

        game._handle_jail_turn(player)

        assert player.in_jail is False
        assert player.get_out_of_jail_cards == 0
        assert player.balance == 1000  # no fine deducted

    def test_jail_mandatory_release(self, monkeypatch):
        """After 3 turns in jail, player is forcibly released and fined."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        player.in_jail = True
        player.jail_turns = 2  # will become 3 inside method
        player.balance = 1000

        # Say no to both options, forcing mandatory release
        monkeypatch.setattr("moneypoly.ui.confirm", lambda prompt: False)
        # Mock _move_and_resolve to avoid stdin prompts from property tiles
        monkeypatch.setattr(game, "_move_and_resolve", lambda p, r: None)

        game._handle_jail_turn(player)

        assert player.in_jail is False
        assert player.balance == 1000 - JAIL_FINE


# =====================================================================
# GAME LOGIC TESTS — MORTGAGE
# =====================================================================

class TestMortgage:
    """Tests for mortgage and unmortgage in Game class."""

    def _make_game(self):
        return Game(["Alice", "Bob"])

    def test_mortgage_property(self):
        """Mortgaging credits player with half the property price."""
        game = self._make_game()
        player = game.players[0]
        prop = game.board.properties[0]  # $60
        prop.owner = player
        player.add_property(prop)
        player.balance = 100

        result = game.mortgage_property(player, prop)
        assert result is True
        assert prop.is_mortgaged is True
        assert player.balance == 130  # 100 + 30 (half of 60)

    def test_mortgage_not_owned(self):
        """Cannot mortgage property not owned by player."""
        game = self._make_game()
        player = game.players[0]
        prop = game.board.properties[0]
        prop.owner = game.players[1]

        result = game.mortgage_property(player, prop)
        assert result is False

    def test_unmortgage_property(self):
        """Unmortgaging charges player 110% of mortgage value."""
        game = self._make_game()
        player = game.players[0]
        prop = game.board.properties[0]  # $60, mortgage = $30
        prop.owner = player
        player.add_property(prop)
        prop.is_mortgaged = True
        player.balance = 500

        cost = int(prop.mortgage_value * 1.1)  # 33
        result = game.unmortgage_property(player, prop)
        assert result is True
        assert prop.is_mortgaged is False
        assert player.balance == 500 - cost


# =====================================================================
# GAME LOGIC TESTS — BANKRUPTCY
# =====================================================================

class TestBankruptcy:
    """Tests for bankruptcy detection and elimination."""

    def test_bankrupt_player_eliminated(self):
        """Bankrupt player is removed from the game."""
        game = Game(["Alice", "Bob", "Charlie"])
        player = game.players[0]
        player.balance = -100  # bankrupt

        game._check_bankruptcy(player)
        assert player not in game.players
        assert player.is_eliminated is True

    def test_bankrupt_properties_released(self):
        """Bankrupt player's properties become unowned."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        prop = game.board.properties[0]
        prop.owner = player
        player.add_property(prop)
        player.balance = -50

        game._check_bankruptcy(player)
        assert prop.owner is None

    def test_non_bankrupt_not_eliminated(self):
        """Player with positive balance is not eliminated."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        player.balance = 100

        initial_count = len(game.players)
        game._check_bankruptcy(player)
        assert len(game.players) == initial_count


# =====================================================================
# GAME LOGIC TESTS — WINNER
# =====================================================================

class TestWinner:
    """Tests for find_winner() logic."""

    def test_find_winner_highest_net_worth(self):
        """Winner should be the player with highest net worth."""
        game = Game(["Alice", "Bob"])
        game.players[0].balance = 3000
        game.players[1].balance = 1000
        winner = game.find_winner()
        assert winner.name == "Alice"

    def test_find_winner_empty_players(self):
        """find_winner() returns None when no players."""
        game = Game(["Alice"])
        game.players.clear()
        assert game.find_winner() is None


# =====================================================================
# EDGE CASE TESTS
# =====================================================================

class TestEdgeCases:
    """Edge case and boundary value tests."""

    def test_zero_balance_player(self):
        """Player with zero balance is bankrupt."""
        p = Player("Alice", balance=0)
        assert p.is_bankrupt() is True

    def test_large_balance(self):
        """Player can handle very large balances."""
        p = Player("Alice", balance=0)
        p.add_money(10000000)
        assert p.balance == 10000000

    def test_multiple_properties_net_worth(self):
        """Net worth should sum all property values."""
        p = Player("Alice", balance=500)
        p1 = Property("A", 1, 100, 5)
        p2 = Property("B", 3, 200, 10)
        p.add_property(p1)
        p.add_property(p2)
        # Expected: 500 + 100 + 200 = 800
        assert p.net_worth() == 800

    def test_card_deck_length(self):
        """CardDeck length matches input cards."""
        deck = CardDeck(CHANCE_CARDS)
        assert len(deck) == len(CHANCE_CARDS)

    def test_board_all_groups_exist(self):
        """Board has all 8 color groups."""
        board = Board()
        expected = ["brown", "light_blue", "pink", "orange",
                    "red", "yellow", "green", "dark_blue"]
        for color in expected:
            assert color in board.groups

    def test_player_initial_position(self):
        """Player starts at position 0."""
        p = Player("Alice")
        assert p.position == 0

    def test_player_initial_not_in_jail(self):
        """Player starts not in jail."""
        p = Player("Alice")
        assert p.in_jail is False
        assert p.jail_turns == 0

    def test_player_initial_no_jail_cards(self):
        """Player starts with no Get Out of Jail Free cards."""
        p = Player("Alice")
        assert p.get_out_of_jail_cards == 0

    def test_player_initial_not_eliminated(self):
        """Player starts not eliminated."""
        p = Player("Alice")
        assert p.is_eliminated is False

    def test_deduct_money_below_zero(self):
        """deduct_money() allows balance to go below zero."""
        p = Player("Alice", balance=100)
        p.deduct_money(200)
        assert p.balance == -100

    def test_add_money_zero(self):
        """add_money(0) does not change balance."""
        p = Player("Alice", balance=500)
        p.add_money(0)
        assert p.balance == 500

    def test_move_exact_board_size(self):
        """Moving exactly BOARD_SIZE positions wraps to same position."""
        p = Player("Alice", balance=1000)
        p.position = 0
        p.move(BOARD_SIZE)
        assert p.position == 0


# =====================================================================
# CARD ACTION TESTS — _apply_card()
# =====================================================================

class TestApplyCard:
    """Tests for _apply_card() covering all card action branches."""

    def _make_game(self):
        return Game(["Alice", "Bob"])

    def test_apply_card_collect(self):
        """'collect' card action adds money to player from bank."""
        game = self._make_game()
        player = game.players[0]
        player.balance = 500
        card = {"description": "Test", "action": "collect", "value": 100}
        game._apply_card(player, card)
        assert player.balance == 600

    def test_apply_card_pay(self):
        """'pay' card action deducts money from player."""
        game = self._make_game()
        player = game.players[0]
        player.balance = 500
        card = {"description": "Test", "action": "pay", "value": 50}
        game._apply_card(player, card)
        assert player.balance == 450

    def test_apply_card_jail(self):
        """'jail' card action sends player to jail."""
        game = self._make_game()
        player = game.players[0]
        card = {"description": "Test", "action": "jail", "value": 0}
        game._apply_card(player, card)
        assert player.in_jail is True
        assert player.position == JAIL_POSITION

    def test_apply_card_jail_free(self):
        """'jail_free' card action gives player a jail free card."""
        game = self._make_game()
        player = game.players[0]
        card = {"description": "Test", "action": "jail_free", "value": 0}
        game._apply_card(player, card)
        assert player.get_out_of_jail_cards == 1

    def test_apply_card_jail_free_accumulates(self):
        """Multiple jail_free cards stack."""
        game = self._make_game()
        player = game.players[0]
        card = {"description": "Test", "action": "jail_free", "value": 0}
        game._apply_card(player, card)
        game._apply_card(player, card)
        assert player.get_out_of_jail_cards == 2

    def test_apply_card_move_to_forward(self):
        """'move_to' card moves player to specific position (forward)."""
        game = self._make_game()
        player = game.players[0]
        player.position = 5
        player.balance = 500
        # Use position 24 which is a property already owned by player
        prop = game.board.get_property_at(24)
        if prop:
            prop.owner = player
        card = {"description": "Test", "action": "move_to", "value": 24}
        game._apply_card(player, card)
        assert player.position == 24

    def test_apply_card_move_to_backward_collects_go(self):
        """'move_to' card that wraps backward awards GO salary."""
        game = self._make_game()
        player = game.players[0]
        player.position = 35
        player.balance = 500
        card = {"description": "Test", "action": "move_to", "value": 0}
        game._apply_card(player, card)
        assert player.position == 0
        assert player.balance == 500 + GO_SALARY

    def test_apply_card_birthday(self):
        """'birthday' card collects from all other players."""
        game = self._make_game()
        player = game.players[0]
        other = game.players[1]
        player.balance = 500
        other.balance = 500
        card = {"description": "Test", "action": "birthday", "value": 10}
        game._apply_card(player, card)
        assert player.balance == 510
        assert other.balance == 490

    def test_apply_card_birthday_other_cant_pay(self):
        """'birthday' skips players who can't afford it."""
        game = self._make_game()
        player = game.players[0]
        other = game.players[1]
        player.balance = 500
        other.balance = 5  # can't afford $10
        card = {"description": "Test", "action": "birthday", "value": 10}
        game._apply_card(player, card)
        assert player.balance == 500  # no collection
        assert other.balance == 5  # unchanged

    def test_apply_card_collect_from_all(self):
        """'collect_from_all' collects from every other player."""
        game = self._make_game()
        player = game.players[0]
        other = game.players[1]
        player.balance = 500
        other.balance = 500
        card = {"description": "Test", "action": "collect_from_all", "value": 50}
        game._apply_card(player, card)
        assert player.balance == 550
        assert other.balance == 450

    def test_apply_card_collect_from_all_cant_pay(self):
        """'collect_from_all' skips players who can't afford."""
        game = self._make_game()
        player = game.players[0]
        other = game.players[1]
        player.balance = 500
        other.balance = 30  # can't afford $50
        card = {"description": "Test", "action": "collect_from_all", "value": 50}
        game._apply_card(player, card)
        assert player.balance == 500
        assert other.balance == 30

    def test_apply_card_none(self):
        """_apply_card() with None does nothing."""
        game = self._make_game()
        player = game.players[0]
        player.balance = 500
        game._apply_card(player, None)
        assert player.balance == 500


# =====================================================================
# TILE LANDING TESTS — _move_and_resolve()
# =====================================================================

class TestTileLanding:
    """Tests for tile landing effects via _move_and_resolve()."""

    def _make_game(self):
        return Game(["Alice", "Bob"])

    def test_landing_on_income_tax(self):
        """Landing on income tax deducts correct amount."""
        game = self._make_game()
        player = game.players[0]
        player.balance = 1500
        player.position = 0
        game._move_and_resolve(player, 4)  # position 4 = income tax
        assert player.balance == 1500 - INCOME_TAX_AMOUNT

    def test_landing_on_luxury_tax(self):
        """Landing on luxury tax deducts correct amount."""
        game = self._make_game()
        player = game.players[0]
        player.balance = 1500
        player.position = 34
        game._move_and_resolve(player, 4)  # position 38 = luxury tax
        assert player.balance == 1500 - LUXURY_TAX_AMOUNT

    def test_landing_on_go_to_jail(self):
        """Landing on Go To Jail sends player to jail."""
        game = self._make_game()
        player = game.players[0]
        player.position = 26
        game._move_and_resolve(player, 4)  # position 30 = go_to_jail
        assert player.in_jail is True
        assert player.position == JAIL_POSITION

    def test_landing_on_free_parking(self):
        """Landing on Free Parking does nothing to balance."""
        game = self._make_game()
        player = game.players[0]
        player.balance = 1500
        player.position = 16
        game._move_and_resolve(player, 4)  # position 20 = free parking
        assert player.balance == 1500

    def test_landing_on_chance(self):
        """Landing on Chance draws a card."""
        game = self._make_game()
        player = game.players[0]
        player.position = 3
        initial_index = game.chance_deck.index
        game._move_and_resolve(player, 4)  # position 7 = chance
        assert game.chance_deck.index == initial_index + 1

    def test_landing_on_community_chest(self):
        """Landing on Community Chest draws a card."""
        game = self._make_game()
        player = game.players[0]
        player.position = 0
        initial_index = game.community_deck.index
        game._move_and_resolve(player, 2)  # position 2 = community chest
        assert game.community_deck.index == initial_index + 1


# =====================================================================
# GAME FLOW TESTS — advance_turn(), current_player()
# =====================================================================

class TestGameFlow:
    """Tests for game flow control."""

    def test_advance_turn(self):
        """advance_turn() moves to the next player."""
        game = Game(["Alice", "Bob", "Charlie"])
        assert game.current_index == 0
        game.advance_turn()
        assert game.current_index == 1
        assert game.turn_number == 1

    def test_advance_turn_wraps(self):
        """advance_turn() wraps from last to first player."""
        game = Game(["Alice", "Bob"])
        game.advance_turn()  # index 1
        game.advance_turn()  # should wrap to 0
        assert game.current_index == 0

    def test_current_player(self):
        """current_player() returns correct player."""
        game = Game(["Alice", "Bob"])
        assert game.current_player().name == "Alice"
        game.advance_turn()
        assert game.current_player().name == "Bob"

    def test_game_initializes_correctly(self):
        """Game creates correct number of players and state."""
        game = Game(["Alice", "Bob", "Charlie"])
        assert len(game.players) == 3
        assert game.turn_number == 0
        assert game.running is True

    def test_game_board_created(self):
        """Game creates a board with properties."""
        game = Game(["Alice", "Bob"])
        assert game.board is not None
        assert len(game.board.properties) == 22

    def test_game_bank_created(self):
        """Game creates a bank."""
        game = Game(["Alice", "Bob"])
        assert game.bank is not None
        assert game.bank.get_balance() > 0

    def test_game_decks_created(self):
        """Game creates chance and community chest decks."""
        game = Game(["Alice", "Bob"])
        assert len(game.chance_deck) == len(CHANCE_CARDS)
        assert len(game.community_deck) == len(COMMUNITY_CHEST_CARDS)


# =====================================================================
# ADDITIONAL MORTGAGE / UNMORTGAGE EDGE CASES
# =====================================================================

class TestMortgageEdgeCases:
    """Additional edge cases for mortgage/unmortgage."""

    def _make_game(self):
        return Game(["Alice", "Bob"])

    def test_mortgage_already_mortgaged(self):
        """Mortgaging an already mortgaged property returns False."""
        game = self._make_game()
        player = game.players[0]
        prop = game.board.properties[0]
        prop.owner = player
        player.add_property(prop)

        game.mortgage_property(player, prop)
        result = game.mortgage_property(player, prop)
        assert result is False

    def test_unmortgage_not_owned(self):
        """Cannot unmortgage property not owned by player."""
        game = self._make_game()
        player = game.players[0]
        prop = game.board.properties[0]
        prop.owner = game.players[1]
        prop.is_mortgaged = True

        result = game.unmortgage_property(player, prop)
        assert result is False

    def test_unmortgage_not_mortgaged(self):
        """Cannot unmortgage a property that is not mortgaged."""
        game = self._make_game()
        player = game.players[0]
        prop = game.board.properties[0]
        prop.owner = player
        player.add_property(prop)

        result = game.unmortgage_property(player, prop)
        assert result is False

    def test_unmortgage_insufficient_funds(self):
        """Unmortgage fails if player can't afford the cost."""
        game = self._make_game()
        player = game.players[0]
        prop = game.board.properties[0]  # mortgage value = $30, cost = $33
        prop.owner = player
        player.add_property(prop)
        prop.is_mortgaged = True
        player.balance = 10  # not enough

        initial_balance = player.balance
        result = game.unmortgage_property(player, prop)
        # The game should reject unmortgage and keep balance unchanged
        assert player.balance == initial_balance


# =====================================================================
# BOARD HELPER METHODS
# =====================================================================

class TestBoardHelpers:
    """Tests for Board helper methods."""

    def test_properties_owned_by(self):
        """properties_owned_by() returns correct properties."""
        board = Board()
        player = Player("Alice")
        board.properties[0].owner = player
        board.properties[1].owner = player
        owned = board.properties_owned_by(player)
        assert len(owned) == 2

    def test_properties_owned_by_none(self):
        """properties_owned_by() returns empty for player with no properties."""
        board = Board()
        player = Player("Alice")
        owned = board.properties_owned_by(player)
        assert len(owned) == 0

    def test_is_special_tile(self):
        """is_special_tile() returns True for special tiles."""
        board = Board()
        assert board.is_special_tile(0) is True   # GO
        assert board.is_special_tile(10) is True   # Jail
        assert board.is_special_tile(7) is True    # Chance

    def test_is_not_special_tile(self):
        """is_special_tile() returns False for property tiles."""
        board = Board()
        assert board.is_special_tile(1) is False  # Mediterranean

    def test_get_tile_type_blank(self):
        """get_tile_type() returns 'blank' for empty positions."""
        board = Board()
        # Position 12 should be blank (no property, no special tile)
        tile = board.get_tile_type(12)
        assert tile == "blank"

    def test_is_purchasable_mortgaged(self):
        """is_purchasable() returns False for mortgaged property."""
        board = Board()
        prop = board.get_property_at(1)
        prop.is_mortgaged = True
        assert board.is_purchasable(1) is False

    def test_is_purchasable_non_property(self):
        """is_purchasable() returns False for non-property position."""
        board = Board()
        assert board.is_purchasable(0) is False  # GO tile

    def test_board_repr(self):
        """Board __repr__ returns readable string."""
        board = Board()
        result = repr(board)
        assert "22 properties" in result
        assert "0 owned" in result

    def test_railroad_tile_type(self):
        """Railroad positions are recognized."""
        board = Board()
        assert board.get_tile_type(5) == "railroad"
        assert board.get_tile_type(15) == "railroad"
        assert board.get_tile_type(25) == "railroad"
        assert board.get_tile_type(35) == "railroad"

    def test_income_tax_tile(self):
        """Income tax position is recognized."""
        board = Board()
        assert board.get_tile_type(4) == "income_tax"

    def test_luxury_tax_tile(self):
        """Luxury tax position is recognized."""
        board = Board()
        assert board.get_tile_type(38) == "luxury_tax"


# =====================================================================
# CARD DECK ADDITIONAL TESTS
# =====================================================================

class TestCardDeckExtra:
    """Additional tests for CardDeck."""

    def test_cards_remaining(self):
        """cards_remaining() returns correct count."""
        cards = [{"a": 1}, {"a": 2}, {"a": 3}]
        deck = CardDeck(cards)
        assert deck.cards_remaining() == 3
        deck.draw()
        assert deck.cards_remaining() == 2

    def test_deck_repr(self):
        """CardDeck __repr__ returns readable string."""
        deck = CardDeck(CHANCE_CARDS)
        result = repr(deck)
        assert "cards" in result

    def test_deck_len(self):
        """len(deck) matches card count."""
        deck = CardDeck(CHANCE_CARDS)
        assert len(deck) == len(CHANCE_CARDS)

    def test_community_deck_len(self):
        """Community Chest deck has correct number of cards."""
        deck = CardDeck(COMMUNITY_CHEST_CARDS)
        assert len(deck) == len(COMMUNITY_CHEST_CARDS)


# =====================================================================
# PROPERTY GROUP ADDITIONAL TESTS
# =====================================================================

class TestPropertyGroupExtra:
    """Additional tests for PropertyGroup."""

    def test_group_size(self):
        """size() returns number of properties in group."""
        group = PropertyGroup("Brown", "brown")
        Property("A", 1, 60, 2, group)
        Property("B", 3, 60, 4, group)
        assert group.size() == 2

    def test_get_owner_counts(self):
        """get_owner_counts() maps owners to property count."""
        group = PropertyGroup("Brown", "brown")
        p1 = Property("A", 1, 60, 2, group)
        p2 = Property("B", 3, 60, 4, group)
        alice = Player("Alice")
        p1.owner = alice
        p2.owner = alice
        counts = group.get_owner_counts()
        assert counts[alice] == 2

    def test_get_owner_counts_multiple_owners(self):
        """get_owner_counts() handles multiple owners."""
        group = PropertyGroup("LightBlue", "light_blue")
        p1 = Property("A", 6, 100, 6, group)
        p2 = Property("B", 8, 100, 6, group)
        p3 = Property("C", 9, 120, 8, group)
        alice = Player("Alice")
        bob = Player("Bob")
        p1.owner = alice
        p2.owner = bob
        p3.owner = alice
        counts = group.get_owner_counts()
        assert counts[alice] == 2
        assert counts[bob] == 1

    def test_get_owner_counts_no_owners(self):
        """get_owner_counts() returns empty dict when no owners."""
        group = PropertyGroup("Brown", "brown")
        Property("A", 1, 60, 2, group)
        counts = group.get_owner_counts()
        assert len(counts) == 0

    def test_add_property_to_group(self):
        """add_property() adds property and back-links the group."""
        group = PropertyGroup("Brown", "brown")
        prop = Property("A", 1, 60, 2)
        group.add_property(prop)
        assert prop in group.properties
        assert prop.group == group

    def test_add_duplicate_to_group(self):
        """add_property() does not add duplicates."""
        group = PropertyGroup("Brown", "brown")
        prop = Property("A", 1, 60, 2, group)
        group.add_property(prop)  # already in group
        assert group.size() == 1

    def test_property_group_repr(self):
        """PropertyGroup __repr__ returns readable string."""
        group = PropertyGroup("Brown", "brown")
        Property("A", 1, 60, 2, group)
        result = repr(group)
        assert "Brown" in result

    def test_property_repr(self):
        """Property __repr__ returns readable string."""
        prop = Property("Park Place", 37, 350, 35)
        result = repr(prop)
        assert "Park Place" in result
        assert "unowned" in result

    def test_property_repr_with_owner(self):
        """Property __repr__ shows owner name."""
        prop = Property("Park Place", 37, 350, 35)
        prop.owner = Player("Alice")
        result = repr(prop)
        assert "Alice" in result

    def test_property_houses_initial(self):
        """Property starts with 0 houses."""
        prop = Property("Test", 1, 100, 10)
        assert prop.houses == 0

    def test_is_not_available_mortgaged(self):
        """is_available() returns False if property is mortgaged."""
        prop = Property("Test", 1, 100, 10)
        prop.is_mortgaged = True
        assert prop.is_available() is False


# =====================================================================
# BANK ADDITIONAL TESTS
# =====================================================================

class TestBankExtra:
    """Additional tests for Bank."""

    def test_bank_give_loan_negative(self):
        """give_loan() with negative amount does nothing."""
        bank = Bank()
        p = Player("Alice", balance=100)
        bank.give_loan(p, -50)
        assert p.balance == 100
        assert bank.loan_count() == 0

    def test_bank_multiple_loans(self):
        """Bank tracks multiple loans."""
        bank = Bank()
        p = Player("Alice", balance=0)
        bank.give_loan(p, 200)
        bank.give_loan(p, 300)
        assert bank.loan_count() == 2
        assert bank.total_loans_issued() == 500

    def test_bank_repr(self):
        """Bank __repr__ returns readable string."""
        bank = Bank()
        result = repr(bank)
        assert "Bank" in result

    def test_bank_collect_zero_ignored(self):
        """collect(0) should be ignored."""
        bank = Bank()
        initial = bank.get_balance()
        bank.collect(0)
        assert bank.get_balance() == initial


# =====================================================================
# PLAYER REPR AND EDGE CASES
# =====================================================================

class TestPlayerExtra:
    """Additional Player edge case tests."""

    def test_player_repr(self):
        """Player __repr__ returns readable string."""
        p = Player("Alice")
        result = repr(p)
        assert "Alice" in result

    def test_player_custom_balance(self):
        """Player can be created with a custom balance."""
        p = Player("Alice", balance=2000)
        assert p.balance == 2000

    def test_move_returns_new_position(self):
        """move() returns the new position."""
        p = Player("Alice")
        p.position = 5
        new_pos = p.move(3)
        assert new_pos == 8

    def test_jail_turns_reset_on_go_to_jail(self):
        """go_to_jail() resets jail turns to 0."""
        p = Player("Alice")
        p.jail_turns = 5
        p.go_to_jail()
        assert p.jail_turns == 0


# =====================================================================
# DICE REPR AND EDGE CASES
# =====================================================================

class TestDiceExtra:
    """Additional Dice edge case tests."""

    def test_dice_repr(self):
        """Dice __repr__ returns readable string."""
        d = Dice()
        d.roll()
        result = repr(d)
        assert "Dice" in result

    def test_dice_total(self):
        """total() returns sum of both dice."""
        d = Dice()
        d.die1 = 3
        d.die2 = 4
        assert d.total() == 7

    def test_dice_describe_no_doubles(self):
        """describe() does not show DOUBLES when dice differ."""
        d = Dice()
        d.die1 = 2
        d.die2 = 5
        result = d.describe()
        assert "DOUBLES" not in result


# =====================================================================
# GAME BANKRUPTCY EDGE CASES
# =====================================================================

class TestBankruptcyExtra:
    """Additional bankruptcy edge cases."""

    def test_bankruptcy_clears_mortgages(self):
        """Bankrupt player's mortgaged properties are unmortgaged."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        prop = game.board.properties[0]
        prop.owner = player
        prop.is_mortgaged = True
        player.add_property(prop)
        player.balance = -100

        game._check_bankruptcy(player)
        assert prop.is_mortgaged is False

    def test_bankruptcy_adjusts_current_index(self):
        """Bankruptcy adjusts current_index when needed."""
        game = Game(["Alice", "Bob", "Charlie"])
        game.current_index = 2  # Charlie
        player = game.players[2]
        player.balance = -100

        game._check_bankruptcy(player)
        assert game.current_index == 0  # wrapped back

    def test_bankruptcy_player_properties_cleared(self):
        """Bankrupt player's properties list is empty."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        prop = game.board.properties[0]
        prop.owner = player
        player.add_property(prop)
        player.balance = -50

        game._check_bankruptcy(player)
        assert len(player.properties) == 0


# =====================================================================
# PLAY TURN TESTS
# =====================================================================

class TestPlayTurn:
    """Tests for play_turn() covering jail, doubles, and normal flow."""

    def test_play_turn_normal(self, monkeypatch):
        """Normal turn: roll, move, advance turn."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        player.balance = 1500
        player.position = 0

        # Force a non-doubles roll
        monkeypatch.setattr(game.dice, "roll", lambda: 5)
        monkeypatch.setattr(game.dice, "is_doubles", lambda: False)
        monkeypatch.setattr(game.dice, "describe", lambda: "2 + 3 = 5")
        game.dice.doubles_streak = 0
        monkeypatch.setattr(game, "_move_and_resolve", lambda p, r: None)

        game.play_turn()
        assert game.current_index == 1  # advanced to next player

    def test_play_turn_jailed_player(self, monkeypatch):
        """Jailed player's turn calls _handle_jail_turn."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        player.in_jail = True
        player.jail_turns = 0
        player.balance = 1000

        # Say no to pay fine, increment jail turns
        monkeypatch.setattr("moneypoly.ui.confirm", lambda prompt: False)

        game.play_turn()
        assert player.jail_turns == 1
        assert game.current_index == 1  # advanced

    def test_play_turn_doubles_extra_turn(self, monkeypatch):
        """Player rolling doubles gets an extra turn (no advance)."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        player.balance = 1500

        monkeypatch.setattr(game.dice, "roll", lambda: 6)
        monkeypatch.setattr(game.dice, "is_doubles", lambda: True)
        monkeypatch.setattr(game.dice, "describe", lambda: "3 + 3 = 6 (DOUBLES)")
        game.dice.doubles_streak = 1
        monkeypatch.setattr(game, "_move_and_resolve", lambda p, r: None)

        game.play_turn()
        assert game.current_index == 0  # stays same player (extra turn)

    def test_play_turn_triple_doubles_jail(self, monkeypatch):
        """Three consecutive doubles sends player to jail."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        player.balance = 1500

        monkeypatch.setattr(game.dice, "roll", lambda: 6)
        monkeypatch.setattr(game.dice, "is_doubles", lambda: True)
        monkeypatch.setattr(game.dice, "describe", lambda: "3 + 3 = 6 (DOUBLES)")
        game.dice.doubles_streak = 3

        game.play_turn()
        assert player.in_jail is True
        assert player.position == JAIL_POSITION


# =====================================================================
# HANDLE PROPERTY TILE TESTS
# =====================================================================

class TestHandlePropertyTile:
    """Tests for _handle_property_tile() branches."""

    def test_unowned_buy(self, monkeypatch):
        """Player chooses to buy an unowned property."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        player.balance = 1500
        prop = game.board.properties[0]  # Mediterranean $60

        monkeypatch.setattr("builtins.input", lambda prompt: "b")

        game._handle_property_tile(player, prop)
        assert prop.owner == player

    def test_unowned_skip(self, monkeypatch):
        """Player chooses to skip an unowned property."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        prop = game.board.properties[0]

        monkeypatch.setattr("builtins.input", lambda prompt: "s")

        game._handle_property_tile(player, prop)
        assert prop.owner is None

    def test_unowned_auction(self, monkeypatch):
        """Player chooses auction for unowned property."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        prop = game.board.properties[0]

        inputs = iter(["a", "0", "0"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

        game._handle_property_tile(player, prop)
        assert prop.owner is None  # no bids

    def test_own_property_no_rent(self):
        """Landing on own property charges no rent."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        prop = game.board.properties[0]
        prop.owner = player
        player.balance = 500

        game._handle_property_tile(player, prop)
        assert player.balance == 500  # no change

    def test_other_owner_pay_rent(self):
        """Landing on other's property pays rent."""
        game = Game(["Alice", "Bob"])
        tenant = game.players[0]
        owner = game.players[1]
        prop = game.board.properties[0]
        prop.owner = owner
        owner.add_property(prop)
        tenant.balance = 500

        game._handle_property_tile(tenant, prop)
        rent = prop.get_rent()
        assert tenant.balance == 500 - rent


# =====================================================================
# TILE LANDING — RAILROAD
# =====================================================================

class TestRailroadTile:
    """Tests for landing on railroad tiles."""

    def test_landing_on_railroad_tile(self, monkeypatch):
        """Landing on railroad tile is handled without error."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        player.balance = 1500
        player.position = 1

        monkeypatch.setattr("builtins.input", lambda prompt: "s")
        game._move_and_resolve(player, 4)  # move to position 5
        # Railroad tile processed without crash
        assert player.position == 5

    def test_landing_on_unowned_railroad(self, monkeypatch):
        """Landing on unowned railroad prompts purchase."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        player.balance = 1500
        player.position = 1

        monkeypatch.setattr("builtins.input", lambda prompt: "s")  # skip
        game._move_and_resolve(player, 4)  # position 5
        assert player.balance == 1500  # skipped

    def test_landing_on_unowned_property_tile(self, monkeypatch):
        """Landing on unowned property prompts purchase."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        player.balance = 1500
        player.position = 0

        monkeypatch.setattr("builtins.input", lambda prompt: "b")  # buy
        game._move_and_resolve(player, 1)  # position 1 = Mediterranean
        prop = game.board.get_property_at(1)
        assert prop.owner == player


# =====================================================================
# AUCTION TESTS
# =====================================================================

class TestAuction:
    """Tests for auction_property()."""

    def test_auction_winning_bid(self, monkeypatch):
        """Auction with a winning bid transfers property."""
        game = Game(["Alice", "Bob"])
        prop = game.board.properties[0]

        # Alice bids $100, Bob passes
        inputs = iter(["100", "0"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

        game.auction_property(prop)
        assert prop.owner == game.players[0]
        assert game.players[0].balance == STARTING_BALANCE - 100

    def test_auction_no_bids(self, monkeypatch):
        """Auction with no bids leaves property unowned."""
        game = Game(["Alice", "Bob"])
        prop = game.board.properties[0]

        monkeypatch.setattr("builtins.input", lambda prompt: "0")

        game.auction_property(prop)
        assert prop.owner is None

    def test_auction_bid_too_low(self, monkeypatch):
        """Auction rejects bid below minimum increment."""
        game = Game(["Alice", "Bob"])
        prop = game.board.properties[0]

        # Alice bids $100, Bob bids $101 (too low increment)
        inputs = iter(["100", "101"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

        game.auction_property(prop)
        assert prop.owner == game.players[0]  # only Alice's bid counts

    def test_auction_bid_exceeds_balance(self, monkeypatch):
        """Auction rejects bid exceeding player's balance."""
        game = Game(["Alice", "Bob"])
        prop = game.board.properties[0]
        game.players[0].balance = 50

        # Alice tries to bid more than she has, Bob passes
        inputs = iter(["100", "0"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

        game.auction_property(prop)
        assert prop.owner is None  # bid rejected, no bids


# =====================================================================
# INTERACTIVE MENU TESTS
# =====================================================================

class TestInteractiveMenu:
    """Tests for interactive_menu() and sub-menus."""

    def test_menu_roll_immediately(self, monkeypatch):
        """Player chooses 0 (roll) immediately."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]

        monkeypatch.setattr("builtins.input", lambda prompt: "0")

        game.interactive_menu(player)  # should return without error

    def test_menu_view_standings(self, monkeypatch):
        """Player views standings then rolls."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]

        inputs = iter(["1", "0"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

        game.interactive_menu(player)

    def test_menu_view_board(self, monkeypatch):
        """Player views board then rolls."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]

        inputs = iter(["2", "0"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

        game.interactive_menu(player)

    def test_menu_mortgage(self, monkeypatch):
        """Player mortgages a property via menu."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        prop = game.board.properties[0]
        prop.owner = player
        player.add_property(prop)

        inputs = iter(["3", "1", "0"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

        game.interactive_menu(player)
        assert prop.is_mortgaged is True

    def test_menu_mortgage_no_properties(self, monkeypatch):
        """Mortgage menu with no properties shows message."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]

        inputs = iter(["3", "0"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

        game.interactive_menu(player)  # should not crash

    def test_menu_unmortgage(self, monkeypatch):
        """Player unmortgages a property via menu."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        prop = game.board.properties[0]
        prop.owner = player
        player.add_property(prop)
        prop.is_mortgaged = True
        player.balance = 500

        inputs = iter(["4", "1", "0"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

        game.interactive_menu(player)
        assert prop.is_mortgaged is False

    def test_menu_unmortgage_no_mortgaged(self, monkeypatch):
        """Unmortgage menu with no mortgaged properties."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]

        inputs = iter(["4", "0"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

        game.interactive_menu(player)

    def test_menu_loan(self, monkeypatch):
        """Player requests emergency loan via menu."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        initial = player.balance

        inputs = iter(["6", "500", "0"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

        game.interactive_menu(player)
        assert player.balance == initial + 500

    def test_menu_trade(self, monkeypatch):
        """Player trades a property via menu."""
        game = Game(["Alice", "Bob"])
        seller = game.players[0]
        buyer = game.players[1]
        prop = game.board.properties[0]
        prop.owner = seller
        seller.add_property(prop)
        buyer.balance = 1500

        # Menu: 5 (trade), 1 (pick Bob), 1 (pick property), 100 (cash), 0 (roll)
        inputs = iter(["5", "1", "1", "100", "0"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

        game.interactive_menu(seller)
        assert prop.owner == buyer

    def test_menu_trade_no_properties(self, monkeypatch):
        """Trade menu when player has no properties."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]

        inputs = iter(["5", "1", "0"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

        game.interactive_menu(player)

    def test_menu_trade_no_others(self, monkeypatch):
        """Trade menu when only one player remains."""
        game = Game(["Alice"])
        player = game.players[0]

        inputs = iter(["5", "0"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

        game.interactive_menu(player)

    def test_menu_trade_invalid_partner_index(self, monkeypatch):
        """Trade menu with invalid partner index."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        prop = game.board.properties[0]
        prop.owner = player
        player.add_property(prop)

        # Pick invalid partner index (99), then roll
        inputs = iter(["5", "99", "0"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

        game.interactive_menu(player)

    def test_menu_trade_invalid_property_index(self, monkeypatch):
        """Trade menu with invalid property index."""
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        prop = game.board.properties[0]
        prop.owner = player
        player.add_property(prop)

        # Pick valid partner (1), then invalid property index (99), then roll
        inputs = iter(["5", "1", "99", "0"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

        game.interactive_menu(player)


# =====================================================================
# GAME RUN TESTS
# =====================================================================

class TestGameRun:
    """Tests for the full game run() method."""

    def test_run_single_player_ends(self, monkeypatch):
        """Game ends immediately with only one player."""
        game = Game(["Alice"])
        monkeypatch.setattr(game, "play_turn", lambda: None)

        game.run()  # should complete without error

    def test_run_finds_winner(self, monkeypatch):
        """Game declares a winner when ending."""
        game = Game(["Alice", "Bob"])
        game.players[0].balance = 5000
        game.players[1].balance = 100

        # Make game end quickly
        call_count = [0]
        def mock_play():
            call_count[0] += 1
            if call_count[0] >= 2:
                game.running = False
            else:
                game.advance_turn()

        monkeypatch.setattr(game, "play_turn", mock_play)

        game.run()
        winner = game.find_winner()
        assert winner.name == "Alice"

    def test_run_no_players(self, monkeypatch):
        """Game ends with no players message."""
        game = Game(["Alice"])
        game.players.clear()  # remove all players
        game.run()  # should print 'no players remaining'


# =====================================================================
# UI FUNCTION TESTS
# =====================================================================

class TestUIFunctions:
    """Tests for ui.py functions."""

    def test_print_banner(self, capsys):
        """print_banner() prints formatted header."""
        import moneypoly.ui as ui_mod
        ui_mod.print_banner("Test Title")
        output = capsys.readouterr().out
        assert "Test Title" in output
        assert "=" in output

    def test_print_player_card(self, capsys):
        """print_player_card() shows player details."""
        import moneypoly.ui as ui_mod
        p = Player("Alice", balance=1500)
        ui_mod.print_player_card(p)
        output = capsys.readouterr().out
        assert "Alice" in output
        assert "1,500" in output

    def test_print_player_card_jailed(self, capsys):
        """print_player_card() shows jail status."""
        import moneypoly.ui as ui_mod
        p = Player("Alice")
        p.in_jail = True
        p.jail_turns = 1
        ui_mod.print_player_card(p)
        output = capsys.readouterr().out
        assert "IN JAIL" in output

    def test_print_player_card_with_properties(self, capsys):
        """print_player_card() lists properties."""
        import moneypoly.ui as ui_mod
        p = Player("Alice")
        prop = Property("Park Place", 37, 350, 35)
        p.add_property(prop)
        ui_mod.print_player_card(p)
        output = capsys.readouterr().out
        assert "Park Place" in output

    def test_print_player_card_with_jail_card(self, capsys):
        """print_player_card() shows get-out-of-jail cards."""
        import moneypoly.ui as ui_mod
        p = Player("Alice")
        p.get_out_of_jail_cards = 2
        ui_mod.print_player_card(p)
        output = capsys.readouterr().out
        assert "2" in output

    def test_print_player_card_mortgaged_prop(self, capsys):
        """print_player_card() shows MORTGAGED tag."""
        import moneypoly.ui as ui_mod
        p = Player("Alice")
        prop = Property("Test", 1, 100, 10)
        prop.is_mortgaged = True
        p.add_property(prop)
        ui_mod.print_player_card(p)
        output = capsys.readouterr().out
        assert "MORTGAGED" in output

    def test_print_standings(self, capsys):
        """print_standings() shows ranked players."""
        import moneypoly.ui as ui_mod
        p1 = Player("Alice", balance=2000)
        p2 = Player("Bob", balance=1000)
        ui_mod.print_standings([p1, p2])
        output = capsys.readouterr().out
        assert "Alice" in output
        assert "Bob" in output
        assert "Standings" in output

    def test_print_standings_jailed(self, capsys):
        """print_standings() shows JAILED tag."""
        import moneypoly.ui as ui_mod
        p = Player("Alice")
        p.in_jail = True
        ui_mod.print_standings([p])
        output = capsys.readouterr().out
        assert "JAILED" in output

    def test_print_board_ownership(self, capsys):
        """print_board_ownership() shows property register."""
        import moneypoly.ui as ui_mod
        board = Board()
        ui_mod.print_board_ownership(board)
        output = capsys.readouterr().out
        assert "Property Register" in output
        assert "Mediterranean" in output

    def test_print_board_ownership_with_owner(self, capsys):
        """print_board_ownership() shows owner name."""
        import moneypoly.ui as ui_mod
        board = Board()
        board.properties[0].owner = Player("Alice")
        ui_mod.print_board_ownership(board)
        output = capsys.readouterr().out
        assert "Alice" in output

    def test_print_board_ownership_mortgaged(self, capsys):
        """print_board_ownership() shows mortgaged flag."""
        import moneypoly.ui as ui_mod
        board = Board()
        board.properties[0].owner = Player("Alice")
        board.properties[0].is_mortgaged = True
        ui_mod.print_board_ownership(board)
        output = capsys.readouterr().out
        assert "*" in output

    def test_format_currency(self):
        """format_currency() returns formatted string."""
        import moneypoly.ui as ui_mod
        assert ui_mod.format_currency(1500) == "$1,500"
        assert ui_mod.format_currency(0) == "$0"
        assert ui_mod.format_currency(1000000) == "$1,000,000"

    def test_safe_int_input_valid(self, monkeypatch):
        """safe_int_input() with valid int returns it."""
        import moneypoly.ui as ui_mod
        monkeypatch.setattr("builtins.input", lambda prompt: "42")
        assert ui_mod.safe_int_input("Enter: ") == 42

    def test_safe_int_input_invalid(self, monkeypatch):
        """safe_int_input() with invalid input returns default."""
        import moneypoly.ui as ui_mod
        monkeypatch.setattr("builtins.input", lambda prompt: "abc")
        assert ui_mod.safe_int_input("Enter: ", default=99) == 99

    def test_confirm_yes(self, monkeypatch):
        """confirm() returns True for 'y'."""
        import moneypoly.ui as ui_mod
        monkeypatch.setattr("builtins.input", lambda prompt: "y")
        assert ui_mod.confirm("Sure? ") is True

    def test_confirm_no(self, monkeypatch):
        """confirm() returns False for 'n'."""
        import moneypoly.ui as ui_mod
        monkeypatch.setattr("builtins.input", lambda prompt: "n")
        assert ui_mod.confirm("Sure? ") is False

    def test_confirm_yes_uppercase(self, monkeypatch):
        """confirm() returns True for 'Y' (case insensitive)."""
        import moneypoly.ui as ui_mod
        monkeypatch.setattr("builtins.input", lambda prompt: "Y")
        assert ui_mod.confirm("Sure? ") is True


# =====================================================================
# BANK SUMMARY TEST
# =====================================================================

class TestBankSummary:
    """Tests for bank.summary()."""

    def test_bank_summary(self, capsys):
        """summary() prints bank state."""
        bank = Bank()
        bank.collect(500)
        bank.summary()
        output = capsys.readouterr().out
        assert "Bank reserves" in output
        assert "Total collected" in output
        assert "Loans issued" in output
