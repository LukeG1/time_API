import React from "react";
import "./App.css";
import { Navbar } from "./components/NavBar";
import { TimeEntryHome } from "./components/TimeEntryHome";
//import SideNav, { NavItem } from "@trendmicro/react-sidenav";
//import "@trendmicro/react-sidenav/dist/react-sidenav.css";
//import { BsHouse, BsBook, BsPieChart, BsPerson } from "react-icons/bs";

//MY TIME TRACKING API KEY: kiE3eTPhGN_8q3CpCvnRpQ
export class App extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			curent_time: null,
			recent: null,
			project_data: [],
		};
	}

	get_recent_time_entries = () => {
		fetch("https://2020gabel.pythonanywhere.com/time_entries?mode=3", {
			mode: "cors",
			method: "GET",
			headers: {
				key: "kiE3eTPhGN_8q3CpCvnRpQ",
			},
		})
			.then((res) => res.json())
			.then((data) => {
				this.setState({
					recent: data.data.slice(-1 * 10).reverse(),
				});
			})
			.catch(console.log);
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
		this.get_recent_time_entries();
	}

	handleTimeEntry = (time_data) => {
		this.setState({ curent_time: time_data });
	};
	handleStopTimeEntry = (time_data) => {
		this.setState({ curent_time: null });
		this.get_recent_time_entries();
	};

	render() {
		return (
			<div className="App">
				<Navbar
					on_start_timer={this.handleTimeEntry}
					on_stop_timer={this.handleStopTimeEntry}
					data={this.state.curent_time}
				/>

				{this.state.recent != null ? (
					<div>
						{this.state.recent.map(function (object, i) {
							return (
								<TimeEntryHome data={object} key={object.id} />
							);
						})}
					</div>
				) : (
					<h1>Start tracking to see something here</h1>
				)}
			</div>
		);
	}
}

export default App;
