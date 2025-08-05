const mongoose = require('mongoose');

// MongoDB Atlas Setup Verification
async function verifySetup() {
  console.log('🔍 MongoDB Atlas Setup Verification');
  console.log('=====================================');
  
  // Test different password variations
  const passwordVariations = [
    'CallmeFOX@007',
    'CallmeFOX007',
    'CallmeFOX@007!',
    'CallmeFOX007!'
  ];
  
  for (let i = 0; i < passwordVariations.length; i++) {
    const password = passwordVariations[i];
    const encodedPassword = encodeURIComponent(password);
    const uri = `mongodb+srv://pmonishreddy19:${encodedPassword}@cluster0.7m6bwkx.mongodb.net/invensis-recruiters?retryWrites=true&w=majority&appName=Cluster0`;
    
    console.log(`\n🧪 Testing password variation ${i + 1}: ${password}`);
    
    try {
      await mongoose.connect(uri, { 
        serverSelectionTimeoutMS: 5000,
        socketTimeoutMS: 5000 
      });
      
      console.log('✅ SUCCESS! This password works!');
      console.log(`📝 Working password: ${password}`);
      console.log(`🔗 Working connection string: ${uri.replace(encodedPassword, '***')}`);
      
      // Test database operations
      const testCollection = mongoose.connection.collection('test');
      await testCollection.insertOne({ test: 'verification', timestamp: new Date() });
      console.log('✅ Database write test: PASSED');
      
      await testCollection.deleteOne({ test: 'verification' });
      console.log('✅ Database cleanup test: PASSED');
      
      await mongoose.disconnect();
      console.log('✅ Connection closed successfully');
      
      return password; // Return the working password
      
    } catch (error) {
      console.log(`❌ Failed with password: ${password}`);
      console.log(`   Error: ${error.message}`);
      
      if (i === passwordVariations.length - 1) {
        console.log('\n🔧 All password variations failed. Please check:');
        console.log('1. Your MongoDB Atlas username: pmonishreddy19');
        console.log('2. Your MongoDB Atlas password');
        console.log('3. Your IP address is whitelisted in MongoDB Atlas');
        console.log('4. Your cluster is running and accessible');
        console.log('5. Your database user has the correct permissions');
        
        console.log('\n📋 To verify your credentials:');
        console.log('1. Go to MongoDB Atlas dashboard');
        console.log('2. Navigate to Database Access');
        console.log('3. Check your username and reset password if needed');
        console.log('4. Go to Network Access and add your IP (or 0.0.0.0/0 for all IPs)');
      }
    }
  }
  
  return null;
}

// Run verification
verifySetup().then(workingPassword => {
  if (workingPassword) {
    console.log('\n🎉 MongoDB Atlas setup verified successfully!');
    console.log(`💾 Update your .env.production files with password: ${workingPassword}`);
  } else {
    console.log('\n❌ MongoDB Atlas setup verification failed');
    console.log('Please check your credentials and try again');
  }
}).catch(error => {
  console.error('❌ Verification script error:', error);
}); 