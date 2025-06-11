#!/usr/bin/env node

/**
 * Script to properly set up Google Sheets with required tabs and structure
 */

import dotenv from 'dotenv';
import { google } from 'googleapis';

// Load environment variables
dotenv.config();

async function setupGoogleSheets() {
  console.log('🔧 Setting up Google Sheets for Scholarship Admin...\n');

  try {
    // Initialize Google Sheets API
    const auth = new google.auth.GoogleAuth({
      credentials: {
        client_email: process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
        private_key: process.env.GOOGLE_PRIVATE_KEY?.replace(/\\n/g, '\n'),
      },
      scopes: ['https://www.googleapis.com/auth/spreadsheets'],
    });

    const sheets = google.sheets({ version: 'v4', auth });
    const spreadsheetId = process.env.GOOGLE_SHEETS_ID;

    if (!spreadsheetId) {
      throw new Error('GOOGLE_SHEETS_ID environment variable is required');
    }

    console.log('📊 Connected to Google Sheets API successfully');
    console.log('📋 Spreadsheet ID:', spreadsheetId);

    // Get current spreadsheet info
    const spreadsheetInfo = await sheets.spreadsheets.get({
      spreadsheetId,
    });

    console.log('📄 Spreadsheet Title:', spreadsheetInfo.data.properties?.title);
    
    const existingSheets = spreadsheetInfo.data.sheets || [];
    const existingSheetNames = existingSheets.map(sheet => sheet.properties?.title);
    
    console.log('📑 Existing sheets:', existingSheetNames.join(', '));

    // Define the sheets we need
    const requiredSheets = [
      {
        name: 'Scholarships',
        headers: [
          'ID', 'Title', 'Description', 'Amount', 'Deadline', 'Eligibility',
          'Requirements', 'Application URL', 'Provider', 'Category', 'Status',
          'Created Date', 'Modified Date', 'Created By', 'Last Modified By'
        ]
      },
      {
        name: 'AuditLog',
        headers: [
          'Timestamp', 'Action', 'Scholarship ID', 'User Email',
          'Changes Made', 'Previous Values', 'IP Address'
        ]
      },
      {
        name: 'Categories',
        headers: [
          'Category Name', 'Description', 'Color Code', 'Active Status'
        ]
      }
    ];

    // Create missing sheets
    const requests: any[] = [];
    
    for (const sheetDef of requiredSheets) {
      if (!existingSheetNames.includes(sheetDef.name)) {
        console.log(`➕ Creating sheet: ${sheetDef.name}`);
        requests.push({
          addSheet: {
            properties: {
              title: sheetDef.name,
              gridProperties: {
                rowCount: 1000,
                columnCount: sheetDef.headers.length
              }
            }
          }
        });
      } else {
        console.log(`✅ Sheet already exists: ${sheetDef.name}`);
      }
    }

    // Execute sheet creation requests
    if (requests.length > 0) {
      await sheets.spreadsheets.batchUpdate({
        spreadsheetId,
        requestBody: {
          requests
        }
      });
      console.log('✅ All required sheets created successfully\n');
    } else {
      console.log('✅ All required sheets already exist\n');
    }

    // Add headers to each sheet
    console.log('📝 Adding headers to sheets...');
    
    for (const sheetDef of requiredSheets) {
      try {
        console.log(`📋 Adding headers to ${sheetDef.name}...`);
        
        await sheets.spreadsheets.values.update({
          spreadsheetId,
          range: `${sheetDef.name}!A1:${String.fromCharCode(64 + sheetDef.headers.length)}1`,
          valueInputOption: 'RAW',
          requestBody: {
            values: [sheetDef.headers]
          }
        });
        
        console.log(`✅ Headers added to ${sheetDef.name}`);
      } catch (error: any) {
        console.log(`⚠️  Warning: Could not add headers to ${sheetDef.name}:`, error.message);
      }
    }

    // Add sample data to Categories sheet
    console.log('\n📊 Adding sample categories...');
    try {
      const sampleCategories = [
        ['Academic Merit', 'Scholarships based on academic performance', '#2196F3', 'Active'],
        ['Community Service', 'Awards for community involvement', '#4CAF50', 'Active'],
        ['Entrepreneurship', 'For students with business initiatives', '#FF9800', 'Active'],
        ['Diversity & Inclusion', 'Supporting underrepresented students', '#9C27B0', 'Active'],
        ['Environmental', 'For environmental science and sustainability', '#8BC34A', 'Active'],
        ['Need-Based', 'Financial need-based assistance', '#F44336', 'Active'],
        ['STEM', 'Science, Technology, Engineering, Math', '#00BCD4', 'Active'],
        ['Arts & Humanities', 'Creative and liberal arts fields', '#E91E63', 'Active'],
        ['Athletics', 'Sports and physical achievement', '#FF5722', 'Active'],
        ['General', 'General scholarships for all students', '#607D8B', 'Active']
      ];

      await sheets.spreadsheets.values.update({
        spreadsheetId,
        range: 'Categories!A2:D11',
        valueInputOption: 'RAW',
        requestBody: {
          values: sampleCategories
        }
      });
      
      console.log('✅ Sample categories added successfully');
    } catch (error: any) {
      console.log('⚠️  Warning: Could not add sample categories:', error.message);
    }

    // Add sample scholarship data
    console.log('\n📚 Adding sample scholarship data...');
    try {
      const currentDate = new Date().toISOString();
      const futureDate1 = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]; // 30 days from now
      const futureDate2 = new Date(Date.now() + 60 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]; // 60 days from now
      
      const sampleScholarships = [
        [
          'scholarship-1',
          'Tech Excellence Scholarship',
          'Supporting outstanding students pursuing technology and computer science degrees with a focus on innovation and academic excellence.',
          '$5,000',
          futureDate1,
          'Undergraduate students, Computer Science majors, GPA 3.5+',
          'Academic transcripts, Portfolio of projects, Letter of recommendation',
          'https://example.com/apply/tech-excellence',
          'Tech Innovation Foundation',
          'STEM',
          'active',
          currentDate,
          currentDate,
          'admin@example.com',
          'admin@example.com'
        ],
        [
          'scholarship-2',
          'Community Impact Award',
          'Recognizing students who have made significant contributions to their communities through volunteer work and social initiatives.',
          '$3,000',
          futureDate2,
          'High school seniors, College students, 50+ volunteer hours',
          'Community service documentation, Personal statement, Reference letters',
          'https://example.com/apply/community-impact',
          'Community Leaders Foundation',
          'Community Service',
          'active',
          currentDate,
          currentDate,
          'admin@example.com',
          'admin@example.com'
        ]
      ];

      await sheets.spreadsheets.values.update({
        spreadsheetId,
        range: 'Scholarships!A2:O3',
        valueInputOption: 'RAW',
        requestBody: {
          values: sampleScholarships
        }
      });
      
      console.log('✅ Sample scholarship data added successfully');
    } catch (error: any) {
      console.log('⚠️  Warning: Could not add sample scholarships:', error.message);
    }

    console.log('\n🎉 Google Sheets setup completed successfully!');
    console.log('\n📋 Summary:');
    console.log('   ✅ Scholarships sheet - Ready for scholarship data');
    console.log('   ✅ AuditLog sheet - Ready for activity tracking');
    console.log('   ✅ Categories sheet - Populated with sample categories');
    console.log('   ✅ Sample data - Added for testing');
    
    console.log('\n🔗 Your Google Sheets URL:');
    console.log(`   https://docs.google.com/spreadsheets/d/${spreadsheetId}/edit`);
    
    console.log('\n🚀 Next steps:');
    console.log('   1. Run: npm run dev');
    console.log('   2. Visit: http://localhost:5000/health');
    console.log('   3. Test the API endpoints');
    console.log('   4. Start building the admin interface!');

  } catch (error: any) {
    console.error('❌ Setup failed:', error.message);
    
    if (error.message.includes('Unable to parse range')) {
      console.log('\n💡 This usually means the sheet tabs need to be created first.');
      console.log('   The script will handle this automatically.');
    } else if (error.message.includes('permission')) {
      console.log('\n💡 Permission error. Please ensure:');
      console.log('   1. The service account has access to the Google Sheets');
      console.log('   2. The sheet is shared with the service account email');
      console.log('   3. The service account has Editor permissions');
    }
    
    process.exit(1);
  }
}

// Run the setup
setupGoogleSheets();
