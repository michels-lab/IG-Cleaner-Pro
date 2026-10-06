// IG Cleaner Android v120.32 — unified account/session + complete list sync
plugins { id("com.android.application") }

android {
    namespace = "com.michelslab.igcleaner"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.michelslab.igcleaner"
        minSdk = 26
        targetSdk = 35
        versionCode = 12032
        versionName = "120.32"
    }

    buildTypes {
        debug {
            applicationIdSuffix = ".beta"
            versionNameSuffix = "-beta"
        }
        release {
            isMinifyEnabled = false
        }
    }

    sourceSets {
        getByName("main") {
            assets.setSrcDirs(listOf("../../desktop"))
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

dependencies {
    implementation("androidx.appcompat:appcompat:1.7.1")
    implementation("androidx.recyclerview:recyclerview:1.4.0")
    implementation("androidx.swiperefreshlayout:swiperefreshlayout:1.1.0")
    implementation("androidx.webkit:webkit:1.12.1")
    implementation("com.google.android.material:material:1.12.0")
}
