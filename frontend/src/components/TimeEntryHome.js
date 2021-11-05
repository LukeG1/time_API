import React from "react";

export class TimeEntryHome extends React.Component {
    render() {
        return (
            <div className="card">
                <div className="card-body">
                    <h5 className="card-title">{ this.props.data.name }</h5>
                    <h6 className="card-subtitle mb-2 text-muted">{ this.props.data.project }</h6>
                    <p className="card-text">{ this.props.data.start } - { this.props.data.end }</p>
                </div>
            </div>
        );
        }
  }