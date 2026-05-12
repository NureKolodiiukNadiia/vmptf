package com.example.pz3

import org.junit.Assert.assertEquals
import org.junit.Test

class FileStatsUtilsTest {

    @Test
    fun `empty string returns zeroes`() {
        val stats = countFileStats("")
        assertEquals(0, stats.letters)
        assertEquals(0, stats.spaces)
        assertEquals(0, stats.symbols)
    }

    @Test
    fun `mixed content is counted by rules`() {
        val stats = countFileStats("Ab c!\n9")
        assertEquals(3, stats.letters)
        assertEquals(2, stats.spaces)
        assertEquals(2, stats.symbols)
    }
}
