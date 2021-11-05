import React from "react";

export class TimeEntryHome extends React.Component {
	render() {
		return (
			<div className="card">
				<div className="card-body">
					<h5 className="card-title">
						{this.props.data.description}
					</h5>
					<h6 className="card-subtitle mb-2 text-muted">
						{this.props.data.project_id}
					</h6>
					<h6 className="card-subtitle mb-2 text-muted">
						{this.props.data.id}
					</h6>
					<p className="card-text">
						{this.props.data.start} - {this.props.data.stop}
					</p>
				</div>
			</div>
		);
	}
}
