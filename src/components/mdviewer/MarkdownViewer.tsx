interface MarkdownViewerProps {
  markdown: string;
  className?: string;
  maxHeight?: string;
}
const MarkdownViewer = ({
  markdown,
  className,
  maxHeight,
}: MarkdownViewerProps) => {
  const parseMarkdown = (text: string): string => {
    let content = text;

    // Normalize line endings and clean up
    content = content.replace(/\r\n/g, "\n").replace(/\r/g, "\n");

    // Handle escaped characters first
    content = content
      .replace(/\\([*_`~|\\])/g, "&#$1;") // Temporarily escape special chars
      .replace(/\\\[/g, "&#91;")
      .replace(/\\\]/g, "&#93;")
      .replace(/\\\(/g, "&#40;")
      .replace(/\\\)/g, "&#41;");

    // Headers (support for both ## and # variations, handle whitespace)
    content = content
      .replace(
        /^#{6}\s*(.*?)$/gm,
        '<h6 class="text-sm font-bold mb-2 mt-4 bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">$1</h6>'
      )
      .replace(
        /^#{5}\s*(.*?)$/gm,
        '<h5 class="text-base font-bold mb-2 mt-4 bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">$1</h5>'
      )
      .replace(
        /^#{4}\s*(.*?)$/gm,
        '<h4 class="text-lg font-bold mb-3 mt-5 bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">$1</h4>'
      )
      .replace(
        /^#{3}\s*(.*?)$/gm,
        '<h3 class="text-xl font-bold mb-3 mt-6 bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">$1</h3>'
      )
      .replace(
        /^#{2}\s*(.*?)$/gm,
        '<h2 class="text-2xl font-bold mb-4 mt-8 bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">$1</h2>'
      )
      .replace(
        /^#{1}\s*(.*?)$/gm,
        '<h1 class="text-3xl font-bold mb-6 mt-4 bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">$1</h1>'
      );

    // Code blocks with language detection and better formatting
    content = content.replace(
      /```(\w+)?\s*\n([\s\S]*?)```/g,
      (match, lang, code) => {
        const language = lang || "text";
        const cleanCode = code.trim();
        return `<div class="relative bg-gray-900 dark:bg-gray-950 rounded-lg p-4 my-4 overflow-x-auto border dark:border-gray-800 border-gray-700">
      <div class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-500 to-blue-500"></div>
      ${
        lang
          ? `<div class="text-xs text-gray-400 dark:text-gray-500 mb-2 font-mono">${language}</div>`
          : ""
      }
      <pre class="text-green-400 dark:text-green-300 font-mono text-sm leading-relaxed"><code>${cleanCode}</code></pre>
    </div>`;
      }
    );

    // Handle single backtick code blocks (less common but occurs)
    content = content.replace(
      /^`([^`\n]+)`$/gm,
      '<div class="bg-gray-100 dark:bg-gray-800 rounded p-2 my-2 font-mono text-sm border">$1</div>'
    );

    // Inline code (improved to handle edge cases)
    content = content.replace(
      /`([^`\n]+)`/g,
      '<code class="bg-gray-100 dark:bg-gray-800 text-purple-600 dark:text-purple-400 px-2 py-1 rounded text-sm font-mono border">$1</code>'
    );

    // MOVE LIST PROCESSING BEFORE BOLD/ITALIC TO PREVENT CONFLICTS
    // This is the key - we need to process lists BEFORE * gets consumed by italic formatting

    // Task lists (checkboxes) - handle first to avoid conflicts
    content = content
      .replace(
        /^(\s*)[-*+]\s+\[x\]\s+(.*)$/gm,
        '$1<li class="mb-2 text-gray-700 dark:text-gray-300 leading-relaxed flex items-center"><input type="checkbox" checked disabled class="mr-2 text-purple-500 dark:text-purple-400"> $2</li>'
      )
      .replace(
        /^(\s*)[-*+]\s+\[\s\]\s+(.*)$/gm,
        '$1<li class="mb-2 text-gray-700 dark:text-gray-300 leading-relaxed flex items-center"><input type="checkbox" disabled class="mr-2"> $2</li>'
      );

    // Numbered lists - various patterns
    content = content
      .replace(
        /^(\s*)(\d+)\.\s+(.*)$/gm,
        '$1<li class="mb-2 text-gray-700 dark:text-gray-300 leading-relaxed">$3</li>'
      )
      .replace(
        /^(\s*)(\d+)\)\s+(.*)$/gm,
        '$1<li class="mb-2 text-gray-700 dark:text-gray-300 leading-relaxed">$3</li>'
      );

    // CRITICAL FIX: Handle * at start of line with different spacing patterns
    // This regex specifically targets the pattern: "* " or "*   " followed by content
    content = content.replace(
      /^\*(\s+)(.*)$/gm,
      '<li class="mb-2 text-gray-700 dark:text-gray-300 leading-relaxed">$2</li>'
    );

    // Handle indented * items with various spacing
    content = content.replace(
      /^(\s+)\*(\s+)(.*)$/gm,
      '<li class="mb-2 ml-4 text-gray-700 dark:text-gray-300 leading-relaxed">$3</li>'
    );

    // Handle other bullet types (-, +)
    content = content.replace(
      /^(\s*)([-+])(\s+)(.*)$/gm,
      '$1<li class="mb-2 text-gray-700 dark:text-gray-300 leading-relaxed">$4</li>'
    );

    // Handle deeply nested items
    content = content
      .replace(
        /^(\s{4,7})\*(\s+)(.*)$/gm,
        '<li class="mb-1 ml-4 text-gray-700 dark:text-gray-300 leading-relaxed">$3</li>'
      )
      .replace(
        /^(\s{8,})\*(\s+)(.*)$/gm,
        '<li class="mb-1 ml-8 text-gray-700 dark:text-gray-300 leading-relaxed">$3</li>'
      );

    // NOW process bold/italic AFTER list processing
    // Strikethrough
    content = content.replace(
      /~~(.*?)~~/g,
      '<del class="text-gray-500 dark:text-gray-400 line-through">$1</del>'
    );

    // Bold and italic combinations (handle before individual formatting)
    content = content
      .replace(
        /\*\*\*(.*?)\*\*\*/g,
        '<strong><em class="font-bold italic text-blue-700 dark:text-blue-300">$1</em></strong>'
      )
      .replace(
        /___([^_]+)___/g,
        '<strong><em class="font-bold italic text-blue-700 dark:text-blue-300">$1</em></strong>'
      )
      .replace(
        /\*\*(.*?)\*\*/g,
        '<strong class="font-bold text-blue-700 dark:text-blue-300">$1</strong>'
      )
      .replace(
        /__(.*?)__/g,
        '<strong class="font-bold text-blue-700 dark:text-blue-300">$1</strong>'
      )
      .replace(
        /\*([^*\n]+)\*/g,
        '<em class="italic text-purple-600 dark:text-purple-400">$1</em>'
      )
      .replace(
        /_([^_\n]+)_/g,
        '<em class="italic text-purple-600 dark:text-purple-400">$1</em>'
      );

    // Links with title attributes
    content = content.replace(
      /\[([^\]]+)\]\(([^)]+)\s+"([^"]+)"\)/g,
      '<a href="$2" title="$3" class="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 underline hover:no-underline transition-all duration-200 font-medium">$1</a>'
    );
    content = content.replace(
      /\[([^\]]+)\]\(([^)]+)\)/g,
      '<a href="$2" class="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 underline hover:no-underline transition-all duration-200 font-medium">$1</a>'
    );

    // Autolinks
    content = content.replace(
      /<([^>\s]+@[^>\s]+)>/g,
      '<a href="mailto:$1" class="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 underline">$1</a>'
    );
    content = content.replace(
      /<(https?:\/\/[^>\s]+)>/g,
      '<a href="$1" class="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 underline">$1</a>'
    );

    // Images
    content = content.replace(
      /!\[([^\]]*)\]\(([^)]+)\s+"([^"]+)"\)/g,
      '<img src="$2" alt="$1" title="$3" class="max-w-full h-auto rounded-lg shadow-md my-4 border">'
    );
    content = content.replace(
      /!\[([^\]]*)\]\(([^)]+)\)/g,
      '<img src="$2" alt="$1" class="max-w-full h-auto rounded-lg shadow-md my-4 border">'
    );

    // Blockquotes (handle nested and multi-line)
    content = content.replace(
      /^>\s*(.*$)/gm,
      '<blockquote class="border-l-4 border-purple-500 bg-purple-50 dark:bg-purple-900/20 pl-4 py-2 my-4 italic text-gray-700 dark:text-gray-300 rounded-r-lg">$1</blockquote>'
    );

    // Handle multiple blockquote lines
    content = content.replace(
      /(<blockquote[^>]*>.*?<\/blockquote>)\s*(<blockquote[^>]*>.*?<\/blockquote>)/g,
      (match, first, second) => {
        const firstContent = first.replace(/<\/?blockquote[^>]*>/g, "");
        const secondContent = second.replace(/<\/?blockquote[^>]*>/g, "");
        return `<blockquote class="border-l-4 border-purple-500 bg-purple-50 dark:bg-purple-900/20 pl-4 py-2 my-4 italic text-gray-700 dark:text-gray-300 rounded-r-lg">${firstContent}<br>${secondContent}</blockquote>`;
      }
    );

    // Horizontal rules (multiple variations)
    content = content
      .replace(
        /^[\s]*---[\s]*$/gm,
        '<hr class="my-8 border-0 h-px bg-gradient-to-r from-transparent via-purple-500 to-transparent">'
      )
      .replace(
        /^[\s]*\*\*\*[\s]*$/gm,
        '<hr class="my-8 border-0 h-px bg-gradient-to-r from-transparent via-purple-500 to-transparent">'
      )
      .replace(
        /^[\s]*___[\s]*$/gm,
        '<hr class="my-8 border-0 h-px bg-gradient-to-r from-transparent via-purple-500 to-transparent">'
      );

    // Enhanced table handling
    const lines = content.split("\n");
    const processedLines = [];
    let inTable = false;
    let tableRows = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const trimmedLine = line.trim();

      if (
        trimmedLine.includes("|") &&
        trimmedLine.length > 2 &&
        trimmedLine !== "|"
      ) {
        if (!inTable) {
          inTable = true;
          tableRows = [];
        }

        // Check if this is a separator row
        if (trimmedLine.match(/^\|[\s\-\|:]+\|$/)) {
          continue; // Skip separator rows
        }

        const cells = trimmedLine
          .split("|")
          .slice(1, -1) // Remove empty first and last elements
          .map((cell) => cell.trim());

        if (cells.length > 0) {
          const cellsHtml = cells
            .map(
              (cell) =>
                `<td class="px-4 py-2 border-b border-gray-200 dark:border-gray-700 text-sm">${cell}</td>`
            )
            .join("");
          tableRows.push(
            `<tr class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">${cellsHtml}</tr>`
          );
        }
      } else if (inTable) {
        // End of table - output the complete table
        if (tableRows.length > 0) {
          processedLines.push(
            `<div class="overflow-x-auto my-6"><table class="min-w-full bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700"><tbody>${tableRows.join(
              ""
            )}</tbody></table></div>`
          );
          tableRows = [];
        }
        inTable = false;
        processedLines.push(line);
      } else {
        processedLines.push(line);
      }
    }

    // Handle remaining table if file ends with table
    if (inTable && tableRows.length > 0) {
      processedLines.push(
        `<div class="overflow-x-auto my-6"><table class="min-w-full bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700"><tbody>${tableRows.join(
          ""
        )}</tbody></table></div>`
      );
    }

    content = processedLines.join("\n");

    // Handle special characters and entities
    content = content
      .replace(/&lt;/g, "<")
      .replace(/&gt;/g, ">")
      .replace(/&amp;/g, "&");

    // Restore escaped characters
    content = content
      .replace(/&#\*/g, "*")
      .replace(/&#_/g, "_")
      .replace(/&#`/g, "`")
      .replace(/&#~/g, "~")
      .replace(/&#\|/g, "|")
      .replace(/&#\\/g, "\\")
      .replace(/&#91;/g, "[")
      .replace(/&#93;/g, "]")
      .replace(/&#40;/g, "(")
      .replace(/&#41;/g, ")");

    // Line breaks and paragraphs (handle multiple newlines)
    content = content
      .replace(/\n{3,}/g, "\n\n") // Normalize multiple newlines
      .replace(
        /\n\n/g,
        '</p><p class="mb-4 text-gray-700 dark:text-gray-300 leading-relaxed">'
      )
      .replace(/(?<!<\/[^>]+>)\n(?![<\n])/g, "<br>"); // Only add <br> for single newlines not after closing tags

    return content;
  };

  // Enhanced wrapper function with better list grouping
  const processMarkdown = (markdown: string): string => {
    let wrappedContent = parseMarkdown(markdown);

    // Wrap content in paragraph if it doesn't start with a block element
    const blockElements = [
      "<h1",
      "<h2",
      "<h3",
      "<h4",
      "<h5",
      "<h6",
      "<div",
      "<blockquote",
      "<ul",
      "<ol",
      "<table",
      "<hr",
      "<pre",
    ];
    const startsWithBlock = blockElements.some((tag) =>
      wrappedContent.trimStart().startsWith(tag)
    );

    if (!startsWithBlock && wrappedContent.trim()) {
      wrappedContent =
        '<p class="mb-4 text-gray-700 dark:text-gray-300 leading-relaxed">' +
        wrappedContent +
        "</p>";
    }

    // IMPROVED LIST GROUPING - This is crucial for fixing your issue
    // Group consecutive list items into proper lists
    wrappedContent = wrappedContent.replace(
      /((?:<li[^>]*>.*?<\/li>\s*)+)/gs,
      (match) => {
        // Check what type of list this should be
        const hasCheckbox = match.includes('type="checkbox"');
        const isNumbered = /^\s*\d+\./.test(match);

        // Remove any existing <br> tags between list items
        const cleanMatch = match.replace(/<br\s*\/?>/g, "");

        if (hasCheckbox) {
          return `<ul class="list-none space-y-2 mb-4 ml-0">${cleanMatch}</ul>`;
        } else if (isNumbered) {
          return `<ol class="list-decimal list-inside space-y-1 mb-4 ml-4 marker:text-purple-500 marker:font-bold">${cleanMatch}</ol>`;
        } else {
          return `<ul class="list-disc list-inside space-y-1 mb-4 ml-4 marker:text-purple-500">${cleanMatch}</ul>`;
        }
      }
    );

    // Clean up: Remove <br> tags that appear right before or after lists
    wrappedContent = wrappedContent
      .replace(/<br\s*\/?>\s*(<ul|<ol)/g, "$1") // Remove <br> before lists
      .replace(/(<\/ul>|<\/ol>)\s*<br\s*\/?>/g, "$1") // Remove <br> after lists
      .replace(/<p[^>]*>\s*<\/p>/g, "") // Remove empty paragraphs
      .replace(
        /(<\/(?:h[1-6]|div|blockquote|ul|ol|table|hr)>)\s*<br\s*\/?>/g,
        "$1"
      ) // Remove br after block elements
      .replace(
        /<br\s*\/?>\s*(<(?:h[1-6]|div|blockquote|ul|ol|table|hr))/g,
        "$1"
      ) // Remove br before block elements
      .replace(/(<\/p>)\s*(<p[^>]*>)/g, "$1\n$2"); // Add spacing between paragraphs

    return wrappedContent;
  };

  let wrappedContent = markdown ? processMarkdown(markdown) : "";

  return (
    <div
      className={`overflow-y-auto text-wrap break-words ${className}`}
      style={{ maxHeight }}
    >
      <div
        className="prose prose-sm max-w-none p-1"
        dangerouslySetInnerHTML={{ __html: wrappedContent }}
      />
    </div>
  );
};

export default MarkdownViewer;
