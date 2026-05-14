package com.example.lab3.ui.history

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.example.lab3.data.repository.HistoryRepository
import com.example.lab3.domain.MatchItem
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class HistoryUiState(
    val loading: Boolean = true,
    val page: Int = 1,
    val total: Int = 0,
    val matches: List<MatchItem> = emptyList(),
    val error: String? = null
)

class HistoryViewModel(
    private val repo: HistoryRepository,
    private val userId: String
) : ViewModel() {
    private val _ui = MutableStateFlow(HistoryUiState())
    val ui: StateFlow<HistoryUiState> = _ui.asStateFlow()

    fun load(page: Int = _ui.value.page) {
        viewModelScope.launch {
            _ui.value = _ui.value.copy(loading = true, error = null, page = page)
            val result = repo.load(userId, page, 10)
            _ui.value = if (result.isSuccess) {
                val body = result.getOrThrow()
                HistoryUiState(loading = false, page = body.page, total = body.total, matches = body.matches)
            } else {
                _ui.value.copy(loading = false, error = result.exceptionOrNull()?.message ?: "Load failed")
            }
        }
    }

    fun prev() = if (_ui.value.page > 1) load(_ui.value.page - 1) else Unit
    fun next() = if (_ui.value.page * 10 < _ui.value.total) load(_ui.value.page + 1) else Unit
}

class HistoryVmFactory(
    private val repo: HistoryRepository,
    private val userId: String
) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        @Suppress("UNCHECKED_CAST")
        return HistoryViewModel(repo, userId) as T
    }
}
