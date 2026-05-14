package com.example.lab3.util

import android.content.Context
import com.example.lab3.data.local.SessionStore
import com.example.lab3.data.remote.NetworkModule
import com.example.lab3.data.repository.AuthRepository
import com.example.lab3.data.repository.HistoryRepository
import com.example.lab3.data.repository.LeaderboardRepository
import com.example.lab3.data.socket.SocketClient

class AppContainer(context: Context) {
    private val api = NetworkModule.apiService
    private val sessionStore = SessionStore(context)

    val authRepository = AuthRepository(api, sessionStore)
    val leaderboardRepository = LeaderboardRepository(api)
    val historyRepository = HistoryRepository(api)
    val socketClient = SocketClient()
}
