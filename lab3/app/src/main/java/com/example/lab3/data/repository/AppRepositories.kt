package com.example.lab3.data.repository

import com.example.lab3.data.local.SessionStore
import com.example.lab3.data.remote.ApiService
import com.example.lab3.data.remote.LoginRequest
import com.example.lab3.domain.LeaderboardUser
import com.example.lab3.domain.MatchHistoryResponse
import com.example.lab3.domain.UserSession
import kotlinx.coroutines.flow.Flow

class AuthRepository(
    private val api: ApiService,
    private val sessionStore: SessionStore
) {
    val session: Flow<UserSession?> = sessionStore.sessionFlow

    suspend fun login(username: String): Result<UserSession> = runCatching {
        val response = api.login(LoginRequest(username.trim()))
        if (!response.isSuccessful || response.body() == null) error("Login failed")
        val body = response.body()!!
        val session = UserSession(body.userId, body.username)
        sessionStore.save(session)
        session
    }

    suspend fun logout() {
        sessionStore.clear()
    }
}

class LeaderboardRepository(private val api: ApiService) {
    suspend fun load(): Result<List<LeaderboardUser>> = runCatching {
        val response = api.leaderboard()
        if (!response.isSuccessful || response.body() == null) error("Leaderboard failed")
        response.body()!!
    }
}

class HistoryRepository(private val api: ApiService) {
    suspend fun load(userId: String, page: Int, limit: Int = 10): Result<MatchHistoryResponse> = runCatching {
        val response = api.history(userId, page, limit)
        if (!response.isSuccessful || response.body() == null) error("History failed")
        response.body()!!
    }
}
