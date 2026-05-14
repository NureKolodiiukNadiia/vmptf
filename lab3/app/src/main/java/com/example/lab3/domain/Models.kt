package com.example.lab3.domain

enum class ArenaState {
    IDLE, SEARCHING, PLAYING, WAITING_OPPONENT, RESULT, ABORTED
}

enum class Move {
    rock, paper, scissors
}

data class UserSession(
    val userId: String,
    val username: String
)

data class LeaderboardUser(
    val _id: String,
    val username: String,
    val score: Int,
    val wins: Int
)

data class MatchItem(
    val playedAt: String,
    val opponent: String,
    val winner: String,
    val moves: MatchMoves
)

data class MatchMoves(
    val p1Move: String?,
    val p2Move: String?
)

data class MatchHistoryResponse(
    val total: Int,
    val page: Int,
    val matches: List<MatchItem>
)

data class ArenaUiState(
    val state: ArenaState = ArenaState.IDLE,
    val opponentName: String = "",
    val roomId: String? = null,
    val myMove: Move? = null,
    val opponentMove: Move? = null,
    val opponentHasMoved: Boolean = false,
    val resultMessage: String = "",
    val winnerId: String? = null,
    val isSocketConnected: Boolean = false,
    val showReconnectOverlay: Boolean = false
)
