import React from "react";

export class TimeEntryHome extends React.Component {
	duration = (props) => {
		var start = Date.parse(props.data.start);
		var stop = Date.parse(props.data.stop);
		var dur = new Date(stop - start);
		return dur.toISOString().substr(11, 8);
	};

	render() {
		return (
			<div className="card">
				<div className="card-body row">
					<h5 className="card-title col">
						{this.props.data.description}
					</h5>
					<h6 className="card-subtitle mb-2 text-muted col">
						{this.props.data.project_id}
					</h6>
					<h6 className="card-subtitle mb-2 text-muted col">
						{this.props.data.id}
					</h6>
					<p className="card-text col">
						{/* {this.props.data.start} - {this.props.data.stop} */}
						{this.duration(this.props)}
					</p>
				</div>
			</div>
		);
	}
}
