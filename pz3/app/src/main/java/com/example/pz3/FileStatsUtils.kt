package com.example.pz3

data class FileStats(
    val letters: Int,
    val spaces: Int,
    val symbols: Int
)

fun countFileStats(content: String): FileStats {
    var letters = 0
    var spaces = 0
    var symbols = 0

    content.forEach { ch ->
        when {
            ch.isLetter() -> {
                letters++
                symbols++
            }
            ch.isWhitespace() -> {
                spaces++
                symbols++
            }
            else -> symbols++
        }
    }

    return FileStats(letters, spaces, symbols)
}
