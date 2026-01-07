/**
 * Build Script for Creating Standalone .exe Application
 * Bundles frontend + backend into a single executable
 */
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Building Standalone Application...\n');

// Step 1: Build frontend
console.log('📦 Step 1: Building frontend...');
process.chdir('frontend');
execSync('npm install', { stdio: 'inherit' });
execSync('npm run build', { stdio: 'inherit' });
process.chdir('..');

// Step 2: Package with Electron Builder
console.log('\n📦 Step 2: Packaging with Electron Builder...');
process.chdir('frontend');
execSync('npm run build:win', { stdio: 'inherit' });
process.chdir('..');

console.log('\n✅ Build complete!');
console.log('📁 Output: frontend/build/');

