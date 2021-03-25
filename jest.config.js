module.exports = {
    "verbose": true,
    "testMatch": [
      "**/tests/frontend/**/*.test.js"
    ],
    "moduleNameMapper": {
        '\\.(css|less|sass)$': "<rootDir>/tests/frontend/_style-mock.js",
        "\\.(eot|svg|ttf|woff)$": "<rootDir>/tests/frontend/_file-mock.js"
    },
    "moduleFileExtensions": ["js", "jsx"],
    "moduleDirectories": ["node_modules", "smartsexplore/frontend"],
    "collectCoverageFrom": ["smartsexplore/frontend/**/*.js"],
    // only output JSON, this will be merged with instrumented Selenium tests.
    // from all that data merged together, HTML&text output will be generated :)
    "coverageReporters": ["json"],
    "coverageDirectory": "coverage/frontend",
    "setupFiles": ["./jest.setup.js"],
    "setupFilesAfterEnv": ["jest-expect-message"]
};
