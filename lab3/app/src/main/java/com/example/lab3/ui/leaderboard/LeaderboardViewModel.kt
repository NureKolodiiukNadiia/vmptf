package com.example.lab3.ui.leaderboard

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.example.lab3.data.repository.LeaderboardRepository
import com.example.lab3.domain.LeaderboardUser
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class LeaderboardUiState(
    val loading: Boolean = true,
    val users: List<LeaderboardUser> = emptyList(),
    val error: String? = null
)

class LeaderboardViewModel(private val repo: LeaderboardRepository) : ViewModel() {
    private val _ui = MutableStateFlow(LeaderboardUiState())
    val ui: StateFlow<LeaderboardUiState> = _ui.asStateFlow()

    fun load() {
        viewModelScope.launch {
            _ui.value = _ui.value.copy(loading = true, error = null)
            val result = repo.load()
            _ui.value = if (result.isSuccess) {
                LeaderboardUiState(loading = false, users = result.getOrDefault(emptyList()))
            } else {
                LeaderboardUiState(loading = false, error = result.exceptionOrNull()?.message ?: "Load failed")
            }
        }
    }
}

class LeaderboardVmFactory(private val repo: LeaderboardRepository) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        @Suppress("UNCHECKED_CAST")
        return LeaderboardViewModel(repo) as T
    }
}
