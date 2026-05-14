package com.example.lab3.data.local

import android.content.Context
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.emptyPreferences
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.example.lab3.domain.UserSession
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.map
import java.io.IOException

private val Context.dataStore by preferencesDataStore(name = "session")

class SessionStore(private val context: Context) {
    private val keyUserId = stringPreferencesKey("user_id")
    private val keyUsername = stringPreferencesKey("username")

    val sessionFlow: Flow<UserSession?> = context.dataStore.data
        .catch { e -> if (e is IOException) emit(emptyPreferences()) else throw e }
        .map { prefs: Preferences ->
            val id = prefs[keyUserId]
            val username = prefs[keyUsername]
            if (id.isNullOrBlank() || username.isNullOrBlank()) null else UserSession(id, username)
        }

    suspend fun save(session: UserSession) {
        context.dataStore.edit {
            it[keyUserId] = session.userId
            it[keyUsername] = session.username
        }
    }

    suspend fun clear() {
        context.dataStore.edit {
            it.remove(keyUserId)
            it.remove(keyUsername)
        }
    }
}
