plugins { id("com.android.application") }

android {
    namespace = "com.michelslab.igcleaner"
    compileSdk = 35
    defaultConfig {
        applicationId = "com.michelslab.igcleaner"
        minSdk = 26
        targetSdk = 35
        versionCode = 12027
        versionName = "120.27"
    }
    buildTypes { release { isMinifyEnabled = false } }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
}
