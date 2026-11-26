To configure this module, you need to:

1.  Go to *Sales \> Configuration \> Online Payments \> Payment
    Providers*, open the Stripe provider of your company and fill in its *Secret Key*. Each
    company uses the Stripe provider of its own. The key must be a secret key
    (`sk_...`) or a restricted key (`rk_...`), not the publishable key
    (`pk_...`). The import only reads this key: the provider can stay
    *Disabled* when Stripe is not a payment method of the website.
2.  Go to *Accounting \> Configuration \> Journals* and create a Stripe
    journal of type *Bank*: tick *Journal used for import*, set *Type of
    import* to *Stripe*, and fill in the *Commission account*, the
    *Receivable/Payable Account* and the *Bank/Payment Office partner*.
3.  Optionally, activate the scheduled action *Import Stripe
    Deposit/Payout* in *Settings \> Technical \> Automation \> Scheduled
    Actions* to import the payouts every day.
