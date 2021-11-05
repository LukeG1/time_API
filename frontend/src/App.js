import React from "react";
import './App.css';
import { TimeEntryHome } from "./components/TimeEntryHome";

//MY TIME TRACKING API KEY: kiE3eTPhGN_8q3CpCvnRpQ
export class App extends React.Component {

  state = {
    curent_time: {}
  }

  componentDidMount(){
      fetch('https://2020gabel.pythonanywhere.com/time_entries', {
      mode: 'cors',
      method: 'GET',
      headers: {
        "key": "kiE3eTPhGN_8q3CpCvnRpQ"
      }
    })
    .then(res => res.json())
    .then((data) => {
      this.setState({ curent_time: 
        {
          name: data.data.description,
          project: data.data.project_id,
          start: data.data.start,
          end: data.data.stop,
        }
      })
    })
    .catch(console.log)
  }

  render(){
    console.log(this.state.curent_time.name)
    return (
      <div className="App">
        
        <TimeEntryHome 
          data = {this.state.curent_time}
        />

      </div>
    );
  }
}

export default App;
