package com.eon.ui

import android.app.Application
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.eon.executor.ToolExecutor
import com.eon.executor.ToolRouter
import com.eon.network.BrainClient
import com.eon.voice.TTSManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainViewModel(application: Application) : AndroidViewModel(application) {
    private val context = application.applicationContext
    
    val messages = mutableStateListOf<Message>()
    val isLoading = mutableStateOf(false)
    val isListening = mutableStateOf(false)
    val isSpeaking = mutableStateOf(true) // Default to true for voice feedback
    
    private val brainClient = BrainClient()
    private val toolRouter = ToolRouter()
    private val toolExecutor = ToolExecutor(context)
    private val ttsManager = TTSManager(context)

    fun sendMessage(text: String) {
        if (text.isBlank()) return

        messages.add(Message(text, isUser = true))
        isLoading.value = true

        viewModelScope.launch(Dispatchers.IO) {
            brainClient.sendMessage(text) { response ->
                viewModelScope.launch(Dispatchers.Main) {
                    isLoading.value = false
                    
                    if (response.startsWith("Failed to connect") || response.contains("CLEARTEXT")) {
                        messages.add(Message("Error: $response", isUser = false))
                        return@launch
                    }

                    println("EON RESPONSE: $response")

                    val result = toolRouter.route(response)
                    if (result != null) {
                        // Execute the tool
                        toolExecutor.execute(result.first, result.second)
                        
                        val responseText = "Action: ${result.first}"
                        messages.add(Message(responseText, isUser = false))
                        
                        if (isSpeaking.value) {
                            ttsManager.speak(responseText)
                        }
                    } else {
                        // Regular chat response
                        messages.add(Message(response, isUser = false))
                        if (isSpeaking.value) {
                            ttsManager.speak(response)
                        }
                    }
                }
            }
        }
    }

    fun setListening(listening: Boolean) {
        isListening.value = listening
    }

    fun toggleSpeaking() {
        isSpeaking.value = !isSpeaking.value
        if (!isSpeaking.value) {
            ttsManager.stop()
        }
    }

    override fun onCleared() {
        super.onCleared()
        ttsManager.shutdown()
    }
}