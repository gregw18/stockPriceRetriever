const securityAmazon= {
    name: "Amazon",
    currentPrice: 114.35,
    lastClosePrice: 112.35,
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
    lastClosePrice: 245.35,
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
    lastClosePrice: 312.35,
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
    lastClosePrice: 0.0,
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
  
export const getFakeData = () => {
  // Return around 90 hardcoded securities;
  let mySecurities = [];
  for (let i = 0; i < 90/4; i++) {
    mySecurities.push(securityAmazon);
    mySecurities.push(securityZero);
    mySecurities.push(securityMicrosoft);
    mySecurities.push(securityLilly);
  }

  return mySecurities;
}
