import React from "react";
import PropTypes from "prop-types";
import { Link, Navigate } from "react-router-dom";
import { connect } from "react-redux";
import { registerUser, registerError } from "../../actions/register";
import { withRouter } from "../../core/withRouter";
import LogoIcon from "../../components/Icons/HeaderIcons/LogoIcon";
import WizBIInput from "../../core/WizBIInput/WizBIInput";

class Register extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
  };
  constructor(props) {
    super(props);

    this.state = {
      email: "",
      password: "",
      confirmPassword: "",
      username: "",
      type: "",
      isSubmitted: false,
    };

    this.doRegister = this.doRegister.bind(this);
    this.changeEmail = this.changeEmail.bind(this);
    this.changePassword = this.changePassword.bind(this);
    this.changeConfirmPassword = this.changeConfirmPassword.bind(this);
    this.checkPassword = this.checkPassword.bind(this);
    this.isPasswordValid = this.isPasswordValid.bind(this);
    this.callbackRefState = this.callbackRefState.bind(this);
  }

  changeEmail(event) {
    this.setState({ email: event.target.value });
  }

  changePassword(event) {
    this.setState({ password: event.target.value });
  }

  changeConfirmPassword(event) {
    this.setState({ confirmPassword: event.target.value });
  }

  checkPassword() {
    if (!this.isPasswordValid()) {
      if (!this.state.password) {
        this.props.dispatch(registerError("Password field is empty"));
      } else {
        this.props.dispatch(registerError("Passwords are not equal"));
      }
      setTimeout(() => {
        this.props.dispatch(registerError());
      }, 3 * 1000);
    }
  }

  isPasswordValid() {
    return (
      this.state.password && this.state.password === this.state.confirmPassword
    );
  }

  // doRegister(e) {
  //     e.preventDefault();
  //     if (!this.isPasswordValid()) {
  //         this.checkPassword();
  //     } else {
  //         this.props.dispatch(registerUser({
  //             creds: {
  //                 email: this.state.email,
  //                 password: this.state.password,
  //                 username: this.state.username
  //             },
  //             history: this.props.history
  //         }));
  //     }
  // }

  validate() {
    this.setState({
      ...this.state,
      userNameBlured: true,
      emailBlured: true,
      passwordBlured: true,
    });

    if (
      this.validEmail(this.state.email) &&
      this.validUserName(this.state.username) &&
      this.validPassword(this.state.password)
    ) {
      this.valid = true;
      this.setState({
        ...this.state,
        valid: true,
      });
    }
  }

  validEmail(email) {
    var re = /(.+)@(.+){2,}\.(.+){2,}/;
    if (re.test(email.toLowerCase())) {
      return true;
    }
  }
  validUserName(userName) {
    var re = /^[a-zA-Z0-9]+$/;
    if (re.test(userName.toLowerCase())) {
      return true;
    }
  }

  doRegister(e) {
    e.preventDefault();
    this.validate();
    if (this.valid) {
      this.setState({ ...this.state, isLoading: true });
      setTimeout(() => {
        this.props.dispatch(
          registerUser({
            creds: {
              email: this.state.email,
              password: this.state.password,
              username: this.state.username,
            },
            history: this.props.history,
            callbackRef: this.callbackRefState,
          }),
        );
        this.setState({ ...this.state, isLoading: false });
      }, 2000);
    }
  }

  callbackRefState() {
    this.setState({
      ...this.state,
      isLoading: false,
      email: "",
      password: "",
      confirmPassword: "",
      username: "",
      type: "",
      isSubmitted: true,
    });
  }

  validPassword(password) {
    if (password.length > 7) {
      return true;
    }
  }

  render() {
    const { from } = this.props.location.state || {
      from: { pathname: "/app" },
    }; // eslint-disable-line

    // cant access login page while logged in
    if (JSON.parse(localStorage.getItem("authenticated"))) {
      return <Navigate to={from} />;
    }

    return (
      <div className="auth-page">
        <div className="container-fluid d-flex h-100 flex-wrap p-0 m-0">
          <div className="col-lg-8 auth-bg"></div>
          <div className="col-lg-4 position-relative auth-container">
            <div
              className={`navbar-brand text-center brand text-wizBi`}
              style={{ marginTop: "50px" }}
            >
              <div className="d-flex align-items-center justify-content-center">
                <LogoIcon /> <h1 className="m-0 p-0">WizBI</h1>
              </div>
              <small>Redefine Your Business</small>
            </div>
            <div className="widget-auth w-100 mt-1">
              {/* <div className="card flex justify-content-center"> */}
              <form onSubmit={this.doLogin} className="flex flex-column gap-2">
                <div className="container mt-3">
                  <div className="row d-flex justify-content-center">
                    <div className="w-100 p-0 m-0">
                      <div className="card w-100" id="register">
                        <div className="form-group mb-2">
                          <WizBIInput
                            labelName="Email"
                            className={`${
                              !this.validEmail(this.state.email) &&
                              this.state.emailBlured &&
                              !this.state.isSubmitted
                                ? "is-invalid"
                                : ""
                            }`}
                            inputClass="background-white active"
                            panelClass="my-2"
                            controls={{
                              value: this.state.email,
                              onBlur: () => {
                                this.setState({
                                  ...this.state,
                                  emailBlured: true,
                                });
                              },
                              onChange: (e) => {
                                this.setState({
                                  ...this.state,
                                  email: e.target.value,
                                  isSubmitted: false,
                                });
                              },
                              id: "email",
                              autoComplete: "off",
                            }}
                          >
                            
                            <div className="invalid-feedback">
                              A valid email is required!
                            </div>
                          </WizBIInput>
                        </div>

                        {/* <div className="forms-inputs mb-4"> <span>Email</span>
                                                <input autoComplete="off" value={this.state.email} type="text" className={`form-control ${(!this.validEmail(this.state.email) && this.state.emailBlured && !this.state.isSubmitted) ? 'is-invalid' : ''}`} required
                                                    onBlur={() => { this.setState({ ...this.state, emailBlured: true }) }}
                                                    onChange={(e) => { this.setState({ ...this.state, email: e.target.value, isSubmitted: false }) }}
                                                />
                                                <div className="invalid-feedback">A valid email is required!</div>
                                            </div> */}

                        <div className="form-group mb-2">
                          <WizBIInput
                            labelName="Username"
                            className={`${
                              !this.validUserName(this.state.username) &&
                              this.state.userNameBlured &&
                              !this.state.isSubmitted
                                ? "is-invalid"
                                : ""
                            }`}
                            inputClass="background-white active"
                            panelClass="my-2"
                            controls={{
                              value: this.state.username,
                              onBlur: () => {
                                this.setState({
                                  ...this.state,
                                  userNameBlured: true,
                                });
                              },
                              onChange: (e) => {
                                this.setState({
                                  ...this.state,
                                  username: e.target.value,
                                  isSubmitted: false,
                                });
                              },
                              id: "reg_username",
                              autoComplete: "off",
                            }}
                          >
                            
                            <div className="invalid-feedback">
                              A valid username is required!
                            </div>
                          </WizBIInput>
                        </div>

                        {/* <div className="forms-inputs mb-4"> <span>Username</span>
                                                    <input autoComplete="off" value={this.state.username} type="text" className={`form-control ${(!this.validUserName(this.state.username) && this.state.userNameBlured && !this.state.isSubmitted) ? 'is-invalid' : ''}`} required
                                                        onBlur={() => { this.setState({ ...this.state, userNameBlured: true }) }}
                                                        onChange={(e) => { this.setState({ ...this.state, username: e.target.value, isSubmitted: false }) }}
                                                    />
                                                    <div className="invalid-feedback">A valid username is required!</div>
                                                </div> */}

                        {/* <div className="forms-inputs mb-2"> <span>Password</span>
                                                    <input autoComplete="off" type="password" value={this.state.password} className={`form-control ${(!this.validPassword(this.state.password) && this.state.passwordBlured && !this.state.isSubmitted) ? 'is-invalid' : ''}`} required
                                                        onBlur={() => { this.setState({ ...this.state, passwordBlured: true }) }}
                                                        onChange={(e) => { this.setState({ ...this.state, password: e.target.value, isSubmitted: false }) }}
                                                    />
                                                    <div className="invalid-feedback">Password must be 8 character!</div>
                                                </div> */}

                        <div className="form-group mb-2">
                          <WizBIInput
                            labelName="Password"
                            className={`${
                              !this.validPassword(this.state.password) &&
                              this.state.passwordBlured &&
                              !this.state.isSubmitted
                                ? "is-invalid"
                                : ""
                            }`}
                            inputClass="background-white active"
                            panelClass="my-2"
                            controls={{
                              value: this.state.password,
                              onBlur: () => {
                                this.setState({
                                  ...this.state,
                                  passwordBlured: true,
                                });
                              },
                              onChange: (e) => {
                                this.setState({
                                  ...this.state,
                                  password: e.target.value,
                                  isSubmitted: false,
                                });
                              },
                              id: "reg_password",
                              type: "password",
                              autoComplete: "off",
                            }}
                          >
                            
                            <div className="invalid-feedback">
                              Password must be 8 character!
                            </div>
                          </WizBIInput>
                        </div>

                        {!!this.props.errorMessage &&
                          !!this.props.errorMessage.length && (
                            <p className="invalid-feedback d-block">
                              {this.props.errorMessage}
                            </p>
                          )}
                        {!!this.props.message &&
                          !!this.props.message.length && (
                            <p className="text-success">{this.props.message}</p>
                          )}

                        <div className="mb-3 mt-2">
                          <button
                            onClick={(evt) => {
                              this.doRegister(evt);
                            }}
                            type="submit"
                            className={`btn sign-in w-100 text-white ${
                              this.state.isLoading ? "opacity-25" : ""
                            }`}
                          >
                            Register
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </form>

              <div className="auth-more-info text-dark mt-2">
                <div>
                  Already have the account ?<Link to="/login">Login now</Link>
                </div>
                {/* <div role='button'>Enter the account</div> */}
              </div>
            </div>
            <footer className="auth-footer my-2">
              {new Date().getFullYear()} &copy; WizBI 3.0 - Nura Solutions
              Private Limited. All Rights Reserved
            </footer>
          </div>
        </div>
      </div>
    );
  }
}

function mapStateToProps(state) {
  return {
    isFetching: state.register.isFetching,
    errorMessage: state.register.errorMessage,
    message: state.register.message,
  };
}

export default withRouter(connect(mapStateToProps)(Register));
