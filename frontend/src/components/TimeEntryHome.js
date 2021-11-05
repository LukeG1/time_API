import React from "react";

export class TimeEntryHome extends React.Component {

    constructor(props){
        super(props);

        this.state = {
            name: props.name,
            project: props.project,
            start: props.start,
            end: props.end,
        }
    }

    render() {
        //style="display: flex; flex-direction: row;"
      return (
        <div >
            <p>{ this.state.name }</p>
            <p>{ this.state.project }</p>
            <p>{ this.state.start }</p>
            <p>{ this.state.end }</p>
        </div>
      );
    }
  }