#coding=utf-8

from flask import Flask,request,redirect,render_template
from create_pcb_order import audit_pcb_order
from create_ic_order import erp_order_cv,passport_login,pcb_login,get_address,create_ic_order,pro_passport_login
from create_smt_order import confirm_order_new
from uat_cashier_desk import create_cashier_desk,pro_create_top_up_order,create_withdrawal_order
from scm_create_order import run
import json,os

app = Flask(__name__,template_folder=os.getcwd() + '/templates')
app.debug = True


@app.route('/create/scmOrder/<sn>',methods=['POST','GET'])
def create_scm_order(sn):
    res = run(sn)
    print(res)
    if res[0] == 0:
        res = {
            'result': {
                'orderSn': res[1],
                'orderNo': res[2],
            },
            'retCode': 0,
            'retMsg': '生成销售订单成功！'
        }
    else:
        res = {
            'result': {
                'orderSn': res[1],
                'orderNo': res[2],
            },
            'retCode': -1,
            'retMsg': '生成销售订单失败，PCB采购单未完成！'
        }
    return json.dumps(res,ensure_ascii=False)
    # return redirect('/help')




@app.route('/help')
def readme():
    return render_template('readme.html')


@app.route('/cv_order')
def cv_order():
    if request.args.get('orderSn') and request.args.get('amount'):
        res = erp_order_cv(request.args.get('orderSn'),request.args.get('amount'))
        return res
    else:
        print('请传入IC订单号和修改金额！')
        res = {
            'result': {
            },
            'retCode': -1,
            'retMsg': '请传入IC订单号和修改金额！'
        }
        return json.dumps(res,ensure_ascii=False)


@app.route('/create_order/<order_source>',methods=['POST','GET'])
def create_order(order_source):
    order_source = order_source.lower()
    if request.args.get('account') and request.args.get('password'):
        log_status = passport_login(request.args.get('account'),request.args.get('password'))
        s = (auth_ic,auth_token,auth_hqpcb) = log_status
        if s[0] == None:
            print('传入芯城用户名或密码有误！')
            res = {
                'result': {
                },
                'retCode': -1,
                'retMsg': '传入芯城用户名或密码有误！'
            }
            return json.dumps(res,ensure_ascii=False)
        pcb_erp_sid = pcb_login()
        add_id = get_address(s[1])
        if add_id == None:
            print('未创建收货地址！')
            res = {
                'result': {
                },
                'retCode': -1,
                'retMsg': '未创建收货地址！'
            }
            return json.dumps(res,ensure_ascii=False)
        if order_source == 'pcb':
            res = audit_pcb_order(add_id,s[2],pcb_erp_sid)
            return res
        if order_source == 'ic' and request.args.get('key'):
            res = create_ic_order(request.args.get('key'),s[0],add_id)
            return res
        if order_source == 'smt':
            res = confirm_order(s[2], add_id)
            return res
        else:
            print('输入路径有误或缺少参数！')
            res = {
                'result': {
                },
                'retCode': -1,
                'retMsg': '输入路径有误或缺少参数！'
            }
            return json.dumps(res,ensure_ascii=False)
    else:
        print('请传入华秋商城登录用户名和密码！')
        res = {
            'result': {
            },
            'retCode': -1,
            'retMsg': '请传入华秋商城登录用户名和密码！'
        }
        return json.dumps(res,ensure_ascii=False)


@app.route('/uat/v3/CashierDesk/<app_source>')
def create_v3_cashier(app_source):
    if request.args.get('userId') and request.args.get('amount') and request.args.get('orderNo'):
        url = create_cashier_desk(request.args.get('userId'),app_source,request.args.get('orderNo'),request.args.get('amount'))
        try:
            assert 'http' in url
            return redirect(url)
        except:
            res = {
                'result': {
                },
                'retCode': -1,
                'retMsg': url
            }
            return json.dumps(res,ensure_ascii=False)
    else:
        print('缺少必传参数！')
        res = {
            'result': {
            },
            'retCode': -1,
            'retMsg': '缺少必传参数！'
        }
        return json.dumps(res, ensure_ascii=False)


@app.route('/pro/v3/topUpDesk')
def create_v3_top_up():
    if request.args.get('account') and request.args.get('password') and request.args.get('amount'):
        token = pro_passport_login(request.args.get('account'),request.args.get('password'))
        if token == None:
            print('传入芯城用户名或密码有误！')
            res = {
                'result': {
                },
                'retCode': -1,
                'retMsg': '传入芯城用户名或密码有误！'
            }
            return json.dumps(res,ensure_ascii=False)
        else:
            url = pro_create_top_up_order(token,request.args.get('amount'))
            try:
                assert 'http' in url
                return redirect(url)
            except:
                res = {
                    'result': {
                    },
                    'retCode': -1,
                    'retMsg': url
                }
                return json.dumps(res, ensure_ascii=False)
    else:
        print('缺少必传参数！')
        res = {
            'result': {
            },
            'retCode': -1,
            'retMsg': '缺少必传参数！'
        }
        return json.dumps(res, ensure_ascii=False)


@app.route('/<environ>/<attr>/createWithdrawal')
def create_withdrawal(environ,attr):
    if request.args.get('account') and request.args.get('password') and request.args.get('amount') and request.args.get('payCode'):
        if attr == '1':
            attr_value = 'companyBank'
        else:
            attr_value = 'personBank'
        if environ == 'pro':
            token = pro_passport_login(request.args.get('account'), request.args.get('password'))
        else:
            token = passport_login(request.args.get('account'), request.args.get('password'))[1]
        if token == None:
            print('传入芯城用户名或密码有误！')
            res = {
                'result': {
                },
                'retCode': -1,
                'retMsg': '传入芯城用户名或密码有误！'
            }
            return json.dumps(res, ensure_ascii=False)
        else:
            msg = create_withdrawal_order(environ,token,attr,request.args.get('amount'),request.args.get('payCode'))
            print(msg)
            res = {
                'result': {
                    'environ': environ,
                    'attr': attr_value,
                    'amount': request.args.get('amount'),
                },
                'retCode': 0,
                'retMsg': msg
            }
            return json.dumps(res, ensure_ascii=False)
    else:
        print('缺少必传参数！')
        res = {
            'result': {
            },
            'retCode': -1,
            'retMsg': '缺少必传参数！'
        }
        return json.dumps(res, ensure_ascii=False)


@app.route('/create_smt_order/',methods=['POST','GET'])
def create_smt_order():
    if request.args.get('hqId') and request.args.get('type') and request.args.get('credit'):
        res = confirm_order_new(request.args.get('hqId'),request.args.get('type'),request.args.get('credit'))
        print(res)
        return res
    else:
        print('缺少必传参数！')
        res = {
            'result': {
            },
            'retCode': -1,
            'retMsg': '缺少必传参数！'
        }
        return json.dumps(res, ensure_ascii=False)




if __name__ == '__main__':
    # app.run(host='192.168.11.14',port='5000')
    app.run(host='192.168.14.36', port='5000')