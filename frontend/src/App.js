import React from "react";
import "./App.css";
import { Navbar } from "./components/NavBar";
import { TimeEntryHome } from "./components/TimeEntryHome";

//MY TIME TRACKING API KEY: kiE3eTPhGN_8q3CpCvnRpQ
export class App extends React.Component {
	state = {
		curent_time: null,
	};
	componentDidMount() {
		fetch("https://2020gabel.pythonanywhere.com/time_entries", {
			mode: "cors",
			method: "GET",
			headers: {
				key: "kiE3eTPhGN_8q3CpCvnRpQ",
			},
		})
			.then((res) => res.json())
			.then((data) => {
				this.setState({
					curent_time: data.data,
				});
			})
			.catch(console.log);
	}

	handleTimeEntry = (time_data) => {
		this.setState({ curent_time: time_data });
	};
	handleStopTimeEntry = (time_data) => {
		this.setState({ curent_time: null });
	};

	render() {
		return (
			<div className="App">
				<Navbar
					on_start_timer={this.handleTimeEntry}
					on_stop_timer={this.handleStopTimeEntry}
					data={this.state.curent_time}
				/>
				{this.state.curent_time != null ? (
					<TimeEntryHome data={this.state.curent_time} />
				) : (
					<h1>No Time Entry Running</h1>
				)}
			</div>
		);
	}
}

export default App;
