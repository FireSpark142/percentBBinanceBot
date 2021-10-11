# percentBBinanceBot

When the command prompts for you API_KEY please navigate to this page: https://www.binance.us/en/usercenter/settings/api-management and setup a key
Insert your public and secret APIKeys into the "APIKeys.json" file. Be sure to include the quotation marks -> ""

in the base folder
```pip install TA_Lib-0.4.21-cp39-cp39-win_amd64.whl```

if you are not a US Citizen, you need to navigate to app.py and change this

```clients = Client(API_KEY, API_SECRET, tld='us')```

to this:

```clients = Client(API_KEY, API_SECRET, tld='com')```

and this

```
@app.route('/bot', methods=['POST', 'GET'])
def bot():
    bot.main()
    return 'run'
```

to this

```
@app.route('/bot', methods=['POST', 'GET'])
def bot():
    boteu.main()
    return 'run'
```

copy and paste the following commands into your client to get things running:

```pip install -r requirements.txt```
```cd src```
``flask run```
then open your browser and navigate to ```localhost:5000``` 
it can sometimes take a second to propigate.
