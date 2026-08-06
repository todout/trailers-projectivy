package com.projectivy.trailers

import android.annotation.SuppressLint
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.os.Environment
import android.view.KeyEvent
import android.view.View
import android.view.WindowManager
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.FileProvider
import androidx.webkit.WebViewAssetLoader
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream
import java.net.HttpURLConnection
import java.net.URL

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Mantener la pantalla encendida y en pantalla completa
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        window.decorView.systemUiVisibility = (
            View.SYSTEM_UI_FLAG_FULLSCREEN
            or View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
            or View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
        )

        webView = WebView(this)
        setContentView(webView)

        val assetLoader = WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this))
            .build()

        val settings: WebSettings = webView.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.databaseEnabled = true
        settings.mediaPlaybackRequiresUserGesture = false
        settings.allowFileAccess = true
        settings.allowContentAccess = true
        settings.useWideViewPort = true
        settings.loadWithOverviewMode = true
        settings.cacheMode = WebSettings.LOAD_DEFAULT

        // Habilitar aceleración por hardware a nivel de vista
        webView.setLayerType(View.LAYER_TYPE_HARDWARE, null)

        webView.webViewClient = object : WebViewClient() {
            override fun shouldInterceptRequest(
                view: WebView,
                request: WebResourceRequest
            ): WebResourceResponse? {
                return assetLoader.shouldInterceptRequest(request.url)
            }
        }
        webView.webChromeClient = WebChromeClient()

        webView.addJavascriptInterface(JavaScriptInterface(this), "Android")

        // Cargar reproductor HTML de TV desde origen virtual HTTPS para evitar Error 153 de YouTube
        webView.loadUrl("https://appassets.androidplatform.net/assets/tv_player.html")
    }

    class JavaScriptInterface(private val activity: MainActivity) {
        @android.webkit.JavascriptInterface
        fun exitApp() {
            activity.runOnUiThread {
                activity.finish()
            }
        }

        @android.webkit.JavascriptInterface
        fun checkAppUpdate(isManual: Boolean) {
            activity.runOnUiThread {
                activity.performUpdateCheck(isManual)
            }
        }
    }

    fun performUpdateCheck(isManual: Boolean) {
        if (isManual) {
            Toast.makeText(this, "Comprobando actualizaciones...", Toast.LENGTH_SHORT).show()
        }
        Thread {
            try {
                val updateUrl = "https://raw.githubusercontent.com/todout/trailers-projectivy/main/app/src/main/assets/version.json?t=${System.currentTimeMillis()}"
                val connection = URL(updateUrl).openConnection() as HttpURLConnection
                connection.connectTimeout = 8000
                connection.readTimeout = 8000
                val inputStream = connection.inputStream
                val jsonStr = inputStream.bufferedReader().use { it.readText() }
                val json = JSONObject(jsonStr)

                val remoteVersionCode = json.optInt("versionCode", 1)
                val apkUrl = json.optString("apkUrl", "")
                val currentVersionCode = getAppVersionCode()

                if (remoteVersionCode > currentVersionCode && apkUrl.isNotEmpty()) {
                    runOnUiThread {
                        Toast.makeText(this, "Descargando actualización de la app...", Toast.LENGTH_LONG).show()
                    }
                    downloadAndInstallApk(apkUrl)
                } else if (isManual) {
                    runOnUiThread {
                        val vName = try { packageManager.getPackageInfo(packageName, 0).versionName } catch(e: Exception) { "1.0.0" }
                        Toast.makeText(this, "La app está en la versión más reciente (v$vName)", Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: Exception) {
                e.printStackTrace()
                if (isManual) {
                    runOnUiThread {
                        Toast.makeText(this, "No se pudo comprobar la actualización.", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        }.start()
    }

    private fun getAppVersionCode(): Long {
        return try {
            val pInfo = packageManager.getPackageInfo(packageName, 0)
            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.P) {
                pInfo.longVersionCode
            } else {
                @Suppress("DEPRECATION")
                pInfo.versionCode.toLong()
            }
        } catch (e: Exception) {
            1L
        }
    }

    private fun downloadAndInstallApk(apkUrl: String) {
        Thread {
            try {
                val url = URL(apkUrl)
                val conn = url.openConnection() as HttpURLConnection
                conn.instanceFollowRedirects = true
                conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Android TV)")
                conn.connectTimeout = 15000
                conn.readTimeout = 15000

                val responseCode = conn.responseCode
                if (responseCode != HttpURLConnection.HTTP_OK) {
                    runOnUiThread {
                        Toast.makeText(this, "El archivo APK de actualización aún no está subido en GitHub (HTTP $responseCode)", Toast.LENGTH_LONG).show()
                    }
                    return@Thread
                }

                val input = conn.inputStream
                val downloadDir = getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS)
                val apkFile = File(downloadDir, "app-update.apk")
                if (apkFile.exists()) apkFile.delete()

                val output = FileOutputStream(apkFile)
                val buffer = ByteArray(4096)
                var bytesRead: Int
                while (input.read(buffer).also { bytesRead = it } != -1) {
                    output.write(buffer, 0, bytesRead)
                }
                output.close()
                input.close()

                runOnUiThread {
                    installApkFile(apkFile)
                }
            } catch (e: Exception) {
                e.printStackTrace()
                runOnUiThread {
                    Toast.makeText(this, "Error al descargar la actualización: ${e.localizedMessage}", Toast.LENGTH_LONG).show()
                }
            }
        }.start()
    }

    private fun installApkFile(apkFile: File) {
        try {
            val intent = Intent(Intent.ACTION_VIEW)
            val apkUri: Uri = FileProvider.getUriForFile(
                this,
                "$packageName.fileprovider",
                apkFile
            )
            intent.setDataAndType(apkUri, "application/vnd.android.package-archive")
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            startActivity(intent)
        } catch (e: Exception) {
            e.printStackTrace()
            Toast.makeText(this, "Error al iniciar instalador de APK.", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onKeyDown(keyCode: Int, event: KeyEvent?): Boolean {
        if (keyCode == KeyEvent.KEYCODE_BACK) {
            webView.evaluateJavascript("handleAndroidBackKey()") { result ->
                if (result == "false" || result == "null" || result == null) {
                    finish()
                }
            }
            return true
        }

        when (keyCode) {
            KeyEvent.KEYCODE_DPAD_UP -> {
                webView.dispatchKeyEvent(KeyEvent(KeyEvent.ACTION_DOWN, KeyEvent.KEYCODE_DPAD_UP))
                return true
            }
            KeyEvent.KEYCODE_DPAD_DOWN -> {
                webView.dispatchKeyEvent(KeyEvent(KeyEvent.ACTION_DOWN, KeyEvent.KEYCODE_DPAD_DOWN))
                return true
            }
            KeyEvent.KEYCODE_DPAD_LEFT -> {
                webView.dispatchKeyEvent(KeyEvent(KeyEvent.ACTION_DOWN, KeyEvent.KEYCODE_DPAD_LEFT))
                return true
            }
            KeyEvent.KEYCODE_DPAD_RIGHT -> {
                webView.dispatchKeyEvent(KeyEvent(KeyEvent.ACTION_DOWN, KeyEvent.KEYCODE_DPAD_RIGHT))
                return true
            }
            KeyEvent.KEYCODE_DPAD_CENTER, KeyEvent.KEYCODE_ENTER, KeyEvent.KEYCODE_MEDIA_PLAY_PAUSE -> {
                webView.dispatchKeyEvent(KeyEvent(KeyEvent.ACTION_DOWN, KeyEvent.KEYCODE_ENTER))
                return true
            }
        }
        return super.onKeyDown(keyCode, event)
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        webView.evaluateJavascript("handleAndroidBackKey()") { result ->
            if (result == "false" || result == "null" || result == null) {
                finish()
            }
        }
    }
}
