import React from "react";
import { fetchPrices } from "./FetchData";
import { ItemsRows } from "./ItemsRows";
import { TimePeriodButtons } from "./TimePeriodButtons";

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
    console.log(new Date().toTimeString(), "componentDidMount calling fetchData.");
    this.fetchData(this.state.timePeriod);
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
    )};
    console.log(new Date().toTimeString(), "ItemsTable.render complete, took ", performance.now() - t5, " ms.");
    return myHtml;
  }

  fetchData(timePeriod) {
    const promise = fetchPrices(timePeriod);
    console.log(new Date().toTimeString(), "fetchData, promise=", promise);
    promise.then((mySecurities) => {
      console.log(new Date().toTimeString(), "SaveSecurities running.");
      this.setState( {
        isLoaded: true,
        securityData: mySecurities
      });
    });
  }

  handleChangeTimePeriod(newPeriod) {
    console.log("handleChangeTimePeriod, changing time period to ", newPeriod);
    this.setState( {
      timePeriod: newPeriod
    });
    console.log("handleChangeTimePeriod calling fetchData, state.timePeriod=", this.state.timePeriod);
    this.fetchData(newPeriod);
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
