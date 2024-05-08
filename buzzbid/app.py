from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import datetime
import os
import sys

app = Flask(__name__)

app.secret_key = "abcd21234455"
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "your_password"

mysql = MySQL(app)

conditions = ["New", "Very Good", "Good", "Fair", "Poor"]
condition_map = {"New": 1, "Very Good": 2, "Good": 3, "Fair": 4, "Poor": 5}


@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    mesage = ""
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
    ):
        userName = request.form["username"]
        password = request.form["password"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT * FROM User WHERE username = % s AND password = % s",
            (
                userName,
                password,
            ),
        )
        user = cursor.fetchone()
        if user:

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT position FROM AdministrativeUser WHERE username = % s ",
                (userName,),
            )
            adminUser = cursor.fetchone()
            if not adminUser:
                usertype = "RegularUser"
                session["position"] = ""
            else:
                usertype = "Admin"
                session["position"] = adminUser["position"]

            session["loggedin"] = True
            session["userid"] = user["username"]
            session["firstname"] = user["first_name"]
            session["lastname"] = user["last_name"]
            session["role"] = usertype
            mesage = "Logged in successfully !"
            return redirect(url_for("dashboard"))
        else:
            mesage = "Please enter correct user name / password !"
    return render_template("login.html", mesage=mesage)


@app.route("/register", methods=["GET", "POST"])
def register():
    mesage = ""
    if (
        request.method == "POST"
        and "firstname" in request.form
        and "lastname" in request.form
        and "password" in request.form
        and "username" in request.form
    ):
        userName = request.form["username"]
        password = request.form["password"]
        firstName = request.form["firstname"]
        lastName = request.form["lastname"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM User WHERE username = % s", (userName,))
        account = cursor.fetchone()
        if account:
            mesage = "Username already exists !"
        elif not userName or not password or not firstName or not lastName:
            mesage = "Please fill out the form !"
        else:
            cursor.execute(
                "INSERT INTO User VALUES (%s, % s, % s, % s)",
                (userName, firstName, lastName, password),
            )
            mysql.connection.commit()
            mesage = "Registered Successfully!!! Please enter your credentials"
            welcome_user = firstName
            return render_template("login.html", mesage=mesage)
    elif request.method == "POST":
        mesage = "Please fill out the form !"
    return render_template("register.html", mesage=mesage)


@app.route("/logout")
def logout():
    session.pop("loggedin", None)
    session.pop("userid", None)
    session.pop("email", None)
    session.pop("name", None)
    session.pop("role", None)
    return redirect(url_for("login"))


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "loggedin" in session:
        item_id = request.args.get("item_id")
        if item_id:
            mesage = "Bid created successfully with Get-It-Now Price"
            return render_template("dashboard.html", mesage=mesage)

        return render_template("dashboard.html")
    return redirect(url_for("login"))


@app.route("/list_items", methods=["GET", "POST"])
def list_items():
    mesage = ""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM category")
    categories = cursor.fetchall()

    if request.method == "POST":

        itemName = request.form["itemName"]
        itemDescription = request.form["itemDescription"]
        itemCategory = request.form["category"]
        itemCondition = request.form["condition"]
        startBid = request.form["startBid"]
        minBid = request.form["minBid"]
        auctionEnd = request.form["auctionEnd"]
        getPrice = None if request.form["getPrice"] == "" else request.form["getPrice"]
        returnable = request.form["jsValue"]
        returnable = 1 if returnable == "yes" else 0

        listedUser = session["userid"]

        if (
            not itemName
            or not itemDescription
            or not itemCategory
            or not itemCondition
            or not startBid
            or not minBid
            or not auctionEnd
        ):
            mesage = "Please fill out the form !"
            return render_template(
                "new_item_for_auction.html", categories=categories, mesage=mesage
            )
        elif float(minBid) < float(startBid):
            mesage = "Minimum Sale Price should not be less than Starting Bid !"
            return render_template(
                "new_item_for_auction.html", categories=categories, mesage=mesage
            )
        elif getPrice != None and float(getPrice) < float(minBid):
            mesage = "Get It Now price should not be less than Minimum Sale Price !"
            return render_template(
                "new_item_for_auction.html", categories=categories, mesage=mesage
            )
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                """INSERT INTO Item (item_name, item_description, item_condition, returnable, starting_bid,
                                                 min_sale_price, auction_end_time, get_it_now_price, listeduser,category_name) 
            VALUES ( %s, %s, %s, %s, %s, %s, DATE_ADD(NOW(), INTERVAL %s DAY), %s, %s, %s)""",
                (
                    itemName,
                    itemDescription,
                    itemCondition,
                    returnable,
                    startBid,
                    minBid,
                    auctionEnd,
                    getPrice,
                    listedUser,
                    itemCategory,
                ),
            )
            mysql.connection.commit()
            mesage = "Item Listed Successfully"
            return render_template(
                "new_item_for_auction.html", categories=categories, mesage=mesage
            )
    else:
        return render_template("new_item_for_auction.html", categories=categories)


