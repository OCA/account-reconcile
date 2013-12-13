## -*- coding: utf-8 -*-
<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <style type="text/css">
            ${css}
        </style>
    </head>
    <body>
           <%!
            def amount(text):
                return text.replace('-', '&#8209;')  # replace by a non-breaking hyphen (it will not word-wrap between hyphen and numbers)
            %>

            <%setLang(user.partner_id.lang)%>
           %for statement in objects:

            <div class="act_as_table data_table">
                <div class="act_as_row labels">
                    <div class="act_as_cell">${_('Bordereau')}</div>
                    <div class="act_as_cell">${_('Date')}</div>
                </div>
                <div class="act_as_row">
                    <div class="act_as_cell">${ statement.name }</div>
                    <div class="act_as_cell">${ formatLang(statement.date,date=True)  }</div>
                </div>
            </div>

            <!-- we use div with css instead of table for tabular data because div do not cut rows at half at page breaks -->
                <div class="act_as_table list_table" style="margin-top: 10px;">
                    <div class="act_as_thead">
                        <div class="act_as_row labels">
                            ## date
                            <div class="act_as_cell first_column" style="width: 100px;">${_('Reference')}</div>
                            ## period
                            <div class="act_as_cell" style="width: 175px;">${_('Partenaire')}</div>
                            ## move
                            <div class="act_as_cell" style="width: 60px;">${_('Montant')}</div>
                            ## journal
                        </div>
                    </div>
                <% sum_statement = 0.0 %>
    	        %for statementline in statement.line_ids:
                    <div class="act_as_tbody">
                       ## curency code
                       <div class="act_as_cell">${statementline.name or '' }</div>
                       ## currency balance
                       <div class="act_as_cell">${statementline.partner_id.name or '' }</div>
                       ## currency balance cumulated
                       <div class="act_as_cell amount">${formatLang(statementline.amount) | amount }</div>
                       <% sum_statement += statementline.amount %>
                    </div>
    	        %endfor
                    <div class="act_as_tbody">
                       ## curency code
                       <div class="act_as_cell"></div>
                       ## currency balance
                       <div class="act_as_cell">Total</div>
                       ## currency balance cumulated
                       <div class="act_as_cell amount_total">${formatLang(sum_statement) }</div>
                    </div>

              </div>
          %endfor

     


    </body>
</html>
