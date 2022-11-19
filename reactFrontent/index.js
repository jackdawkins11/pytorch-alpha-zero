

class ChessBoard extends React.Component {

	constructor(props){
		super(props)
	
		this.state = { pieces: [
			["R", "N", "B", "Q", "K", "B", "N", "R"],
			["P", "P", "P", "P", "P", "P", "P", "P"],
			[" ", " ", " ", " ", " ", " ", " ", " "], 
			[" ", " ", " ", " ", " ", " ", " ", " "], 
			[" ", " ", " ", " ", " ", " ", " ", " "], 
			[" ", " ", " ", " ", " ", " ", " ", " "], 
			["p", "p", "p", "p", "p", "p", "p", "p"],
			["r", "n", "b", "q", "k", "b", "n", "r"]
		], selected: null, turn: "w" }
	}

	render(){
		console.log( this.state )
		return <div> {this.state.pieces.slice().reverse().map( (row, rowIdx) => {
			return <div key={rowIdx} style={{display: "flex" }} > { row.map( ( piece, colIdx ) => {
				return <button key={colIdx} onClick={ (e) => {
					sIdx = this.state.selected
					pieces = this.state.pieces.slice()
					if( sIdx == null || pieces[ sIdx[ 1 ] ][ sIdx[ 0 ] ] == " " ){
						this.setState( {selected: [colIdx, 7 - rowIdx  ] } )
					}else{
						pieces[ 7 - rowIdx ][ colIdx ] = pieces[ sIdx[ 1 ] ][ sIdx[ 0 ] ]
						pieces[ sIdx[ 1 ] ][ sIdx[ 0 ] ] = " "
						this.setState( {selected: null, pieces: pieces, turn: this.state.turn == "w" ? "b" : "w" } )
					}
				}}
	style={{outline: "none", border: "none", width: "50px", height: "50px", background: (rowIdx + colIdx) % 2 == 0 ? "gainsboro" : "darkGrey" }} >
					{piece != " " &&(<img style={{width: "25px", height: "25px"}} src={"/pngs/" + piece + ".png"} alt={""} />)}
					</button>
			} ) } </div>
		} ) }</div>
	}
}

ReactDOM.createRoot(document.getElementById('root')).render(<ChessBoard />);