@app.route("/search_items", methods=["GET", "POST"])
def search_items():
    if "loggedin" in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute("SELECT * FROM category")
        categories = cursor.fetchall()

        return render_template(
            "search_items.html", categories=categories, conditions=conditions
        )
    return redirect(url_for("login"))


@app.route(rule="/search_results", methods=["GET", "POST"])
def search_results():
    if "loggedin" in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute("SELECT * FROM category")
        categories = cursor.fetchall()

        keyword = None
        category = None
        minPrice = None
        maxPrice = None
        condition = None

        if request.method == "GET":
            return render_template(
                "search_items.html",
                categories=categories,
                conditions=conditions,
                items=[],
                selected_category="",
                selected_condition="",
                keyword_value=keyword,
                minprice_value=minPrice,
                maxprice_value=maxPrice,
            )

        if "keyword" in request.form and request.form["keyword"] != "":
            keyword = request.form["keyword"]
        if "itemcategory" in request.form and request.form["itemcategory"] != "":
            category = request.form["itemcategory"]
        if "minprice" in request.form and request.form["minprice"] != "":
            minPrice = request.form["minprice"]
        if "maxprice" in request.form and request.form["maxprice"] != "":
            maxPrice = request.form["maxprice"]
        if "itemcondition" in request.form and request.form["itemcondition"] != "":
            condition = condition_map.get(request.form["itemcondition"])

        search_query = """SELECT Item.itemID, item_name, b1.bid_amount , b1.username , get_it_now_price , DATE_FORMAT(auction_end_time, '%%m/%%d/%%y  %%h:%%i %%p') AS auction_end_time
            FROM Item LEFT JOIN (SELECT b.itemID, b.bid_amount, b.username FROM Bid b INNER JOIN (
            SELECT itemID, MAX(bid_amount) AS MaxBid FROM Bid GROUP BY itemID) AS MaxBids ON b.itemID = MaxBids.itemID AND b.bid_amount = MaxBids.MaxBid) AS b1 ON Item.itemID = b1.itemID WHERE Item.itemID IN (
            SELECT Item.itemID FROM Item LEFT JOIN Bid ON Item.itemID = Bid.itemID
            WHERE
                (%s IS NULL OR BINARY item_name LIKE CONCAT('%%', %s, '%%') OR BINARY item_description LIKE CONCAT('%%', %s, '%%'))
                AND (%s IS NULL OR category_name = %s)
                AND (%s IS NULL OR (SELECT MAX(bid_amount) FROM Bid WHERE Item.itemID = Bid.itemID) >= %s OR starting_bid >= %s)
                AND (%s IS NULL OR (SELECT MAX(bid_amount) FROM Bid WHERE Item.itemID = Bid.itemID) <= %s OR starting_bid <= %s)
                AND (%s IS NULL OR item_condition <= %s)
            GROUP BY Item.itemID) AND cancelled_username IS NULL AND auction_end_time > NOW()
            ORDER BY auction_end_time DESC;"""
        cursor.execute(
            search_query,
            (
                keyword,
                keyword,
                keyword,
                category,
                category,
                minPrice,
                minPrice,
                minPrice,
                maxPrice,
                maxPrice,
                maxPrice,
                condition,
                condition,
            ),
        )
        items = cursor.fetchall()

        return render_template(
            "search_items.html",
            categories=categories,
            conditions=conditions,
            items=items,
            selected_category=request.form["itemcategory"],
            selected_condition=request.form["itemcondition"],
            keyword_value=request.form["keyword"],
            minprice_value=request.form["minprice"],
            maxprice_value=request.form["maxprice"],
        )
    return redirect(url_for("login"))


