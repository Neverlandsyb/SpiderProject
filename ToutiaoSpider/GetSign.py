import execjs

with open('Sign.js',encoding='utf-8') as f:
    js_code = f.read()

node = execjs.get()

sign = execjs.compile(js_code).call("get_sign")

print(sign)
