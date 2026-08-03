package com.projectivy.trailers

import android.annotation.SuppressLint
import android.os.Bundle
import android.view.KeyEvent
import android.view.View
import android.view.WindowManager
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity
import androidx.webkit.WebViewAssetLoader

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
        settings.mediaPlaybackRequiresUserGesture = false
        settings.allowFileAccess = true
        settings.allowContentAccess = true
        settings.useWideViewPort = true
        settings.loadWithOverviewMode = true
        settings.cacheMode = WebSettings.LOAD_NO_CACHE
        webView.clearCache(true)

        webView.webViewClient = object : WebViewClient() {
            override fun shouldInterceptRequest(
                view: WebView,
                request: WebResourceRequest
            ): WebResourceResponse? {
                return assetLoader.shouldInterceptRequest(request.url)
            }
        }
        webView.webChromeClient = WebChromeClient()

        // Cargar reproductor HTML de TV desde origen virtual HTTPS para evitar Error 153 de YouTube
        webView.loadUrl("https://appassets.androidplatform.net/assets/tv_player.html")
    }

    override fun onKeyDown(keyCode: Int, event: KeyEvent?): Boolean {
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
            KeyEvent.KEYCODE_BACK -> {
                finish()
                return true
            }
        }
        return super.onKeyDown(keyCode, event)
    }
}