@app.route("/auction_results", methods=["GET", "POST"])
def auction_results():
    if "loggedin" in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        auction_results_query = """SELECT i1.itemID AS 'ID', i1.item_name AS 'ItemName', 
                CASE
                    WHEN b1.bid_amount IS NULL THEN '-'
                    WHEN b1.bid_amount < i1.min_sale_price THEN '-'
                    WHEN i1.cancelled_username IS NULL THEN b1.bid_amount
                    ELSE '-'
                END AS 'SalePrice',
                CASE
                    WHEN i1.cancelled_username IS NOT NULL THEN 'Cancelled'
                    WHEN b1.username IS NULL THEN '-'
                    WHEN b1.bid_amount < i1.min_sale_price THEN '-'
                    WHEN i1.cancelled_username IS NULL THEN b1.username
                    ELSE 'Cancelled'
                END AS 'Winner',
                DATE_FORMAT(i1.auction_end_time, '%m/\%d/%y  %h:\%i %p') AS 'AuctionEnded'
            FROM Item i1 LEFT JOIN (
                SELECT b2.itemID, b2.username, b2.bid_amount FROM Bid b2 INNER JOIN (
                    SELECT itemID, MAX(bid_amount) AS MaxBid FROM Bid GROUP BY itemID
                ) AS MaxBids ON b2.itemID = MaxBids.itemID AND b2.bid_amount = MaxBids.MaxBid
            ) b1 ON i1.itemID = b1.itemID
            WHERE i1.auction_end_time<= NOW()
            ORDER BY i1.auction_end_time DESC;"""
        cursor.execute(auction_results_query)
        results = cursor.fetchall()
        return render_template("auction_results.html", results=results)
    return redirect(url_for("login"))


@app.route("/item_result", methods=["GET", "POST"])
def item_result():
    if "loggedin" in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        item_id = request.args.get("item_id")
        winner = request.args.get("winner")
        firstRowColor = (
            "yellow"
            if (winner == "-")
            else "lightcoral" if (winner == "Cancelled") else "lightgreen"
        )

        cursor.execute(
            "SELECT itemID, item_name, item_description, category_name, item_condition, returnable, CASE WHEN get_it_now_price IS NULL THEN '-' ELSE get_it_now_price END AS 'get_it_now_price', DATE_FORMAT(auction_end_time, '%%m/%%d/%%y  %%h:%%i %%p') AS 'auction_end_time' FROM Item WHERE itemID = %s",
            (item_id,),
        )
        item_detail = cursor.fetchall()

        bid_query = """(SELECT 'Cancelled' AS 'BidAmount', DATE_FORMAT(auction_end_time, '%%m/%%d/%%y  %%h:%%i %%p') AS 'BidTime', 'Administrator' AS 'Username'  FROM Item WHERE itemID = %s AND cancelled_username IS NOT NULL)
            UNION ALL
                (SELECT CAST(bid_amount AS CHAR) AS 'BidAmount', DATE_FORMAT(time_of_bid, '%%m/%%d/%%y  %%h:%%i %%p') AS 'BidTime', username AS 'Username'  FROM Bid WHERE itemID = %s ORDER BY bid_amount DESC LIMIT 4)
            LIMIT 4;"""
        cursor.execute(bid_query, (item_id, item_id))
        bid_list = cursor.fetchall()

        return render_template(
            "item_result.html",
            item=item_detail,
            bids=bid_list,
            firstRowColor=firstRowColor,
            winner=winner,
        )
    return redirect(url_for("login"))


@app.route("/category", methods=["GET"])
def category():
    if "loggedin" in session and "Admin" in session["role"]:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            """ SELECT 
        c.category_name AS 'Category', 
        COUNT(i.itemID) AS 'Total_Items',  
        MIN(CASE WHEN i.get_it_now_price IS NOT NULL THEN i.get_it_now_price END) as 'Min_Price',  
        MAX(CASE WHEN i.get_it_now_price IS NOT NULL THEN i.get_it_now_price END) as 'Max_Price',  
        ROUND(AVG(CASE WHEN i.get_it_now_price IS NOT NULL  THEN i.get_it_now_price END), 2) as 'Average_Price'  
        FROM Category c LEFT JOIN Item i ON c.category_name = i.category_name
        WHERE i.cancelled_username IS NULL
        GROUP BY c.category_name
        ORDER BY c.category_name ASC
         """
        )
        categories = cursor.fetchall()

        return render_template("category.html", categories=categories)
    return redirect(url_for("login"))


