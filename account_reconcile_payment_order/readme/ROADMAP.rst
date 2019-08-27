* It would be good to check references too, but bank usually change some
  characters, so this doesn't seem to be a general solution.
* Take into account different currencies (in payment order or in bank
  statement).
* Try to match payment orders resulting entries grouped by due date, instead of
  a whole, but this will affect performance for sure.
* Develop real UI tests, instead of mimicking the call to the involved method.
