package com.example.lab3.ui.arena

import com.example.lab3.data.socket.SocketEvent
import com.example.lab3.domain.ArenaState
import com.example.lab3.domain.ArenaUiState
import com.example.lab3.domain.Move

fun reduceArena(state: ArenaUiState, event: SocketEvent, userId: String): ArenaUiState {
    return when (event) {
        SocketEvent.Connected -> state.copy(isSocketConnected = true, showReconnectOverlay = false)
        SocketEvent.Disconnected -> state.copy(isSocketConnected = false, showReconnectOverlay = true)
        is SocketEvent.GameStarted -> state.copy(
            state = ArenaState.PLAYING,
            roomId = event.payload.roomId,
            opponentName = event.payload.opponentName,
            myMove = null,
            opponentMove = null,
            opponentHasMoved = false,
            resultMessage = "",
            winnerId = null
        )
        is SocketEvent.OpponentMoved -> state.copy(opponentHasMoved = event.payload.hasMoved)
        is SocketEvent.RoundResult -> state.copy(
            state = ArenaState.RESULT,
            myMove = Move.valueOf(event.payload.myMove),
            opponentMove = Move.valueOf(event.payload.opponentMove),
            opponentHasMoved = true,
            resultMessage = event.payload.message,
            winnerId = event.payload.winnerId
        )
        is SocketEvent.StateRecovered -> {
            val myMove = event.payload.myMove?.let { Move.valueOf(it) }
            state.copy(
                roomId = event.payload.roomId,
                opponentName = event.payload.opponentName,
                myMove = myMove,
                opponentHasMoved = event.payload.opponentHasMoved,
                state = when {
                    myMove == null -> ArenaState.PLAYING
                    event.payload.opponentHasMoved -> ArenaState.RESULT
                    else -> ArenaState.WAITING_OPPONENT
                }
            )
        }
        SocketEvent.OpponentDisconnected -> state.copy(state = ArenaState.ABORTED)
        SocketEvent.StateNotFound -> state
        is SocketEvent.Error -> {
            if (event.payload.code in listOf("SERVER_ERROR", "INVALID_PAYLOAD", "ALREADY_IN_QUEUE", "NOT_IN_QUEUE")) {
                state.copy(state = ArenaState.IDLE)
            } else state
        }
        is SocketEvent.QueueLeft -> state.copy(state = ArenaState.IDLE)
    }
}