@app.route("/userReport", methods=["GET"])
def userReport():
    if "loggedin" in session and "Admin" in session["role"]:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            """ WITH WinnerTable AS
                (SELECT i1.itemID, 
                    CASE
                        WHEN b1.username IS NULL THEN NULL
                            WHEN b1.bid_amount < i1.min_sale_price THEN NULL
                        WHEN i1.cancelled_username IS NULL THEN b1.username
                            ELSE NULL
                    END AS 'winner'
                FROM Item i1 INNER JOIN (
                    SELECT b2.itemID, b2.username, b2.bid_amount FROM Bid b2 INNER JOIN (
                        SELECT itemID, MAX(bid_amount) AS MaxBid FROM Bid GROUP BY itemID
                    ) AS MaxBids ON b2.itemID = MaxBids.itemID AND b2.bid_amount = MaxBids.MaxBid
                ) b1 ON i1.itemID = b1.itemID
                WHERE i1.auction_end_time<= NOW() AND b1.bid_amount >= i1.min_sale_price),
                UserWonTable AS
                (SELECT u.username, COUNT(w.itemID) AS 'Won' FROM `User` u LEFT JOIN WinnerTable w ON u.username = w.winner GROUP BY u.username),
                UserSoldTable AS
                (SELECT u.username, COUNT(i.itemID) AS 'Sold' FROM `User` u LEFT JOIN Item i ON u.username = i.listeduser LEFT JOIN WinnerTable w ON i.itemID = w.itemID WHERE w.winner IS NOT NULL GROUP BY u.username),
                UserRatedTable AS
                (SELECT w.winner, COUNT(r.itemID) AS 'Rated' FROM Rating r INNER JOIN WinnerTable w ON r.itemID = w.itemID GROUP BY w.winner),
                MostFrequentTable AS
                (SELECT u.username, COUNT(i.itemID) AS 'Listed',
                COALESCE((
                    SELECT i1.item_condition FROM Item i1 WHERE i1.listeduser = u.username GROUP BY i1.item_condition 
                            ORDER BY COUNT(*) DESC, 
                                FIELD(i1.item_condition, 'Poor', 'Fair', 'Good', 'Very Good', 'New') ASC
                            LIMIT 1
                        ), 'N/A') AS 'Most_Frequent_Condition'
                FROM `User` u LEFT JOIN Item i ON u.username = i.listeduser
                GROUP BY u.username)
                SELECT m.username AS 'Username', m.Listed, 
                    CASE 
                        WHEN s.Sold IS NULL THEN 0
                        ELSE s.Sold
                    END AS 'Sold',
                    CASE 
                        WHEN w.Won IS NULL THEN 0
                        ELSE w.Won
                    END AS 'Won',
                    CASE 
                        WHEN r.Rated IS NULL THEN 0
                        ELSE r.Rated
                    END AS 'Rated',
                    m.Most_Frequent_Condition 
                FROM MostFrequentTable m LEFT JOIN UserSoldTable s ON m.username = s.username 
                LEFT JOIN UserWonTable w ON m.username = w.username 
                LEFT JOIN UserRatedTable r ON m.username = r.winner
         """
        )
        userReports = cursor.fetchall()

        return render_template("userReport.html", userReports=userReports)
    return redirect(url_for("login"))


@app.route("/topRated", methods=["GET"])
def topRated():
    if "loggedin" in session and "Admin" in session["role"]:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            """ 
        SELECT 
	i.item_name AS 'Item_Name',
    	ROUND(AVG(r.star), 1) AS 'Average_Rating', 
    	COUNT(*) AS 'Rating_Count'
FROM Item i
LEFT JOIN Rating r ON i.itemID = r.itemID
WHERE r.star IS NOT NULL
GROUP BY item_name
ORDER BY Average_Rating DESC, item_name ASC
LIMIT 10
         """
        )
        topRatedReports = cursor.fetchall()

        return render_template("topRated.html", topRatedReports=topRatedReports)
    return redirect(url_for("login"))


@app.route("/aucStats", methods=["GET"])
def aucStats():
    if "loggedin" in session and "Admin" in session["role"]:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            """ 
        SELECT 
    COUNT(CASE WHEN auction_end_time > NOW() AND cancelled_username IS NULL THEN 1 END) AS 'Auctions_Active',
    (SELECT COUNT(i1.auction_end_time) FROM Item i1 WHERE i1.auction_end_time <= NOW() AND i1.cancelled_username IS NULL) AS 'Auctions_Finished',
    (SELECT COUNT(DISTINCT i2.itemID) FROM Item i2 JOIN Bid b2 ON i2.itemID = b2.itemID WHERE i2.auction_end_time <= NOW() AND i2.cancelled_username IS NULL AND i2.min_sale_price <= b2.bid_amount) AS 'Auctions_Won',
    COUNT(CASE WHEN cancelled_username IS NOT NULL THEN 1 END) AS 'Auctions_Cancelled',
    COUNT(DISTINCT r.itemID) AS 'Items_Rated',
    (SELECT COUNT(DISTINCT i.itemID) 
     FROM Item i 
     LEFT JOIN Rating r ON i.itemID = r.itemID 
     WHERE r.itemID IS NULL 
       AND EXISTS (
           SELECT 1
           FROM Bid b
           WHERE b.itemID = i.itemID
             AND i.auction_end_time <= NOW()
             AND i.cancelled_username IS NULL
             AND i.min_sale_price <= b.bid_amount
       )
    ) AS 'Items_Not_Rated'
FROM Item i
LEFT JOIN Bid b ON i.itemID = b.itemID
LEFT JOIN Rating r ON i.itemID = r.itemID;


         """
        )
        aucStats = cursor.fetchall()

        return render_template("aucStats.html", aucStats=aucStats)
    return redirect(url_for("login"))


