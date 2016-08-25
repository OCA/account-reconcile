from openerp import models, api, _
from openerp.exceptions import UserError


class AutocompleteAccountMove(models.TransientModel):
    _name = "autocomplete.account.move"
    _description = "Autocomplete Account Move"

    @api.multi
    def autocomplete_move(self):
        context = dict(self._context or {})
        moves = self.env['account.move'].browse(context.get('active_ids'))
        draft_move_ids = []
        journal_error_names = []
        for move in moves:
            if move.state != 'draft':
                draft_move_ids.append(move.id)
            if not move.used_for_completion:
                if move.journal_id.name not in journal_error_names:
                    journal_error_names.append(move.journal_id.name)
        if draft_move_ids:
            raise UserError(
                _('Some journal entries are not at draft state : %s'
                    % (draft_move_ids,)))
        if journal_error_names:
            raise UserError(
                _('Autocompletion is not allowed on journals %s'
                    % (journal_error_names,)))
        moves.button_auto_completion()
        return {'type': 'ir.actions.act_window_close'}
