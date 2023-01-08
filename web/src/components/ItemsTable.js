import React, {useEffect, useState} from "react";
import {Chart, GainChart, TimeRangeChart, BuySellChart, PriceHistoryChart} from "./Chart";
//import './App.css';
import { getFakeData } from "./FakeData";

const api_endpoint = "https://n7zmmbsqxc.execute-api.us-east-1.amazonaws.com/Prod/data";


export function logSecurities(securityData) {
  securityData.forEach(function (security) {
    console.log(security.data.name);
  })
}


//function retrieveData(newTimePeriod, haveData, setTimePeriod, setChartData, setHaveData) {
//  console.log("retrieveData, newTimePeriod=", newTimePeriod);
//  setTimePeriod(newTimePeriod);
  //fetchTestPrices(newTimePeriod, setChartData, setHaveData);
  //fetchPricesHttp();
//  fetchPrices(newTimePeriod, haveData, setChartData, setHaveData);
//}

export class ItemsTable extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoaded: false,
      securityData: [],
      timePeriod: "3months",
      sortCol: "name",
      sortAscending: true
    }
  }

  parseJson(srcData) {
    let mySecurities = [];
    let i = 1;
    for (const security of srcData) {
      mySecurities.push( {
        id: i,
        data:security
      });
      i++;
    };
    this.addCalculatedData(mySecurities);

    this.setState( {
      isLoaded: true,
      securityData: mySecurities
    });
  }

  componentDidMount() {
    this.fetchPrices();
  }

  async fetchPrices () {
    const startTime = performance.now();
    let myTimePeriod = this.state.timePeriod;
    var params = {timeframe: myTimePeriod};
    const urlStr = api_endpoint + "?" + new URLSearchParams(params);
    console.log(new Date().toTimeString(), "fetchPrices, urlStr=", urlStr);
    var url = new URL(urlStr);
  
    const fetchPromise = fetch(url);
    fetchPromise.then((response) => {
      console.log("1. status=", response.status);
      if (response.ok) {
        const jsonPromise = response.json();
        console.log("2.", new Date().toTimeString(), ", jsonPromise=", jsonPromise);
        jsonPromise.then((data) => {
          console.log("3.", new Date().toTimeString(), ", fetchPrices, data=", data);
          this.parseJson(data);
  
          //addCalculatedData(mySecurities, timePeriod);
          //setChartData(mySecurities);
          //setHaveData(true);
          console.log(new Date().toTimeString(), "fetchPrices took ", performance.now() - startTime, " ms.");
        });
      } else {
        console.log("request failed again.");
      }
    })
    .catch((error) => {
      console.log("fetchPrices failed, error=", error);
    });
  }

  // Add buy low and sell high points to data, along with percent gain.
  // For both, if current not outside buy/sell range, are equal to buy/sell,
  // otherwise, are equal to current.
  addCalculatedData(origData) {
    const t2 = performance.now();
    console.log("running addCalculatedData");
    const myTimePeriod = this.state.timePeriod;
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
      if (myTimePeriod === "1day") {
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

  render() {
      const t5 = performance.now();
      var myHtml = "";
      if (this.state.isLoaded) {
        //let mySecurityData = this.state.securityData;
        myHtml = (
        <div>
          {this.generateTimePeriodButtons()}
          <table style={{width: "100%"}}>
            <tbody>
              <tr>
                <th style={{width: "10%"}}>
                  <button id="sort_name" type="button" 
                    onClick={() => this.handleSortByCol('name')}>Name</button>
                </th>
                <th style={{width: "5%"}}>
                  <button id="sort_group" type="button"
                  onClick={() => this.handleSortByCol('group')}>Group</button>
                </th>
                <th style={{width: "5%"}}>
                  <button id="sort_rating" type="button"
                  onClick={() => this.handleSortByCol('rating')}>Rating</button>
                </th>
                <th style={{width: "5%"}}>Last Close</th>
                <th style={{width: "15%"}}>
                  <button id="sort_gain" type="button" 
                    onClick={() => this.handleSortByCol('percentGain')}>Gain</button>
                </th>
                <th style={{width: "15%"}}>Price Range</th>
                <th style={{width: "15%"}}>Buy/Sell Range</th>
                <th style={{width: "30%"}}>Price History</th>
              </tr>
              {this.generateRows(this.state.securityData)}
            </tbody>
          </table>
        </div>
      );
    }
    console.log(new Date().toTimeString(), "GenerateTable took ", performance.now() - t5, " ms.");
    return myHtml;
  }

  generateRows(mySecurityData) {
    console.log("generateRows, data=", mySecurityData);
    let myMinMaxGain = getMinMaxGain(mySecurityData);
    return (
      <>
        {mySecurityData.map(
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

  generateTimePeriodButtons() {
    let myTimePeriod = this.state.timePeriod;
    console.log("GenerateTimePeriodButtons, timePeriod=", myTimePeriod);
    return (
    <div>
    <input type="radio" value="1day" checked={myTimePeriod==="1day"}
    onChange={(e) => this.handleChangeTimePeriod(e.target.value)}
    name="timePeriods" /> 1 Day
    <input type="radio" value="30days" checked={myTimePeriod==="30days"}
    onChange={(e) => this.handleChangeTimePeriod(e.target.value)}
    name="timePeriods" /> 1 Month
    <input type="radio" value="3months" checked={myTimePeriod==="3months"} 
    onChange={(e) => this.handleChangeTimePeriod(e.target.value)}
    name="timePeriods" /> 3 Months
    <input type="radio" value="1year" checked={myTimePeriod==="1year"} 
    onChange={(e) => this.handleChangeTimePeriod(e.target.value)}
    name="timePeriods" /> 1 Year
    <input type="radio" value="3years" checked={myTimePeriod==="3years"} 
    onChange={(e) => this.handleChangeTimePeriod(e.target.value)}
    name="timePeriods" /> 3 Years
    <input type="radio" value="5years" checked={myTimePeriod==="5years"} 
    onChange={(e) => this.handleChangeTimePeriod(e.target.value)}
    name="timePeriods" /> 5 Years
    </div>
    );
  }

  handleChangeTimePeriod = (newPeriod, e) => {
    console.log("Changing time period to ", newPeriod);
    this.setState( {
      timePeriod: newPeriod
    });
    this.fetchPrices();
  }

  //toggleSortOrder() {
  //  setSortOrder(sortOrder => !sortOrder);
  //}

  handleSortByCol(colName) {
    const t1 = performance.now();
    console.log("Resorting");
    let sortAscending = this.state.sortAscending;
    if (this.state.sortCol === colName) {
      // If we're already sorted on the same column, just reverse the order
      //console.log("column=", colName);
      sortAscending = !sortAscending;
      //setSortOrder(thisOrder);
    }
    else {
      // If we're changing the sort column, default to the standard order for that column.
      sortAscending = false;
      //setSortColumn(colName);
    }
    //this.setState({
    //  sortAscending: sortAscending,
    //  sortCol: colName
    //})
    console.log("sortAcending=", sortAscending, ", colName=", colName);

    let getVal = function(security) { return security.data[colName].toUpperCase()};
    if (colName ==="percentGain" || colName ==="rating") {
      getVal = function(security) {return security.data[colName]};
    }
    let lt = -1;
    let gt = 1;
    if (sortAscending) {
      lt = 1;
      gt = -1;
    }

    let chartData = this.state.securityData;
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
    this.setState({
      securityData: chartData,
      sortAscending: sortAscending,
      sortCol: colName
    })
    console.log("sortByCol took ", performance.now() - t1, " ms.");
  }

}



// Get lowest and highest percent gains from given set of securities.
function getMinMaxGain(myChartData) {
  const t3 = performance.now();
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
  console.log(new Date().toTimeString(), "getMinMaxGain took ", performance.now() - t3, " ms.");
  return {minGain: minGain, maxGain: maxGain};
}

/*
const fetchTestPrices = async (timePeriod, setChartData, setHaveData) => {
  console.log("fetchTestPrices, timePeriod=", timePeriod)
  let mySecurities = getFakeData();
  addCalculatedData(mySecurities, timePeriod);
  setChartData(mySecurities);
  setHaveData(true);
}
*/
