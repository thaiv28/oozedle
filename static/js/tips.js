// A tooltip label inside a <summary> row shows its tip; it should not also open the row.
document.addEventListener("click", (event) => {
  if (event.target.closest(".tip")) event.preventDefault();
});
