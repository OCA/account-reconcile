1. Access Reconcile Models
2. On an invoice matching rule, add a regex match
3. From now on, the match will be used for searching and obtaining the information to find

For example, if we set "Fattura (.*)", and we receive a settlment with the following label "Fattura INV/21/12323",
Odoo will transform it to INV/21/12323 and search for this exact text.
