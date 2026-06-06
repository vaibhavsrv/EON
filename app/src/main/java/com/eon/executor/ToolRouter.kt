package com.eon.executor

import org.json.JSONObject

class ToolRouter {

    fun route(
        response: String
    ): Pair<String, Map<String, Any>>? {

        return try {
            val json = JSONObject(response)

            val action =
                json.getString("action")

            val dataObject =
                json.getJSONObject("data")

            val data =
                mutableMapOf<String, Any>()

            val keys =
                dataObject.keys()

            while (keys.hasNext()) {

                val key =
                    keys.next()

                data[key] =
                    dataObject.getString(key)
            }

            Pair(
                action,
                data
            )
        } catch (e: Exception) {
            println("EON ERROR = Parsing failed: ${e.message}")
            null
        }
    }
}