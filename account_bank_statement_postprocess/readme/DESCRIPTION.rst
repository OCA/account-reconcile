This module extends the functionality of Bank Statements to support various
post-processing models that are applied to the records.

Supported models:

 * "Extract fee" creates an extra record on the statement with fee and
   subtracts that from the original record.
 * "Multi-currency" adjusts the record to reflect multi-currency
   transaction values.
 * "Multi-currency (fee included)" adjusts the record to reflect multi-currency
   transaction values (with fee included).
 * "Trim field" adjusts the record by trimming part of the value.
 * "Append field" adjusts the record by appending part of the value using the
   value of the other field.
 * "Merge per statement" merged matching records into a new one within the
   same statement, e.g. merge fees for faster reconcile.
 * "Delete" removes matching records from the statement.
