import json, os
import curses
import secrets
from eth_account import Account

def main(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    stdscr.addstr(1, 2, "SPAZ NODE INITIALIZATION", curses.A_BOLD)
    stdscr.addstr(3, 2, "1. Generate new Ethereum key")
    stdscr.addstr(4, 2, "2. Use existing key")
    stdscr.addstr(5, 2, "3. Federate with existing server")
    stdscr.refresh()

    k = stdscr.getkey()

    os.makedirs("/app/keys", exist_ok=True)
    if k == '1':
        acct = Account.create()
        with open("/app/keys/private.key", "w") as f:
            f.write(acct.key.hex())
        with open("/app/keys/public.key", "w") as f:
            f.write(acct.address)
        stdscr.addstr(7, 2, f"Created account: {acct.address}")

    elif k == '2':
        stdscr.addstr(7, 2, "Paste private key:")
        curses.echo()
        priv = stdscr.getstr(8, 2, 66).decode()
        acct = Account.from_key(priv)
        with open("/app/keys/private.key", "w") as f:
            f.write(priv)
        with open("/app/keys/public.key", "w") as f:
            f.write(acct.address)
        stdscr.addstr(10, 2, f"Loaded account: {acct.address}")

    elif k == '3':
        curses.echo()
        stdscr.addstr(7, 2, "Enter federated contract endpoint:")
        url = stdscr.getstr(8, 2, 100).decode()
        stdscr.addstr(9, 2, "Fetching ABI and address...")
        # In a real use case, you'd fetch actual contract metadata

    stdscr.refresh()
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)