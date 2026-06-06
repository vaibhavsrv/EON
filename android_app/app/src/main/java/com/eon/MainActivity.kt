package com.eon

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.eon.network.BrainClient
import com.eon.executor.ToolRouter
import com.eon.executor.ToolExecutor

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {

            var message by remember {
                mutableStateOf("")
            }

            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp)
            ) {

                Text(
                    text = "EON",
                    style = MaterialTheme.typography.headlineMedium
                )

                Spacer(
                    modifier = Modifier.height(24.dp)
                )

                OutlinedTextField(
                    value = message,
                    onValueChange = {
                        message = it
                    },
                    label = {
                        Text("Command")
                    },
                    modifier = Modifier.fillMaxWidth()
                )

                Spacer(
                    modifier = Modifier.height(16.dp)
                )

                Button(
                    onClick = {

                        BrainClient()
                            .sendMessage(message) { response ->

                                runOnUiThread {

                                    try {

                                        val result =
                                            ToolRouter()
                                                .route(response)

                                        ToolExecutor(this@MainActivity)
                                            .execute(
                                                result.first,
                                                result.second
                                            )

                                    } catch (e: Exception) {

                                        e.printStackTrace()
                                    }
                                }
                            }
                    }
                ) {

                    Text("Execute")
                }
            }
        }
    }
}