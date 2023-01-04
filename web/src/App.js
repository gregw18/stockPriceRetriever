import {useEffect, useState} from "react";
import {Chart, GainChart, TimeRangeChart, BuySellChart, PriceHistoryChart} from "../src/components/Chart";
import './App.css';


const api_endpoint = "https://n7zmmbsqxc.execute-api.us-east-1.amazonaws.com/Prod/data";
//const api_endpoint = "https://jep1avv9ui.execute-api.us-east-1.amazonaws.com/Prod/data";
//const api_endpoint = "https://jep1a9ui.execute-api.us-east-1.amazonaws.com/Prod/data";

const securityAmazon= {
  name: "Amazon",
  currentPrice: 114.35,
  periodStartPrice: 165.06,
  periodHighPrice: 188.11,
  periodLowPrice: 113.23,
  buyPrice: 115.8,
  sellPrice: 150.3,
  group: "2.near buy",
  rating: 5.43,
  periodPrices: [24.7, 26.5, 23.4, 34.3, 32.1, 40.3, 38.6, 35.4, 33.2],
  periodDates: ["2022-12-05", "2022-12-06", "2022-12-07", "2022-12-08", "2022-12-09",
           "2022-12-12", "2022-12-13", "2022-12-14", "2022-12-15" ]
};

const securityMicrosoft= {
  name: "Microsoft",
  currentPrice: 239.04,
  periodStartPrice: 283.11,
  periodHighPrice: 349.67,
  periodLowPrice: 235.2,
  buyPrice: 170.90,
  sellPrice: 274.70,
  group: "3.middle",
  rating: 54.32,
  periodPrices: [283.11, 349.67, 323.4, 334.3, 232.1, 240.3, 338.6, 235.4, 233.2],
  periodDates: ["2022-12-05", "2022-12-06", "2022-12-07", "2022-12-08", "2022-12-09",
           "2022-12-12", "2022-12-13", "2022-12-14", "2022-12-15" ]
};

const securityLilly= {
  name: "Eli Lilly",
  currentPrice: 307.59,
  periodStartPrice: 224.85,
  periodHighPrice: 331.56,
  periodLowPrice: 224.85,
  buyPrice: 93.10,
  sellPrice: 171.10,
  group: "5.sell",
  rating: 80.54,
  periodPrices: [224.85, 265.67, 245.4, 277.3, 237.1, 249.3, 289.6, 324.4, 307.72],
  periodDates: ["2022-12-05", "2022-12-06", "2022-12-07", "2022-12-08", "2022-12-09",
           "2022-12-12", "2022-12-13", "2022-12-14", "2022-12-15" ]
};

const securityZero= {
  name: "FTX",
  currentPrice: 0.0,
  periodStartPrice: 0,
  periodHighPrice: 0,
  periodLowPrice: 0,
  buyPrice: 93.10,
  sellPrice: 171.10,
  group: "1.buy",
  rating: -100,
  periodPrices: [0],
  periodDates: ["2022-12-05"]
};

//const sortContext = createContext(null);

function logSecurities(securityData) {
  securityData.forEach(function (security) {
    console.log(security.data.name);
  })
}

function GenerateTimePeriodButtons(timePeriod, setTimePeriod) {
  console.log("GenerateTimePeriodButtons, timePeriod=", timePeriod);
  return (
    <div>
      <input type="radio" value="1day" checked={timePeriod==="1day"}
        onChange={(e) => setTimePeriod(e.target.value)}
        name="timePeriods" /> 1 Day
      <input type="radio" value="30days" checked={timePeriod==="30days"}
        onChange={(e) => setTimePeriod(e.target.value)}
        name="timePeriods" /> 1 Month
      <input type="radio" value="3months" checked={timePeriod==="3months"} 
        onChange={(e) => setTimePeriod(e.target.value)}
        name="timePeriods" /> 3 Months
      <input type="radio" value="1year" checked={timePeriod==="1year"} 
        onChange={(e) => setTimePeriod(e.target.value)}
        name="timePeriods" /> 1 Year
      <input type="radio" value="3years" checked={timePeriod==="3years"} 
        onChange={(e) => setTimePeriod(e.target.value)}
        name="timePeriods" /> 3 Years
      <input type="radio" value="5years" checked={timePeriod==="5years"} 
        onChange={(e) => setTimePeriod(e.target.value)}
        name="timePeriods" /> 5 Years
    </div>
  );
}

