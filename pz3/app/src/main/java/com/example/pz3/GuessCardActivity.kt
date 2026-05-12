package com.example.pz3

import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import kotlin.random.Random

class GuessCardActivity : AppCompatActivity() {

    private lateinit var cards: List<Button>
    private lateinit var resultText: TextView
    private var winningCardIndex: Int = 0
    private var roundFinished: Boolean = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_guess_card)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = getString(R.string.title_guess_card)

        resultText = findViewById(R.id.resultText)
        cards = listOf(
            findViewById(R.id.card1),
            findViewById(R.id.card2),
            findViewById(R.id.card3)
        )

        cards.forEachIndexed { index, button ->
            button.setOnClickListener { onCardChosen(index) }
        }
        findViewById<Button>(R.id.newGameBtn).setOnClickListener { startNewGame() }

        startNewGame()
    }

    private fun startNewGame() {
        winningCardIndex = Random.nextInt(0, 3)
        roundFinished = false
        resultText.text = getString(R.string.guess_prompt)
        cards.forEach { card ->
            card.isEnabled = true
            card.text = getString(R.string.card_closed)
        }
    }

    private fun onCardChosen(chosenIndex: Int) {
        if (roundFinished) return

        roundFinished = true
        val isWin = chosenIndex == winningCardIndex
        resultText.text = if (isWin) {
            getString(R.string.guess_win)
        } else {
            getString(R.string.guess_lose, winningCardIndex + 1)
        }

        cards.forEachIndexed { index, button ->
            button.isEnabled = false
            button.text = if (index == winningCardIndex) {
                getString(R.string.card_win)
            } else {
                getString(R.string.card_lose)
            }
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
