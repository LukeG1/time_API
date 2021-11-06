import React from "react";
import startSVG from "../start.svg";
import Select from "react-select";
import chroma from "chroma-js";

const dot = (color = "transparent") => ({
	alignItems: "center",
	display: "flex",

	":before": {
		backgroundColor: color,
		borderRadius: 10,
		content: '" "',
		display: "block",
		marginRight: 8,
		height: 10,
		width: 10,
	},
});

const colourOptions = [
	{
		value: "",
		label: "No Project",
		color: "#313131",
	},
	{
		value: "ALGORITHM IMPLEMENTATION",
		label: "ALGORITHM IMPLEMENTATION",
		color: "#00B8D9",
	},
	{
		value: "BASIC MUSICIANSHIP: CLASS PIANO",
		label: "BASIC MUSICIANSHIP: CLASS PIANO",
		color: "#0052CC",
	},
	{
		value: "COMPARATIVE DIGITAL PRIVACIES",
		label: "COMPARATIVE DIGITAL PRIVACIES",
		color: "#5243AA",
	},
	{
		value: "COMPUTER ORGANIZATION AND ASSEMBLY LANGUAGE",
		label: "COMPUTER ORGANIZATION AND ASSEMBLY LANGUAGE",
		color: "#FF5630",
	},
	{
		value: "INTRODUCTION TO PHILOSOPHICAL PROBLEMS",
		label: "INTRODUCTION TO PHILOSOPHICAL PROBLEMS",
		color: "#FF8B00",
	},
];

const colourStyles = {
	control: (styles) => ({ ...styles, backgroundColor: "white" }),
	option: (styles, { data, isDisabled, isFocused, isSelected }) => {
		const color = chroma(data.color);
		return {
			...styles,
			backgroundColor: isDisabled
				? undefined
				: isSelected
				? data.color
				: isFocused
				? color.alpha(0.1).css()
				: undefined,
			color: isDisabled
				? "#ccc"
				: isSelected
				? chroma.contrast(color, "white") > 2
					? "white"
					: "black"
				: data.color,
			cursor: isDisabled ? "not-allowed" : "default",

			":active": {
				...styles[":active"],
				backgroundColor: !isDisabled
					? isSelected
						? data.color
						: color.alpha(0.3).css()
					: undefined,
			},
		};
	},
	input: (styles) => ({ ...styles, ...dot() }),
	placeholder: (styles) => ({ ...styles, ...dot("#ccc") }),
	singleValue: (styles, { data }) => ({ ...styles, ...dot(data.color) }),
};

export class StartTimeEntry extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			inputValue: "",
		};
	}

	handleInputChange = (newValue) => {
		const inputValue = newValue;
		this.setState({ inputValue });
		return inputValue;
	};

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
				console.log(this.state);
			})
			.catch(console.log);
	};

	render() {
		return (
			<div className="row">
				<input
					type="text"
					className="form-control bg-light input-large col-xs-4"
					placeholder="description..."
					id="time_entry_description"
					style={{
						outline: "0",
						borderWidth: "0 0 2px",
						borderColor: "#5cb85c",
						borderRadius: "0",
					}}
				/>
				<Select
					key="time_entry_project"
					id="time_entry_project"
					defaultValue={colourOptions[0]}
					options={colourOptions}
					styles={colourStyles}
					onChange={this.handleInputChange}
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
						className="d-inline-block align-top text-success"
						alt="Start time entry!"
					></img>
				</button>
			</div>
		);
	}
}