//function retrieveData(newTimePeriod) {
//  console.log("retrieveData, newTimePeriod=", newTimePeriod);
//  setTimePeriod(newTimePeriod);
//}

function GenerateTable({securityData, minMaxGain,  setChartData, 
                        sortByCol, timePeriod, setTimePeriod}) {
  return (
    <div>
      {GenerateTimePeriodButtons(timePeriod, setTimePeriod)}
      <table style={{width: "100%"}}>
        <tbody>
          <tr>
            <th style={{width: "15%"}}>
              <button id="sort_name" type="button" 
                onClick={() => sortByCol('name')}>Name</button>
            </th>
            <th style={{width: "5%"}}>
              <button id="sort_group" type="button"
              onClick={() => sortByCol('group')}>Group</button>
            </th>
            <th style={{width: "5%"}}>
              <button id="sort_rating" type="button"
              onClick={() => sortByCol('rating')}>Rating</button>
            </th>
            <th style={{width: "5%"}}>Current</th>
            <th style={{width: "15%"}}>
              <button id="sort_gain" type="button" 
                onClick={() => sortByCol('percentGain')}>Gain</button>
            </th>
            <th style={{width: "15%"}}>Price Range</th>
            <th style={{width: "15%"}}>Buy/Sell Range</th>
            <th style={{width: "25%"}}>Price History</th>
          </tr>
          {generateRows(securityData, minMaxGain)}
        </tbody>
      </table>
    </div>
  );
}

function generateRows(securityData, minMaxGain) {
  console.log(securityData);
  return (
    <>
      {securityData.map(
        d => (
          <tr>
            <td>{d.data.name}</td>
            <td>{d.data.group}</td>
            <td>{d.data.rating}</td>
            <td>{d.data.currentPrice}</td>
            <td><GainChart chartData={d.data} minMax={minMaxGain} /></td>
            <td><TimeRangeChart chartData={d.data} /></td>
            <td><BuySellChart chartData={d.data} /></td>
            <td><PriceHistoryChart chartData={d.data} /></td>
          </tr>
          )
      )}
    </>
  );
}

// Add buy low and sell high points to data, along with percent gain.
// For both, if current not outside buy/sell range, are equal to buy/sell,
// otherwise, are equal to current.
function addCalculatedData(chartData) {
  console.log("running addCalculatedData");
  chartData.forEach(function (security) {
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

    if (security.data.periodStartPrice > 0) {
      security.data.percentGain = 100 * (security.data.currentPrice - security.data.periodStartPrice) / security.data.periodStartPrice;
    }
    else {
      // Shouldn't have many with a price of zero, but if do, above formula gives Nan as gain,
      // which prevents the item from being sorted on gain, messing up entire sort order.
      security.data.percentGain = 0;
    }
  })
}

// Get lowest and highest percent gains from given set of securities.
function getMinMaxGain(chartData) {
  let minGain = 9999;
  let maxGain = -9999;
  chartData.forEach(function (security) {
    if (security.data.percentGain < minGain ) {
      minGain = security.data.percentGain;
    }
    if (security.data.percentGain > maxGain) {
      maxGain = security.data.percentGain;
    }
  });

  // Want range (gain resolution) to be a multiple of five.
  let gainres = 5;
  minGain = Math.floor(minGain/gainres) * gainres;
  maxGain = Math.ceil(maxGain/gainres) * gainres;

  // If max gain is less than zero, or min gain is greater than zero, want
  // range to include zero.
  minGain = (minGain > 0 ? 0 : minGain);
  maxGain = (maxGain < 0 ? 0 : maxGain);
  console.log("ran getMinMaxGain, returning: ", minGain, ", ", maxGain)
  return {minGain: minGain, maxGain: maxGain};
}

