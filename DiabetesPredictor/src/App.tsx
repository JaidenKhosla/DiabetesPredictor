import React, { useState, type MapHTMLAttributes, type MouseEventHandler } from 'react'

import "./assets/stylesheets/App.css"

import DiabetesForm from './DiabetesForm'
import HeartDiseaseForm from './HeartDiseaseForm'

const tabMap: {[key: string]: React.ReactElement} = {
  "Diabetes": <DiabetesForm/>,
  "Heart Disease": <HeartDiseaseForm/>
}

function App() {

  const [useTab, setTab] = useState<React.ReactElement>(<DiabetesForm/>);
  const [useTitle, setTitle] = useState<string>("Diabetes");

  function tab(mouseEvent: React.MouseEvent<HTMLButtonElement>) {
      const active: HTMLButtonElement| null = document.querySelector("button.active");
  
      if(active)
        active.classList.remove("active");

      mouseEvent.currentTarget.classList.add("active");
      setTab(tabMap[mouseEvent.currentTarget.innerText]);
      setTitle(mouseEvent.currentTarget.innerText)
  }

  return (
    <div className="App">
      <h1>{useTitle} Predictor</h1>
      <div className="tabs">
        <button onClick={tab} className='active'>Diabetes</button>
        <button onClick={tab}>Heart Disease</button>
      </div>
      <br/>
      <br/>
      {useTab}
    </div>
  )
}

export default App
