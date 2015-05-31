$(function () {
	$('[data-datepicker]').datepicker();

	$('.form-inline').on('inline:created', '.inline-tr', function (){
		$(this).find('[data-datepicker]').datepicker();
	});
});