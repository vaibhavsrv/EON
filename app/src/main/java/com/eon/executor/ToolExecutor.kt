package com.eon.executor

import android.content.Context
import com.eon.bridges.CallingBridge
import com.eon.bridges.NavigationBridge
import com.eon.bridges.DeviceBridge

class ToolExecutor(
    private val context: Context
) {

    fun execute(
        action: String,
        data: Map<String, Any>
    ) {

        when (action) {

            "call" -> {
                val contact = data["contact"]?.toString() ?: run {
                    println("EON ERROR = Missing 'contact' for call action")
                    return
                }
                CallingBridge(context).call(contact)
            }

            "navigation" -> {
                val destination = data["destination"]?.toString() ?: run {
                    println("EON ERROR = Missing 'destination' for navigation action")
                    return
                }
                println("EON INFO = Navigating to: $destination")
                NavigationBridge(context).navigate(destination)
            }

            "device_control" -> {
                val setting = data["setting"]?.toString() ?: run {
                    println("EON ERROR = Missing 'setting' for device_control action")
                    return
                }
                val actionType = data["action"]?.toString() ?: run {
                    println("EON ERROR = Missing 'action' for device_control action")
                    return
                }
                println("EON INFO = Device Control: $setting -> $actionType")
                if (setting == "bluetooth") {
                    if (actionType == "on") DeviceBridge().bluetoothOn()
                    else if (actionType == "off") DeviceBridge().bluetoothOff()
                }
            }

            else -> {
                println("EON ERROR = Unknown action: $action")
            }
        }
    }
}