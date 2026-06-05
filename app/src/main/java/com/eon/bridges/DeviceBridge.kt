package com.eon.bridges

import android.bluetooth.BluetoothAdapter

class DeviceBridge {

    fun bluetoothOn() {

        BluetoothAdapter
            .getDefaultAdapter()
            ?.enable()
    }

    fun bluetoothOff() {

        BluetoothAdapter
            .getDefaultAdapter()
            ?.disable()
    }
}