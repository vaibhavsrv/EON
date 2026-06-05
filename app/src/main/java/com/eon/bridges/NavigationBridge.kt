package com.eon.bridges

import android.content.Context
import android.content.Intent
import android.net.Uri

class NavigationBridge(
    private val context: Context
) {

    fun navigate(
        destination: String
    ) {

        val intent = Intent(
            Intent.ACTION_VIEW,
            Uri.parse(
                "google.navigation:q=$destination"
            )
        )

        intent.addFlags(
            Intent.FLAG_ACTIVITY_NEW_TASK
        )

        context.startActivity(intent)
    }
}