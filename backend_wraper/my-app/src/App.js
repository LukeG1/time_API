import logo from './logo.svg';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

//=========================================================================================


function register(username,password,timezone) {
  const Http = new XMLHttpRequest();
  const user_url = base_url + "/users";
  // var results;
  // fetch(user_url, {
  //   mode: "cors",
  //   method: "POST",
  //   body: JSON.stringify({
  //     "username" : username,
  //     "password" : password,
  //     "tz" : timezone,
  //   }),
  // })
  //   .then((res) => 
  //     return res.json();
  //   )

  var data = {
        "username" : username,
        "password" : password,
        "tz" : timezone,
      }


  const response = fetch(base_url, {
    method: 'POST', // *GET, POST, PUT, DELETE, etc.
    mode: 'cors', // no-cors, *cors, same-origin
    cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
    credentials: 'same-origin', // include, *same-origin, omit
    headers: {
      'Content-Type': 'application/json'
      // 'Content-Type': 'application/x-www-form-urlencoded',
    },
    redirect: 'follow', // manual, *follow, error
    referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
    body: JSON.stringify(data) // body data type must match "Content-Type" header
  });
  console.log(response)
  return response.json(); // parses JSON response into native JavaScript objects
}


//=========================================================================================
window.addEventListener('DOMContentLoaded', (event) => {
  



  results = register(
    "admin",
    "pass",
    "UTC"
  )

  console.log(results)
  









});

export default App;