@app.route("/canAuction", methods=["GET"])
def canAuction():
    if "loggedin" in session and "Admin" in session["role"]:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            """ 
        SELECT 
    itemID as 'ID',
	listeduser as 'Listed_by',
    DATE_FORMAT(auction_end_time, '%m/\%d/%y  %h:\%i %p') as 'Cancelled_Date',
    cancelled_reason as 'Reason'
FROM Item 
WHERE cancelled_username IS NOT NULL
GROUP BY itemID
ORDER BY itemID DESC

         """
        )
        canAuctions = cursor.fetchall()

        return render_template("canAuction.html", canAuctions=canAuctions)
    return redirect(url_for("login"))


@app.route("/item_details", methods=["GET", "POST"])
def item_details():
    if "loggedin" in session:
        item_id = request.args.get("item_id")
        print("item ID: ", item_id)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            """SELECT itemID, item_name, item_description, 
                                item_condition, category_name, returnable, 
                                starting_bid, get_it_now_price, DATE_FORMAT(auction_end_time, '%%m/%%d/%%y  %%h:%%i %%p') AS auction_end_time
                            FROM Item 
                            WHERE itemID=%s;""",
            (item_id,),
        )
        item = cursor.fetchone()

        # Display lastest four bids on item
        cursor.execute(
            """SELECT bid_amount AS `Bid Amount`,DATE_FORMAT(time_of_bid, '%%m/%%d/%%y  %%h:%%i %%p') AS `Time of Bid`, username AS `Username`  
                            FROM Bid WHERE itemID=%s 
                            ORDER BY bid_amount DESC LIMIT 4;""",
            (item_id,),
        )
        latest_bids = cursor.fetchall()
        for bid in latest_bids:
            bid_amount = bid["Bid Amount"]
            print("Latest bid Fetch: ", bid_amount)

        # Get current highest bid and starting bid
        cursor.execute(
            """SELECT MAX(bid_amount) AS 'MaxBid' 
                        FROM Bid WHERE itemID=%s
                        GROUP BY itemID;""",
            (item_id,),
        )
        highest_bid = cursor.fetchone()
        if highest_bid:
            print("Highest bid: ", highest_bid["MaxBid"])
        startingBid = item["starting_bid"]
        print("startingBid: ", startingBid)

        # Find the user who listed the item
        cursor.execute("""SELECT listeduser FROM Item WHERE itemID=%s;""", (item_id,))
        listedUser = cursor.fetchone()
        listedUser_username = listedUser["listeduser"]
        currentUser_username = session["userid"]
        print("listedUser_username: ", listedUser_username)
        print("currentUser_username: ", currentUser_username)

        if item:
            return render_template(
                "item_details.html",
                item=item,
                latest_bids=latest_bids,
                highest_bid=highest_bid,
                listedUser_username=listedUser_username,
                currentUser_username=currentUser_username,
                usertype=session["role"],
            )
        else:
            return "Item not found"

    else:
        return redirect(url_for("login"))


@app.route("/edit_item_description", methods=["GET", "POST"])
def edit_item_description():
    if "loggedin" in session:
        item_id = request.args.get("item_id")
        print("itemID: ", item_id)

        if request.method == "GET":
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                """SELECT itemID, item_name, item_description FROM Item WHERE itemID=%s;""",
                (item_id,),
            )
            item = cursor.fetchone()
            print("Item: ", item)
            if item:
                return render_template("edit_item_description.html", item=item)
            else:
                return "Item not Found"

        if request.method == "POST":
            newDescription = request.form.get("new_description")
            print("New description: ", newDescription)

            if not newDescription:
                flash("Please enter new description !", "warning")
                return redirect(url_for("item_details", item_id=item_id))
            else:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(
                    "UPDATE Item SET item_description=%s WHERE itemID=%s",
                    (newDescription, item_id),
                )
                mysql.connection.commit()
                flash("Updated description successfully", "success")
                return redirect(url_for("item_details", item_id=item_id))
    else:
        return redirect(url_for("login"))


