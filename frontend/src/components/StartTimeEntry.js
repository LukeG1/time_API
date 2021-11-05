import React from "react";

export class StartTimeEntry extends React.Component {
	send_time_entry = () => {
		var descString = "";
		if (document.getElementById("time_entry_description").value !== "") {
			descString =
				"?description=" +
				document.getElementById("time_entry_description").value;
		}

		fetch(
			"https://2020gabel.pythonanywhere.com/time_entries" + descString,
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
				this.props.on_start_timer(data.data);
				console.log(data.data);
			})
			.catch(console.log);
	};

	render() {
		return (
			<div>
				<input
					type="text"
					className="form-control mr-sm-2"
					placeholder="description..."
					id="time_entry_description"
				/>
				<button
					className="btn btn-outline-success my-2 my-sm-0"
					onClick={this.send_time_entry}
				>
					Start Time entry!
				</button>
			</div>
		);
	}
}
