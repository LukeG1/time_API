import React from "react";
import './App.css';
import { Counter } from "./components/Counter";
import { TimeEntryHome } from "./components/TimeEntryHome";
//import { Header } from "./components/Header";


//<Header title="hello from App" />
function App() {
  return (
    <div className="App">
      
      <Counter startingValue={100}/>
      <Counter startingValue={-100}/>
      <TimeEntryHome 
        name = {"this is a test"}
        project = {"random project"}
        start = {Date()}
        end = {Date()}
      />

    </div>
  );
}

export default App;