@app.route("/get_it_now_price", methods=["GET", "POST"])
def get_it_now_price():
    if "loggedin" in session:
        item_id = request.args.get("item_id")
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""SELECT * FROM Item WHERE itemID=%s;""", (item_id,))
        item = cursor.fetchone()
        print("item: ", item)

        getItNowPrice = item["get_it_now_price"]
        bidAmount = getItNowPrice
        currentUser = session["userid"]
        currentTime = datetime.now()
        print("itemID: ", item_id)
        print("bidAmount: ", bidAmount)
        print("currentUser: ", currentUser)
        print("currentTime: ", currentTime)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            """INSERT INTO Bid (itemID, username,time_of_bid,bid_amount) 
                        VALUES (%s, %s, %s, %s);""",
            (item_id, currentUser, currentTime, bidAmount),
        )
        mysql.connection.commit()
        flash("Bid created successfully with Get-It-Now Price", "success")

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            """UPDATE Item SET auction_end_time=%s WHERE itemID=%s;""",
            (currentTime, item_id),
        )
        mysql.connection.commit()

        return redirect(url_for("dashboard", item_id=item_id))
    else:
        return redirect(url_for("login"))


@app.route("/bid_item", methods=["GET", "POST"])
def bid_item():
    if "loggedin" in session:
        item_id = request.args.get("item_id")
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""SELECT * FROM Item WHERE itemID=%s;""", (item_id,))
        item = cursor.fetchone()

        # Find the user who listed the item
        cursor.execute("""SELECT listeduser FROM Item WHERE itemID=%s;""", (item_id,))
        listedUser = cursor.fetchone()
        listedUser_username = listedUser["listeduser"]
        currentUser_username = session["userid"]

        bidAmount = float(request.form.get("bid_amount"))
        currentUser = session["userid"]
        currentTime = datetime.now()

        cursor.execute(
            """SELECT bid_amount AS `Bid Amount`,DATE_FORMAT(time_of_bid, '%%m/%%d/%%y  %%h:%%i %%p') AS `Time of Bid`, username AS `Username`  
                            FROM Bid WHERE itemID=%s 
                            ORDER BY bid_amount DESC LIMIT 4;""",
            (item_id,),
        )
        latest_bids = cursor.fetchall()
        for bid in latest_bids:
            bid_amount = bid["Bid Amount"]
            print("Latest bid Fetch: ", bid_amount)

        # Get current highest bid and starting bid
        cursor.execute(
            """SELECT MAX(bid_amount) AS 'MaxBid' 
                        FROM Bid WHERE itemID=%s
                        GROUP BY itemID;""",
            (item_id,),
        )
        highest_bid = cursor.fetchone()
        if highest_bid:
            print("Highest bid: ", highest_bid["MaxBid"])
        startingBid = float(item["starting_bid"])

        if item["get_it_now_price"] != None and bidAmount >= float(
            item["get_it_now_price"]
        ):
            mesage = f"Bid should not be more than Get It Now Price. Click Get It Now Price Button !"
            return render_template(
                "item_details.html",
                item=item,
                item_id=item_id,
                mesage=mesage,
                latest_bids=latest_bids,
                highest_bid=highest_bid,
                listedUser_username=listedUser_username,
                currentUser_username=currentUser_username,
                usertype=session["role"],
            )
        if highest_bid:
            highest_bidValue = float(highest_bid["MaxBid"]) + 1.0
            if bidAmount < highest_bidValue:
                mesage = f"Minimum bid has to be more than ${highest_bidValue}"
                return render_template(
                    "item_details.html",
                    item=item,
                    item_id=item_id,
                    mesage=mesage,
                    latest_bids=latest_bids,
                    highest_bid=highest_bid,
                    listedUser_username=listedUser_username,
                    currentUser_username=currentUser_username,
                    usertype=session["role"],
                )
            else:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(
                    """INSERT INTO Bid (itemID, username,time_of_bid,bid_amount) 
                                    VALUES (%s, %s, %s, %s);""",
                    (item_id, currentUser, currentTime, bidAmount),
                )
                mysql.connection.commit()
                flash("Bid created successfully", "success")
                return redirect(url_for("item_details", item_id=item_id))
        elif bidAmount < (startingBid + 1.0):
            mesage = f"Minimum bid has to be more than ${startingBid}"
            return render_template(
                "item_details.html",
                item=item,
                item_id=item_id,
                mesage=mesage,
                latest_bids=latest_bids,
                highest_bid=highest_bid,
                listedUser_username=listedUser_username,
                currentUser_username=currentUser_username,
                usertype=session["role"],
            )
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                """INSERT INTO Bid (itemID, username,time_of_bid,bid_amount) 
                                VALUES (%s, %s, %s, %s);""",
                (item_id, currentUser, currentTime, bidAmount),
            )
            mysql.connection.commit()
            flash("Bid created successfully", "success")
            return redirect(url_for("item_details", item_id=item_id))
    else:
        return redirect(url_for("login"))


