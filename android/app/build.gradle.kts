// IG Cleaner Android v120.34 — unified account/session + complete list sync
plugins { id("com.android.application") }

val releaseKeystorePath = System.getenv("IGC_ANDROID_KEYSTORE_PATH")
val releaseStorePassword = System.getenv("IGC_ANDROID_KEYSTORE_PASSWORD")
val releaseKeyAlias = System.getenv("IGC_ANDROID_KEY_ALIAS")
val releaseKeyPassword = System.getenv("IGC_ANDROID_KEY_PASSWORD")
val releaseSigningConfigured = listOf(
    releaseKeystorePath,
    releaseStorePassword,
    releaseKeyAlias,
    releaseKeyPassword,
).all { !it.isNullOrBlank() }

android {
    namespace = "com.michelslab.igcleaner"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.michelslab.igcleaner"
        minSdk = 26
        targetSdk = 35
        versionCode = 12034
        versionName = "120.34"
    }

    signingConfigs {
        if (releaseSigningConfigured) {
            create("release") {
                storeFile = file(releaseKeystorePath!!)
                storePassword = releaseStorePassword
                keyAlias = releaseKeyAlias
                keyPassword = releaseKeyPassword
                enableV1Signing = true
                enableV2Signing = true
                enableV3Signing = true
                enableV4Signing = true
            }
        }
    }

    buildTypes {
        debug {
            applicationIdSuffix = ".beta"
            versionNameSuffix = "-beta"
        }
        release {
            isMinifyEnabled = false
            signingConfigs.findByName("release")?.let { signingConfig = it }
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

tasks.matching { it.name == "assembleRelease" || it.name == "bundleRelease" }.configureEach {
    doFirst {
        if (!releaseSigningConfigured) {
            throw GradleException(
                "Production Android signing is required. Set IGC_ANDROID_KEYSTORE_PATH, " +
                    "IGC_ANDROID_KEYSTORE_PASSWORD, IGC_ANDROID_KEY_ALIAS and IGC_ANDROID_KEY_PASSWORD."
            )
        }
    }
}

dependencies {
    implementation("androidx.appcompat:appcompat:1.7.1")
    implementation("androidx.recyclerview:recyclerview:1.4.0")
    implementation("androidx.swiperefreshlayout:swiperefreshlayout:1.1.0")
    implementation("androidx.webkit:webkit:1.12.1")
    implementation("com.google.android.material:material:1.12.0")
}