export default function App() {
  useEffect(() => {
    
    const fetchTestPrices = async () => {
      let mySecurities = [];
      mySecurities.push( 
        {
          id: 1,
          data: securityAmazon
        }
      );
      mySecurities.push( 
        {
          id: 4,
          data: securityZero
        }
      );
      mySecurities.push( 
        {
          id: 2,
          data: securityMicrosoft
        }
      );
      mySecurities.push( 
        {
          id: 3,
          data: securityLilly
        }
      );
      setChartData(mySecurities);
      setHaveData(true);
    }

    const parseJson = function (srcData) {
            let mySecurities = [];
            let i = 1;
            for (const security of srcData) {
              mySecurities.push( {
                id: i,
                data:security
              });
              i++;
            }
            return mySecurities;
      }

    //const fetchPricesHttp = async () => {
      //const requestDataLambda = function() {
    //    var xhttp = new XMLHttpRequest();
    //    xhttp.onloadend = function() {
    //      if (this.readyState ==4 && this.status == 200) {
    //        console.log("responseText= ", xhttp.responseText);
    //        console.log("responseHeaders= ", xhttp.getAllResponseHeaders());
    //        const myjson = JSON.parse(xhttp.responseText);
    //        let mySecurities = parseJson(myjson);

    //        setChartData(mySecurities);
    //        setHaveData(true);
    //      } else {
    //        console.log("request failed again.");
    //      }
    //    }
    //    xhttp.open("GET", api_endpoint + "?timeframe=30days", false);
    //    xhttp.setRequestHeader("mode", "no-cors");
    //    xhttp.send();
    //  }


    const fetchPrices = async () => {
      var params = {timeframe: "30days"};
      const urlStr = api_endpoint + "?" + new URLSearchParams(params);
      console.log("fetchPrices, urlStr=", urlStr);
      var url = new URL(urlStr);

      const fetchPromise = fetch(url);
      //console.log("1. promise=", fetchPromise);
      fetchPromise.then((response) => {
        //console.log("2. promise=", fetchPromise);
        console.log("1. status=", response.status);
        if (response.ok) {
          const jsonPromise = response.json();
          console.log("1. jsonPromise=", jsonPromise);
          jsonPromise.then((data) => {
            console.log("data=", data);
            let mySecurities = parseJson(data);

            setChartData(mySecurities);
            setHaveData(true);
          });
        } else {
          console.log("request failed again.");
        }
      })
      .catch((error) => {
        console.log("fetchPrices failed, error=", error);
      });
    }

    fetchTestPrices();
    //fetchPricesHttp();
    //fetchPrices();
  }, []);

  const [chartData, setChartData] = useState({});
  const [haveData, setHaveData] = useState(false);
  const [sortOrder, setSortOrder] = useState(false); // False = ascending, True = descending.
  const [sortColumn, setSortColumn] = useState("");
  const [timePeriod, setTimePeriod] = useState("3months");

  function toggleSortOrder() {
    setSortOrder(sortOrder => !sortOrder);
  }

  function sortByCol(colName) {
    console.log("Resorting");
    let thisOrder = sortOrder;
    if (sortColumn === colName) {
      // If we're already sorted on the same column, just reverse the order
      console.log("column=", colName);
      thisOrder = !sortOrder;
      setSortOrder(thisOrder);
    }
    else {
      // If we're changing the sort column, default to the standard order for that column.
      setSortOrder(false);
      setSortColumn(colName);
    }
    console.log("thisOrder=", thisOrder, ", sortColumn=", sortColumn);

    let getVal = function(security) { return security.data[colName].toUpperCase()};
    if (colName ==="percentGain" || colName ==="rating") {
      getVal = function(security) {return security.data[colName]};
    }

    let lt = -1;
    let gt = 1;
    if (thisOrder) {
      lt = 1;
      gt = -1;
    }

    chartData.sort((a ,b) => {
      let sortResult = 0;
      const valA = getVal(a);
      const valB = getVal(b);
      if (valA < valB) {
        sortResult = lt;
      }
      if (valA > valB) {
        sortResult = gt;
      }
      return sortResult;
    })
    logSecurities(chartData);
    setChartData(chartData);
  }

  if (!haveData) {
    return <div> Loading...</div>
  }
  else {
    addCalculatedData(chartData);
    const minMaxGain = getMinMaxGain(chartData);
    return (
      <>
      {/* <sortContext.Provider
        value={{sortOrder, sortColumn, toggleSortOrder, setSortColumn}}
    > */}
        <GenerateTable securityData={chartData} minMaxGain={minMaxGain} 
          setChartData={setChartData} sortByCol={sortByCol} timePeriod={timePeriod} setTimePeriod={setTimePeriod} />
      {/* </sortContext.Provider> */}
      </>
      );
  }
}