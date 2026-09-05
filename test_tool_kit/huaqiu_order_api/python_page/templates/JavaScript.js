document.querySelectorAll('input[type=checkbox]').forEach(function(checkbox) {
  checkbox.addEventListener('change', function() {
    if (this.checked) {
      document.getElementById('myField').value += this.value + ',';
    } else {
      var values = document.getElementById('myField').value.split(',');
      values = values.filter(function(value) { return value != this.value; }, this);
      document.getElementById('myField').value = values.join(',');
    }
  });
});