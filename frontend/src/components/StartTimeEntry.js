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

var colourOptions = [];

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
			project_id: "",
		};
	}

	componentDidMount() {
		fetch("https://2020gabel.pythonanywhere.com/projects", {
			mode: "cors",
			method: "GET",
			headers: {
				key: "PbaXVplsecyyj9xjjO6pfQ",
			},
		})
			.then((res) => res.json())
			.then((data) => {
				colourOptions = [
					{
						value: "",
						label: "No Project",
						color: "#313131",
					},
				];
				for (var i = 0; i < data.data.length; i++) {
					colourOptions.push({
						label: data.data[i].name,
						value: data.data[i].name,
						color: data.data[i].color,
						id: data.data[i].id,
					});
				}
			})
			.catch(console.log);
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
		var projectString = "";
		if (this.state.inputValue.value !== "" && this.state.inputValue.value) {
			if (descString === "") {
				projectString += "?";
			} else {
				projectString += "&";
			}
			projectString += "project_id=" + this.state.inputValue.id;
		}

		fetch(
			"https://2020gabel.pythonanywhere.com/time_entries" +
				descString +
				projectString,
			{
				mode: "cors",
				method: "POST",
				headers: {
					key: "PbaXVplsecyyj9xjjO6pfQ",
				},
			}
		)
			.then((res) => res.json())
			.then((data) => {
				this.props.on_start_timer(data.data);
				console.log(
					"https://2020gabel.pythonanywhere.com/time_entries" +
						descString +
						projectString
				);
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
