package com.eon.network

import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException

class BrainClient {

    private val client = OkHttpClient()

    fun sendMessage(
        message: String,
        callback: (String) -> Unit
    ) {

        val json =
            """
            {
                "message":"$message"
            }
            """.trimIndent()

        val body =
            json.toRequestBody(
                "application/json".toMediaType()
            )

        val request =
            Request.Builder()
                .url("http://10.0.2.2:8000/chat")
                .post(body)
                .build()

        client.newCall(request)
            .enqueue(
                object : Callback {

                    override fun onFailure(
                        call: Call,
                        e: IOException
                    ) {

                        callback(
                            e.message ?: "Error"
                        )
                    }

                    override fun onResponse(
                        call: Call,
                        response: Response
                    ) {

                        callback(
                            response.body?.string()
                                ?: ""
                        )
                    }
                }
            )
    }
}