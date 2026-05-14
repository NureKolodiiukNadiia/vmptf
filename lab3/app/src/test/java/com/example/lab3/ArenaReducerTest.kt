package com.example.lab3

import com.example.lab3.data.remote.GameStartedPayload
import com.example.lab3.data.remote.RoundResultPayload
import com.example.lab3.data.remote.StateRecoveredPayload
import com.example.lab3.data.socket.SocketEvent
import com.example.lab3.domain.ArenaState
import com.example.lab3.domain.ArenaUiState
import com.example.lab3.domain.Move
import com.example.lab3.ui.arena.reduceArena
import org.junit.Assert.assertEquals
import org.junit.Test

class ArenaReducerTest {
    @Test
    fun gameStarted_movesToPlaying() {
        val state = reduceArena(
            ArenaUiState(state = ArenaState.SEARCHING),
            SocketEvent.GameStarted(GameStartedPayload("room-1", "bob")),
            "u1"
        )
        assertEquals(ArenaState.PLAYING, state.state)
        assertEquals("room-1", state.roomId)
        assertEquals("bob", state.opponentName)
    }

    @Test
    fun roundResult_movesToResult() {
        val state = reduceArena(
            ArenaUiState(state = ArenaState.WAITING_OPPONENT),
            SocketEvent.RoundResult(RoundResultPayload("u1", "rock", "scissors", "you win")),
            "u1"
        )
        assertEquals(ArenaState.RESULT, state.state)
        assertEquals(Move.rock, state.myMove)
        assertEquals(Move.scissors, state.opponentMove)
    }

    @Test
    fun recoveredWithOwnMove_waitingOpponent() {
        val state = reduceArena(
            ArenaUiState(),
            SocketEvent.StateRecovered(StateRecoveredPayload("room-2", "paper", false, "alice")),
            "u1"
        )
        assertEquals(ArenaState.WAITING_OPPONENT, state.state)
        assertEquals(Move.paper, state.myMove)
    }

    @Test
    fun recoveredNoMove_playing() {
        val state = reduceArena(
            ArenaUiState(),
            SocketEvent.StateRecovered(StateRecoveredPayload("room-3", null, false, "alice")),
            "u1"
        )
        assertEquals(ArenaState.PLAYING, state.state)
    }
}
