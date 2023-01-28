# Stock Price Retriever
This project has two purposes - to give me some experience with AWS Lambdas and to help monitor my investment portfolio.

It consists mainly of two AWS Lambda functions, written in Python. The first automatically runs every day and retrieves data, stores it and sends a summary email. The second retrieves data for an associated web page.

The daily Lambda retrieves stock prices, saves them in a database, performs some calculations and sends a daily email notification. For each stock, the notification includes a rating, the current price, the specified buy and sell prices for that stock, the current price as a percentage of its 52 week high and the percent that the stock price changed today. Each stock is placed in one of five groups - buy, near buy, middle, near sell and sell, based on where its current price is relative to the buy and sell prices. (The user of this program has to supply the buy and sell prices, based on whatever they like.)

The rating is a calculation used to further rank each stock within the group.

        Buy group: percentage of buy price that current price is below buy price. i.e.
                        (buyPrice - currentPrice)/buyPrice

        Near Buy/Middle/Near Sell Groups: percentage of buy/sell range that current price is above the buy price. i.e.
                        (currentPrice - buyPrice)/(sellPrice - buyPrice)

        Sell Group: percentage of sell price that current price is over sell price. i.e.
                        (currentPrice - sellPrice)/sellPrice

Note that these calculations have no particular meaning - they're just a way for me to pseudo-sensibly sort the stocks within each group.

The buy/sell groups should be fairly obvious - stocks that are below their buy prices or above their sell prices. For the rest, stocks within 25% of the bottom of the range between the buy and sell prices are near buy, while those within 25% of the top are near sell - the rest are in the middle. Again, these calculations are completely arbitrary.

A web site has been added, to display all this information, over a selectable period of time, and sortable by various columns. The data is now stored in an AWS RDS/MySQL database, as the project now keeps historical prices for graphing on the web page - daily closing prices for 3 months, weekly for 5 years. The web site is rather slow and aesthetically-challenged, but provides the information that I'm looking for in an easy to understand format (lots of graphs.)

![Screen Shot](images/StockRetrieverScreenshot.jpg?raw=true "Screen")

There are also a few maintenance-type functions that are run locally but access the RDS database. The most common ones are described below, the rest can be listed by running "python spr.py --help"

Note that because of the MySQL database, running this project on AWS now has a cost, unless you qualify for the AWS RDS free tier. It had previously snuck under the free tier limit, at least for me.


## Usage
After successfully following the "Getting Started" instructions below, the program will automatically run at the selected time, every weekday, retrieving and saving the most recent price for each security and the Friday close price for each, and sending an email containing a summary of that data. The email also contains a link to a web page showing more of the data, mostly in chart form, that can be sorted by various columns. You are also able to select the period of time for which you want to view data.

If you want to refresh your list of securities, update the spreadsheet that was created in step 1 below (or, create an entirely new one) and run the "python spr.py -o Portfolio.xls" command again, where Portlolio.xls is the name of your updated spreadsheet. The update process uses the symbol to update values for existing securities, add new ones and remove any that are no longer in the spreadsheet. 

If something like a stock split happens, that invalidates all the existing price history data for a security, you can manually remove the existing data and tell the program to reload it, using the following process:

1. Connect to your database. Run 7-connect-rds.sh. Enter the DbPassword that you put in dbparams.json in step 5 below.

2. Select your database. Run "use stock_retriever_db;", replacing stock_retriever_db with the name of your database.

3. Retrieve the id for the security that you want to update prices for. Run "select * from securities;" and scroll to find the security of interest. (Or, add an appropriate query.)

4. Update the security so that the program knows that it needs to reload its price history. Run "update securities set fullHistoryDownloaded='0' where id=999;", replacing 999 with the security id from step 3.

5. Delete daily price history for this security. Run "delete * from dailyPriceHistory where securityId = 999;", again replacing 999 with the security id from step 3.

6. Delete weekly price history for this security. Run "delete * from weeklyPriceHistory where securityId = 999;", similarly to above.

7. Disconnect - "quit".

Now, when the next automatic daily price update runs, the program will recognize that it doesn't have full data for that security and automatically retrieve and store it.


## Getting Started
I assume that you have an AWS account and the AWS Python libraries and cli installed.
Most of the AWS resources required to run this are created automatically, but names can be changed. Unless you happen to be running the same operating system, on near-identical hardware, as your lambda function will be running under on AWS, it's probably best to perform the following steps in a vm running AWS' latest Python3 Lambda environment.

