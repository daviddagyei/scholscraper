/**
 * Test script to verify the enhanced audit service functionality
 */
import { auditService } from './src/services/auditService';

async function testAuditServiceEnhancements() {
  console.log('🧪 Testing Enhanced Audit Service Functionality');
  console.log('='.repeat(50));

  try {
    // Test agent start logging
    console.log('1. Testing agent start logging...');
    await auditService.logAgentStart("STEM scholarships for college students 2025");
    console.log('✅ Agent start logged successfully');

    // Test agent completion logging
    console.log('2. Testing agent completion logging...');
    await auditService.logAgentCompletion({
      success: true,
      scholarships_discovered: 5,
      scholarships_saved: 4,
      scholarships_skipped: 1,
      duration_seconds: 45.7
    });
    console.log('✅ Agent completion logged successfully');

    // Test agent failure logging
    console.log('3. Testing agent failure logging...');
    await auditService.logAgentCompletion({
      success: false,
      error: "API rate limit exceeded"
    });
    console.log('✅ Agent failure logged successfully');

    // Test batch import logging
    console.log('4. Testing batch import logging...');
    await auditService.logBatchImport(['test-id-1', 'test-id-2', 'test-id-3']);
    console.log('✅ Batch import logged successfully');

    // Test duplicate detection logging
    console.log('5. Testing duplicate detection logging...');
    await auditService.logDuplicateDetected("Test Scholarship", "existing-id-123");
    console.log('✅ Duplicate detection logged successfully');

    // Test data quality issue logging
    console.log('6. Testing data quality issue logging...');
    await auditService.logDataQualityIssues([
      {
        scholarshipTitle: "Incomplete Scholarship",
        issueType: 'missing_field',
        description: "Missing application URL",
        severity: 'high'
      }
    ]);
    console.log('✅ Data quality issues logged successfully');

    // Test agent activity logging (legacy method)
    console.log('7. Testing legacy agent activity logging...');
    await auditService.logAgentActivity({
      success: true,
      scholarships_discovered: 3,
      scholarships_saved: 3,
      search_criteria: "Test search",
      timestamp: new Date().toISOString(),
      duration_seconds: 30.5,
      pipeline_type: "JSON-first enhanced pipeline"
    });
    console.log('✅ Legacy agent activity logged successfully');

    console.log('\n🎉 All audit service enhancements tested successfully!');
    console.log('The enhanced audit logging is ready for production use.');

  } catch (error) {
    console.error('❌ Error testing audit service:', error);
    process.exit(1);
  }
}

// Only run if this file is executed directly
if (require.main === module) {
  testAuditServiceEnhancements()
    .then(() => process.exit(0))
    .catch(error => {
      console.error('Test failed:', error);
      process.exit(1);
    });
}

export { testAuditServiceEnhancements };
