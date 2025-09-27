import React from "react";
import PropTypes from "prop-types";
import { Link, Navigate } from "react-router-dom";
import { connect } from "react-redux";
import { loginUser } from "../../actions/user";
import { withRouter } from "../../core/withRouter";
import LogoIcon from "../../components/Icons/HeaderIcons/LogoIcon";
import config from "../../assets/data/settings.json";
import WizBIInput from "../../core/WizBIInput/WizBIInput";

class Login extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
  };

  static isAuthenticated(token) {
    if (token) return true;
  }

  constructor(props) {
    super(props);
    this.state = {
      username: "",
      password: "",
      isLoading: false,
      emailBlured: false,
      passwordBlured: false,
      valid: false,
      submitted: false,
    };

    this.doLogin = this.doLogin.bind(this);
    this.changeEmail = this.changeEmail.bind(this);
    this.changePassword = this.changePassword.bind(this);
    this.signUp = this.signUp.bind(this);
    this.validEmail = this.validEmail.bind(this);
    this.validate = this.validate.bind(this);
    this.validPassword = this.validPassword.bind(this);
  }

  changeEmail(event) {
    this.setState({ email: event.target.value });
  }

  changePassword(event) {
    this.setState({ password: event.target.value });
  }

  doLogin(e) {
    e.preventDefault();
    this.validate();
    if (this.valid) {
      this.setState({ ...this.state, isLoading: true });
      setTimeout(() => {
        this.props.dispatch(
          loginUser({
            username: this.state.username,
            password: this.state.password,
          }),
        );
        this.setState({ ...this.state, isLoading: false });
      }, 2000);
    }
  }

  signUp() {
    this.props.history.push("/register");
  }

  validate() {
    this.setState({
      ...this.state,
      emailBlured: true,
      passwordBlured: true,
    });

    if (
      this.validEmail(this.state.username) &&
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
    var re = /^[a-zA-Z0-9]+$/;
    if (re.test(email.toLowerCase())) {
      return true;
    }
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
    if (
      Login.isAuthenticated(JSON.parse(localStorage.getItem("authenticated")))
    ) {
      return <Navigate to={from} />;
    }

    return (
      <div className="auth-page">
        <div
          className="container-fluid d-flex h-100 flex-wrap p-0 m-0 position-relative"
          style={{ overflow: "hidden" }}
        >
          <div className="col-lg-8 auth-bg"></div>
          <div className="col-lg-4 position-relative auth-container  d-flex flex-column justify-content-center align-items-center">
            <div className={`navbar-brand text-center brand text-wizBi`}>
              <div className="d-flex align-items-center justify-content-center">
                <LogoIcon className='brand'/> <h1 className="m-0 p-0">WizBI</h1>
              </div>
              <small>Redefine Your Business</small>
            </div>
            <div className="widget-auth w-100 mt-3">
              <form onSubmit={this.doLogin} className="d-flex flex-column">
                <div className="container mt-3">
                  <div className="row d-flex justify-content-center">
                    <div className="w-100 p-0 m-0">
                      <div
                        className="card w-100"
                        style={{ background: "transparent" }}
                      >
                        <div className="form-group mb-2">
                          <WizBIInput
                            labelName="Username"
                            className={`${
                              !this.validEmail(this.state.username) &&
                              this.state.emailBlured
                                ? "is-invalid"
                                : ""
                            }`}
                            inputClass="background-white active"
                            panelClass="my-3"
                            controls={{
                              value: this.state.username,
                              onBlur: () => {
                                this.setState({
                                  ...this.state,
                                  emailBlured: true,
                                });
                              },
                              onChange: (e) => {
                                this.setState({
                                  ...this.state,
                                  username: e.target.value,
                                });
                              },
                              id: "username",
                              autoComplete: "off",
                            }}
                          >
                            
                            <div className="invalid-feedback">
                              A valid username is required!
                            </div>
                          </WizBIInput>
                        </div>

                        {/* <div className="forms-inputs mb-4"> <span>Username</span>
                                                    <input autoComplete="off" value={this.state.username} type="text" className={`form-control ${(!this.validEmail(this.state.username) && this.state.emailBlured) ? 'is-invalid' : ''}`} required
                                                        onBlur={() => { this.setState({ ...this.state, emailBlured: true }) }}
                                                        onChange={(e) => { this.setState({ ...this.state, username: e.target.value }) }}
                                                    />
                                                    <div className="invalid-feedback">A valid username is required!</div>
                                                </div> */}
                        <div className="form-group mb-2">
                          <WizBIInput
                            labelName="Password"
                            className={`${
                              !this.validPassword(this.state.password) &&
                              this.state.passwordBlured
                                ? "is-invalid"
                                : ""
                            }`}
                            inputClass="background-white active"
                            panelClass="my-3"
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
                                });
                              },
                              id: "password",
                              type: "password",
                              autoComplete: "off",
                            }}
                          >
                            
                            <div className="invalid-feedback">
                              Password must be 8 character!
                            </div>
                          </WizBIInput>
                        </div>

                        {/* <div className="forms-inputs mb-4"> <span>Password</span>
                                                <input autoComplete="off" type="password" value={this.state.password} className={`form-control ${(!this.validPassword(this.state.password) && this.state.passwordBlured) ? 'is-invalid' : ''}`} required
                                                    onBlur={() => { this.setState({ ...this.state, passwordBlured: true }) }}
                                                    onChange={(e) => { this.setState({ ...this.state, password: e.target.value }) }}
                                                />
                                                <div className="invalid-feedback">Password must be 8 character!</div>
                                            </div> */}

                        {!!this.props.errorMessage &&
                          !!this.props.errorMessage.length && (
                            <p style={{ color: "#db2a34" }}>
                              {this.props.errorMessage}
                            </p>
                          )}
                        <div className="mb-3">
                          <button
                            onClick={(evt) => {
                              this.doLogin(evt);
                            }}
                            type="submit"
                            className={`p-button p-component bg-wizBi p-2 sign-in w-100 text-white justify-content-center ${
                              this.state.isLoading ? "opacity-25" : ""
                            }`}
                          >
                            Login
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </form>

              <div className="auth-more-info text-dark mt-3">
                <div>
                  {config.signUp && (
                    <>
                      New User ? <Link to="/register">Sign Up</Link>
                    </>
                  )}
                </div>
                {config.forgotPasswordLink && (
                  <div role="button">Forgot your credentials ?</div>
                )}
              </div>
            </div>
          </div>
          <footer className="auth-footer d-flex justify-content-end position-absolute mx-4">
            {new Date().getFullYear()} &copy; WizBI 3.0 - Nura Solutions Private
            Limited. All Rights Reserved
          </footer>
        </div>
      </div>
    );
  }
}

function mapStateToProps(state) {
  return {
    isFetching: state.auth.isFetching,
    isAuthenticated: state.auth.isAuthenticated,
    errorMessage: state.auth.errorMessage,
  };
}

export default withRouter(connect(mapStateToProps)(Login));
