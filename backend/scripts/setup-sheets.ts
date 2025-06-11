#!/usr/bin/env node

/**
 * Script to set up Google Sheets with the required structure
 */

import dotenv from 'dotenv';
import { google } from 'googleapis';

// Load environment variables
dotenv.config();

async function setupGoogleSheets() {
  console.log('🔧 Setting up Google Sheets structure...\n');

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

    console.log('1. Getting current spreadsheet info...');
    
    // Get current spreadsheet info
    const spreadsheetInfo = await sheets.spreadsheets.get({
      spreadsheetId,
    });

    const existingSheets = spreadsheetInfo.data.sheets?.map(sheet => sheet.properties?.title) || [];
    console.log('   Existing sheets:', existingSheets.join(', '));

    // Define required sheets
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

    console.log('\n2. Creating missing sheets and headers...');

    for (const sheetConfig of requiredSheets) {
      if (!existingSheets.includes(sheetConfig.name)) {
        console.log(`   Creating sheet: ${sheetConfig.name}`);
        
        // Create the sheet
        await sheets.spreadsheets.batchUpdate({
          spreadsheetId,
          requestBody: {
            requests: [{
              addSheet: {
                properties: {
                  title: sheetConfig.name,
                  gridProperties: {
                    rowCount: 1000,
                    columnCount: sheetConfig.headers.length
                  }
                }
              }
            }]
          }
        });
      } else {
        console.log(`   Sheet already exists: ${sheetConfig.name}`);
      }

      // Add headers
      console.log(`   Adding headers to: ${sheetConfig.name}`);
      try {
        await sheets.spreadsheets.values.update({
          spreadsheetId,
          range: `${sheetConfig.name}!A1`,
          valueInputOption: 'RAW',
          requestBody: {
            values: [sheetConfig.headers],
          },
        });
        console.log(`   ✅ Headers added to ${sheetConfig.name}`);
      } catch (error: any) {
        console.log(`   ❌ Error adding headers to ${sheetConfig.name}:`, error.message);
      }
    }

    console.log('\n3. Adding sample categories...');
    
    const sampleCategories = [
      ['Academic Merit', 'Merit-based scholarships for academic excellence', '#4CAF50', 'Active'],
      ['Community Service', 'Scholarships for community involvement', '#2196F3', 'Active'],
      ['Entrepreneurship', 'Business and innovation scholarships', '#FF9800', 'Active'],
      ['Diversity & Inclusion', 'Scholarships promoting diversity', '#9C27B0', 'Active'],
      ['Environmental', 'Environmental and sustainability scholarships', '#4CAF50', 'Active'],
      ['Need-Based', 'Financial need-based scholarships', '#F44336', 'Active'],
      ['STEM', 'Science, Technology, Engineering, Math', '#3F51B5', 'Active'],
      ['Arts & Humanities', 'Creative and liberal arts scholarships', '#E91E63', 'Active'],
      ['Athletics', 'Sports and athletic scholarships', '#FF5722', 'Active'],
      ['General', 'General scholarships', '#607D8B', 'Active']
    ];

    try {
      await sheets.spreadsheets.values.append({
        spreadsheetId,
        range: 'Categories!A2',
        valueInputOption: 'RAW',
        requestBody: {
          values: sampleCategories,
        },
      });
      console.log('   ✅ Sample categories added');
    } catch (error: any) {
      console.log('   ❌ Error adding sample categories:', error.message);
    }

    console.log('\n4. Adding sample scholarship data...');
    
    const sampleScholarships = [
      [
        'scholarship-1',
        'Merit Excellence Scholarship',
        'A prestigious scholarship for outstanding academic achievement in STEM fields. Recipients demonstrate exceptional performance in mathematics, science, and technology courses.',
        '$5,000',
        '2025-12-15',
        'Undergraduate students, GPA 3.5+, STEM majors',
        'Academic transcripts, Letter of recommendation, Personal essay',
        'https://example.com/apply/merit',
        'STEM Education Foundation',
        'Academic Merit',
        'active',
        new Date().toISOString(),
        new Date().toISOString(),
        'system',
        'system'
      ],
      [
        'scholarship-2',
        'Community Impact Award',
        'Supporting students who have made significant contributions to their communities through volunteer work and social initiatives.',
        '$3,000',
        '2026-01-31',
        'High school seniors, College students, Volunteer experience required',
        'Community service documentation, Personal statement, Reference letters',
        'https://example.com/apply/community',
        'Community Leaders Foundation',
        'Community Service',
        'active',
        new Date().toISOString(),
        new Date().toISOString(),
        'system',
        'system'
      ]
    ];

    try {
      await sheets.spreadsheets.values.append({
        spreadsheetId,
        range: 'Scholarships!A2',
        valueInputOption: 'RAW',
        requestBody: {
          values: sampleScholarships,
        },
      });
      console.log('   ✅ Sample scholarships added');
    } catch (error: any) {
      console.log('   ❌ Error adding sample scholarships:', error.message);
    }

    console.log('\n🎉 Google Sheets setup completed successfully!');
    console.log('\n📊 Your spreadsheet now has:');
    console.log('   - Scholarships sheet with sample data');
    console.log('   - AuditLog sheet for tracking changes');
    console.log('   - Categories sheet with predefined categories');
    console.log('\n🔗 View your sheet at:');
    console.log(`   https://docs.google.com/spreadsheets/d/${spreadsheetId}/edit`);
    
    console.log('\n✅ Next steps:');
    console.log('   1. Run: npm run dev');
    console.log('   2. Test the API at: http://localhost:5000/health');
    console.log('   3. Try the endpoints in the README');

  } catch (error: any) {
    console.error('❌ Setup failed:', error.message);
    if (error.response?.data?.error) {
      console.error('   Google API Error:', error.response.data.error);
    }
    process.exit(1);
  }
}

// Run the setup
setupGoogleSheets();
