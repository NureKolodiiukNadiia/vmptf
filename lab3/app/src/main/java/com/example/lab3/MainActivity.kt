package com.example.lab3

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.lab3.ui.auth.AuthViewModel
import com.example.lab3.ui.auth.AuthVmFactory
import com.example.lab3.ui.navigation.AppShell
import com.example.lab3.util.AppContainer

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val container = AppContainer(applicationContext)
        setContent {
            Surface(color = MaterialTheme.colorScheme.background) {
                val authVm: AuthViewModel = viewModel(factory = AuthVmFactory(container.authRepository))
                AppShell(authVm = authVm, appContainer = container)
            }
        }
    }
}