@app.route("/cancel_item", methods=["GET", "POST"])
def cancel_item():
    if "loggedin" in session:
        item_id = request.args.get("item_id")
        print("itemID: ", item_id)

        if request.method == "GET":
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("""SELECT * FROM Item WHERE itemID=%s;""", (item_id,))
            item = cursor.fetchone()

            if item:
                return render_template("cancel_item.html", item=item)
            else:
                return "Item not Found"

        if request.method == "POST":
            cancelReason = request.form.get("cancelled_reason")
            currentTime = datetime.now()
            currentUser = session["userid"]
            print("cancelReason: ", cancelReason)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("""SELECT * FROM Item WHERE itemID=%s;""", (item_id,))
            item = cursor.fetchone()
            if not cancelReason:

                mesage = "Please enter cancel descriptions !"
                return render_template("cancel_item.html", item=item, mesage=mesage)

            else:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(
                    """UPDATE Item SET auction_end_time=%s,cancelled_username=%s,cancelled_reason=%s
                                WHERE itemID=%s;""",
                    (currentTime, currentUser, cancelReason, item_id),
                )

                mysql.connection.commit()
                mesage = "Cancel Item successfully"
                return render_template("search_items.html", mesage=mesage)

    else:
        return redirect(url_for("login"))


@app.route("/view_rating", methods=["GET", "POST"])
def view_rating():
    if "loggedin" in session:
        item_id = request.args.get("item_id")
        print("item ID: ", item_id)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            """SELECT itemID, item_name FROM Item WHERE itemID=%s;""", (item_id,)
        )
        item = cursor.fetchone()

        # Get average ratign for the item
        itemName = item["item_name"]
        print("Item name: ", itemName)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            """SELECT ROUND(AVG(r.star), 1) AS `Average Rating`
                            FROM Rating r 
                            INNER JOIN Item i ON r.itemID = i.itemID
                            WHERE BINARY i.item_name=%s;""",
            (itemName,),
        )
        average_rating = cursor.fetchone()
        print("Average rating: ", average_rating["Average Rating"])

        # Get all rating for the item_name by winers
        cursor.execute(
            """SELECT r1.itemID, r2.Winner AS 'Rated By', r1. rating_date_time AS 'Date', r1.star AS 'Star', r1.`comment` AS 'Comment' FROM (
                            SELECT r.itemID, r.rating_date_time, r.star, r.`comment`
                            FROM Rating r INNER JOIN Item i ON r.itemID = i.itemID
                            WHERE BINARY i.item_name=%s) r1
                            INNER JOIN 
                            (SELECT i1.itemID, 
                                CASE
                                    WHEN i1.cancelled_username IS NULL THEN b1.username
                                            ELSE NULL
                                END AS 'Winner'
                            FROM Item i1 INNER JOIN (
                                SELECT b2.itemID, b2.username, b2.bid_amount FROM Bid b2 INNER JOIN (
                                    SELECT itemID, MAX(bid_amount) AS MaxBid FROM Bid GROUP BY itemID
                                ) AS MaxBids ON b2.itemID = MaxBids.itemID AND b2.bid_amount = MaxBids.MaxBid
                            ) b1 ON i1.itemID = b1.itemID
                            WHERE i1.auction_end_time<= NOW() AND b1.bid_amount >= i1.min_sale_price) r2 ON r1.itemID=r2.itemID
                            ORDER BY r1.rating_date_time DESC;""",
            (itemName,),
        )
        ratings = cursor.fetchall()
        print("All ratings: ", ratings)

        if item:
            return render_template(
                "view_rating.html",
                item=item,
                average_rating=average_rating,
                ratings=ratings,
                usertype=session["role"],
            )
        else:
            return "Item not Found"
    else:
        return redirect(url_for("login"))


