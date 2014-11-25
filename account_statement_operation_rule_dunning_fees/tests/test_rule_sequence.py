# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import exceptions
from openerp.tests import common


class TestRuleSequence(common.TransactionCase):

    def setUp(self):
        super(TestRuleSequence, self).setUp()
        self.operation_obj = self.env['account.statement.operation.template']
        self.rule_obj = self.env['account.statement.operation.rule']
        self.rule_dunning = self.rule_obj.create({
            'name': 'Dunning Fees',
            'rule_type': 'dunning_fees',
            'sequence': 5,
        })
        self.rule_round_1 = self.rule_obj.create({
            'name': 'Rounding -1.0 to 0.0',
            'rule_type': 'rounding',
            'amount_min': -1.0,
            'amount_max': 0,
            'sequence': 10,
        })
        self.rule_round_2 = self.rule_obj.create({
            'name': 'Rounding -2.0 to -1.0',
            'rule_type': 'rounding',
            'amount_min': -2.0,
            'amount_max': -1.0,
            'sequence': 15,
        })
        self.rule_currency = self.rule_obj.create({
            'name': 'Currency',
            'rule_type': 'currency',
            'amount_min': -2.0,
            'amount_max': -1.0,
            'sequence': 20,
        })

    def test_dunning_first(self):
        """ Dunning rule can be the first """
        self.rule_dunning.sequence = 1
        self.rule_round_1.sequence = 2
        self.rule_round_2.sequence = 3
        self.rule_currency.sequence = 4

    def test_dunning_after_rounding(self):
        """ Dunning rule cannot be after a rounding rule """
        with self.assertRaises(exceptions.ValidationError):
            self.rule_dunning.sequence = 30

    def test_dunning_equal_rounding(self):
        """ Dunning rule cannot be equal to a rounding rule """
        with self.assertRaises(exceptions.ValidationError):
            self.rule_dunning.sequence = 10

    def test_rounding_before_dunning(self):
        """ Rounding cannot be before dunning """
        with self.assertRaises(exceptions.ValidationError):
            self.rule_round_1.sequence = 1

    def test_currency_before_dunning(self):
        """ Currency can be before dunning"""
        self.rule_currency.sequence = 1
