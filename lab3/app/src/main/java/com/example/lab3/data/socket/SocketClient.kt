package com.example.lab3.data.socket

import com.example.lab3.BuildConfig
import com.example.lab3.data.remote.GameStartedPayload
import com.example.lab3.data.remote.OpponentMovedPayload
import com.example.lab3.data.remote.RoundResultPayload
import com.example.lab3.data.remote.SocketErrorPayload
import com.example.lab3.data.remote.StateRecoveredPayload
import com.example.lab3.domain.Move
import com.google.gson.Gson
import io.socket.client.IO
import io.socket.client.Socket
import io.socket.emitter.Emitter
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import org.json.JSONObject

sealed class SocketEvent {
    data object Connected : SocketEvent()
    data object Disconnected : SocketEvent()
    data class GameStarted(val payload: GameStartedPayload) : SocketEvent()
    data class QueueLeft(val ok: Boolean) : SocketEvent()
    data class OpponentMoved(val payload: OpponentMovedPayload) : SocketEvent()
    data class RoundResult(val payload: RoundResultPayload) : SocketEvent()
    data class StateRecovered(val payload: StateRecoveredPayload) : SocketEvent()
    data object StateNotFound : SocketEvent()
    data object OpponentDisconnected : SocketEvent()
    data class Error(val payload: SocketErrorPayload) : SocketEvent()
}

class SocketClient {
    private val gson = Gson()
    private var socket: Socket? = null

    fun connect(userId: String) {
        if (socket != null) return
        val options = IO.Options().apply {
            extraHeaders = mapOf("ngrok-skip-browser-warning" to listOf("true"))
        }
        socket = IO.socket(BuildConfig.SOCKET_BASE_URL, options).apply { connect() }
    }

    fun disconnect() {
        socket?.disconnect()
        socket = null
    }

    fun reconnectAttempt(userId: String) {
        socket?.emit("reconnect_attempt", JSONObject(mapOf("userId" to userId)))
    }

    fun joinQueue(userId: String) {
        socket?.emit("join_queue", JSONObject(mapOf("userId" to userId)))
    }

    fun leaveQueue(userId: String) {
        socket?.emit("leave_queue", JSONObject(mapOf("userId" to userId)))
    }

    fun makeMove(roomId: String, userId: String, move: Move) {
        socket?.emit(
            "make_move",
            JSONObject(mapOf("roomId" to roomId, "userId" to userId, "move" to move.name))
        )
    }

    fun events(): Flow<SocketEvent> = callbackFlow {
        val s = socket ?: run {
            close()
            return@callbackFlow
        }
        fun parse(arg: Any?): String = arg?.toString() ?: "{}"

        val onConnect = Emitter.Listener { _: Array<Any> -> trySend(SocketEvent.Connected) }
        val onDisconnect = Emitter.Listener { _: Array<Any> -> trySend(SocketEvent.Disconnected) }
        val onGameStarted = Emitter.Listener { args: Array<Any> ->
            trySend(SocketEvent.GameStarted(gson.fromJson(parse(args.firstOrNull()), GameStartedPayload::class.java)))
        }
        val onQueueLeft = Emitter.Listener { _: Array<Any> -> trySend(SocketEvent.QueueLeft(true)) }
        val onOpponentMoved = Emitter.Listener { args: Array<Any> ->
            trySend(SocketEvent.OpponentMoved(gson.fromJson(parse(args.firstOrNull()), OpponentMovedPayload::class.java)))
        }
        val onRoundResult = Emitter.Listener { args: Array<Any> ->
            trySend(SocketEvent.RoundResult(gson.fromJson(parse(args.firstOrNull()), RoundResultPayload::class.java)))
        }
        val onStateRecovered = Emitter.Listener { args: Array<Any> ->
            trySend(SocketEvent.StateRecovered(gson.fromJson(parse(args.firstOrNull()), StateRecoveredPayload::class.java)))
        }
        val onStateNotFound = Emitter.Listener { _: Array<Any> -> trySend(SocketEvent.StateNotFound) }
        val onOpponentDisconnected = Emitter.Listener { _: Array<Any> -> trySend(SocketEvent.OpponentDisconnected) }
        val onError = Emitter.Listener { args: Array<Any> ->
            trySend(SocketEvent.Error(gson.fromJson(parse(args.firstOrNull()), SocketErrorPayload::class.java)))
        }

        s.on(Socket.EVENT_CONNECT, onConnect)
        s.on(Socket.EVENT_DISCONNECT, onDisconnect)
        s.on("game_started", onGameStarted)
        s.on("queue_left", onQueueLeft)
        s.on("opponent_moved", onOpponentMoved)
        s.on("round_result", onRoundResult)
        s.on("state_recovered", onStateRecovered)
        s.on("state_not_found", onStateNotFound)
        s.on("opponent_disconnected", onOpponentDisconnected)
        s.on("error", onError)

        awaitClose {
            s.off(Socket.EVENT_CONNECT, onConnect)
            s.off(Socket.EVENT_DISCONNECT, onDisconnect)
            s.off("game_started", onGameStarted)
            s.off("queue_left", onQueueLeft)
            s.off("opponent_moved", onOpponentMoved)
            s.off("round_result", onRoundResult)
            s.off("state_recovered", onStateRecovered)
            s.off("state_not_found", onStateNotFound)
            s.off("opponent_disconnected", onOpponentDisconnected)
            s.off("error", onError)
        }
    }
}
