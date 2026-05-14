package com.example.lab3.data.remote

import com.example.lab3.domain.LeaderboardUser
import com.example.lab3.domain.MatchHistoryResponse
import com.google.gson.annotations.SerializedName

data class LoginRequest(val username: String)

data class LoginResponse(
    val userId: String,
    val username: String
)

data class ErrorResponse(val error: String?)

typealias LeaderboardResponse = List<LeaderboardUser>
typealias HistoryResponse = MatchHistoryResponse

data class SocketErrorPayload(
    val message: String? = null,
    val code: String? = null
)

data class GameStartedPayload(
    val roomId: String,
    val opponentName: String
)

data class OpponentMovedPayload(
    val hasMoved: Boolean
)

data class RoundResultPayload(
    val winnerId: String? = null,
    val myMove: String,
    val opponentMove: String,
    val message: String
)

data class StateRecoveredPayload(
    val roomId: String,
    val myMove: String? = null,
    val opponentHasMoved: Boolean,
    val opponentName: String
)

data class GenericMessagePayload(
    @SerializedName("message") val message: String? = null
)
