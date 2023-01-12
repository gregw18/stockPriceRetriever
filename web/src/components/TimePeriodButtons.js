import React from "react";

export class TimePeriodButtons extends React.Component {
    constructor(props) {
      super(props);
      this.handleChangeTimePeriod = this.handleChangeTimePeriod.bind(this);
    }
  
    render() {
      let myTimePeriod = this.props.timePeriod;
      console.log("generateTimePeriodButtons, timePeriod=", myTimePeriod);
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
      console.log("TimePeriodButtons.handleChangeTimePeriod, changing time period to ", newPeriod);
      this.props.onPeriodChange(newPeriod);
    }
  }
  