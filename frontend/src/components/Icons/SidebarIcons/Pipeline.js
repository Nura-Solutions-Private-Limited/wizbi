import React from "react";

class Pipeline extends React.Component {
  render() {
    return (
      <svg
        className={this.props.className}
        width="40"
        height="40"
        viewBox="0 0 40 40"
        xmlns="http://www.w3.org/2000/svg"
      >
        <g
          transform="translate(0.000000,271.000000) scale(0.100000,-0.100000)"
          fill="#000000"
          stroke="none"
        >
          <path d="M1411 1729 c-123 -49 -190 -160 -199 -328 -4 -83 -2 -96 14 -108 23 -17 164 -18 187 0 10 7 20 38 26 77 12 75 35 111 79 124 53 15 83 -1 173 -95 107 -109 165 -140 280 -147 211 -12 339 121 356 368 5 61 2 78 -10 88 -23 19 -115 26 -164 13 -46 -13 -46 -14 -58 -105 -9 -70 -47 -106 -111 -106 -46 0 -49 2 -138 93 -119 121 -159 141 -286 144 -77 2 -105 -1 -149 -18z" />
        </g>
      </svg>
    );
  }
}

export default Pipeline;
