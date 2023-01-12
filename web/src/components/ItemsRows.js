import React from "react";
import {GainChart, TimeRangeChart, BuySellChart, PriceHistoryChart} from "./Chart";

export class ItemsRows extends React.Component {
    constructor(props) {
        super(props);
    }
  
    render() {
        let mySecurityData = this.props.securityData;
        console.log("ItemsRows.render, data=", mySecurityData);
        let myMinMaxGain = this.getMinMaxGain(mySecurityData);
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

    // Get lowest and highest percent gains from given set of securities.
    getMinMaxGain(myChartData) {
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
        //console.log("ran getMinMaxGain, returning: ", minGain, ", ", maxGain)
        console.log(new Date().toTimeString(), "getMinMaxGain took ", performance.now() - t3, " ms.");
        return {minGain: minGain, maxGain: maxGain};
    }
  
}
