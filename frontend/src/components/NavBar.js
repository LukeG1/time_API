import React from "react";
import { StartTimeEntry } from "./StartTimeEntry";
import { StopTimeEntry } from "./StopTimeEntry";

export class Navbar extends React.Component {
	on_start_timer = (data) => {
		this.props.on_start_timer(data);
	};
	on_stop_timer = (data) => {
		this.props.on_stop_timer(data);
	};
	render() {
		function show_curent_timer(props) {
			if (props.data != null) {
				return (
					<div className="row">
						{props.data.description != null ? (
							<p className="col-md-3">{props.data.description}</p>
						) : (
							<p className="col-md-3">(no description)</p>
						)}
						<p className="col-md-3">{props.data.id}</p>
						<p className="col-md-3">{props.data.start}</p>
					</div>
				);
			}
			return null;
		}

		return (
			<nav className="navbar navbar-expand-lg navbar-light bg-light sticky-top">
				{/* <a className="navbar-brand">Time Tracker</a> */}
				<ul className="navbar-nav mr-auto">
					<li className="nav-item active">
						{/* CURRENT TIME ENTRY */}
						{show_curent_timer(this.props)}
					</li>
				</ul>
				<div className="form-inline my-2 my-lg-0">
					{this.props.data == null ? (
						<StartTimeEntry on_start_timer={this.on_start_timer} />
					) : (
						<StopTimeEntry
							data={this.props.data}
							on_stop_timer={this.on_stop_timer}
						/>
					)}
				</div>
			</nav>
		);
	}
}
