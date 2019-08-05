# Import packages
from flask import Flask, render_template, request
from keras.models import load_model
import matplotlib.pyplot as plt
import sys
sys.path.append('./utils')
import utils
import io
import base64

# Load model
model = load_model('./model/TA model v2.h5')

application = Flask(__name__)

@application.route('/', methods=["POST","GET"])
def show_stock():

    # Initialize variables
    percent_chg = 'Unknown'
    target_price = 'Unknown'

    # Get stock list
    df_stock_price = utils.get_df_stock_price()
    stocks = df_stock_price['stockcode'].unique()

    # Get stock latest update date
    stocks_latest_update = []
    for stock in df_stock_price['stockcode'].unique():
        latest_update = max(df_stock_price[df_stock_price.stockcode == stock].date).strftime('%Y-%m-%d')
        stocks_latest_update.append([stock, latest_update])

    if request.method == 'POST':
        # Predict stock price

        print('[Debug]'+request.form['stock'])

        stock = request.form['stock']
        X_Ori, y_Ori, X_Date = utils.get_df_pred(stock)
        y_pred = model.predict(X_Ori)

        # Percentage change
        chg = (float(y_pred[-1]) - y_Ori[-2]) * 100.0 / y_Ori[-2]
        percent_chg = str(format(chg, '.2f')) + '%'

        # Target Price
        current_price = list(df_stock_price[df_stock_price.stockcode == stock].adjclose)[-1]
        target_price = str(format(current_price * (1 + chg/100.0),'.2f'))


        # Plot stock price
        img = io.BytesIO()
        plt.figure(figsize=(10, 5))
        plt.plot(X_Date, y_Ori)
        plt.plot(X_Date, y_pred)
        plt.title(stock+' Stock Price')
        plt.savefig(img, format='png')
        plt.close()
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
    else:
        plot_url = ""
    return render_template("index.html",
                           plot_url=plot_url,
                           stocks=stocks,
                           stocks_latest_update = stocks_latest_update,
                           percent_chg = percent_chg,
                           target_price = target_price)


if __name__ == '__main__':
    application .run(host='0.0.0.0')
