package com.eon.bridges

import android.content.Context
import android.content.Intent
import android.net.Uri

class CallingBridge(
    private val context: Context
) {

    fun call(number: String) {

        val intent = Intent(
            Intent.ACTION_DIAL,
            Uri.parse("tel:$number")
        )

        intent.addFlags(
            Intent.FLAG_ACTIVITY_NEW_TASK
        )

        context.startActivity(intent)
    }
}