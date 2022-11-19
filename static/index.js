var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var ChessBoard = function (_React$Component) {
	_inherits(ChessBoard, _React$Component);

	function ChessBoard(props) {
		_classCallCheck(this, ChessBoard);

		var _this = _possibleConstructorReturn(this, (ChessBoard.__proto__ || Object.getPrototypeOf(ChessBoard)).call(this, props));

		_this.state = { pieces: [["R", "N", "B", "Q", "K", "B", "N", "R"], ["P", "P", "P", "P", "P", "P", "P", "P"], [" ", " ", " ", " ", " ", " ", " ", " "], [" ", " ", " ", " ", " ", " ", " ", " "], [" ", " ", " ", " ", " ", " ", " ", " "], [" ", " ", " ", " ", " ", " ", " ", " "], ["p", "p", "p", "p", "p", "p", "p", "p"], ["r", "n", "b", "q", "k", "b", "n", "r"]], selected: null, turn: "w" };
		return _this;
	}

	_createClass(ChessBoard, [{
		key: "render",
		value: function render() {
			var _this2 = this;

			console.log(this.state);
			return React.createElement(
				"div",
				null,
				" ",
				this.state.pieces.slice().reverse().map(function (row, rowIdx) {
					return React.createElement(
						"div",
						{ key: rowIdx, style: { display: "flex" } },
						" ",
						row.map(function (piece, colIdx) {
							return React.createElement(
								"button",
								{ key: colIdx, onClick: function onClick(e) {
										sIdx = _this2.state.selected;
										pieces = _this2.state.pieces.slice();
										if (sIdx == null || pieces[sIdx[1]][sIdx[0]] == " ") {
											_this2.setState({ selected: [colIdx, 7 - rowIdx] });
										} else {
											pieces[7 - rowIdx][colIdx] = pieces[sIdx[1]][sIdx[0]];
											pieces[sIdx[1]][sIdx[0]] = " ";
											_this2.setState({ selected: null, pieces: pieces, turn: _this2.state.turn == "w" ? "b" : "w" });
										}
									},
									style: { outline: "none", border: "none", width: "50px", height: "50px", background: (rowIdx + colIdx) % 2 == 0 ? "gainsboro" : "darkGrey" } },
								piece != " " && React.createElement("img", { style: { width: "25px", height: "25px" }, src: "/pngs/" + piece + ".png", alt: "" })
							);
						}),
						" "
					);
				})
			);
		}
	}]);

	return ChessBoard;
}(React.Component);

ReactDOM.createRoot(document.getElementById('root')).render(React.createElement(ChessBoard, null));