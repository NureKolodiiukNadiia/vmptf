package com.example.lab3.ui.history

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun HistoryScreen(ui: HistoryUiState, onPrev: () -> Unit, onNext: () -> Unit) {
    if (ui.loading) {
        Column(Modifier.fillMaxSize(), verticalArrangement = Arrangement.Center) {
            CircularProgressIndicator()
        }
        return
    }
    if (ui.error != null) {
        Text("Failed to load history: ${ui.error}")
        return
    }
    Column(Modifier.fillMaxSize().padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Spacer(modifier = Modifier.height(16.dp))
        ui.matches.forEach {
            val result = when (it.winner) {
                "you" -> "Win"
                "draw" -> "Draw"
                else -> "Loss"
            }
            Text("${it.opponent} | ${it.playedAt.take(10)} | You:${it.moves.p1Move ?: "-"} Them:${it.moves.p2Move ?: "-"} | $result")
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = onPrev, enabled = ui.page > 1) { Text("Previous") }
            Text("Page ${ui.page}")
            Button(onClick = onNext, enabled = ui.page * 10 < ui.total) { Text("Next") }
        }
    }
}
