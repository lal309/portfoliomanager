from .models import Folio, MutualFundTransaction
import datetime
from dateutil.relativedelta import relativedelta
from shared.handle_real_time_data import get_historical_mf_nav

class MfInterface:

    @classmethod
    def get_chart_name(self):
        return 'MF'

    @classmethod
    def get_start_day(self, user_id=None):
        start_day = None
        try:
            if user_id:
                objs = Folio.objects.filter(user=user_id)
            else:
                objs = Folio.objects.all()
            
            for obj in objs:
                mf_trans = MutualFundTransaction.objects.filter(folio=obj)
                for trans in mf_trans:
                    if not start_day:
                        start_day = trans.trans_date
                    else:
                        start_day = start_day if start_day < trans.trans_date else trans.trans_date
        except Exception as ex:
            print(f'exception finding start day for Mutual Fund {ex}')
        return start_day

    @classmethod
    def get_start_day_for_goal(self, goal_id):
        start_day = None
        try:
            objs = Folio.objects.filter(goal=goal_id)
            for obj in objs:
                mf_trans = MutualFundTransaction.objects.filter(folio=obj)
                for trans in mf_trans:
                    if not start_day:
                        start_day = trans.trans_date
                    else:
                        start_day = start_day if start_day < trans.trans_date else trans.trans_date
        except Exception as ex:
            print(f'exception finding start day for goal {goal_id} ppf {ex}')
        return start_day

    @classmethod
    def get_start_day_for_user(self, user_id):
        start_day = None
        try:
            objs = Folio.objects.filter(user=user_id)
            for obj in objs:
                mf_trans = MutualFundTransaction.objects.filter(folio=obj)
                for trans in mf_trans:
                    if not start_day:
                        start_day = trans.trans_date
                    else:
                        start_day = start_day if start_day < trans.trans_date else trans.trans_date
        except Exception as ex:
            print(f'exception finding start day for user {user_id} ppf {ex}')
        return start_day

    @classmethod
    def get_no_goal_amount(self, user_id=None):
        amt = 0
        if user_id:
            objs = Folio.objects.filter(user=user_id)
        else:
            objs = Folio.objects.all()
        for obj in objs:
            if not obj.goal:
                amt += 0 if not obj.latest_value else obj.latest_value
        return amt

    @classmethod
    def get_goal_yearly_contrib(self, goal_id, yr):
        st_date = datetime.date(year=yr, day=1, month=1)
        end_date = datetime.date(year=yr, day=31, month=12)
        if end_date > datetime.date.today():
            end_date = datetime.date.today()
        year_end_mf = dict()
        contrib = 0
        deduct = 0
        total = 0
        cash_flows = list()
        try:
            for folio_obj in Folio.objects.filter(goal=goal_id):
                for trans in MutualFundTransaction.objects.filter(folio=folio_obj, trans_date__lte=end_date):
                    if trans.trans_date.year == yr:
                        if trans.trans_type == 'Buy' and not trans.switch_trans:
                            contrib += trans.trans_price
                            cash_flows.append((trans.trans_date, -1*float(trans.trans_price)))
                            year_end_mf[folio_obj.fund.code] = year_end_mf.get(folio_obj.fund.code, 0)+trans.units
                        elif trans.trans_type == 'Sell' and not trans.switch_trans:
                            deduct += -1*trans.trans_price
                            cash_flows.append((trans.trans_date, float(trans.trans_price)))
                            year_end_mf[folio_obj.fund.code] = year_end_mf.get(folio_obj.fund.code, 0)-trans.units
                    else:
                        if trans.trans_type == 'Buy' and not trans.switch_trans:
                            year_end_mf[folio_obj.fund.code] = year_end_mf.get(folio_obj.fund.code, 0)+trans.units
                        elif trans.trans_type == 'Sell' and not trans.switch_trans:
                            year_end_mf[folio_obj.fund.code] = year_end_mf.get(folio_obj.fund.code, 0)-trans.units
        except Exception as ex:
            print(f'exception during getting mf goal yearly contribution {ex}')
        print('year_end_mf', year_end_mf)
            
        for code,qty in year_end_mf.items():
            historical_mf_prices = get_historical_mf_nav(code, end_date+relativedelta(days=-5), end_date)
            if len(historical_mf_prices) > 0:
                print('historical_mf_prices',historical_mf_prices)
                for k,v in historical_mf_prices[0].items():
                    total += v*qty
            else:
                print(f'failed to get year end vals for mutual fund {code} goal {goal_id} year {yr}')
        return cash_flows, contrib, deduct, total
    
    @classmethod
    def get_user_yearly_contrib(self, user_id, yr):
        st_date = datetime.date(year=yr, day=1, month=1)
        end_date = datetime.date(year=yr, day=31, month=12)
        contrib = 0
        deduct = 0
        for folio_obj in Folio.objects.filter(user=user_id):
            for trans in MutualFundTransaction.objects.filter(folio=folio_obj, trans_date__lte=end_date):
                if trans.trans_date.year == yr:
                    if trans.trans_type == 'Buy' and not trans.switch_trans:
                        contrib += trans.trans_price
                    elif trans.trans_type == 'Sell' and not trans.switch_trans:
                        deduct += -1*trans.trans_price
        return contrib, deduct

    @classmethod
    def get_user_monthly_contrib(self, user_id, yr):
        st_date = datetime.date(year=yr, day=1, month=1)
        end_date = datetime.date(year=yr, day=31, month=12)
        today = datetime.date.today()
        if end_date > today:
            end_date = today
        contrib = [0]*12
        deduct = [0]*12
        for folio_obj in Folio.objects.filter(user=user_id):
            for trans in MutualFundTransaction.objects.filter(folio=folio_obj, trans_date__lte=end_date):
                if trans.trans_date.year == yr:
                    if trans.trans_type == 'Buy' and not trans.switch_trans:
                        contrib[trans.trans_date.month-1] += float(trans.trans_price)
                    elif trans.trans_type == 'Sell' and not trans.switch_trans:
                        deduct[trans.trans_date.month-1] += -1*float(trans.trans_price)
        return contrib, deduct

    @classmethod
    def get_export_name(self):
        return 'mf'
    
    @classmethod
    def get_current_version(self):
        return 'v1'

    @classmethod
    def export(self, user_id):
        from shared.handle_get import get_goal_name_from_id

        ret = {
            self.get_export_name(): {
                'version':self.get_current_version()
            }
        }
        data = list()
        for fo in Folio.objects.filter(user=user_id):
            eod = {
                'country': fo.country,
                'folio': fo.folio,
                'fund': {
                    'code':fo.fund.code,
                    'name':fo.fund.name,
                    'fund_house':fo.fund.fund_house,
                    'isin':fo.fund.isin,
                    'isin2':fo.fund.isin2
                },
                'notes':fo.notes,
                'goal_name':''
            }
            if fo.goal:
                eod['goal_name'] = get_goal_name_from_id(fo.goal)
            t = list()
            for trans in MutualFundTransaction.objects.filter(folio=fo):
                t.append({
                    'trans_date':trans.trans_date,
                    'price':trans.price,
                    'units': trans.units,
                    'conversion_rate':trans.conversion_rate,
                    'trans_price':trans.trans_price,
                    'broker':trans.broker,
                    'notes':trans.notes,
                    'trans_type':trans.trans_type,
                    'switch_trans':trans.switch_trans
                })
            eod['transactions'] = t
            data.append(eod)
        
        ret[self.get_export_name()]['data'] = data
        print(ret)
        return ret
    
    @classmethod
    def get_amount_for_user(self, user_id):
        mf_objs = Folio.objects.filter(user=user_id)
        total = 0
        for mf_obj in mf_objs:
            if mf_obj.latest_value:
                total += mf_obj.latest_value
        return total

    @classmethod
    def get_amount_for_all_users(self, ext_user):
        from users.user_interface import get_users
        amt = 0
        for u in get_users(ext_user):
            amt += self.get_amount_for_user(u.id)
        return amt
