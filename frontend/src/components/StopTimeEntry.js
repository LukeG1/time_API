import React from "react";

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
				className="btn btn-outline-danger my-2 my-sm-0"
				onClick={this.send_time_entry}
			>
				Stop the timer
			</button>
		);
	}
}
