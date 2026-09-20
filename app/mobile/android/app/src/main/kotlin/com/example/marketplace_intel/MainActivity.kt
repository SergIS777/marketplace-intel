package com.example.marketplace_intel

import io.flutter.embedding.android.FlutterActivity
import androidx.window.layout.WindowMetricsCalculator

class MainActivity: FlutterActivity() {
    // ТРЮК: Принудительно вызываем метод, чтобы компилятор D8 
    // увидел его использование и НЕ ВЫРЕЗАЛ из APK при сборке.
    @Suppress("UNUSED_VARIABLE")
    private val keepWindowMetricsCalculator = WindowMetricsCalculator.getOrCreate()
}