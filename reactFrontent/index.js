

class ChessBoard extends React.Component {

	constructor(props){
		super(props)

		this.state = { pieces: [
			["R", "N", "B", "Q", "K", "B", "N", "R"],
			["P", "P", "P", "P", "P", "P", "P", "P"],
			["1", "1", "1", "1", "1", "1", "1", "1"], 
			["1", "1", "1", "1", "1", "1", "1", "1"], 
			["1", "1", "1", "1", "1", "1", "1", "1"], 
			["1", "1", "1", "1", "1", "1", "1", "1"], 
			["p", "p", "p", "p", "p", "p", "p", "p"],
			["r", "n", "b", "q", "k", "b", "n", "r"]
		], selected: null, turn: "w" }
	}

	castleCheck( pieces, fromRank, fromFile, toRank, toFile ){
		return (pieces[ fromRank ][fromFile] == 'k' || pieces[fromRank][fromFile] == 'K') && ( ( toFile - fromFile ) % 2 == 0 )
	}

	getMoveFromAPI(pieces, turn){
		let fen = pieces[7].join("") + "/" +
			pieces[6].join("") + "/" +
			pieces[5].join("") + "/" +
			pieces[4].join("") + "/" +
			pieces[3].join("") + "/" +
			pieces[2].join("") + "/" +
			pieces[1].join("") + "/" +
			pieces[0].join("") + " " + turn + " KQkq - 0 1"
		fen = fen.replace(/\d{2,}/g, function(m) { // get all digit combination, contains more than one digit
			return m.split('').reduce(function(sum, v) { // split into individual digit
				return sum + Number(v) // parse and add to sum
			}, 0) // set initial value as 0 (sum)
		})
		var data = new FormData()
		data.append('fen', fen)
		fetch('/AI', {
			method: 'POST',
			body: data
		}).then( (r) => { return r.text() } ).then( (r) => {

			//castles
			if( r == "e1g1" && pieces[0][4] == 'K' ){
				pieces[0][4] = '1';
				pieces[0][5] = 'R';
				pieces[0][6] = 'K';
				pieces[0][7] = '1';
			}else if( r == "e1c1" && pieces[0][4] == 'K' ){
				pieces[0][0] = '1';
				pieces[0][1] = '1';
				pieces[0][2] = 'K';
				pieces[0][3] = 'R';
				pieces[0][4] = '1';
			}else if( r == "e8g8" && pieces[7][4] == 'k' ){
				pieces[7][4] = '1';
				pieces[7][5] = 'r';
				pieces[7][6] = 'k';
				pieces[7][7] = '1';
			}else if( r == "e8c8" && pieces[7][4] == 'k' ){
				pieces[7][0] = '1';
				pieces[7][1] = '1';
				pieces[7][2] = 'k';
				pieces[7][3] = 'r';
				pieces[7][4] = '1';
			}else{ ///normal
				let file1 = r.charCodeAt(0) - 'a'.charCodeAt(0)
				let rank1 = r.charCodeAt(1) - '1'.charCodeAt(0)
				let file2 = r.charCodeAt(2) - 'a'.charCodeAt(0)
				let rank2 = r.charCodeAt(3) - '1'.charCodeAt(0)
				pieces[ rank2 ][ file2 ] = pieces[ rank1 ][ file1 ]
				pieces[ rank1 ][ file1 ] = "1"
			}

			let newTurn = turn == "w" ? "b" : "w"
			this.setState( {selected: null, pieces: pieces, turn: newTurn } )
		})
	}

	render(){
		return <div> {this.state.pieces.slice().reverse().map( (row, rowIdx) => {
			return <div key={rowIdx} style={{display: "flex" }} > { row.map( ( piece, colIdx ) => {
				return <button key={colIdx} onClick={ (e) => {
					sIdx = this.state.selected
					pieces = this.state.pieces.slice()
					if( sIdx == null || pieces[ sIdx[ 1 ] ][ sIdx[ 0 ] ] == "1" ){
						this.setState( {selected: [colIdx, 7 - rowIdx  ] } )
					}else{

						//castles
						if( sIdx[1] == 0 && sIdx[0] == 4 && colIdx == 6 && pieces[0][4] == 'K' ){
							pieces[0][4] = '1';
							pieces[0][5] = 'R';
							pieces[0][6] = 'K';
							pieces[0][7] = '1';
						}else if( sIdx[1] == 0 && sIdx[0] == 4 && colIdx == 2 && pieces[0][4] == 'K' ){
							pieces[0][0] = '1';
							pieces[0][1] = '1';
							pieces[0][2] = 'K';
							pieces[0][3] = 'R';
							pieces[0][4] = '1';
						}else if( sIdx[1] == 7 && sIdx[0] == 4 && colIdx == 6 && pieces[7][4] == 'k' ){
							pieces[7][4] = '1';
							pieces[7][5] = 'r';
							pieces[7][6] = 'k';
							pieces[7][7] = '1';
						}else if( sIdx[1] == 7 && sIdx[0] == 4 && colIdx == 2 && pieces[7][4] == 'k' ){
							pieces[7][0] = '1';
							pieces[7][1] = '1';
							pieces[7][2] = 'k';
							pieces[7][3] = 'r';
							pieces[7][4] = '1';
						}else{ ///normal
							pieces[ 7 - rowIdx ][ colIdx ] = pieces[ sIdx[ 1 ] ][ sIdx[ 0 ] ]
							pieces[ sIdx[ 1 ] ][ sIdx[ 0 ] ] = "1"
						}
						let newTurn = this.state.turn == "w" ? "b" : "w"
						this.setState( {selected: null, pieces: pieces, turn: newTurn } )
						this.getMoveFromAPI( pieces, newTurn )
					}
				}}
				style={{outline: "none", border: "none", width: "100px", height: "100px", background: (rowIdx + colIdx) % 2 == 0 ? "gainsboro" : "darkGrey" }} >
					{piece != "1" &&(<img style={{width: "50px", height: "50px"}} src={"/pngs/" + piece + ".png"} alt={""} />)}
					</button>
			} ) } </div>
		} ) }</div>
	}
}

ReactDOM.createRoot(document.getElementById('root')).render(
	<div style={{width: "100%", display: "flex", justifyContent: "center"}}>
		<ChessBoard /> 
	</div>);
