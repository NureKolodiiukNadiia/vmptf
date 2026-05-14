package com.example.lab3.ui.arena

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.example.lab3.data.socket.SocketClient
import com.example.lab3.domain.ArenaState
import com.example.lab3.domain.ArenaUiState
import com.example.lab3.domain.Move
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class ArenaViewModel(
    private val socketClient: SocketClient,
    private val userId: String
) : ViewModel() {
    private val _ui = MutableStateFlow(ArenaUiState())
    val ui: StateFlow<ArenaUiState> = _ui.asStateFlow()

    init {
        socketClient.connect(userId)
        bindEvents()
    }

    private fun bindEvents() {
        viewModelScope.launch {
            socketClient.events().collect {
                _ui.value = reduceArena(_ui.value, it, userId)
            }
        }
    }

    fun reconnectAttempt() = socketClient.reconnectAttempt(userId)

    fun findGame() {
        _ui.value = _ui.value.copy(state = ArenaState.SEARCHING)
        socketClient.joinQueue(userId)
    }

    fun cancelQueue() {
        socketClient.leaveQueue(userId)
        _ui.value = _ui.value.copy(state = ArenaState.IDLE)
    }

    fun move(move: Move) {
        val roomId = _ui.value.roomId ?: return
        socketClient.makeMove(roomId, userId, move)
        _ui.value = _ui.value.copy(myMove = move, state = ArenaState.WAITING_OPPONENT)
    }

    fun nextMatch() {
        _ui.value = ArenaUiState(isSocketConnected = _ui.value.isSocketConnected)
    }

    fun returnToLobby() {
        _ui.value = _ui.value.copy(state = ArenaState.IDLE)
    }

    fun disconnect() {
        socketClient.disconnect()
    }
}

class ArenaVmFactory(
    private val socketClient: SocketClient,
    private val userId: String
) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        @Suppress("UNCHECKED_CAST")
        return ArenaViewModel(socketClient, userId) as T
    }
}
