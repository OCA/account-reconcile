This module makes visible the currency columns in the bank statements lines.

Notice that all banks will provide the amounts in the account's main
currency and in the foreign currency. You are not supposed to rely on
Odoo's currency rate of the moment. The exchange rate is given by the bank.

For example, You buy a widget in Amazon.com for $100.

You can see in your statement:
Amazon.com -80€ (-$100)

Then you enter exactly this in Odoo's bank statement. The rate 80€/$100 is the
rate that the bank applied to the payment you made in USD in Amazon.com,
because your bank account is held in EUR. You need the $100 to be able to
reconcile with the invoice, and you need the €80 because that's what hit your
bank.
