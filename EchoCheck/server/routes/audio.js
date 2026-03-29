const express = require('express');
const multer = require('multer');
const path = require('path');
const audioController = require('../controllers/audioController');
const auth = require('../middleware/auth');

const router = express.Router();

// Configure multer for audio uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/');
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, 'audio-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({
  storage: storage,
  limits: {
    fileSize: 50 * 1024 * 1024 // 50MB max
  },
  fileFilter: (req, file, cb) => {
    // Check file extension
    const extname = path.extname(file.originalname).toLowerCase();
    const allowedExtensions = ['.wav', '.mp3', '.ogg', '.webm', '.m4a', '.aac', '.flac'];
    
    if (allowedExtensions.includes(extname)) {
      return cb(null, true);
    }
    
    // Also check MIME type as backup
    const allowedMimeTypes = [
      'audio/wav',
      'audio/wave',
      'audio/x-wav',
      'audio/mpeg',
      'audio/mp3',
      'audio/ogg',
      'audio/webm',
      'audio/x-m4a',
      'audio/m4a',
      'audio/aac',
      'audio/flac',
      'application/octet-stream' // Some browsers use this for audio
    ];
    
    if (allowedMimeTypes.includes(file.mimetype)) {
      return cb(null, true);
    }
    
    console.log(`❌ Rejected file: ${file.originalname}, mimetype: ${file.mimetype}, extension: ${extname}`);
    cb(new Error('Only audio files allowed (WAV, MP3, OGG, M4A, AAC, FLAC)'));
  }
});

// Routes
router.post('/analyze', auth, upload.single('audio'), audioController.analyzeAudio);
router.get('/history', auth, audioController.getScanHistory);

module.exports = router;