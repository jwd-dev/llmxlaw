import React from "react"
import { Chrono } from "react-chrono";

const App = () => {

  const transformData = (data) => {
    return data.map(entry => ({
      title: entry[2], // Assuming this is the date you want as the title
      cardTitle: entry[0],
      url: "", // Placeholder as the original data does not provide a URL
      cardSubtitle: entry[1],
      cardDetailedText: entry[1]
    }));
  };
  const inputData = [
    ["Imposition of Sentence on Paras Jha","The court hearing for the imposition of sentence on Paras Jha took place","09-18-2018 1:08 PM","09-18-2018 1:08 PM","d313286829947beeb9df0b0e30ec2be6"],
    ["Imposition of Sentence on Paras Jha","The court hearing for the imposition of sentence on Paras Jha took place.","09-18-2018","09-18-2018","d313286829947beeb9df0b0e30ec2be6"]
  ];

  const items = transformData(inputData);

  return (
      <div style={{ width: '500px', height: '950px' }}>
        <Chrono items={items} mode="VERTICAL" />
      </div>
  )
}

export default App;