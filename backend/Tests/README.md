### Make sure to install pytest

# How to run test suite
Navigate to frontend directory
`cd frontend/`
Run script
```
npm run test-backend
```

If this does not work, you can test without a script
`cd backend && pytest Tests/`

# Unit test naming criteria
These criteria must be followed or pytest will not run the test(s).
1. testing files must begin with "test_"
2. testing classes must begin with "test" or "Test" (classes are not required)
3. testing methods must begin with "test_"