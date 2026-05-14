package com.example.lab3.ui.leaderboard

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.height
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun LeaderboardScreen(ui: LeaderboardUiState) {
    if (ui.loading) {
        Column(Modifier.fillMaxSize(), verticalArrangement = Arrangement.Center) {
            CircularProgressIndicator()
        }
        return
    }
    if (ui.error != null) {
        Text("Failed to load leaderboard: ${ui.error}")
        return
    }
    Column(Modifier.fillMaxSize().padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Spacer(modifier = Modifier.height(16.dp))
        Row { Text("Rank   User   Score   WinRate") }
        ui.users.forEachIndexed { i, user ->
            val winRate = if (user.wins > 0) "100%" else "0%"
            Text("${i + 1}   ${user.username}   ${user.score}   $winRate")
        }
    }
}
