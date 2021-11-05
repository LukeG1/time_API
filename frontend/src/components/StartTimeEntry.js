import React from "react";
import startSVG from "../start.svg";

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
			<div className="">
				<input
					type="text"
					className="form-control bg-light"
					placeholder="description..."
					id="time_entry_description"
					style={{
						outline: "0",
						borderWidth: "0 0 2px",
						borderColor: "#5cb85c",
						borderRadius: "0",
					}}
				/>
				<button
					// btn-outline-success
					className="btn my-2 my-sm-0 bg-light"
					onClick={this.send_time_entry}
				>
					<img
						src={startSVG}
						width="30"
						height="30"
						class="d-inline-block align-top text-success"
						alt="Start time entry!"
					></img>
				</button>
			</div>
		);
	}
}
