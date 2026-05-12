package com.example.pz3

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        supportActionBar?.title = getString(R.string.title_main)

        findViewById<Button>(R.id.btnHolidays).setOnClickListener {
            startActivity(Intent(this, HolidaysActivity::class.java))
        }
        findViewById<Button>(R.id.btnGuessCard).setOnClickListener {
            startActivity(Intent(this, GuessCardActivity::class.java))
        }
        findViewById<Button>(R.id.btnFileStats).setOnClickListener {
            startActivity(Intent(this, FileStatsActivity::class.java))
        }
    }
}
