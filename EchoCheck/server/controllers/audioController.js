const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000';

exports.analyzeAudio = async (req, res) => {
  try {
    console.log(`📁 Received file: ${req.file.filename} (${req.file.size} bytes)`);

    // Create form data for AI service
    const formData = new FormData();
    formData.append('file', fs.createReadStream(req.file.path));

    // Call AI service
    const aiResponse = await axios.post(`${AI_SERVICE_URL}/analyze`, formData, {
      headers: formData.getHeaders(),
      timeout: 120000,
      maxContentLength: Infinity,
      maxBodyLength: Infinity
    });

    console.log('✅ AI analysis complete');
    console.log('📊 AI Response:', JSON.stringify(aiResponse.data, null, 2));

    // Delete uploaded file
    fs.unlinkSync(req.file.path);

    // Ensure all fields are present
    const results = {
      isDeepfake: aiResponse.data.is_deepfake || false,
      deepfakeConfidence: aiResponse.data.deepfake_confidence || 0,
      deepfakeDetails: aiResponse.data.deepfake_details || null,
      isScam: aiResponse.data.is_scam || false,
      scamConfidence: aiResponse.data.scam_confidence || 0,
      transcript: aiResponse.data.transcript || '',
      indicators: aiResponse.data.scam_indicators || [],
      riskLevel: aiResponse.data.risk_level || 'LOW',
      voiceType: aiResponse.data.voice_type || 'UNKNOWN',  // CRITICAL FIELD!
      detectionMethod: aiResponse.data.detection_method || 'unknown'
    };

    console.log('📤 Sending to frontend:', JSON.stringify(results, null, 2));

    res.json({
      success: true,
      results: results
    });

  } catch (error) {
    console.error('❌ Analysis error:', error.message);
    
    if (error.response) {
      console.error('AI Service Error:', error.response.data);
      console.error('Status:', error.response.status);
    }

    // Cleanup file on error
    if (req.file && fs.existsSync(req.file.path)) {
      fs.unlinkSync(req.file.path);
    }

    res.status(500).json({
      error: 'Analysis failed',
      details: error.response?.data || error.message
    });
  }
};

exports.getScanHistory = async (req, res) => {
  res.json({
    success: true,
    history: []
  });
};