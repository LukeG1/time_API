import React from "react";
import startSVG from "../stop.svg";

export class StopTimeEntry extends React.Component {
	send_time_entry = () => {
		fetch(
			"https://2020gabel.pythonanywhere.com/time_entries?time_entry_id=" +
				this.props.data.id,
			{
				mode: "cors",
				method: "POST",
				headers: {
					key: "kiE3eTPhGN_8q3CpCvnRpQ",
				},
			}
		)
			.then((res) => res.json())
			.then((data) => {
				this.props.on_stop_timer(data.data);
			})
			.catch(console.log);
	};

	render() {
		return (
			<button
				className="btn btn-outline-danger my-2 my-sm-0 bg-light"
				onClick={this.send_time_entry}
			>
				<img
					src={startSVG}
					width="30"
					height="30"
					className="d-inline-block align-top text-success"
					alt="Stop time entry"
				></img>
			</button>
		);
	}
}
