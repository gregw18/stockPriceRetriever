# Stock Price Retriever
This project had two purposes - to give me some experience with AWS Lambdas and to give me some information to help monitor my investment portfolio.
This Python project, intended to run as an AWS Lambda, retrieves stock prices, performs some calculations and sends a daily email notification. For each stock, the notification includes a rating, the current price, the specified buy and sell prices for that stock, the current price as a percentage of its 52 week high and the percent that the stock price changed today. Each stock is placed in one of five groups - buy, near buy, middle, near sell and sell, based on where its current price is relative to the buy and sell prices. (The user of this program has to supply the buy and sell prices, based on whatever they like.)
The rating is a calculation used to further rank each stock within each group.
        Buy group: percentage of buy price that current price is below buy price. i.e.
                        (buyPrice - currentPrice)/buyPrice
        Near Buy/Middle/Near Sell Groups: percentage of buy/sell range that current price is above the buy price. i.e.
                        (currentPrice - buyPrice)/(sellPrice - buyPrice)
        Sell Group: percentage of sell price that current price is over sell price. i.e.
                        (currentPrice - sellPrice)/sellPrice
Note that these calculations have no particular meaning - they're just a way for me to pseudo-sensibly sort the stocks within each group.
The buy/sell groups should be fairly obvious - stocks that are below their buy prices or above their sell prices. For the rest, stocks within 25% of the bottom of the range between the buy and sell prices are near buy, while those within 25% of the top are near sell - the rest are in the middle. Again, these calculations are completely arbitrary.
A web site has been added, to display all this information, over a selectable period of time, and sorted by various columns. The data is now stored in an AWS RDS/MySQL database, as it now keeps historical prices - daily closing prices for 3 months, weekly for 5 years. It is rather slow and aesthetically-challenged, but provides the information that I'm looking for in an easy to understand format (lots of graphs.)
![Screen Shot](images/StockRetrieverScreenshot.jpg?raw=true "Screen")
Note that because of the MySQL database, running this project on AWS now has a cost, unless you qualify for the AWS RDS free tier. It had previously snuck under the free tier limit, at least for me.

## Getting Started
I assume that you have an AWS account and the AWS python libraries and cli installed.
Most of the AWS resources required to run this are created automatically, but names can be chosen and have to be provided. Unless you happen to be running the same operating system, on near-identical hardware, as your lambda function will be running under on AWS, it's probably best to perform the following steps in a vm running AWS' latest Python3 Lambda environment.
1. S3 bucket. If you don't like the name "stock-price-retriever" for your bucket, change it in 1-create-bucket.sh. Run 1-create-bucket-sh to create the S3 bucket to use for this lambda.
2. Prepare install libraries. Run 2-build-layer.sh, which will install the libraries required for this application, in the package directory.
3. Create your stocks spreadsheet. You can start with the provided sample (Portfolio.xls) or from scratch. It has to be in a format that xlrd can read - I stuck with plain old xls. It must have the following fields: Stock, Buy_price, Sell_price, Symbol and Ignore. The program assumes that the data is on a tab named "Current", but you can specify a different tab name in "src/code/settings.json" if desired. As a Canadian, I acknowledge the primacy of Americal stock markets, so American stocks don't need any prefix - i.e. use AAPL for Apple. Just kidding - the symbols used are those of Yahoo finance, except that Canadian symbols have a "TSX:" prefix rather than a ".TO" suffix. See sample files for examples of US and Canadian symbols. The "Ignore" column should contain either Y or N - even a space will result in the record being ignored.
4. Configuration. The template.yml contains the Cloudformation template for this project. 
        Time to run. The default is to run the function every weekday at 22:04 UTC, which is 5:04pm or 6:04pm, depending on daylight savings time. My goal was to run it sometime after US markets close. If yours is different, change the value in the cron function.
        SNS topics. This lambda uses two SNS topics, one to send out the daily stock data and the second to send out any errors executing the lambda. The first is called "StockRetrieverResultsTopic" and the second StockRetrieverTopic. If you don't like these names, you will have to change them in several places in the template as well as in settings.py.
        Topic subscriber. If you would like to receive emails when the program publishes something to the topics, change the "Endpoint" entries to the desired email address.
        Timeout. If your list of securities is particularly long, the lambda might timeout when retrieving all the prices. If this happens, you can change the Timeout in the function resource from 600 to up to 900 seconds (15 minutes is currently the maximum allowable run time.)
4. Deploy everything. Run 3-deploy.sh, providing as a parameter the spreadsheet to read from. If you're not comfortable with making your stocks of interest and corresponding buy/sell prices public, I recommend keeping the spreadsheet in the directory above this project, so you would deploy the script with something like "./3-deploy.sh ./mystocks.xls".


Development Environment
        Ubuntu
        Virtual Machine Manager and image for AWS' latest Python3 Lambda environment, if want to fully test locally.

Requirements
        Python 3
        AWS cli
        boto3
        botocore
        datetime
        getopt
        json
        lxml
        matplotlib
        math
        moto
        numpy
        os
        pandas
        pytest
        requests
        socket
        sys
        urllib3
        xlrd
        yahoo-fin
        

