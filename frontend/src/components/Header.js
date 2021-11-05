import React from "react";

export class Header extends React.Component {
    render() {
      return (
      <header className="App-header">
          <p>
            Edit <code>src/App.js</code> and save to reload.
          </p>
          <p>
            { this.props.title }
          </p>
          <a
            className="App-link" 
            href="https://reactjs.org"
            target="_blank"
            rel="noopener noreferrer"
          >
            Learn React
          </a>
        </header>
      );
    }
  }