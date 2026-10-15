"""Order processing logic."""
import database
import auth

TAX = 0.15
COUPONS_DISCOUNTS = {"ADMIN": 0.7, "STAFF": 0.7, "BLACKFRIDAY": 0.5, "WELCOME10": 0.9 }

def process_order(token, items, coupon=None, shipping="standard", log=[]):
    username = auth.sessions.get(token)
    if username != None:
        if items == []:
            print("Empty order")
            return None
        total = 0
        for item in items:
            book = database.get_book(item["book_id"])
            if book:
                if book[3] >= item["qty"]:
                    if item["qty"] > 0:
                        total = total + book[2] * item["qty"]
                        database.update_stock(book[0], book[3] - item["qty"])
                    else:
                        print("Invalid quantity")
                else:
                    if book[3] > 0:
                        print("Only " + str(book[3]) + " units available for " + book[1])
                    else:
                        print("Book out of stock: " + book[1])
            else:
                print("Book not found")
        if coupon:
            total = total * COUPONS_DISCOUNTS[coupon]


        if shipping == "express":
            total = total + 10
        elif shipping == "standard":
            total = total + 3
        total = total + total * TAX
        order_id = len(log) + 1
        database.save_order(order_id, username, total, "PENDING")
        log.append(order_id)
        return round(total, 2)
    else:
        print("Invalid session")
        return None


def _generate_document_body(title, username, items):
    """Función auxiliar que calcula los montos e imprime el cuerpo común."""
    print("==============================")
    print(f"BOOKSTORE {title}")
    print(f"Customer: {username}")
    print("==============================")
    
    subtotal = 0
    for item in items:
        book = database.get_book(item["book_id"])
        line_total = book[2] * item["qty"]
        subtotal += line_total
        print(f"{book[1]} x{item['qty']} = {line_total}")
        
    tax = subtotal * TAX
    print(f"Subtotal: {round(subtotal, 2)}")
    print(f"Tax: {round(tax, 2)}")
    print(f"Total: {round(subtotal + tax, 2)}")


def print_invoice(username, items):
    _generate_document_body("INVOICE", username, items)
    print("==============================")


def print_quote(username, items):
    _generate_document_body("QUOTE", username, items)
    print("This quote is valid for 7 days.")
    print("==============================")


def cancel_order(order_id):
    try:
        conn = database.get_connection()
        conn.execute(f"UPDATE orders SET status = 'CANCELLED' WHERE id = {order_id}")
        conn.commit()
    except:
        pass
