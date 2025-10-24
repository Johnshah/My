#!/bin/bash
# Build Android APK for My

echo "📱 Building Android APK..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if Capacitor is installed
if [ ! -d "node_modules/@capacitor" ]; then
    echo -e "${YELLOW}Installing Capacitor...${NC}"
    npm install @capacitor/core @capacitor/cli @capacitor/android
fi

# Check if Android platform is added
if [ ! -d "android" ]; then
    echo -e "${YELLOW}Adding Android platform...${NC}"
    npx cap add android
fi

# Build frontend
echo -e "${BLUE}Building frontend...${NC}"
cd frontend
npm run build
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Frontend build failed!${NC}"
    exit 1
fi
cd ..

# Sync with Capacitor
echo -e "${BLUE}Syncing with Capacitor...${NC}"
npx cap sync android

# Copy web assets
echo -e "${BLUE}Copying web assets...${NC}"
npx cap copy android

# Update Capacitor
echo -e "${BLUE}Updating Capacitor...${NC}"
npx cap update android

echo ""
echo -e "${YELLOW}Building APK...${NC}"
echo ""
echo "You have two options:"
echo ""
echo "1. ${GREEN}Debug APK${NC} (Quick, for testing)"
echo "   cd android && ./gradlew assembleDebug"
echo "   Output: android/app/build/outputs/apk/debug/app-debug.apk"
echo ""
echo "2. ${GREEN}Release APK${NC} (Optimized, for distribution)"
echo "   cd android && ./gradlew assembleRelease"
echo "   Output: android/app/build/outputs/apk/release/app-release.apk"
echo ""
echo "3. ${BLUE}Android Studio${NC} (GUI, recommended)"
echo "   npx cap open android"
echo "   Then: Build > Build Bundle(s)/APK(s) > Build APK(s)"
echo ""

read -p "Choose option (1/2/3): " choice

case $choice in
    1)
        echo -e "${YELLOW}Building debug APK...${NC}"
        cd android
        ./gradlew assembleDebug
        if [ $? -eq 0 ]; then
            echo ""
            echo -e "${GREEN}✅ Debug APK built successfully!${NC}"
            echo -e "${BLUE}Location:${NC} android/app/build/outputs/apk/debug/app-debug.apk"
            echo ""
            echo "Install on your Poco X6 Pro:"
            echo "  adb install android/app/build/outputs/apk/debug/app-debug.apk"
            echo "Or copy the APK to your phone and install manually"
        else
            echo -e "${RED}❌ Build failed!${NC}"
        fi
        ;;
    2)
        echo -e "${YELLOW}Building release APK...${NC}"
        echo -e "${YELLOW}⚠️  Note: Release APK requires signing${NC}"
        cd android
        ./gradlew assembleRelease
        if [ $? -eq 0 ]; then
            echo ""
            echo -e "${GREEN}✅ Release APK built successfully!${NC}"
            echo -e "${BLUE}Location:${NC} android/app/build/outputs/apk/release/app-release.apk"
        else
            echo -e "${RED}❌ Build failed!${NC}"
        fi
        ;;
    3)
        echo -e "${BLUE}Opening Android Studio...${NC}"
        npx cap open android
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        ;;
esac