@app.route("/delete_rating", methods=["GET", "POST"])
def delete_rating():
    if "loggedin" in session:
        item_id = request.args.get("item_id")
        redirect_location = request.args.get("redirect")
        print("item ID: ", item_id)
        print("redirec", redirect_location)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""DELETE FROM Rating WHERE itemID= %s;""", (item_id,))
        mysql.connection.commit()
        flash("Successfully deleted the rating", "success")
        if redirect_location == "view_rating":
            return redirect(url_for("view_rating", item_id=item_id))
        elif redirect_location == "item_rating":
            return redirect(
                url_for(
                    "item_rating", item_id=item_id, winner=request.args.get("winner")
                )
            )
        else:
            return redirect(url_for(endpoint="dashboard"))
    else:
        return redirect(url_for("login"))


@app.route("/item_rating", methods=["GET", "POST"])
def item_rating():
    if "loggedin" in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        mesage = ""
        item_id = request.args.get("item_id")
        cursor.execute(
            """SELECT i1.itemID, 
                            CASE
                                WHEN b1.username IS NULL THEN ''
                                WHEN b1.bid_amount < i1.min_sale_price THEN ''
                                WHEN i1.cancelled_username IS NULL THEN b1.username
                                ELSE 'Cancelled'
                            END AS 'winner'
                        FROM Item i1 LEFT JOIN (
                            SELECT b2.itemID, b2.username, b2.bid_amount FROM Bid b2 INNER JOIN (
                                SELECT itemID, MAX(bid_amount) AS MaxBid FROM Bid GROUP BY itemID
                            ) AS MaxBids ON b2.itemID = MaxBids.itemID AND b2.bid_amount = MaxBids.MaxBid
                        ) b1 ON i1.itemID = b1.itemID
                        WHERE i1.itemID=%s;""",
            (item_id,),
        )
        winner = cursor.fetchone()["winner"]

        print("itemID: ", item_id)
        print("winner: ", winner)
        item = {}
        average_rating = ""
        cursor.execute(
            """SELECT itemID, item_name FROM Item WHERE itemID=%s;""", (item_id,)
        )
        item = cursor.fetchone()

        # Get average ratign for the item
        itemName = item["item_name"]
        print("Item name: ", itemName)
        # Get all rating for the item_name by winers
        cursor.execute(
            """SELECT r1.itemID, r2.Winner AS 'Rated By', r1. rating_date_time AS 'Date', r1.star AS 'Star', r1.`comment` AS 'Comment' FROM (
                            SELECT r.itemID, r.rating_date_time, r.star, r.`comment`
                            FROM Rating r INNER JOIN Item i ON r.itemID = i.itemID
                            WHERE BINARY i.item_name=%s) r1
                            INNER JOIN 
                            (SELECT i1.itemID, 
                                CASE
                                    WHEN i1.cancelled_username IS NULL THEN b1.username
                                            ELSE NULL
                                END AS 'Winner'
                            FROM Item i1 INNER JOIN (
                                SELECT b2.itemID, b2.username, b2.bid_amount FROM Bid b2 INNER JOIN (
                                    SELECT itemID, MAX(bid_amount) AS MaxBid FROM Bid GROUP BY itemID
                                ) AS MaxBids ON b2.itemID = MaxBids.itemID AND b2.bid_amount = MaxBids.MaxBid
                            ) b1 ON i1.itemID = b1.itemID
                            WHERE i1.auction_end_time<= NOW() AND b1.bid_amount >= i1.min_sale_price) r2 ON r1.itemID=r2.itemID
                            ORDER BY r1.rating_date_time DESC;""",
            (itemName,),
        )
        ratings = cursor.fetchall()

        enable_delete_button = False
        enable_comment_box = False
        if winner == session["userid"]:
            enable_comment_box = True
            enable_delete_button = True
        for rating in ratings:
            if rating["Rated By"] == winner:
                enable_comment_box = False
                break

        cursor.execute(
            """SELECT ROUND(AVG(r.star), 1) AS `Average Rating`
                            FROM Rating r 
                            INNER JOIN Item i ON r.itemID = i.itemID
                            WHERE BINARY i.item_name=%s;""",
            (itemName,),
        )
        average_rating = cursor.fetchone()
        print("Average rating: ", average_rating["Average Rating"])
        if request.method == "GET":
            if item and average_rating:
                return render_template(
                    "item_rating.html",
                    item=item,
                    average_rating=average_rating,
                    winner=winner,
                    ratings=ratings,
                    enable_comment_box=enable_comment_box,
                    usertype=session["role"],
                    enable_delete_button=enable_delete_button,
                )
            else:
                return "Item not Found"

        if request.method == "POST" and "star" in request.form:
            star = request.form["star"]
            time = datetime.now()
            if "comment" in request.form and request.form["comment"] == "":
                cursor.execute(
                    "INSERT INTO Rating (itemID, rating_date_time, star, comment) VALUES (%s, %s, % s, % s)",
                    (item_id, time, star, ""),
                )
                mysql.connection.commit()
                flash("Item Rating added succesfully", "success")
                return redirect(url_for("item_rating", item_id=item_id, winner=winner))
            else:
                comment = request.form["comment"]
                cursor.execute(
                    "INSERT INTO Rating (itemID, rating_date_time, star, comment) VALUES (%s, %s, % s, % s)",
                    (item_id, time, star, comment),
                )
                mysql.connection.commit()
                flash("Item Rating added succesfully", "success")
                return redirect(url_for("item_rating", item_id=item_id, winner=winner))
        else:
            mesage = "Please fill out the form!"
            return render_template(
                "item_rating.html",
                item=item,
                average_rating=average_rating,
                winner=winner,
                ratings=ratings,
                enable_comment_box=enable_comment_box,
                usertype=session["role"],
                enable_delete_button=enable_delete_button,
                mesage=mesage,
            )
    else:
        return redirect(url_for("login"))


if __name__ == "__main__":
    app.run()
    os.execv(__file__, sys.argv)
