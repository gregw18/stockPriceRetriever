import {useEffect, useState} from "react";
import {Chart, GainChart, TimeRangeChart, BuySellChart, PriceHistoryChart} from "../src/components/Chart";
import './App.css';
import { getFakeData } from "./FakeData";

const api_endpoint = "https://n7zmmbsqxc.execute-api.us-east-1.amazonaws.com/Prod/data";
//const api_endpoint = "https://jep1avv9ui.execute-api.us-east-1.amazonaws.com/Prod/data";
//const api_endpoint = "https://jep1a9ui.execute-api.us-east-1.amazonaws.com/Prod/data";


function logSecurities(securityData) {
  securityData.forEach(function (security) {
    console.log(security.data.name);
  })
}

function GenerateTimePeriodButtons(timePeriod, setTimePeriod, setChartData, setHaveData) {
  console.log("GenerateTimePeriodButtons, timePeriod=", timePeriod);
  return (
    <div>
      <input type="radio" value="1day" checked={timePeriod==="1day"}
        onChange={(e) => retrieveData(e.target.value, setTimePeriod, setChartData, setHaveData)}
        name="timePeriods" /> 1 Day
      <input type="radio" value="30days" checked={timePeriod==="30days"}
        onChange={(e) => retrieveData(e.target.value, setTimePeriod, setChartData, setHaveData)}
        name="timePeriods" /> 1 Month
      <input type="radio" value="3months" checked={timePeriod==="3months"} 
        onChange={(e) => retrieveData(e.target.value, setTimePeriod, setChartData, setHaveData)}
        name="timePeriods" /> 3 Months
      <input type="radio" value="1year" checked={timePeriod==="1year"} 
        onChange={(e) => retrieveData(e.target.value, setTimePeriod, setChartData, setHaveData)}
        name="timePeriods" /> 1 Year
      <input type="radio" value="3years" checked={timePeriod==="3years"} 
        onChange={(e) => retrieveData(e.target.value, setTimePeriod, setChartData, setHaveData)}
        name="timePeriods" /> 3 Years
      <input type="radio" value="5years" checked={timePeriod==="5years"} 
        onChange={(e) => retrieveData(e.target.value, setTimePeriod, setChartData, setHaveData)}
        name="timePeriods" /> 5 Years
    </div>
  );
}

function retrieveData(newTimePeriod, setTimePeriod, setChartData, setHaveData) {
  console.log("retrieveData, newTimePeriod=", newTimePeriod);
  setTimePeriod(newTimePeriod);
  fetchTestPrices(newTimePeriod, setChartData, setHaveData);
  //fetchPricesHttp();
  //fetchPrices(newTimePeriod, setChartData, setHaveData);
}

function GenerateTable({securityData, setChartData, setHaveData, 
                        sortByCol, timePeriod, setTimePeriod}) {
  return (
    <div>
      {GenerateTimePeriodButtons(timePeriod, setTimePeriod, setChartData, setHaveData)}
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
          {generateRows(securityData)}
        </tbody>
      </table>
    </div>
  );
}

function generateRows(securityData) {
  console.log(securityData);
  let myMinMaxGain = getMinMaxGain(securityData);
  return (
    <>
      {securityData.map(
        d => (
          <tr>
            <td>{d.data.name}</td>
            <td>{d.data.group}</td>
            <td>{d.data.rating}</td>
            <td>{d.data.currentPrice}</td>
            <td><GainChart chartData={d.data} minMax={myMinMaxGain} /></td>
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
function addCalculatedData(origData, timePeriod) {
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
}

// Get lowest and highest percent gains from given set of securities.
function getMinMaxGain(myChartData) {
  let minGain = 9999;
  let maxGain = -9999;
  myChartData.forEach(function (security) {
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

const fetchTestPrices = async (timePeriod, setChartData, setHaveData) => {
  console.log("fetchTestPrices, timePeriod=", timePeriod)
  let mySecurities = getFakeData();
  addCalculatedData(mySecurities, timePeriod);
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

const fetchPrices = async (timePeriod, setChartData, setHaveData) => {
  var params = {timeframe: timePeriod};
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

        addCalculatedData(mySecurities, timePeriod);
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

export default function App() {
  useEffect(() => {

    fetchTestPrices(timePeriod, setChartData, setHaveData);
    //fetchPricesHttp();
    //fetchPrices(timePeriod, setChartData, setHaveData);
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
    return (
      <>
        <GenerateTable securityData={chartData}
          setChartData={setChartData} sortByCol={sortByCol} timePeriod={timePeriod} setTimePeriod={setTimePeriod} setHaveData={setHaveData} />
      </>
      );
  }
}