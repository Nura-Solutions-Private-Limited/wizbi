# Getting Started with WizBi

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.


### update airflow link

1. update the JSON file in  `src/assets/data/settings.json`
    - if `isProdAirflow` value is `true` it will render `http://192.168.1.8:8081/home` or else it will be `http://3.23.175.166:8081/home` airflow navigation URL.
    - Use `signUp` To enable sign up functionality.
    - Use `forgotPasswordLink` To enable forgot password functionality.
2. save and do the deployment process

### deployment
1. Connect to the remote server for deployment using the IP address and account credentials
    execute the following command:
    ```
    ssh uat@192.168.1.6
    ```
2. navigate to directory `repos/rebiz-frontend/rebiz`
3. check out the main branch and fetch the latest changes
    ```
    git checkout main or git checkout branch_name(checkout to latest branch)
    git pull
    ``` 
4. To initiate the build process, execute the following command
```
npm run build
```
this command will generate a build folder containing the compiled output.

5. Connect to `WinSCP` using the credentials of the remote server 
copy the files in that build folder `/home/uat/rebiz-frontend/rebiz/build`  and paste it in deployment location `var/www/wizbi/build` 