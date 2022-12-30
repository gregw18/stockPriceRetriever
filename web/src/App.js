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
  periodPrices: [24.7, 26.5, 23.4, 34.3, 32.1, 40.3, 38.6, 35.4, 33.2]
};

const securityMicrosoft= {
  name: "Microsoft",
  currentPrice: 239.04,
  periodStartPrice: 283.11,
  periodHighPrice: 349.67,
  periodLowPrice: 235.2,
  buyPrice: 170.90,
  sellPrice: 274.70,
  periodPrices: [283.11, 349.67, 323.4, 334.3, 232.1, 240.3, 338.6, 235.4, 233.2]
};

const securityLilly= {
  name: "Eli Lilly",
  currentPrice: 307.59,
  periodStartPrice: 224.85,
  periodHighPrice: 331.56,
  periodLowPrice: 224.85,
  buyPrice: 93.10,
  sellPrice: 171.10,
  periodPrices: [224.85, 265.67, 245.4, 277.3, 237.1, 249.3, 289.6, 324.4, 307.72]
};

//const sortContext = createContext(null);

function logSecurities(securityData) {
  securityData.forEach(function (security) {
    console.log(security.data.name);
  })
}

function GenerateTable({securityData, minMaxGain, setChartData, sortByCol}) {
  return (
    <table style={{width: "100%"}}>
      <tbody>
        <tr>
          <th style={{width: "15%"}}>
            <button id="sort_name" type="button" 
              onClick={() => sortByCol('name')}>Name</button>
          </th>
          <th style={{width: "5%"}}>Current</th>
          <th style={{width: "20%"}}>
            <button id="sort_gain" type="button" 
              onClick={() => sortByCol('percentGain')}>Gain</button>
          </th>
          <th style={{width: "20%"}}>Price Range</th>
          <th style={{width: "20%"}}>Buy/Sell Range</th>
          <th style={{width: "20%"}}>Price History</th>
        </tr>
        {generateRows(securityData, minMaxGain)}
      </tbody>
    </table>
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
  chartData.forEach(function (security) {
    let buyLowPrice = security.data.buyPrice;
    if (security.data.currentPrice < buyLowPrice){
      buyLowPrice = security.data.currentPrice;
    }
    security.data.buyLowPrice = buyLowPrice;

    let sellHighPrice = security.data.sellPrice;
    if (security.data.currentPrice > sellHighPrice) {
      sellHighPrice = security.data.currentPrice;
    }
    security.data.sellHighPrice = sellHighPrice;

    security.data.percentGain = 100 * (security.data.currentPrice - security.data.periodStartPrice) / security.data.periodStartPrice;
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

  // Want range to be a multiple of ten.
  minGain = Math.floor(minGain/10) * 10;
  maxGain = Math.ceil(maxGain/10) * 10;

  // If max gain is less than zero, or min gain is greater than zero, want
  // range to include zero.
  minGain = (minGain > 0 ? 0 : minGain);
  maxGain = (maxGain < 0 ? 0 : maxGain);

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
          id: 2,
          data: securityMicrosoft
        }
      );
      mySecurities.push( 
        {
          id: 2,
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

    const fetchPricesHttp = async () => {
      //const requestDataLambda = function() {
        var xhttp = new XMLHttpRequest();
        xhttp.onloadend = function() {
          if (this.readyState ==4 && this.status == 200) {
            console.log("responseText= ", xhttp.responseText);
            console.log("responseHeaders= ", xhttp.getAllResponseHeaders());
            const myjson = JSON.parse(xhttp.responseText);
            let mySecurities = parseJson(myjson);

            setChartData(mySecurities);
            setHaveData(true);
          } else {
            console.log("request failed again.");
          }
        }
        xhttp.open("GET", api_endpoint + "?timeframe=30days", false);
        xhttp.setRequestHeader("mode", "no-cors");
        xhttp.send();
      }


    const fetchPrices = async () => {
      var params = {timeframe: "30days"};
      const urlStr = api_endpoint + "?" + new URLSearchParams(params);
      console.log("urlStr=", urlStr);
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

    //fetchTestPrices();
    //fetchPricesHttp();
    fetchPrices();
  }, []);

  const [chartData, setChartData] = useState({});
  const [haveData, setHaveData] = useState(false);
  const [sortOrder, setSortOrder] = useState(false); // False = ascending, True = descending.
  const [sortColumn, setSortColumn] = useState("");

  function toggleSortOrder() {
    setSortOrder(sortOrder => !sortOrder);
  }

  function sortByCol(colName) {
    console.log("Sort me by name");
    let thisOrder = sortOrder;
    if (sortColumn === colName) {
      console.log("column=", colName);
      thisOrder = !sortOrder;
      setSortOrder(thisOrder);
    }
    else {
      setSortOrder(false);
      setSortColumn(colName);
    }
    console.log("thisOrder=", thisOrder, ", sortColumn=", sortColumn);

    let getVal = function(security) { return security.data[colName].toUpperCase()};
    if (colName ==="percentGain") {
      getVal = function(security) {return security.data[colName]};
    }

    let lt = -1;
    let gt = 1;
    if (thisOrder) {
      lt = 1;
      gt = -1;
    }

    let sortedData = chartData.slice().sort((a, b) => {
      //const nameA = a.data[colName].toUpperCase();
      //const nameB = b.data[colName].toUpperCase();
      const nameA = getVal(a);
      const nameB = getVal(b);
      if (nameA < nameB) {
        return lt;
      }
      if (nameA > nameB) {
        return gt;
      }
      return 0;
    })
    logSecurities(sortedData);
    setChartData(sortedData);
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
          setChartData={setChartData} sortByCol={sortByCol} />
      {/* </sortContext.Provider> */}
      </>
      );
  }
}