The various parts of the deployment - i.e. the lambdas, the database and the website - depend on each other. This results in a rather circular installation process, where most of the steps have to be executed in the exact order listed below.
1. Create your stocks spreadsheet. You can start with the provided sample (Portfolio.xls) or from scratch. It has to be in a format that xlrd can read - I stuck with plain old xls. It must have the following fields: Stock, Buy_price, Sell_price, Symbol and Ignore. The program assumes that the data is on a tab named "Current", but you can specify a different tab name in "src/code/settings.json" if desired. As a Canadian, I acknowledge the primacy of American stock markets, so American stocks don't need any prefix - i.e. use AAPL for Apple. Just kidding - the symbols used are those of Yahoo finance, except that Canadian symbols have a "TSX:" prefix rather than a ".TO" suffix. See sample files for examples of US and Canadian symbols. The "Ignore" column should contain either Y or N - even a space will result in the record being ignored.
2. S3 bucket. If you don't like the name "stock-price-retriever" for your bucket, change it in 1-create-bucket.sh. Run 1-create-bucket-sh to create the S3 bucket to use for this lambda.
3. Prepare install libraries. Run 2-build-layer.sh, which will install the libraries required for this application, in the package directory.
4. Configuration. The template.yml contains the Cloudformation template for this project, which has various names and settings that can be changed.

- Time to run. The default is to run the function every weekday at 22:04 UTC, which is 5:04pm or 6:04pm eastern, depending on daylight savings time. My goal was to run it sometime after US markets close. If yours is different, change the Schedule in the "function" resource.

- Timeout. If your list of securities is particularly long (mine contains 87 securities and takes 4-8 minutes to run), the "function" lambda might timeout when retrieving all the prices. If this happens, you can change the Timeout in the function resource from 600 to up to 900 seconds (15 minutes is currently the maximum allowable run time for a Lambda function.)

- SNS topics. This lambda uses two SNS topics, one to send out the daily stock data email and the second to send out any errors executing the lambda. The first is called "StockRetrieverResultsTopic" and the second StockRetrieverErrorsTopic. If you don't like these names, you will have to change them in several places in the template as well as in settings.py.

- Topic subscriber. If you would like to receive emails when the program publishes something to the topics, change the "Endpoint" entries in the template for both topics to the desired email address.
5. Deploy the lambdas and supporting infrastructure. Run 3-deploy.sh
6. Retrieve the identifier for the database instance. Run 3a-get-dbidentifier.sh.
7. Create the database. (The previous step only created an empty database instance. This step creates a database and users with appropriate rights.) Copy the json fragment below, paste it into a file called dbparams.json in the src/code directory. Change the password to one that isn't publicly known. Run 8-create-db-and-user.sh.

        {
        "Parameters": {
                "DbUsername": "stockDbRoot",
                "DbPassword": "mySecurePassword",
                "DbUserSR": "dbUserSR",
                "DbName": "stock_retriever_db"
                }
        }
8. Redeploy the lambdas. Run 3-deploy.sh. This will add the various endpoints/identifiers that have been created to the project, for the python code to use.
9. Create the database tables. From the src/code directory run "python spr.py -d". This will create the tables required for the program.
10. Load your target securities into the database. From the src/code directory, run "python spr.py -o Portfolio.xls", where Portfolio.xls is the name of the spreadsheet that you created in step 3. If you're not comfortable with making your stocks of interest and corresponding buy/sell prices public, I recommend keeping the spreadsheet in the directory above this project. You can then load the securities with something like "python spr.py -o ../mystocks.xls".
11. Prepare for website deployment. Ensure that have npm and the AWS Amplify cli installed.
12. Retrieve the url for the api. Run 9-get-apigateway.sh. Copy the contents of the api_url.txt file that is created into the api_endpoint variable in the web/src/components/FetchData.js file and save it. (Please let me know if you have a way to avoid hardcoding this value.)
13. Deploy the website. From the web directory, run "amplify publish".
14. (Optional) Secure the website. If you don't want everyone to be able to see your securities of interest and associated buy/sell prices, the website should be secured. I used the AWS Amplify console to go to the deployed app, selected settings/access control on the left side and changed the "access setting" from public to restricted, which lets you set a username and password that are required to access the site. (I haven't been able to find a way to do this when publishing or through the cli.)
15. Retrieve the url for the website. Run 9a-get-amplify-url.sh.
16. Redeploy the lambdas. Run 3-deploy.sh. This will include the file containing the url for the website in the lambda project so that it can be included in the daily email.


Development Environment

- Ubuntu
- Virtual Machine Manager and image for AWS' latest Python3 Lambda environment, if want to fully test locally.

Python Requirements

- Python 3
- AWS cli
- boto3
- botocore
- cryptogoraphy
- datetime
- getopt
- idna
- json
- lxml
- matplotlib
- math
- moto
- numpy
- os
- pandas
- pymysql
- pytest
- requests
- socket
- sys
- urllib3
- xlrd
- yahoo-fin

Web Requirements

- AWS Amplify
- Chart.js
- NPM
- React
- React-chartjs


## Authors

* **Greg Walker** - *Initial work* - (https://github.com/gregw18)


## License

MIT
