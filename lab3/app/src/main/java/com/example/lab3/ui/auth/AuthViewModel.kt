package com.example.lab3.ui.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.example.lab3.data.repository.AuthRepository
import com.example.lab3.domain.UserSession
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class AuthUiState(
    val session: UserSession? = null,
    val loading: Boolean = true,
    val error: String? = null
)

class AuthViewModel(private val repo: AuthRepository) : ViewModel() {
    private val _ui = MutableStateFlow(AuthUiState())
    val ui: StateFlow<AuthUiState> = _ui.asStateFlow()

    init {
        viewModelScope.launch {
            repo.session.collect { session ->
                _ui.value = _ui.value.copy(session = session, loading = false)
            }
        }
    }

    fun login(username: String) {
        if (username.isBlank()) return
        viewModelScope.launch {
            _ui.value = _ui.value.copy(loading = true, error = null)
            val result = repo.login(username)
            _ui.value = if (result.isSuccess) {
                _ui.value.copy(loading = false, session = result.getOrNull())
            } else {
                _ui.value.copy(loading = false, error = result.exceptionOrNull()?.message ?: "Login failed")
            }
        }
    }

    fun logout(onAfter: () -> Unit = {}) {
        viewModelScope.launch {
            repo.logout()
            onAfter()
        }
    }
}

class AuthVmFactory(private val repo: AuthRepository) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        @Suppress("UNCHECKED_CAST")
        return AuthViewModel(repo) as T
    }
}
