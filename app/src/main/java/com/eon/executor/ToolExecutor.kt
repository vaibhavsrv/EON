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

                val contact =
                    data["contact"]?.toString()
                        ?: return

                CallingBridge(context)
                    .call(contact)
            }

            "navigation" -> {

                val destination =
                    data["destination"]?.toString()
                        ?: return

                NavigationBridge(context)
                    .navigate(destination)
            }

            "device_control" -> {

                val setting =
                    data["setting"]?.toString()
                        ?: return

                val actionType =
                    data["action"]?.toString()
                        ?: return

                if (
                    setting == "bluetooth"
                    && actionType == "on"
                ) {

                    DeviceBridge()
                        .bluetoothOn()
                }

                if (
                    setting == "bluetooth"
                    && actionType == "off"
                ) {

                    DeviceBridge()
                        .bluetoothOff()
                }
            }
        }
    }
}