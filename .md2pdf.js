/*
ref: https://github.com/simonhaenisch/md-to-pdf
Github-like output
---
stylesheet: https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/2.10.0/github-markdown.min.css
body_class: markdown-body
css: |-
  .page-break { page-break-after: always; }
  .markdown-body { font-size: 11px; }
  .markdown-body pre > code { white-space: pre-wrap; }
---
*/
module.exports = {
	stylesheet: ['https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/2.10.0/github-markdown.min.css'],
	css: `
  .page-break { page-break-after: always; }
  .markdown-body { font-size: 10pt; }
  .markdown-body pre > code { white-space: pre-wrap; }
	`,
	body_class: 'markdown-body',
	pdf_options: {
		format: 'A4',
		margin: '12mm'
	},
	stylesheet_encoding: 'utf-8'
};
