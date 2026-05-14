package com.example.lab3.ui.arena

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.lab3.domain.ArenaState
import com.example.lab3.domain.ArenaUiState
import com.example.lab3.domain.Move

@Composable
fun ArenaScreen(
    ui: ArenaUiState,
    onFind: () -> Unit,
    onCancel: () -> Unit,
    onMove: (Move) -> Unit,
    onNext: () -> Unit,
    onReturn: () -> Unit
) {
    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        if (ui.showReconnectOverlay) Text("Connection lost. Reconnecting...")
        when (ui.state) {
            ArenaState.IDLE -> Button(onClick = onFind) { Text("Find Game") }
            ArenaState.SEARCHING -> {
                CircularProgressIndicator()
                Button(onClick = onCancel) { Text("Cancel") }
            }
            ArenaState.PLAYING, ArenaState.WAITING_OPPONENT -> {
                Text("VS ${ui.opponentName}")
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    Move.entries.forEach { move ->
                        Button(onClick = { onMove(move) }, enabled = ui.myMove == null) { Text(move.name) }
                    }
                }
                if (ui.myMove != null && !ui.opponentHasMoved) Text("Waiting for opponent...")
            }
            ArenaState.RESULT -> {
                Text(ui.resultMessage)
                Text("You: ${ui.myMove?.name ?: "-"} | Them: ${ui.opponentMove?.name ?: "-"}")
                Button(onClick = onNext) { Text("Next Match") }
            }
            ArenaState.ABORTED -> {
                Text("Opponent disconnected.")
                Button(onClick = onReturn) { Text("Return to Lobby") }
            }
        }
    }
}
