import React, { useState, useRef, useEffect } from 'react';
import './TranslatePage.css';
import { FaRegClipboard, FaDownload, FaUpload, FaHistory, FaJsSquare, FaPython, FaCuttlefish, FaJava, FaRust, FaArrowRight, FaTrash } from 'react-icons/fa';
import CodeMirror from '@uiw/react-codemirror';
import { material } from '@uiw/codemirror-theme-material';
import { javascript } from '@codemirror/lang-javascript';
import { python } from '@codemirror/lang-python';
import { java } from '@codemirror/lang-java';
import { cpp } from '@codemirror/lang-cpp';
import { rust } from '@codemirror/lang-rust';
import { vscodeDark, vscodeDarkInit } from '@uiw/codemirror-theme-vscode';
import axios from 'axios';
import { SITE_URL, FLASK_URL, Logout } from '../../vars';
import { isExpired } from '../../vars';
import { ToastContainer, toast } from 'react-toastify';
import TranslationFeedback from './TranslationFeedback';
import { useNavigate } from 'react-router-dom';
import DisplayFeedback from './DisplayFeedback';

const TranslatePage = () => {
  const [inputText, setInputText] = useState('');
  const [outputText, setOutputText] = useState('');
  const [sourceLanguage, setSourceLanguage] = useState('JavaScript');
  const [targetLanguage, setTargetLanguage] = useState('Python');
  const [isLoading, setIsLoading] = useState(false);
  const [showLoading, setShowLoading] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState('');
  const [isTranslating, setIsTranslating] = useState(false);
  const [showSidebar, setShowSidebar] = useState(false);
  const [translationHistory, setTranslationHistory] = useState([]);
  const [sortMethod, setSortMethod] = useState('date');
  const [dateFilter, setDateFilter] = useState('');
  const [sourceLanguageFilter, setSourceLanguageFilter] = useState('');
  const [targetLanguageFilter, setTargetLanguageFilter] = useState('');
  const [charCount, setCharCount] = useState(0); // State to track character count
  const maxCharLimit =  16383; // Define maximum character limit
  const [showDots, setShowDots] = useState(false);
  const [currentTranslationId, setCurrentTranslationId] = useState(null);

  const handleCheck = (message) => {
    switch (message){
      case 'stop': case 'from_db':
        return "Translation Success!!"
        break;
      case 'length':
        return "Unsuccessful Translation :((, input text is too long"
        break;
      case 'content_filter':
        return "Code content was flagged by openai content filters"
        break;
      case '401':
        return "OpenAI API Authentication failed "
        break;
      case '403':
        return "Country not supported with OpenAI"
        break;
      case '429':
        return "Please wait you sent too many characters"
        break;
      case '500':
        return "Unknown OpenAI server error"
        break;
      case '503':
        return "OpenAI server is currently being overloaded, please before submitting again"
        break;
      default:
        return message
        break;
    }
  }
  
  const navigate = useNavigate()

  const handleClickOnHistoryItem = (item) => {
    populateCodeMirror(item.original_code, item.translated_code, item.source_language, item.target_language);
    console.log(`inside translate page ${item.translation_id}`);
    console.log(typeof item.translation_id);
    setCurrentTranslationId(item.translation_id);  // Store the current translation ID in state
    console.log(`inside translate CHECKING VAR ${currentTranslationId}`);
    console.log(typeof currentTranslationId);
  };


  const filterTranslationHistory = (history) => {
    return history
      .filter((item) => {
        // Filter by date if a date filter is set
        return dateFilter ? item.formattedDate === dateFilter : true;
      })
      .filter((item) => {
        // Filter by source language if a source language filter is set
        return sourceLanguageFilter ? item.source_language === sourceLanguageFilter : true;
      })
      .filter((item) => {
        // Filter by target language if a target language filter is set
        return targetLanguageFilter ? item.target_language === targetLanguageFilter : true;
      });
  };


  // Function to get the appropriate icon based on the language
  const extensions = {
    'JavaScript': ['.js', '.jsx'],
    'Python': ['.py'],
    'C++': ['.cpp', '.cxx', '.cc', '.h', '.hh', '.hpp'],
    'Java': ['.java'],
    'Rust': ['.rs'],
  };

  const languageIcons = {
    'JavaScript': FaJsSquare,
    'Python': FaPython,
    'C++': FaCuttlefish,
    'Java': FaJava,
    'Rust': FaRust,
  }

  // Function to create icon elements with proper classes
  const getLanguageIconElement = (language) => {
    const iconClass = language.replace('+', 'p').toLowerCase(); // Replace '+' with 'p' and make it lowercase
    const IconComponent = languageIcons[language];
    return IconComponent ? <IconComponent className={`language-icon ${iconClass}`} /> : null;
  };

  const handleClick = () => {
    setIsTranslating(true);
    handleTranslate();
  };

  axios.get(`${FLASK_URL}/getApiStatus`)
    .then((response) => {
      const res = response.data;
      console.log(`Status: ${res.code} ${res.reason}`);
      // by javascript selects background
      document.querySelector('.status').style.background = setBackgroundStats(res);
    }).catch((error) => {
      if (error.response) {
        console.log(error.response);
        console.log(error.response.status);
        console.log(error.response.headers);
      }
    });

  // checks response to determine background clor
  function setBackgroundStats(res) {
    if (res.code === 200) {
      return 'green';
    }
    else {
      return 'red';
    }
  }
  
  const fileInputRef = useRef(null);

  const getLanguageExtension = (language) => {
    switch (language) {
      case 'JavaScript':
        return javascript();
      case 'Python':
        return python();
      case 'C++':
        return cpp(); // Make sure you have the correct import for C++
      case 'Java':
        return java();
      case 'Rust':
        return rust(); // Assuming you find a suitable Rust extension
      default:
        return javascript(); // Default case to handle any unforeseen values
    }
  };

  const populateCodeMirror = (original_code, translated_code, source_lang, target_lang) => {
    setInputText(original_code);
    setOutputText(translated_code);
    setSourceLanguage(source_lang); // Update the source language dropdown
    setTargetLanguage(target_lang); // Update the target language dropdown
  };

  const filteredTranslationHistory = filterTranslationHistory(translationHistory);

  const groupByDate = filteredTranslationHistory.reduce((group, item) => {
    const { formattedDate } = item;
    group[formattedDate] = group[formattedDate] ?? [];
    group[formattedDate].push(item);
    return group;
  }, {});

  useEffect(() => {
    const sessionToken = localStorage.getItem("sessionToken");
    axios.post(`${FLASK_URL}/translationHistory`, { sessionToken: sessionToken })
      .then(response => {
        // Process the data to format dates as 'Today', 'Yesterday', etc.
        res = response.data;
        if (res.success) {
          const processedHistory = res.rows.map(item => {
            // Create a new Date object from item.submission_date
            const submissionDate = new Date(item.submission_date);
            // Format the date
            const formattedDate = formatSubmissionDate(submissionDate);
            // Return a new object with the formatted date
            return { ...item, formattedDate };
          });
          // Set the processed history to state
          setTranslationHistory(processedHistory);
        }
        else if (res.hasError) {
          console.log(`Response has error: ${res.hasError}`);
          console.log(`Error message: ${res.errorMessage}`);
        }
        if (res.logout) {
          toast(handleCheck("Please login again."), {
            className: 'fail',
            autoClose: 2000
          })
          Logout(navigate)
        }
      })
      .catch(error => console.error("Error fetching translation history:", error));
  }, [setTranslationHistory, sortMethod, dateFilter, sourceLanguageFilter, targetLanguageFilter]); // Add any other dependencies if needed
  //reruns whenever dependencies change 

  // Helper function to format the date
  function formatSubmissionDate(date) {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday';
    } else {
      return 'Previous 30 Days';
    }
  }

  // Function to trigger the hidden file input
  const handleUploadClick = () => {
    fileInputRef.current.click();
  };

  // Function to handle file input change
  const handleFileInputChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

  

    // Ensure the sourceLanguage matches the keys in the extensions object
    const expectedExtensions = extensions[sourceLanguage];

    if (!expectedExtensions) {
      console.error('No expected extensions found for the selected source language.');
      return;
    }

    const fileExtension = `.${file.name.split('.').pop()}`;

    if (!expectedExtensions.includes(fileExtension)) {
      toast(handleCheck(`Please upload a file with the following extensions: ${expectedExtensions.join(', ')}`), {
        className: 'fail',
        autoClose: 2000
      });
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      setInputText(event.target.result);
    };
    reader.readAsText(file);
  };


  // Example validation functions for each language
  const validateJavaScript = (text) => {
    // Check for common JavaScript patterns and syntax
    return /function|var|let|const|=>|console\.log\(/.test(text);
  };

  const validatePython = (text) => {
    // Enhanced Python validation to exclude non-Python code and include Python-specific syntax
    // Check for clear signs of Python code
    const pythonSigns = /def |import |print\(|if |elif |else:|for |in |range\(|class |self/.test(text);
    // Check for patterns common in JavaScript/JSX, indicating it's likely not Python
    const nonPythonSigns = /import .* from '.*'|class .* extends|return \(<\/?[\w\s="/.]+>\);|export default /.test(text);

    // Consider valid if it looks like Python and doesn't contain patterns common in JavaScript/JSX
    return pythonSigns && !nonPythonSigns;
  };

  const validateCpp = (text) => {
    // Check for C++ specific indicators, including common library includes and main function
    return /#include <iostream>|using namespace std;|int main\(\)|cout <<|cin >>/.test(text);
  };

  const validateJava = (text) => {
    // Enhanced to include class definition, main method, and common print statement
    return /class |import java.|public static void main|System\.out\.println\(/.test(text);
  };

  const validateRust = (text) => {
    // Check for Rust-specific syntax, including function declaration and common imports
    return /fn |use |let |println!\(|struct |enum |impl |mod |pub /.test(text);
  };

  const isValidInput = (text, language) => {
    switch (language) {
      case 'JavaScript':
        return validateJavaScript(text);
      case 'Python':
        return validatePython(text);
      case 'C++':
        return validateCpp(text);
      case 'Java':
        return validateJava(text);
      case 'Rust':
        return validateRust(text);
      default:
        return false; // Consider invalid if language is not recognized
    }
  };


  const handleTranslate = () => {
    if (typeof inputText !== 'string' || inputText.trim() === '') {
      toast(handleCheck('inputText is undefined, not a string, or empty'), {
        className: 'fail',
        autoClose: 2000
      });
      console.error('inputText is undefined, not a string, or empty');
      setIsTranslating(false);
      return;
    }

    // Validate input text before translating
    if (!isValidInput(inputText, sourceLanguage)) {
      toast(handleCheck(`Invalid ${sourceLanguage} code. Please check your input and try again.`), {
        className: 'fail',
        autoClose: 2000
    });
      setIsTranslating(false)
      return; // Prevent translation from proceeding
    }

    // Proceed with translation if input is valid
    setNotificationMessage("Translation in progress...");
    setShowLoading(true);
    getTranslation();
  };

  const confirmDelete = (id) => {
    if (window.confirm("Are you sure you want to delete this translation?")) {
      axios.post(`${FLASK_URL}/deleteTranslations`, {
        sessionToken: localStorage.getItem("sessionToken"),
        ids: [id]
      }).then(response => {
        if (response.data.success) {
          const updatedHistory = translationHistory.filter(item => item.translation_id !== id);
          setTranslationHistory(updatedHistory);
          // Clear the input and output if the deleted translation was displayed
          if (inputText || outputText) {
            const currentDisplayed = translationHistory.find(item => item.translation_id === id);
            if (currentDisplayed && (inputText === currentDisplayed.original_code && outputText === currentDisplayed.translated_code)) {
              setInputText('');
              setOutputText('');
            }
          }
          toast(handleCheck("Translation deleted successfully."),  {
            className: 'success',
            autoClose: 2000
          });
        } else {
          toast(handleCheck("Failed to delete translation: " + response.data.errorMessage), {
            className: 'fail',
            autoClose: 2000
          });
        }
      }).catch(error => {
        console.error("Deletion error:", error);
      });
    }
  };

  const confirmClearAll = () => {
    if (window.confirm("Are you sure you want to clear all translation history?")) {
      axios.post(`${FLASK_URL}/deleteTranslations`, {
        sessionToken: localStorage.getItem("sessionToken"),
        ids: "all"
      }).then(response => {
        if (response.data.success) {
          setTranslationHistory([]); // Clear the history
          setInputText(''); // Clear input text box
          setOutputText(''); // Clear output text box
          toast(handleCheck("All translations have been deleted."), {
            className: 'success',
            autoClose: 2000
          });
        } else {
          toast(handleCheck("Failed to clear translations: " + response.data.errorMessage), {
            className: 'fail',
            autoClose: 2000
          });
        }
      }).catch(error => {
        console.error("Clear all error:", error);
      });
    }
  };

  const handleDeleteClick = (event, id) => {
    event.stopPropagation(); // This stops the click from affecting parent elements
    confirmDelete(id);
  };

  var res;
  const getTranslation = () => {
    setIsLoading(true);
    const message = {
      text: inputText,
      srcLang: sourceLanguage,
      toLang: targetLanguage,
      sessionToken: localStorage.getItem("sessionToken")
    };
    setIsLoading(true);
    axios.post(`${FLASK_URL}/translate`, message)
      .then((response) => {
        res = response.data;
        if (res.success) {
          setOutputText(res.output)
          console.log(`Finish reason: ${res.finish_reason}`)
          const reasonMessage = res.finish_reason || 'No reason provided'
          setCurrentTranslationId(res.translation_id)
          toast(handleCheck(reasonMessage), {
            className: 'success',
            autoClose: 2000
          })
        }
        console.log(`Response has error: ${res.hasError}`);
        if (res.errorMessage) console.log(`Errors: ${res.errorMessage}`);
        if (res.apiErrorMessage) {
          toast(handleCheck(`${res.errorCode}`), {
            className: 'fail',
            autoClose: 2000
          })
        }
        if (res.logout) {
          toast(handleCheck("Session expired. Please login again.."), {
            className: 'fail',
            autoClose: 2000
          })
          Logout(navigate)
        }
      }).catch((error) => {
        if (error.response) {
          setIsTranslating(`Error enocuntered: ${res.errorMessage}`);
          console.log(error.response);
          console.log(error.response.status);
          console.log(error.response.headers);
        }
        // Hide loading box after translation
      }).finally(() => {
        setIsTranslating(false); // Call the callback function to reset the button state
      });
  };

  const handleCopyToClipboard = (onSuccess) => {
    navigator.clipboard.writeText(outputText).then(() => {
      console.log('Copied to clipboard');
    });
  };

  const handleDownloadCode = () => {
    // Mapping of target language to file extension
    const extensions = {
      'JavaScript': 'js',
      'Python': 'py',
      'C++': 'cpp',
      'Java': 'java',
      'Rust': 'rs',
    };

    // Determine the file extension based on the target language
    const extension = extensions[targetLanguage] || 'txt';

    // Create a blob with the output text
    const blob = new Blob([outputText], { type: 'text/plain' });
    const href = URL.createObjectURL(blob);

    // Create a temporary link to trigger the download
    const link = document.createElement('a');
    link.href = href;
    link.download = `translated_code.${extension}`; // Use the extension directly
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(href);
  };

  useEffect(() => {
    if (currentTranslationId) {
      // You can perform actions here that depend on currentTranslationId being updated
      console.log(`Updated currentTranslationId: ${currentTranslationId}`);
      // If there are actions to perform, place them here
    }
  }, [currentTranslationId]);


  if (!(localStorage.getItem("isLoggedIn") === "true")) window.location.assign(`${SITE_URL}/login?redirect=true`);
  else {
    return (
      <div className="translate-page">
      <ToastContainer position='top-center'/>
        <div className="sidebar-container">
          <button className="sidebar-toggle" onClick={() => setShowSidebar(!showSidebar)} data-testid="history-button">
            <FaHistory className="history-icon" title="Translation History" />
          </button>
          {showSidebar && (
            <div className={`sidebar ${showSidebar ? 'show-sidebar' : ''}`}>
              <div className="sorting-controls">
                <div className="sort-by-date">
                  <label htmlFor="dateFilter">Date:</label>
                  <select
                    id="dateFilter"
                    value={dateFilter}
                    onChange={(e) => setDateFilter(e.target.value)}
                    className="form-control"
                    data-testid="date-filter"
                  >
                    <option value="">All Dates</option>
                    <option value="Today">Today</option>
                    <option value="Yesterday">Yesterday</option>
                    <option value="Previous 30 Days">Previous 30 Days</option>
                  </select>
                </div>
                <div className="sort-by-source-language">
                  <label htmlFor="sourceLanguageFilter">Source Language:</label>
                  <select
                    id="sourceLanguageFilter"
                    value={sourceLanguageFilter}
                    onChange={(e) => setSourceLanguageFilter(e.target.value)}
                    className="form-control"
                    data-testid="source-language-filter"
                  >
                    <option value="">All Languages</option>
                    <option value="JavaScript">JavaScript</option>
                    <option value="Python">Python</option>
                    <option value="C++">C++</option>
                    <option value="Java">Java</option>
                    <option value="Rust">Rust</option>
                  </select>
                </div>
                <div className="sort-by-target-language">
                  <label htmlFor="targetLanguageFilter">Target Language:</label>
                  <select
                    id="targetLanguageFilter"
                    value={targetLanguageFilter}
                    onChange={(e) => setTargetLanguageFilter(e.target.value)}
                    className="form-control"
                    data-testid="target-language-filter"
                  >
                    <option value="">All Languages</option>
                    <option value="JavaScript">JavaScript</option>
                    <option value="Python">Python</option>
                    <option value="C++">C++</option>
                    <option value="Java">Java</option>
                    <option value="Rust">Rust</option>
                  </select>
                </div>
              </div>

              <div
                className="translation-history-title"
                onMouseOver={() => setShowDots(true)}
                onMouseOut={() => setShowDots(false)}
                data-testid="translation-history-title"
              >
                <div className="translation-history-title" onMouseOver={() => setShowDots(true)} onMouseOut={() => setShowDots(false)}>
                  Translation History
                  {showDots && (
                    <FaTrash
                      className="dots-icon"
                      onClick={confirmClearAll}
                      data-testid="clear-all-icon" // Add a consistent data-testid
                      title="Clear Translation History"
                    />
                  )}
                </div>
              </div>

              {Object.entries(groupByDate).map(([date, items], dateIndex) => (
                <div key={dateIndex}>
                  <div className={`${date.toLowerCase().replace(/\s/g, '-')}-section section-title`}>{date}</div>
                  {items.map((item, itemIndex) => (
                    <div>
                      <div
                        key={itemIndex}
                        className="history-item"
                        data-testid={`history-item-${item.translation_id}`} // Make it unique
                        // onClick={() => populateCodeMirror(item.original_code, item.translated_code, item.source_language, item.target_language)}
                        onClick={() => handleClickOnHistoryItem(item)}

                      >
                        {getLanguageIconElement(item.source_language)}
                        <span className="source-language">{item.source_language}</span>
                        <FaArrowRight className="arrow-icon" />
                        {getLanguageIconElement(item.target_language)}
                        <span className="target-language">{item.target_language}</span>
                        <FaTrash
                          className="delete-icon"
                          onClick={(event) => {
                            event.stopPropagation();
                            handleDeleteClick(event, item.translation_id);
                          }}
                          data-testid={`delete-button-${item.translation_id}`} // Make it unique
                          title="Delete Translation"
                        />
                      </div>
                      {/* <DisplayFeedback currentTranslationId={item.translation_id}/> */}
                    </div>
                  ))}
                </div>
              ))}
            </div>
          )}

        </div>
        <div className="container main-content">
          <div className="status">
            <a className='status_display' >Chat-GPT Status</a>
          </div>
          <div className="code-container">
            <div className="code-box input-box">
              <h2>Input</h2>
              <div className="input-header">
                <div className="form-group">
                  <label htmlFor="sourceLanguage">Source Language</label>
                  <select
                    className="form-control"
                    id="sourceLanguage"
                    value={sourceLanguage}
                    onChange={(e) => {
                      // Set the new source language
                      setSourceLanguage(e.target.value);

                      // Clear the input text and reset the character count
                      setInputText('');
                      setCharCount(0);

                      // Optionally clear the output text if you also want to clear translations
                      setOutputText('');
                    }}
                  >
                    <option value="JavaScript">JavaScript</option>
                    <option value="Python">Python</option>
                    <option value="C++">C++</option>
                    <option value="Java">Java</option>
                    <option value="Rust">Rust</option>
                  </select>
                </div>
                <FaUpload className="icon upload-icon" onClick={handleUploadClick} title="Upload File" />
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileInputChange}
                  style={{ display: 'none' }}
                  data-testid="fileInput"

                />
              </div>
              <div className="custom-codemirror-wrapper">

                <CodeMirror
                  value={inputText}
                  theme={vscodeDark}
                  extensions={[getLanguageExtension(sourceLanguage)]}
                  onChange={(value) => {
                    if (value.length <= maxCharLimit) {
                      setInputText(value);
                      setCharCount(value.length);
                    }
                  }}
                  testIdSuffix="input"
                  basicSetup={{ lineNumbers: true }}
                />

              </div>
              <div className="char-count">Characters: {charCount}/{maxCharLimit}</div> {/* Display character count */}
            </div>
            <div className="code-box output-box">
              <h2>Output</h2>
              <div className="form-group">
                <label htmlFor="targetLanguage">Target Language</label>
                <select
                  className="form-control"
                  id="targetLanguage"
                  value={targetLanguage}
                  onChange={(e) => setTargetLanguage(e.target.value)}
                >
                  <option value="Python">Python</option>
                  <option value="JavaScript">JavaScript</option>
                  <option value="C++">C++</option>
                  <option value="Java">Java</option>
                  <option value="Rust">Rust</option>
                </select>
              </div>
              <div className="position-relative textarea-container">
                <div className="custom-codemirror-wrapper">
                  <CodeMirror
                    value={outputText}
                    theme={vscodeDark}
                    extensions={[
                      getLanguageExtension(targetLanguage) // This function will select the proper language mode
                    ]}
                    testIdSuffix="output"
                    editable={true} // Makes the editor read-only
                    basicSetup={{ lineNumbers: true }} // Line numbers and other basic setups
                  />
                </div>
                <div className="icons">
                  <FaRegClipboard className="icon" onClick={handleCopyToClipboard} title="Copy to Clipboard" />
                  <FaDownload className="icon" onClick={handleDownloadCode} title="Download Code" />
                </div>
              </div>
            </div>
          </div>
          <div className="translate-button-container">
            <button
              id="translateBtn"
              className={`btn-translate-button${isTranslating ? '-translating' : '-regular'}`}
              onClick={handleClick}
              disabled={isTranslating}
            >
              {isTranslating ? 'Translating...' : 'Get Translation'}
            </button>
          </div>
        </div>
        <div>
          <TranslationFeedback currentTranslationId={currentTranslationId} />
        </div>
      </div>
    );
  }
};


export default TranslatePage;
//test
