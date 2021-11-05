import React from "react";

export class Counter extends React.Component {

    constructor(props){
        super(props);

        this.state = {
            count: props.startingValue,
        }
    }

    handleButtonClick = () => {
        this.setState({
            count: this.state.count + 1,
        })
    
    }

    render() {
      return (
        <div>
            <div>count: {this.state.count}</div>
            <button onClick={this.handleButtonClick}>increment</button>
        </div>
      );
    }
  }