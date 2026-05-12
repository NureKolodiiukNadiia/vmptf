package com.example.pz3

import android.os.Bundle
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Spinner
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class HolidaysActivity : AppCompatActivity() {

    private val holidaysByMonth: Map<String, List<String>> = mapOf(
        "January" to listOf("New Year's Day", "Orthodox Christmas"),
        "February" to emptyList(),
        "March" to listOf("International Women's Day"),
        "April" to listOf("Easter (demo)"),
        "May" to listOf("Labour Day", "Victory Day"),
        "June" to listOf("Constitution Day"),
        "July" to emptyList(),
        "August" to listOf("Independence Day"),
        "September" to emptyList(),
        "October" to listOf("Defenders Day"),
        "November" to emptyList(),
        "December" to listOf("Christmas")
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_holidays)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = getString(R.string.title_holidays)

        val spinner = findViewById<Spinner>(R.id.monthSpinner)
        val holidaysText = findViewById<TextView>(R.id.holidaysText)

        val months = holidaysByMonth.keys.toList()
        spinner.adapter = ArrayAdapter(
            this,
            android.R.layout.simple_spinner_item,
            months
        ).also { adapter ->
            adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        }

        spinner.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                val month = months[position]
                val holidays = holidaysByMonth[month].orEmpty()
                holidaysText.text = if (holidays.isEmpty()) {
                    getString(R.string.no_data)
                } else {
                    holidays.joinToString(separator = "\n")
                }
            }

            override fun onNothingSelected(parent: AdapterView<*>?) = Unit
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
