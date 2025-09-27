document.addEventListener("DOMContentLoaded", function () {
  // Get all superscript elements that are footnote references
  const footnoteRefs = document.querySelectorAll('.footnote-ref');

  // Create a tooltip element and add it to the body
  const tooltip = document.createElement('div');
  tooltip.style.position = 'absolute';
  tooltip.style.backgroundColor = '#333';
  tooltip.style.color = 'white';
  tooltip.style.padding = '5px';
  tooltip.style.fontSize = '14px';
  tooltip.style.borderRadius = '5px';
  tooltip.style.display = 'none';
  tooltip.style.zIndex = '10';
  tooltip.style.whiteSpace = 'nowrap';
  document.body.appendChild(tooltip);

  // Loop over each footnote reference
  footnoteRefs.forEach(function (footnoteRef) {
    footnoteRef.addEventListener('mouseover', function () {
      // Get the ID of the footnote
      const footnoteId = footnoteRef.getAttribute('href').substring(1);

      // Find the corresponding footnote content
      const footnote = document.getElementById(footnoteId);

      if (footnote) {
        // Use a temporary div to manipulate the footnote's content
        const tempDiv = document.createElement('div');
        // Get the inner HTML of the footnote's paragraph
        tempDiv.innerHTML = footnote.querySelector('p').innerHTML;

        // Find and remove the backlink anchor tag
        const backlink = tempDiv.querySelector('a.footnote-back');
        if (backlink) {
          backlink.remove();
        }
        
        // Use the cleaned text content for the tooltip
        const footnoteText = tempDiv.textContent.trim();

        // Update the tooltip content
        tooltip.textContent = footnoteText;

        // Get the position of the footnote reference
        const rect = footnoteRef.getBoundingClientRect();
        const offset = 10; // Optional offset to adjust position

        // Position the tooltip above the superscript (footnote reference)
        tooltip.style.left = `${rect.left + window.scrollX + rect.width / 2 - tooltip.offsetWidth / 2}px`;
        tooltip.style.top = `${rect.top + window.scrollY - tooltip.offsetHeight - offset}px`;

        // Show the tooltip
        tooltip.style.display = 'block';
      }
    });

    // Hide the tooltip when the mouse leaves the superscript
    footnoteRef.addEventListener('mouseout', function () {
      tooltip.style.display = 'none';
    });
  });
});


