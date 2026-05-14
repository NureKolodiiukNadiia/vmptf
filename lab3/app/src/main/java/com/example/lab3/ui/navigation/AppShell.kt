package com.example.lab3.ui.navigation

import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.example.lab3.ui.arena.ArenaScreen
import com.example.lab3.ui.arena.ArenaViewModel
import com.example.lab3.ui.arena.ArenaVmFactory
import com.example.lab3.ui.auth.AuthViewModel
import com.example.lab3.ui.auth.LoginScreen
import com.example.lab3.ui.history.HistoryScreen
import com.example.lab3.ui.history.HistoryViewModel
import com.example.lab3.ui.history.HistoryVmFactory
import com.example.lab3.ui.leaderboard.LeaderboardScreen
import com.example.lab3.ui.leaderboard.LeaderboardViewModel
import com.example.lab3.ui.leaderboard.LeaderboardVmFactory
import com.example.lab3.util.AppContainer

@Composable
fun AppShell(authVm: AuthViewModel, appContainer: AppContainer) {
    val auth by authVm.ui.collectAsStateWithLifecycle()
    if (auth.session == null) {
        LoginScreen(auth.loading, auth.error, authVm::login)
        return
    }

    val navController = rememberNavController()
    val tabs = listOf("play", "leaderboard", "history")
    val entry by navController.currentBackStackEntryAsState()
    val current = entry?.destination?.route ?: "play"
    val userId = auth.session!!.userId

    val arenaVm: ArenaViewModel = viewModel(factory = ArenaVmFactory(appContainer.socketClient, userId))
    val leaderboardVm: LeaderboardViewModel = viewModel(factory = LeaderboardVmFactory(appContainer.leaderboardRepository))
    val historyVm: HistoryViewModel = viewModel(factory = HistoryVmFactory(appContainer.historyRepository, userId))

    val arenaUi by arenaVm.ui.collectAsStateWithLifecycle()
    val leaderboardUi by leaderboardVm.ui.collectAsStateWithLifecycle()
    val historyUi by historyVm.ui.collectAsStateWithLifecycle()

    LaunchedEffect(Unit) {
        arenaVm.reconnectAttempt()
        leaderboardVm.load()
        historyVm.load(1)
    }

    Scaffold(
        topBar = {
            Column {
                Spacer(modifier = Modifier.height(27.dp))
                Text("User: ${auth.session!!.username}")
            }
        },
        bottomBar = {
            NavigationBar {
                tabs.forEach { tab ->
                    NavigationBarItem(
                        selected = current == tab,
                        onClick = { navController.navigate(tab) },
                        label = { Text(tab) },
                        icon = {}
                    )
                }
            }
        }
    ) { padding ->
        NavHost(navController = navController, startDestination = "play") {
            composable("play") {
                Column(Modifier.padding(padding)) {
                    ArenaScreen(
                        ui = arenaUi,
                        onFind = arenaVm::findGame,
                        onCancel = arenaVm::cancelQueue,
                        onMove = arenaVm::move,
                        onNext = arenaVm::nextMatch,
                        onReturn = arenaVm::returnToLobby
                    )
                    OutlinedButton(onClick = { authVm.logout { arenaVm.disconnect() } }) {
                        Text("Logout")
                    }
                }
            }
            composable("leaderboard") { Column(Modifier.padding(padding)) { LeaderboardScreen(leaderboardUi) } }
            composable("history") { Column(Modifier.padding(padding)) { HistoryScreen(historyUi, historyVm::prev, historyVm::next) } }
        }
    }
}
