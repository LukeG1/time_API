## Time tracking and task management API
-----


### Functions

1. /users
   1. post
      1. the only method that doent require an API key in the header, send a username email and password and it will respond with a user json containing the new API key that you now need to save
   2. get
      1. returns the user of the API key that you are using
2. /times
   1. post
      1. this is where you go to start stop and manually enter timers
         1. starting
            1. optionally add a description and project_id and a timer will be started, be sure to save its id
         2. stoping
            1. if only pass a time_id then it will end whatever timer that is, which should be the most recent
         3. manual entry coming soon
   2. get
      1. this is how you can see your times
         1. mode = 0
            1. returns the running timer
         2. mode = 1
            1. returns the timers since a start date (coming soon)
         3. mode = 2
            1. returns the timers within a date range (coming soon)
         4. mode = 3
            1. returns all timers belonging to the user