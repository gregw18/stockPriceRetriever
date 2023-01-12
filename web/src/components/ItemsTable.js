import React, {useEffect, useState} from "react";
//import './App.css';
import { getFakeData } from "./FakeData";
import { ItemsRows } from "./ItemsRows";
import { TimePeriodButtons } from "./TimePeriodButtons";

const api_endpoint = "https://n7zmmbsqxc.execute-api.us-east-1.amazonaws.com/Prod/data";

export class ItemsTable extends React.Component {
  constructor(props) {
    super(props);
    this.handleChangeTimePeriod = this.handleChangeTimePeriod.bind(this);
    this.state = {
      isLoaded: false,
      securityData: [],
      timePeriod: "3months",
      sortCol: "name",
      sortAscending: true
    }
  }

  componentDidMount() {
    console.log(new Date().toTimeString(), "componentDidMount calling fetchPrices.");
    this.fetchPrices(this.state.timePeriod);
  }

  render() {
    const t5 = performance.now();
    console.log(new Date().toTimeString(), "ItemsTable.render starting.");
    var myHtml = "";
    if (this.state.isLoaded) {
      myHtml = (
      <div>
        <div>
          <TimePeriodButtons 
            timePeriod={this.state.timePeriod}
            onPeriodChange={this.handleChangeTimePeriod} />
        </div>
        <table style={{width: "100%"}}>
          <thead>
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
          </thead>
          <tbody>
            <ItemsRows
              securityData={this.state.securityData} />
          </tbody>
        </table>
      </div>
    );
  }
  console.log(new Date().toTimeString(), "ItemsTable.render complete, took ", performance.now() - t5, " ms.");
  return myHtml;
}

fetchPrices (timePeriod) {
  //this.fetchFakeData(timePeriod);
  this.fetchPricesHttp(timePeriod);
}

fetchFakeData(timePeriod) {
  let newData = getFakeData();
  this.parseJson(newData);
}

async fetchPricesHttp (timePeriod) {
  const startTime = performance.now();
  let myTimePeriod = timePeriod;
  console.log("fetchPrices, state.timePeriod=", this.state.timePeriod);
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
    console.log("Finished parseJson");
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

  handleChangeTimePeriod(newPeriod) {
    console.log("handleChangeTimePeriod, changing time period to ", newPeriod);
    this.setState( {
      timePeriod: newPeriod
    });
    console.log("handleChangeTimePeriod calling fetchPrices, state.timePeriod=", this.state.timePeriod);
    this.fetchPrices(newPeriod);
  }

  handleSortByCol(colName) {
    const t1 = performance.now();
    console.log("Resorting");
    let sortAscending = this.state.sortAscending;
    if (this.state.sortCol === colName) {
      // If we're already sorted on the same column, just reverse the order
      sortAscending = !sortAscending;
    }
    else {
      // If we're changing the sort column, default to the standard order for that column.
      sortAscending = false;
    }
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
    logSecurityNames(chartData);
    this.setState({
      securityData: chartData,
      sortAscending: sortAscending,
      sortCol: colName
    })
    console.log("sortByCol took ", performance.now() - t1, " ms.");
  }
}

function logSecurityNames(securityData) {
  securityData.forEach(function (security) {
    console.log(security.data.name);
  })
}
