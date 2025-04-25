import matplotlib.pyplot as plt

months = ["Jan", "Feb", "Mar", "Apr", "May"]
checkout_issues = [45, 60, 90, 70, 65]
shipping_issues = [30, 25, 20, 15, 10]

plt.plot(months, checkout_issues, label="Checkout Issues", marker="o")
plt.plot(months, shipping_issues, label="Shipping Issues", marker="o")

plt.title("Ticket Trends by Category (2025)")
plt.xlabel("Month")
plt.ylabel("Number of Tickets")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("ticket_trends.png")
plt.show()
