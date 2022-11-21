var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var ChessBoard = function (_React$Component) {
	_inherits(ChessBoard, _React$Component);

	function ChessBoard(props) {
		_classCallCheck(this, ChessBoard);

		var _this = _possibleConstructorReturn(this, (ChessBoard.__proto__ || Object.getPrototypeOf(ChessBoard)).call(this, props));

		_this.state = { pieces: [["R", "N", "B", "Q", "K", "B", "N", "R"], ["P", "P", "P", "P", "P", "P", "P", "P"], ["1", "1", "1", "1", "1", "1", "1", "1"], ["1", "1", "1", "1", "1", "1", "1", "1"], ["1", "1", "1", "1", "1", "1", "1", "1"], ["1", "1", "1", "1", "1", "1", "1", "1"], ["p", "p", "p", "p", "p", "p", "p", "p"], ["r", "n", "b", "q", "k", "b", "n", "r"]], selected: null, turn: "w" };
		return _this;
	}

	_createClass(ChessBoard, [{
		key: "castleCheck",
		value: function castleCheck(pieces, fromRank, fromFile, toRank, toFile) {
			return (pieces[fromRank][fromFile] == 'k' || pieces[fromRank][fromFile] == 'K') && (toFile - fromFile) % 2 == 0;
		}
	}, {
		key: "getMoveFromAPI",
		value: function getMoveFromAPI(pieces, turn) {
			var _this2 = this;

			var fen = pieces[7].join("") + "/" + pieces[6].join("") + "/" + pieces[5].join("") + "/" + pieces[4].join("") + "/" + pieces[3].join("") + "/" + pieces[2].join("") + "/" + pieces[1].join("") + "/" + pieces[0].join("") + " " + turn + " KQkq - 0 1";
			fen = fen.replace(/\d{2,}/g, function (m) {
				// get all digit combination, contains more than one digit
				return m.split('').reduce(function (sum, v) {
					// split into individual digit
					return sum + Number(v); // parse and add to sum
				}, 0); // set initial value as 0 (sum)
			});
			var data = new FormData();
			data.append('fen', fen);
			fetch('/AI', {
				method: 'POST',
				body: data
			}).then(function (r) {
				return r.text();
			}).then(function (r) {

				//castles
				if (r == "e1g1" && pieces[0][4] == 'K') {
					pieces[0][4] = '1';
					pieces[0][5] = 'R';
					pieces[0][6] = 'K';
					pieces[0][7] = '1';
				} else if (r == "e1c1" && pieces[0][4] == 'K') {
					pieces[0][0] = '1';
					pieces[0][1] = '1';
					pieces[0][2] = 'K';
					pieces[0][3] = 'R';
					pieces[0][4] = '1';
				} else if (r == "e8g8" && pieces[7][4] == 'k') {
					pieces[7][4] = '1';
					pieces[7][5] = 'r';
					pieces[7][6] = 'k';
					pieces[7][7] = '1';
				} else if (r == "e8c8" && pieces[7][4] == 'k') {
					pieces[7][0] = '1';
					pieces[7][1] = '1';
					pieces[7][2] = 'k';
					pieces[7][3] = 'r';
					pieces[7][4] = '1';
				} else {
					///normal
					var file1 = r.charCodeAt(0) - 'a'.charCodeAt(0);
					var rank1 = r.charCodeAt(1) - '1'.charCodeAt(0);
					var file2 = r.charCodeAt(2) - 'a'.charCodeAt(0);
					var rank2 = r.charCodeAt(3) - '1'.charCodeAt(0);
					pieces[rank2][file2] = pieces[rank1][file1];
					pieces[rank1][file1] = "1";
				}

				var newTurn = turn == "w" ? "b" : "w";
				_this2.setState({ selected: null, pieces: pieces, turn: newTurn });
			});
		}
	}, {
		key: "render",
		value: function render() {
			var _this3 = this;

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
										sIdx = _this3.state.selected;
										pieces = _this3.state.pieces.slice();
										if (sIdx == null || pieces[sIdx[1]][sIdx[0]] == "1") {
											_this3.setState({ selected: [colIdx, 7 - rowIdx] });
										} else {

											//castles
											if (sIdx[1] == 0 && sIdx[0] == 4 && colIdx == 6 && pieces[0][4] == 'K') {
												pieces[0][4] = '1';
												pieces[0][5] = 'R';
												pieces[0][6] = 'K';
												pieces[0][7] = '1';
											} else if (sIdx[1] == 0 && sIdx[0] == 4 && colIdx == 2 && pieces[0][4] == 'K') {
												pieces[0][0] = '1';
												pieces[0][1] = '1';
												pieces[0][2] = 'K';
												pieces[0][3] = 'R';
												pieces[0][4] = '1';
											} else if (sIdx[1] == 7 && sIdx[0] == 4 && colIdx == 6 && pieces[7][4] == 'k') {
												pieces[7][4] = '1';
												pieces[7][5] = 'r';
												pieces[7][6] = 'k';
												pieces[7][7] = '1';
											} else if (sIdx[1] == 7 && sIdx[0] == 4 && colIdx == 2 && pieces[7][4] == 'k') {
												pieces[7][0] = '1';
												pieces[7][1] = '1';
												pieces[7][2] = 'k';
												pieces[7][3] = 'r';
												pieces[7][4] = '1';
											} else {
												///normal
												pieces[7 - rowIdx][colIdx] = pieces[sIdx[1]][sIdx[0]];
												pieces[sIdx[1]][sIdx[0]] = "1";
											}
											var newTurn = _this3.state.turn == "w" ? "b" : "w";
											_this3.setState({ selected: null, pieces: pieces, turn: newTurn });
											_this3.getMoveFromAPI(pieces, newTurn);
										}
									},
									style: { outline: "none", border: "none", width: "100px", height: "100px", background: (rowIdx + colIdx) % 2 == 0 ? "gainsboro" : "darkGrey" } },
								piece != "1" && React.createElement("img", { style: { width: "50px", height: "50px" }, src: "/pngs/" + piece + ".png", alt: "" })
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

ReactDOM.createRoot(document.getElementById('root')).render(React.createElement(
	"div",
	{ style: { width: "100%", display: "flex", justifyContent: "center" } },
	React.createElement(ChessBoard, null)
));