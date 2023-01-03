import { Chart as ChartJS } from "chart.js/auto"
import { Bar, Line } from "react-chartjs-2";
import "./Chart.css";

export const Chart = ({chartData}) => {
    console.log(chartData);
    return (
        <div className="chartCard">
            <div className="dataText">
                {chartData.name}
                {chartData.currentPrice}
            </div>
            <div className="chartBox">
                {GainChart(chartData)}
            </div>

            <div className="chartBox">
                {TimeRangeChart(chartData)}
            </div>
            <div className="chartBox">
                {BuySellChart(chartData)}
            </div>
            <div className="chartBox">
                {PriceHistoryChart(chartData)}
            </div>
        </div>
);
};

const addCurrentPriceLine = {
    id: 'addCurrentPriceLine',
    afterDatasetDraw(chart, args, options) {
        const {ctx, chartArea: {top, bottom, left, right, width, height},
            scales: {x, y}} = chart;
        ctx.save();
        
        let lineExtension = 3;

        function drawLine(xValue) {
          let yStart = y.getPixelForValue(0) + (args.meta.data[0].height/2 + lineExtension);
          let yEnd = y.getPixelForValue(0) - (args.meta.data[0].height/2 + lineExtension);
          ctx.strokeStyle = 'black';
          ctx.lineWidth=3;
          ctx.beginPath();
          ctx.moveTo(x.getPixelForValue(xValue), yStart);
          ctx.lineTo(x.getPixelForValue(xValue), yEnd);
          ctx.stroke();
          ctx.closePath();
          ctx.restore();
        }
        
        drawLine(options.xValue);
    }
}

const defltAxisOptions = {
    ticks: {
        display: true,
        font: {
            size: 10,
            padding: 0
        }
    }
};
const scales = {
    grid: {
        tickLength: 0,
        display: false
    },
    x: defltAxisOptions,
    y: {
        display: false
    }
};

const defltBarOptions = {
    aspectRatio: 3.5,
    indexAxis: 'y',
    scales: scales,
    plugins: {
        title: {
            display:false
        },
        legend: {
            display: false
        }
    }
};

export const GainChart = ( {chartData, minMax} ) => {
    //const percentGain = 100 * (chartData.currentPrice - chartData.periodStartPrice) / chartData.periodStartPrice;
    var barColor = "green";
    if (chartData.percentGain < 0) { barColor = "red"};

    let myOptions = JSON.parse(JSON.stringify(defltBarOptions));
    myOptions.scales.x.min = minMax.minGain;
    myOptions.scales.x.max = minMax.maxGain;

    const chartDataSet = {
        labels: ["1"],
        datasets: [
            {
                data: [ chartData.percentGain ],
                backgroundColor: [barColor]
            }
        ]
    }
    return (
        <Bar 
        data={chartDataSet}
        options={myOptions}
        />
    );
};

export const TimeRangeChart = ( {chartData} ) => {
    // Does a deep copy of the defltBarOptions object, so can modify independently.
    let myOptions = JSON.parse(JSON.stringify(defltBarOptions));

    const chartDataSet = {
        labels: ["1"],
        datasets: [
            {
                data: [ [ chartData.periodLowPrice, chartData.periodHighPrice]],
                backgroundColor: "green"
            }
        ]
    };
    myOptions.scales.x.beginAtZero = false;
    myOptions.scales.x.min = Math.floor(0.9 * chartData.periodLowPrice);
    myOptions.scales.x.max = Math.ceil(1.1 * chartData.periodHighPrice);
    myOptions.plugins.addCurrentPriceLine = {xValue: chartData.currentPrice};
    return (
        <Bar 
        data={chartDataSet}
        options={myOptions}
        plugins= { [addCurrentPriceLine] }
        />
    );
};

export const BuySellChart = ( {chartData} ) => {
    let myOptions = JSON.parse(JSON.stringify(defltBarOptions));

    const chartDataSet = {
        labels: "1",
        datasets: [
            {
                backgroundColor: ["green"],
                data: [ [chartData.buyLowPrice, chartData.buyPrice]]
            },
            {
                backgroundColor: ["yellow"],
                data: [ [chartData.buyPrice, chartData.sellPrice]]
            },
            {
                backgroundColor: ["red"],
                data: [ [chartData.sellPrice, chartData.sellHighPrice]]
            }
        ]
    };

    myOptions.scales.x.beginAtZero = false;
    myOptions.scales.x.stacked = false;
    myOptions.scales.y.beginAtZero = false;
    myOptions.scales.y.stacked = true;

    myOptions.scales.x.min = Math.floor(0.9 * Math.min(chartData.currentPrice, chartData.buyLowPrice));
    myOptions.scales.x.max = Math.ceil(1.1 * Math.max(chartData.currentPrice, chartData.sellHighPrice));
    myOptions.plugins.addCurrentPriceLine = {xValue: chartData.currentPrice};
    //console.log("x.min=", myOptions.scales.x.min, ", buyLowPrice=", chartData.buyLowPrice);
    return (
        <Bar 
        data={chartDataSet}
        options={myOptions}
        plugins={ [addCurrentPriceLine] }
        />
    );
};

export const PriceHistoryChart = ( {chartData} ) => {
    let myOptions = JSON.parse(JSON.stringify(defltBarOptions));
    console.log("PriceHistoryChart 1, myOptions=", myOptions);
    const chartDataSet = {
        labels: chartData.periodDates,
        datasets: [
            {
                backgroundColor: ["#FF5733"],
                data: chartData.periodPrices
            }
        ]
    };

    myOptions.indexAxis = 'x';
    myOptions.scales.x.ticks.display = false;
    myOptions.scales.y = JSON.parse(JSON.stringify(defltAxisOptions));
    myOptions.scales.y.ticks.font.size = 8;
    console.log("PriceHistoryChart 2, myOptions=", myOptions);
    return (
        <Line 
        data={chartDataSet}
        options={myOptions}
        />
        );
};
