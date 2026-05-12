package com.example.pz3

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity

class FileStatsActivity : AppCompatActivity() {

    private lateinit var lettersText: TextView
    private lateinit var spacesText: TextView
    private lateinit var symbolsText: TextView
    private lateinit var statusText: TextView

    private val openDocumentLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        val selectedUri = result.data?.data
        if (selectedUri == null) {
            statusText.text = getString(R.string.file_pick_canceled)
            return@registerForActivityResult
        }
        readAndShowStats(selectedUri)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_file_stats)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = getString(R.string.title_file_stats)

        lettersText = findViewById(R.id.lettersText)
        spacesText = findViewById(R.id.spacesText)
        symbolsText = findViewById(R.id.symbolsText)
        statusText = findViewById(R.id.statusText)

        showStats(FileStats(0, 0, 0))

        findViewById<Button>(R.id.pickFileBtn).setOnClickListener {
            launchFilePicker()
        }
    }

    private fun launchFilePicker() {
        val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE)
            type = "text/*"
        }
        openDocumentLauncher.launch(intent)
    }

    private fun readAndShowStats(uri: Uri) {
        try {
            val content = contentResolver.openInputStream(uri)?.bufferedReader()?.use { it.readText() } ?: ""
            val stats = countFileStats(content)
            showStats(stats)
            statusText.text = ""
        } catch (e: Exception) {
            Toast.makeText(this, getString(R.string.file_read_error), Toast.LENGTH_SHORT).show()
            statusText.text = getString(R.string.file_read_error)
        }
    }

    private fun showStats(stats: FileStats) {
        lettersText.text = getString(R.string.letters, stats.letters)
        spacesText.text = getString(R.string.spaces, stats.spaces)
        symbolsText.text = getString(R.string.symbols, stats.symbols)
    }

    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
