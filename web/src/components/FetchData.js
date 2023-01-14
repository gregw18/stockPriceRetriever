import { getFakeData } from "./FakeData";

const api_endpoint = "https://n7zmmbsqxc.execute-api.us-east-1.amazonaws.com/Prod/data";

export function fetchPrices (timePeriod) {
  //return fetchFakeData(timePeriod);
  return fetchPricesHttp(timePeriod);
}

function fetchFakeData(timePeriod) {
  let newData = getFakeData();
  return parseJson(newData, timePeriod);
}

async function fetchPricesHttp (timePeriod) {
  const startTime = performance.now();
  let mySecurities = [];
  var params = {timeframe: timePeriod};
  const urlStr = api_endpoint + "?" + new URLSearchParams(params);
  console.log(new Date().toTimeString(), "fetchPrices, urlStr=", urlStr);
  var url = new URL(urlStr);

  //const fetchPromise = fetch(url);
  const response = await fetch(url);
  //fetchPromise.then((response) => {
    console.log("1. status=", response.status);
    if (response.ok) {
      //const jsonPromise = response.json();
      const data = await response.json();
      //console.log("2.", new Date().toTimeString(), ", jsonPromise=", jsonPromise);
      //jsonPromise.then((data) => {
        console.log("3.", new Date().toTimeString(), ", fetchPrices, data=", data);
        mySecurities = parseJson(data, timePeriod);

        console.log(new Date().toTimeString(), "fetchPrices took ", performance.now() - startTime, " ms.");
      //});
    } else {
      console.log("request failed again.");
    }
  //})
  //.catch((error) => {
  //  console.log("fetchPrices failed, error=", error);
  //});

  return mySecurities;
}

function parseJson(srcData, timePeriod) {
    let mySecurities = [];
    let i = 1;
    for (const security of srcData) {
        mySecurities.push( {
            id: i,
            data:security
        });
        i++;
    };
    addCalculatedData(mySecurities, timePeriod);
    console.log("Finished parseJson");

    //this.setState( {
    //    isLoaded: true,
    //    securityData: mySecurities
    //});
    return mySecurities;
}

  // Add buy low and sell high points to data, along with percent gain.
  // For both, if current not outside buy/sell range, are equal to buy/sell,
  // otherwise, are equal to current.
function addCalculatedData(origData, timePeriod) {
    const t2 = performance.now();
    console.log("running addCalculatedData");
    origData.forEach(function (security) {
        let buyLowPrice = security.data.buyPrice;
        if (security.data.currentPrice < buyLowPrice){
            buyLowPrice = security.data.currentPrice;
            //console.log("using current for buyLow, ", security.data.currentPrice, ", buyPrice=", security.data.buyPrice);
        }
        security.data.buyLowPrice = buyLowPrice;

        let sellHighPrice = security.data.sellPrice;
        if (security.data.currentPrice > sellHighPrice) {
            sellHighPrice = security.data.currentPrice;
        }
        security.data.sellHighPrice = sellHighPrice;

        let prevPrice = security.data.periodStartPrice;
        if (timePeriod === "1day") {
            // Don't get historical prices if ask for just one day, so use previous close price.
            prevPrice = security.data.lastClosePrice;
        }
        if (prevPrice > 0) {
            security.data.percentGain = 100 * (security.data.currentPrice - prevPrice) / prevPrice;
        }
        else {
            // Shouldn't have many with a price of zero, but if do, above formula gives Nan as gain,
            // which prevents the item from being sorted on gain, messing up entire sort order.
            security.data.percentGain = 0;
        }
    })
    console.log("addCalculatedData took ", performance.now() - t2, " ms.");
}
