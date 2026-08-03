const fs = require('fs');
const path = require('path');

// Target HTML tags to strip leading/trailing whitespace
const TARGET_TAGS = [
  'title', 'p', 'b', 'i', 'a', 'span', 'em', 'strong', 
  'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'td', 'th'
];

// Inline text formatting tags where internal newlines/tabs/spaces should be collapsed to a single space
const INLINE_TAGS = ['a', 'i', 'b', 'span', 'em', 'strong'];

// Directories to ignore during recursive search
const IGNORED_DIRS = ['css', 'misc','node_modules', '.git', '.codespaces', 'dist', 'build'];

// Build regex patterns
const tagList = TARGET_TAGS.join('|');
const inlineTagList = INLINE_TAGS.join('|');

// 1. Remove whitespace right after opening tags: <i>  text -> <i>text
const leadingWhitespaceRegex = new RegExp(`(<(${tagList})\\b[^>]*>)\\s+`, 'gi');

// 2. Remove whitespace right before closing tags: text   </i> -> text</i>
const trailingWhitespaceRegex = new RegExp(`\\s+(<\\/(${tagList})>)`, 'gi');

// 3. Collapse newlines, tabs, and multiple spaces INSIDE inline tags to a single space
const internalInlineSpacesRegex = new RegExp(`<(${inlineTagList})\\b[^>]*>([\\s\\S]*?)<\\/\\2>`, 'gi');

// 4. Ensure a space exists before inline tags when preceded directly by text, numbers, or punctuation (not after open brackets/quotes or line starts)
const missingSpaceBeforeInlineRegex = new RegExp(`([a-zA-Z0-9_\\.\\,\\!\\?\\:\\;\\)\\>])(<(${inlineTagList})\\b[^>]*>)`, 'gi');

/**
 * Cleans inline whitespace, fixes hidden Unicode/path issues, and normalizes <hr> and <br> tags.
 */
function cleanFile(filePath) {
  try {
    const originalContent = fs.readFileSync(filePath, 'utf8');

    // Convert non-breaking spaces (U+00A0) to standard spaces
    let cleanedContent = originalContent.replace(/\u00a0/g, ' ');

    // Fix malformed relative paths (e.g., ".. /" -> "../")
    cleanedContent = cleanedContent.replace(/\.\.\s+\//g, '../');

    // Fix malformed protocols (e.g., "http: //" -> "http://")
    cleanedContent = cleanedContent.replace(/(https?):\s+\/\//gi, '$1://');

    // Strip leading whitespace right after opening tags
    cleanedContent = cleanedContent.replace(leadingWhitespaceRegex, '$1');

    // Strip trailing whitespace right before closing tags
    cleanedContent = cleanedContent.replace(trailingWhitespaceRegex, '$1');

    // Collapse newlines/tabs/extra spaces inside inline tags (<i>, <a>, <b>, etc.)
    cleanedContent = cleanedContent.replace(internalInlineSpacesRegex, (match) => {
      return match.replace(/\s+/g, ' ');
    });

    // Add back a space before opening inline tags if adjacent to non-whitespace content
    cleanedContent = cleanedContent.replace(missingSpaceBeforeInlineRegex, '$1 $2');

    // Normalize all <hr> tag variations to HTML5 <hr>
    cleanedContent = cleanedContent.replace(/<hr\s*\/?>/gi, '<hr>');

    // Normalize all <br> tag variations to HTML5 <br>
    cleanedContent = cleanedContent.replace(/<br\s*\/?>/gi, '<br>');

    if (originalContent !== cleanedContent) {
      fs.writeFileSync(filePath, cleanedContent, 'utf8');
      console.log(`[CLEANED] ${filePath}`);
      return 1;
    } else {
      console.log(`[UNCHANGED] ${filePath}`);
      return 0;
    }
  } catch (err) {
    console.error(`[ERROR] Failed to process ${filePath}:`, err.message);
    return 0;
  }
}

/**
 * Recursively walks directory tree looking for .html and .htm files.
 */
function walkDirectory(dirPath) {
  let modifiedCount = 0;
  let totalFiles = 0;

  function walk(currentDir) {
    const entries = fs.readdirSync(currentDir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(currentDir, entry.name);

      if (entry.isDirectory()) {
        if (!IGNORED_DIRS.includes(entry.name)) {
          walk(fullPath);
        }
      } else if (entry.isFile()) {
        const ext = path.extname(entry.name).toLowerCase();
        if (ext === '.html' || ext === '.htm') {
          totalFiles++;
          modifiedCount += cleanFile(fullPath);
        }
      }
    }
  }

  walk(dirPath);
  return { modifiedCount, totalFiles };
}

// Execute script
const targetFolder = process.argv[2] ? path.resolve(process.argv[2]) : process.cwd();

console.log(`Starting cleanup in: ${targetFolder}\n---`);
const { modifiedCount, totalFiles } = walkDirectory(targetFolder);
console.log(`\n---`);
console.log(`Finished! Checked ${totalFiles} HTML/HTM file(s), updated ${modifiedCount} file(s).`);
