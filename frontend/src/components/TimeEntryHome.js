import React from "react";

export class TimeEntryHome extends React.Component {
	duration = (props) => {
		var start = Date.parse(props.data.start);
		var stop = Date.parse(props.data.stop);
		var dur = new Date(stop - start);
		return dur.toISOString().substr(11, 8);
	};

	formatAMPM = (date) => {
		var hours = date.getHours();
		var minutes = date.getMinutes();
		var ampm = hours >= 12 ? "PM" : "AM";
		hours = hours % 12;
		hours = hours ? hours : 12; // the hour '0' should be '12'
		minutes = minutes < 10 ? "0" + minutes : minutes;
		var strTime = hours + ":" + minutes + " " + ampm;
		return strTime;
	};

	start_time = (props) => {
		var start = new Date(Date.parse(props.data.start));
		return this.formatAMPM(start);
	};

	stop_time = (props) => {
		var stop = new Date(Date.parse(props.data.stop));
		return this.formatAMPM(stop);
	};

	render() {
		return (
			<div className="card">
				<li
					style={{
						display: "flex",
						overflow: "hidden",
						styleType: "none",
						alignContent: "center",
					}}
				>
					<div
						className="row"
						style={{
							justifyItems: "center",
						}}
					>
						<div style={{ paddingRight: 20 }} className="col">
							{this.props.data.description !== null ? (
								<b>{this.props.data.description}</b>
							) : (
								<p>(no description)</p>
							)}
						</div>
						<p
							style={{ color: this.props.data.project_color }}
							className="col-md-50"
						>
							{" "}
							{this.props.data.project_name}
						</p>
					</div>
					<div
						style={{
							marginLeft: "auto",
							display: "flex",
							overflow: "hidden",
							styleType: "none",
						}}
					>
						<p pr={0} display="grid" ml="auto">
							{" "}
							{this.start_time(this.props)} -
							{this.stop_time(this.props)}
						</p>
						<p
							style={{
								fontSize: "md",
								display: "flex",
								marginLeft: "auto",
								paddingRight: 40,
								paddingLeft: 40,
							}}
						>
							{this.duration(this.props)}
						</p>
					</div>
				</li>
			</div>
		);
	}
}
