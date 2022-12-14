import os
import boto3


class Base():
    __abstract__ = True

    IS_LOCAL = bool(os.environ.get('IS_LOCAL'))
    PRJ_PREFIX = os.environ['CMS_PRJ_PREFIX']

    reserved_values = None

    @classmethod
    def connect_dynamodb(self):
        if self.IS_LOCAL:
            dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
        else:
            dynamodb = boto3.resource('dynamodb')
        return dynamodb


    @classmethod
    def get_table(self, table_name=None):
        dynamodb = self.connect_dynamodb()
        table_name = self.get_table_name()
        return dynamodb.Table(table_name)


    @classmethod
    def get_table_name(self):
        return '-'.join([self.PRJ_PREFIX, self.table_name])


    @classmethod
    def prj_exps_str(self, is_public=True):
        attrs = self.public_attrs if is_public else self.all_attrs
        res = [ attr['key'] if isinstance(attr, dict) else attr for attr in attrs ]
        return ', '.join(res)


    @classmethod
    def to_response(self, item):
        res = {}
        for i in self.response_attrs:
            if isinstance(i, str):
                k = i
                l = i
            if isinstance(i, dict):
                k = i['key']
                l = i['label']

            if k in item:
                val = item.get(k)
                if val:
                    res[l] = val

        return res


    @classmethod
    def scan(self, options=None):
        if options is None:
            options = {}
        table = self.get_table()
        res = table.scan(**options)
        return res.get('Items', [])


    @classmethod
    def get_all(self, keys, is_desc=False, index_name=None, limit=0, projections=None):
        table = self.get_table()
        option = {
            'ScanIndexForward': not is_desc,
        }
        if limit:
            option['Limit'] = limit

        if projections:
            if isinstance(projections, list):
                projections = ', '.join(projections)
            option['ProjectionExpression'] = projections

        if index_name:
            option['IndexName'] = index_name

        if not keys.get('p'):
            raise ModelInvalidParamsException("'p' is required on keys")

        key_cond_exps = ['#pk = :pk']
        exp_attr_names = {'#pk': keys['p']['key']}
        exp_attr_vals = {':pk': keys['p']['val']}

        if keys.get('s'):
            exp_attr_names['#sk'] = keys['s']['key']
            exp_attr_vals[':sk'] = keys['s']['val']
            key_cond_exps.append('#sk = :sk')

        option['KeyConditionExpression'] = ' AND '.join(key_cond_exps)
        option['ExpressionAttributeNames'] = exp_attr_names
        option['ExpressionAttributeValues'] = exp_attr_vals
        res = table.query(**option)
        return res['Items'] if len(res['Items']) > 0 else []


    @classmethod
    def get_one(self, keys, is_desc=False, index_name=None, projections=None):
        items = self.get_all(keys, is_desc, index_name, 1, projections)
        return items[0] if len(items) > 0 else None


    @classmethod
    def get_all_by_pkey(self, pkeys, params=None, index_name=None):
        table = self.get_table()

        if params and params.get('order') and not params.get('is_desc'):
            if params is None:
                params = {}
            params['is_desc'] = params.get('order') == 'desc'

        option = {'ScanIndexForward': not (params and  params.get('is_desc', False))}

        if params and params.get('count'):
            option['Limit'] = params['count']

        if index_name:
            option['IndexName'] = index_name

        key_cond_exp = '#pk = :pk'
        exp_attr_names = {'#pk': pkeys['key']}
        exp_attr_vals = {':pk': pkeys['val']}

        option['KeyConditionExpression'] = key_cond_exp
        option['ExpressionAttributeNames'] = exp_attr_names
        option['ExpressionAttributeValues'] = exp_attr_vals
        res = table.query(**option)
        return res.get('Items')


    @classmethod
    def get_one_by_pkey(self, hkey_name, hkey_val, is_desc=False, index_name=None):
        table = self.get_table()
        option = {
            'ScanIndexForward': not is_desc,
            'Limit': 1,
        }
        if index_name:
            option['IndexName'] = index_name
        exp_attr_names = {}
        exp_attr_vals = {}
        exp_attr_names['#hk'] = hkey_name
        exp_attr_vals[':hv'] = hkey_val
        option['KeyConditionExpression'] = '#hk = :hv'
        option['ExpressionAttributeNames'] = exp_attr_names
        option['ExpressionAttributeValues'] = exp_attr_vals
        res = table.query(**option)
        return res['Items'][0] if len(res['Items']) > 0 else None


    @classmethod
    def get_reserved_values(self, attr):
        if not self.reserved_values:
            return []

        if attr not in self.reserved_values:
            return []

        return self.reserved_values[attr]


    @classmethod
    def check_set_reserved_value(self, vals, is_raise_exp=True):
        if not self.reserved_values:
            return False

        for attr in self.reserved_values:
            if attr not in vals:
                continue

            if vals[attr] in self.reserved_values[attr]:
                if is_raise_exp:
                    raise ModelInvalidParamsException('%s value is not allowed' % attr)
                else:
                    return True

        return False


class ModelInvalidParamsException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
