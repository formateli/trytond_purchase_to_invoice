# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool, PoolMeta

__all__ = ['Purchase']


class Purchase:
    __metaclass__ = PoolMeta
    __name__ = 'purchase.purchase'

    @classmethod
    def process(cls, purchases):
        super(Purchase, cls).process(purchases)
        Invoice = Pool().get('account.invoice')
        Move = Pool().get('stock.move')
        invoices = []
        for purchase in purchases:
            if purchase.invoice_method != 'order':
                continue
            if purchase.state != 'processing':
                continue
            for inv in purchase.invoices:
                if inv.state == 'draft':
                    inv.invoice_date = purchase.purchase_date
                    inv.save()
                    invoices.append(inv)

            if purchase.shipments:
                continue
            moves = []
            for line in purchase.lines:
                if not line.moves:
                    continue
                for move in line.moves:
                    if move.state == 'draft':
                        move.effective_date = purchase.purchase_date
                        move.save()
                        moves.append(move)
            if moves:
                Move.do(moves)
        if invoices:
            Invoice.post(invoices)
