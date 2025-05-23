"""Application to manage part inventory."""

import logging
import sqlite3

from flask import Flask, g, redirect, render_template, request

#
# Variable setup
#
app = Flask(__name__)
PARTLIST = []  #  type: ignore
MESSAGE = ""


#
# Logging setup
#
logging.basicConfig(
    filename="app/opdb-app.log",
    format="%(asctime)s %(levelname)-8s [%(filename)-12s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.INFO,
)
log = logging.getLogger("inventory-app")


#
# Database connection
#
def get_db():
    """Opens a new database connection if there is none yet for the current application context."""

    if "db" not in g:

        try:
            log.info("Database Connection")
            g.db = sqlite3.connect("app/inventory.db")
            g.db.row_factory = sqlite3.Row

        except Exception as d:
            raise Exception("Failed to connect to the database.") from d

    return g.db


@app.teardown_appcontext
def teardown_db(exception):
    """Close database connection."""

    print(exception)
    db = g.pop("db", None)

    if db is not None:
        db.close()
        log.info("Closed DB Connection")


#
# Inventory parts management
#
def getparts():
    """Retrieve current part inventory"""

    result = (
        get_db()
        .execute(
            "select part_no, quant from part_inventory_app",
        )
        .fetchall()
    )
    log.info("GETPARTS() - CURRENT PART INVENTORY:\n\t\t%s", result)
    return result


@app.route("/requestparts", methods=["POST"])
def requestparts():
    """Update part quantity for given part number."""

    global PARTLIST
    global MESSAGE

    part_no = request.form["part_requested"]
    req_amt = request.form["amount_requested"]

    log.info("RECEIVED FORM DATA:\n\t\tPART = %s\n\t\tQUANTITY = %i", part_no, req_amt)

    if part_no and req_amt:

        req_amt = int(req_amt)
        db = get_db()

        result = db.execute(
            f"select quant from part_inventory_app where part_no = '{part_no}'"
        ).fetchone()

        log.info("REQUESTPARTS().results = %s", result)

        if result is not None:

            cur_val = result["QUANT"]
            print(f"cur_val = {cur_val}")

            if cur_val >= req_amt:
                new_amt = cur_val - req_amt
                print("new amount is " + str(new_amt))
                db.execute(
                    f'UPDATE part_inventory_app SET quant = {str(new_amt)} WHERE part_no = "{part_no}"'
                )
                db.commit()
                return redirect("/")
            else:
                MESSAGE = f"INSUFFICIENT QUANTITY FOR {part_no}: inventory = {cur_val}, requested {req_amt}"
                return render_template("index.html", partlist=PARTLIST, message=MESSAGE)
        else:
            MESSAGE = f"PART NOT FOUND: {part_no}"
            return render_template("index.html", partlist=PARTLIST, message=MESSAGE)
    else:
        MESSAGE = "INVALID PART NUMBER / QUANTITY"
        return render_template("index.html", partlist=PARTLIST, message=MESSAGE)


@app.route("/")
def index():
    """Render index.html using parts from the database."""

    global PARTLIST
    global MESSAGE

    log.info("PAGE REFRESH")
    MESSAGE = ""
    PARTLIST = getparts()
    PARTLIST = [dict(row) for row in PARTLIST]
    return render_template("index.html", partlist=PARTLIST, message=MESSAGE)


if __name__ == "__main__":

    log.info("BEGIN PROGRAM")

    try:
        app.run(host="127.0.0.1", debug=True)
    except Exception as e:
        print(f"ERROR: unable to run application:\n {str(e)}")

    log.info("END PROGRAM")