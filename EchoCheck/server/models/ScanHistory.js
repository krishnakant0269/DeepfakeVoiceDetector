const mongoose = require('mongoose');

const ScanHistorySchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  fileName: String,
  fileSize: Number,
  duration: Number, // in seconds
  
  // AI Analysis Results
  deepfakeDetected: {
    type: Boolean,
    required: true
  },
  deepfakeConfidence: {
    type: Number,
    min: 0,
    max: 1
  },
  scamDetected: {
    type: Boolean,
    required: true
  },
  scamConfidence: {
    type: Number,
    min: 0,
    max: 1
  },
  riskLevel: {
    type: String,
    enum: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
  },
  
  // Transcript & Analysis
  transcript: String,
  scamIndicators: [{
    category: String,
    matchedPattern: String
  }],
  
  // Metadata
  audioUrl: String, // S3 or local path (optional)
  ipAddress: String,
  userAgent: String,
  
  createdAt: {
    type: Date,
    default: Date.now
  }
});

// Index for fast queries
ScanHistorySchema.index({ userId: 1, createdAt: -1 });
ScanHistorySchema.index({ riskLevel: 1 });

module.exports = mongoose.model('ScanHistory', ScanHistorySchema);