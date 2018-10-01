
  $(document).ready(function () {
    $('.sidebar-menu').tree()
  });

  //validate report input parameter
  function ValidateReportInput(from, to, reportid) {
    if (from != "" && to != "") {

      var toParts = to.split("/")
      var newToDate = toParts[1] + "/" + toParts[0] + "/" + toParts[2];

      var fromParts = from.split("/")
      var newFromDate = fromParts[1] + "/" + fromParts[0] + "/" + fromParts[2];

      var f = new Date(newFromDate);
      var t = new Date(newToDate);
      if (f > t) {
        document.getElementById("from_validate_" + reportid).style.display = "none";
        document.getElementById("to_validate_" + reportid).style.display = "none";
        document.getElementById("compare_validate_" + reportid).style.display = "block";
        $('#fromdatepicker').focus();
        return false;
      }
    } else {
      if (from == "" && to == "") {
        document.getElementById("compare_validate_" + reportid).style.display = "none";
        document.getElementById("from_validate_" + reportid).style.display = "block";
        document.getElementById("to_validate_" + reportid).style.display = "block";
        $('#fromdatepicker').focus();
        return false;
      }

      if (from == "" && to != "") {
        document.getElementById("compare_validate_" + reportid).style.display = "none";
        document.getElementById("from_validate_" + reportid).style.display = "block";
        document.getElementById("to_validate_" +reportid).style.display = "none";
        $('#fromdatepicker').focus();
        return false;
      }

      if (to == "" && from != "") {
        document.getElementById("compare_validate_" + reportid).style.display = "none";
        document.getElementById("from_validate_" + reportid).style.display = "none";
        document.getElementById("to_validate_" + reportid).style.display = "block";
        $('#todatepicker').focus();
        return false;
      }
    }
    return true;
  }


  function exportReport(id, name, query) {
    var params = [];
    var hasDate = false;
    var from = '';
    var to = '';
    var date_param_name = ''
    $( "#" + id + "-" + name).find(".modal-body div").each( function(){
      var type = $(this).find("p[name='hidden_type']").text();

      if (type == "String") {
        var label = $(this).find("label").text();
        var value = $(this).find("input").val();

        params.push({ Label: label, Value: value, Type: type });
        hasDate = false;
      }

      if (type == "Date") { 
        from = $(this).find('.form-group').eq(0).find("input").val();
        to = $(this).find('.form-group').eq(1).find("input").val();
        date_param_name = $(this).find("p[name='hidden_param_name']").text();

        params.push({ Label: "FromDate", Value: from, Type: type });
        params.push({ Label: "ToDate", Value: to, Type: type });
        hasDate = true;
      }
      
    }); 

    $('#saveLocal_' + id + "_" + name).text('Downloading');
    $('#saveLocal_' + id + "_" + name).prop( "disabled", true );
    $('#saveLocal_' + id + "_" + name).css("display", "none");
    $('#spinner_' + id + "_" + name).css("visibility", "visible");

    if (!hasDate) {
      $.ajax({
        type: 'POST',
        url: "{% url 'execute' %}",
        data: JSON.stringify({
          rp_name: name,
          rp_query: query,
          params: params,
          hasDate: hasDate,
          date_param_name: date_param_name
        }),
        success: function (data) {
          console.log('success', data);
          $('#saveLocal_' + id + "_" + name).text('Export');
          $('#saveLocal_' + id + "_" + name).prop( "disabled", false );
          $('#saveLocal_' + id + "_" + name).css("display", "block");
          $('#spinner_' + id + "_" + name).css("visibility", "hidden");
          if (data == 'No Data') {
            alert('No Data !')
          }

          var blob=new Blob([data]); 
          var link=document.createElement('a'); 
          link.href=window.URL.createObjectURL(blob); 
          link.download= rp_name + ".xls"; 
          link.click(); 
        },
        error: function (exception) {
          alert('Oops! Something went wrong.');
          console.log('ERROR', exception);
        }
      });
    }
    else {
      if(ValidateReportInput(from, to, id)) {

        $.ajax({
          type: 'POST',
          url: "{% url 'execute' %}",
          data: JSON.stringify({
            rp_name: name,
            rp_query: query,
            params: params,
            hasDate: hasDate,
            date_param_name: date_param_name
          }),
          success: function (data) {
            console.log('success', data);
            $('#saveLocal_' + id + "_" + name).prop( "disabled", false );
            $('#saveLocal_' + id + "_" + name).text('Export');
            $('#saveLocal_' + id + "_" + name).css("display", "block");
            $('#spinner_' + id + "_" + name).css("visibility", "hidden");

            //JSONToCSVConvertor(data, name, true);
          },
          error: function (exception) {
            alert('Oops! Something went wrong.');
            console.log('ERROR', exception);
          }
        });
      }
    }
  }


  function JSONToCSVConvertor(JSONData, ReportTitle, ShowLabel) {
    //If JSONData is not an object then JSON.parse will parse the JSON string in an Object
    var arrData = typeof JSONData != 'object' ? JSON.parse(JSONData) : JSONData;
    
    //var CSV = 'sep=,' + '\r\n';
    var CSV = '';

    //This condition will generate the Label/Header
    if (ShowLabel) {
        var row = "";
        
        //This loop will extract the label from 1st index of on array
        for (var index in arrData[0]) {
            
            //Now convert each value to string and comma-seprated
            row += index + ',';
        }

        row = row.slice(0, -1);
        
        //append Label row with line break
        CSV += row + '\r\n';
    }
    
    //1st loop is to extract each row
    for (var i = 0; i < arrData.length; i++) {
        var row = "";
        
        //2nd loop will extract each column and convert it in string comma-seprated
        for (var index in arrData[i]) {
            row += '"\'' + arrData[i][index] + '",';
            //row += "'" + arrData[i][index] + ',';
        }

        row.slice(0, row.length - 1);
        
        //add a line break after each row
        CSV += row + '\r\n';
    }

    if (CSV == '') {        
        alert("Invalid data");
        return;
    }   
    
    //Generate a file name
    //this will remove the blank-spaces from the title and replace it with an underscore
    var fileName = ReportTitle.replace(/ /g,"_");   
    
    //Initialize file format you want csv or xls
    var uri = 'data:text/csv;charset=utf-8,' + "\ufeff" + CSV;

    // Now the little tricky part.
    // you can use either>> window.open(uri);
    // but this will not work in some browsers
    // or you will not get the correct file extension    
    
    //this trick will generate a temp <a /> tag
    var link = document.createElement("a");    
    link.href = uri;
    
    //set the visibility hidden so it will not effect on your web-layout
    link.style = "visibility:hidden";
    link.download = fileName + ".xls";
    
    //this part will append the anchor tag and remove it after automatic click
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }


  // export customer feedback data
  $('#addReport').click(function () {
    // Get the checkbox
    var checkbox = document.getElementById('check_param');
    var rp_name = $('#rp_name').val();
    var rp_dsc = $('#rp_dsc').val();
    var rp_query = $('#rp_query').val();
    
    // If the checkbox is checked, display the output text
    if (checkbox.checked){
      var params = []
      //get first row class
      var tr_class = $("#paramTable tr td:first").attr('class');

      //check empty row, if existed then remove
      if (tr_class != 'dataTables_empty'){
        $('#paramTable tbody tr').each(function (){
          var param_name = $(this).find("td").eq(0).find("select").val();
          var data_type = $(this).find("td").eq(1).find("select").val();
          var param_hint = $(this).find("td").eq(2).find(":text").val();
          params.push({ Name: param_name, Type: data_type, Hint: param_hint } );
        });

        $.ajax({
          type: 'POST',
          url: "{% url 'addReport' %}",
          data: JSON.stringify({
            hasParam: 1,
            rp_name: rp_name,
            rp_dsc: rp_dsc,
            rp_query: rp_query,
            params: params
          }),
          success: function (data) {
            console.log('success', data);
            location.reload();
          },
          error: function (exception) {
            alert('Oops! Something went wrong.');
            console.log('ERROR', exception);
          }
        });
      }
      else {
        $.ajax({
          type: 'POST',
          url: "{% url 'addReport' %}",
          data: JSON.stringify({
            hasParam: 0,
            rp_name: rp_name,
            rp_dsc: rp_dsc,
            rp_query: rp_query,
          }),
          success: function (data) {
            console.log('success', data);
            location.reload();
          },
          error: function (exception) {
            alert('Oops! Something went wrong.');
            console.log('ERROR', exception);
          }
        });
      }
    } 
    else {
      $.ajax({
        type: 'POST',
        url: "/Reports/check_view/",
        data: JSON.stringify({
          rp_name: rp_name
        }),
        success: function (data){
          if (addReportInputValidate(rp_name, rp_dsc, rp_query, checkbox, data)){
            $.ajax({
              type: 'POST',
              url: "{% url 'addReport' %}",
              data: JSON.stringify({
                hasParam: 0,
                rp_name: rp_name,
                rp_dsc: rp_dsc,
                rp_query: rp_query,
              }),
              success: function (data) {
                console.log('success', data);
                location.reload();
              },
              error: function (exception) {
                alert('Oops! Something went wrong.');
                console.log('ERROR', exception);
              }
            });
          }
        },
        error: function (exception) {
          alert('Oops! Something went wrong.');
          console.log('ERROR', exception);
        }
      });
    }
  });


  //click Export To Excal Button
  $('#showBtn').click(function (event) {
		var fromDate = $('#fromdatepicker').val();
		var toDate = $('#todatepicker').val();
		var csUser = $("#CSUser option:selected").attr("id");

		var today = new Date();
		var date = today.getDate();
		var month = today.getMonth() + 1;
		if (date < 10) {
		  date = '0' + date;
		}
		if (month < 10) {
		  month = '0' + month;
		}

		var current = date + '-' + month + '-' + today.getFullYear();
		//var time = today.getHours() + "-" + today.getMinutes() + "-" + today.getSeconds();
		//var dateTime = date + '_' + time;

		if (ValidateInput(fromDate, toDate)) {
			$.ajax({
				type: 'POST',
				url: "{% url 'showReport' %}",
				data: JSON.stringify({
				  from: fromDate,
				  to: toDate,
				  user: csUser
				}),
				success: function (data) {
				  console.log('success', data);

				  //hide validate field
				  document.getElementById("from_validate").style.display = "none";
				  document.getElementById("to_validate").style.display = "none";
				  document.getElementById("compare_validate").style.display = "none";

				  //prevent user from click "Export Data" button twice
				  //var disabled = $("#export").is(":disabled");
				  //if (disabled) {
					//document.getElementById("export").disabled = false;
				  //}
				  
				  // remove Excel button
				  if ($("button:contains('Excel')").length != 0) {
					$("button:contains('Excel')").remove();
				  }

				  //clear data_table if already existed
				  if ($('#data_table_wrapper').length)         // use this if you are using id to check
				  {
					$('#data_table_wrapper').remove();
				  }

				  //show div "result"
				  document.getElementById("result").style.display = 'block';

				  //append table inside div
				  $('#data').append(CreateTableView(data, 'table table-bordered table-hover', true));
				  
				  // config table
				  var table = $('#data_table').DataTable({
					'paging': true,
					'lengthChange': false,
					'searching': false,
					'ordering': true,
					'info': true,
					'autoWidth': true,
					dom: 'Bfrtip',
					buttons: [
					{
					  extend: 'excelHtml5',
					  title: 'Export_Data' + '_' + current,
					  className: 'btn btn-block btn-default'
					}
					]
				  });

				  //set place to put button
				  table.buttons().container().appendTo('#feedback_rp_header');
				},
				error: function (exception) {
				  alert('Oops! Something went wrong.');
				  console.log('ERROR', exception);
				}
			});
			event.preventDefault();
		}
	});


  //validate input
  function ValidateInput(from, to) {
    if (from != "" && to != "") {

      var toParts = to.split("/")
      var newToDate = toParts[1] + "/" + toParts[0] + "/" + toParts[2];

      var fromParts = from.split("/")
      var newFromDate = fromParts[1] + "/" + fromParts[0] + "/" + fromParts[2];

      var f = new Date(newFromDate);
      var t = new Date(newToDate);
      if (f > t) {
        document.getElementById("from_validate").style.display = "none";
        document.getElementById("to_validate").style.display = "none";
        document.getElementById("compare_validate").style.display = "block";
        $('#fromdatepicker').focus();
        return false;
      }
    } else {
      if (from == "" && to == "") {
        document.getElementById("compare_validate").style.display = "none";
        document.getElementById("from_validate").style.display = "block";
        document.getElementById("to_validate").style.display = "block";
        $('#fromdatepicker').focus();
        return false;
      }

      if (from == "" && to != "") {
        document.getElementById("compare_validate").style.display = "none";
        document.getElementById("from_validate").style.display = "block";
        document.getElementById("to_validate").style.display = "none";
        $('#fromdatepicker').focus();
        return false;
      }

      if (to == "" && from != "") {
        document.getElementById("compare_validate").style.display = "none";
        document.getElementById("from_validate").style.display = "none";
        document.getElementById("to_validate").style.display = "block";
        $('#todatepicker').focus();
        return false;
      }
    }
    return true;
  }

  //create html table
	 function CreateTableView(objArray, theme, enableHeader) {
		// set optional theme parameter
		if (theme === undefined) {
		  theme = 'mediumTable'; //default theme
		}

		if (enableHeader === undefined) {
		  enableHeader = true; //default enable headers
		}
		// If the returned data is an object do nothing, else try to parse
		var array = typeof objArray != 'object' ? JSON.parse(objArray) : objArray;

		var str = '<table id="data_table" class="' + theme + '">';

		// table head
		if (enableHeader) {
		  str += '<thead><tr>';
		  str += '<th>{{ request.session.lang_content.Username }}</th>';
		  str += '<th>{{ request.session.lang_content.Vote }}</th>';
		  str += '<th>{{ request.session.lang_content.Date }}</th>';
		  str += '</tr></thead>';
		}

		// table body
		str += '<tbody>';
		for (var i = 0; i < array.length; i++) {
		  str += '<tr>';
		  str += '<td>' + array[i]["USERNAME"] + '</td>';
		  str += '<td>' + array[i]["VOTE"] + '</td>';
		  str += '<td>' + array[i]["TIMESTAMP"] + '</td>';
		  var count = Object.keys(array[i]).length;
		  //for (var j = 1; j < count+1; j++) {
		  // str += '<td>' + array[i]["TIMESTAMP"] + '</td>';
		  //}
		  str += '</tr>';
		}
		str += '</tbody>';
		str += '<tfoot><tr>';
		str += '<th>{{ request.session.lang_content.Username }}</th>';
		str += '<th>{{ request.session.lang_content.Vote }}</th>';
		str += '<th>{{ request.session.lang_content.Date }}</th>';
		str += '</tr></tfoot>';
		str += '</table>';
		return str;
	}

  
  // highlight today
  $(function () {
		//Date picker
		$('[id^=fromdatepicker]').datepicker({
		  todayHighlight: true,
		  format: 'dd/mm/yyyy',
		  autoclose: true
		})
	  
		//Date picker
		$('[id^=todatepicker]').datepicker({
		  todayHighlight: true,
		  format: 'dd/mm/yyyy',
		  autoclose: true,
		})
	});

  
  // set default value for date input field
  $(document).ready(function () {
		var now = new Date();
		var month = (now.getMonth() + 1);
		var day = now.getDate();
		if (month < 10)
		  month = "0" + month;
		if (day < 10)
		  day = "0" + day;
		var today = day + '/' + month + '/' + now.getFullYear();
		$('[id^=fromdatepicker]').val(today);
		$('[id^=todatepicker]').val(today);
	});


  // export customer feedback data
  $('#export').click(function () {
		document.getElementById("export").disabled = true;

		var today = new Date();
		var date = today.getDate() + '-' + (today.getMonth() + 1) + '-' + today.getFullYear();
		var time = today.getHours() + "-" + today.getMinutes() + "-" + today.getSeconds();
		var dateTime = date + '_' + time;

		$("#data_table").tableExport({
		  headings: true,                    // (Boolean), display table headings (th/td elements) in the <thead>
		  footers: false,                     // (Boolean), display table footers (th/td elements) in the <tfoot>
		  formats: ["xls", "xlsx", "csv", "txt"],    // (String[]), filetypes for the export
		  fileName: "Feedback_Report" + '_' + dateTime,                    // (id, String), filename for the downloaded file
		  bootstrap: true,                   // (Boolean), style buttons using bootstrap
		  position: "bottom",                 // (top, bottom), position of the caption element relative to table
		  ignoreRows: null,                  // (Number, Number[]), row indices to exclude from the exported file(s)
		  ignoreCols: null,                  // (Number, Number[]), column indices to exclude from the exported file(s)
		  ignoreCSS: ".tableexport-ignore",  // (selector, selector[]), selector(s) to exclude from the exported file(s)
		  emptyCSS: ".tableexport-empty",    // (selector, selector[]), selector(s) to replace cells with an empty string in the exported file(s)
		  trimWhitespace: false
		});
	});


  $('#exportVNPostData').click(function () {
		document.getElementById("exportVNPostData").disabled = true;

		var today = new Date();
		var date = today.getDate() + '-' + (today.getMonth() + 1) + '-' + today.getFullYear();
		var time = today.getHours() + "-" + today.getMinutes() + "-" + today.getSeconds();
		var dateTime = date + '_' + time;

		$("#VNPostTable").tableExport({
		  headings: true,                    // (Boolean), display table headings (th/td elements) in the <thead>
		  footers: false,                     // (Boolean), display table footers (th/td elements) in the <tfoot>
		  formats: ["xls", "xlsx", "csv", "txt"],    // (String[]), filetypes for the export
		  fileName: "SMS_Data" + '_' + dateTime,                    // (id, String), filename for the downloaded file
		  bootstrap: true,                   // (Boolean), style buttons using bootstrap
		  position: "bottom",                 // (top, bottom), position of the caption element relative to table
		  ignoreRows: null,                  // (Number, Number[]), row indices to exclude from the exported file(s)
		  ignoreCols: null,                  // (Number, Number[]), column indices to exclude from the exported file(s)
		  ignoreCSS: ".tableexport-ignore",  // (selector, selector[]), selector(s) to exclude from the exported file(s)
		  emptyCSS: ".tableexport-empty",    // (selector, selector[]), selector(s) to replace cells with an empty string in the exported file(s)
		  trimWhitespace: true
		});
	});

	
	//click send SMS button (VNPost)
  $('#sendSMS').click(function (event) {
		$.ajax({
		  type: 'POST',
		  url: "{% url 'sendSMS' %}",
		  data: JSON.stringify('{{ data }}'),
		  success: function (data) {
			console.log('success', data);
			document.getElementById("content").innerHTML = data;
			$('#modal-result').modal('show');
		  },
		  error: function (exception) {
			alert('Oops! Something went wrong.');
			console.log('ERROR', exception);
		  }
		});
		event.preventDefault();
	});

	//table settings
  $(function () {

		var today = new Date();
		var date = today.getDate();
		var month = today.getMonth() + 1;
		if (date < 10) {
		  date = '0' + date;
		}
		if (month < 10) {
		  month = '0' + month;
		}

		var current = date + '-' + month + '-' + today.getFullYear();
		//var time = today.getHours() + "-" + today.getMinutes() + "-" + today.getSeconds();
		//var dateTime = date;

		$('#example1').DataTable();

		var cs_report = $('#reportTable').DataTable({
		  'paging': true,
		  'lengthChange': true,
		  'searching': true,
		  'ordering': false,
		  'info': true,
		  'autoWidth': true
		});
		
		//table with export excel button
		var vnpTable = $('#VNPostTable').DataTable({
		  'paging': true,
		  'lengthChange': false,
		  'searching': false,
		  'ordering': true,
		  'info': true,
		  'autoWidth': true,
		  dom: 'Bfrtip',
		  buttons: [
		  {
			extend: 'excelHtml5',
			title: "SMS_Data" + '_' + current,
			className: 'btn btn-block btn-default'
		  }
		  ]
		});

	
		$('#paramTable').DataTable({
		  'paging': false,
		  'lengthChange': false,
		  'searching': false,
		  'ordering': false,
		  'info': false,
		  'autoWidth': true
		});

		//table with export excel button
		var mrcTable = $('#MRCTable').DataTable({
		  'paging': true,
		  'lengthChange': false,
		  'searching': false,
		  'ordering': true,
		  'info': true,
		  'autoWidth': true,
		  dom: 'Bfrtip',
		  buttons: [
		  {
			extend: 'excelHtml5',
			title: "MRC_Data" + '_' + current,
			className: 'btn btn-block btn-default'
		  }
		  ]
		});


		vnpTable.buttons().container().appendTo('#vnp_header .col-md-2:eq(1)');
		mrcTable.buttons().container().appendTo('#mrc_header .col-md-2:eq(1)');
	})


	function changeLanguage(id){
		$.ajax({
		  type: 'POST',
		  url: "{% url 'language' %}",
		  data: JSON.stringify({
			lang: id
		  }),
		  success: function (data) {
			console.log('success', data);
			location.reload();
		  },
		  error: function (exception) {
			alert('Oops! Something went wrong.');
			console.log('ERROR', exception);
		  }
		});
	}


    function addReportInputValidate(name, dsc, query, checkbox, hasData){
      if (name != '' && dsc != '' && query != '' && hasData == 0){
        if (name != '' && hasData == 0) {
          document.getElementById('check_exist_validate').style.display = "block";
          document.getElementById("rp_name_validate").style.display = "none";
        }
        document.getElementById('check_exist_validate').style.display = "block";
        document.getElementById("rp_name_validate").style.display = "none";
        document.getElementById("rp_dsc_validate").style.display = "none";
        document.getElementById("rp_query_validate").style.display = "none";
        checkbox.checked = false;
        $('#rp_name').val('');
        $('#rp_name').focus();
        return false;
      }
      else {
        document.getElementById('check_exist_validate').style.display = "none";
        
        if (name == '' && dsc == '' && query == ''){
          document.getElementById("rp_name_validate").style.display = "block";
          document.getElementById("rp_dsc_validate").style.display = "block";
          document.getElementById("rp_query_validate").style.display = "block";
          checkbox.checked = false;
          $('#rp_name').focus();
          return false;
        }
        else {
          if (name == "") {
            document.getElementById("rp_name_validate").style.display = "block";

            if (query != '' && dsc != '') {
              document.getElementById("rp_dsc_validate").style.display = "none";
              document.getElementById("rp_query_validate").style.display = "none";
            }
            else {
              if (dsc != '') {
                document.getElementById("rp_dsc_validate").style.display = "none";
                document.getElementById("rp_query_validate").style.display = "block";
              }
              if (query != '') {
                document.getElementById("rp_query_validate").style.display = "none";
                document.getElementById("rp_dsc_validate").style.display = "block";
              }
            }

            $('#rp_name').focus();
            checkbox.checked = false;
            return false;
          } else {
            document.getElementById("rp_name_validate").style.display = "none";
          }
    
          if (dsc == "") {
            document.getElementById("rp_dsc_validate").style.display = "block";

            if (name != '' && query != '') {
              document.getElementById("rp_name_validate").style.display = "none";
              document.getElementById("rp_query_validate").style.display = "none";
            }
            else {
              if (name != '') {
                document.getElementById("rp_name_validate").style.display = "none";
                document.getElementById("rp_query_validate").style.display = "block";
              }
              if (query != '') {
                document.getElementById("rp_query_validate").style.display = "none";
                document.getElementById("rp_name_validate").style.display = "block";
              }
            }

            $('#rp_dsc').focus();
            checkbox.checked = false;
            return false;
          }
          else {
            document.getElementById("rp_dsc_validate").style.display = "none";
          }
    
          if (query == "") {
            document.getElementById("rp_query_validate").style.display = "block";

            if (name != '' && dsc != '') {
              document.getElementById("rp_name_validate").style.display = "none";
              document.getElementById("rp_dsc_validate").style.display = "none";
            }
            else {
              if (name != '') {
                document.getElementById("rp_name_validate").style.display = "none";
                document.getElementById("rp_dsc_validate").style.display = "block";
              }
              if (dsc != '') {
                document.getElementById("rp_dsc_validate").style.display = "none";
                document.getElementById("rp_name_validate").style.display = "block";
              }
            }

            $('#rp_query').focus();
            checkbox.checked = false;
            return false;
          } else {
            document.getElementById("rp_query_validate").style.display = "none";
          }  
        }      
      }
      return true;
    }


    function onChecked() {    
		// Get the checkbox
		var checkbox = document.getElementById('check_param');
		var rp_name = $('#rp_name').val();
		var rp_dsc = $('#rp_dsc').val();
		var rp_query = $('#rp_query').val();

		$.ajax({
			type: 'POST',
			url: "/Reports/check_view/",
			data: JSON.stringify({
			  rp_name: rp_name
			}),
			success: function (data){
			  if (addReportInputValidate(rp_name, rp_dsc, rp_query, checkbox, data)){
				checkbox.checked = true;  
				
				// If the checkbox is checked, display the output text
				  if (checkbox.checked == true) {
					$('#param_div').show();
				  } 
				  else {
					$('#param_div').hide();
				  }
			  }
			},
			error: function (exception) {
			  alert('Oops! Something went wrong.');
			  console.log('ERROR', exception);
			}
		});     
    }


    function deleteRow(ele) {    
      // Get the checkbox
      var row_id = $(ele).attr('name')
      $("#" + row_id).remove();
    }


    $('#addParam').click(function() {  
		var rp_name = $('#rp_name').val();
		$.ajax({
			type: 'POST',
			url: "{% url 'loadCol' %}",
			data: JSON.stringify({
			  rp_name: rp_name
			}),
			success: function (data) {
			  console.log('success', data);
			  var col_array = JSON.parse(data)
			  
			  // combobox to select table column
			  var str = "<option selected='selected' id='0'>" + col_array[0] + "</option>";
			  var i;
			  for (i = 1; i < col_array.length; i++) {
				str += "<option id='" + i + "'>" + col_array[i] + "</option>"
			  }

			  //combobox to select data type
			  var type = "<option selected='selected'>String</option>"
			  type += "<option>Date</option>"

			  //get num of row
			  var rowCount = $('table#paramTable tr:last').index() + 1;     
				  
			  if (rowCount == 1) {
				//get first row class
				var tr_class = $("#paramTable tr td:first").attr('class');

				//check empty row, if existed then remove
				if (tr_class == 'dataTables_empty'){
				  $("#paramTable tbody tr:first").remove();

				  //add new row
				  $('#paramTable > tbody:last-child')
				  .append("<tr id='row_" + rowCount + "'>"
					+ "<td><select class='form-control select2 param_input' style='width: 100%;' id='col_name_" + rowCount + "'>" + str + "</select></td>"
					//+ "<td><input type='text' class='param_input' name='param_name_" + rowCount + "' id='param_name_" + rowCount + "'><p style='color: red' id='name_validate_" + rowCount + "' hidden><i class='fa fa-exclamation-triangle'></i> Field cannot be null !</p></td>"
					+ "<td><select class='form-control select2 param_input' style='width: 100%;' id='data_type_" + rowCount + "'>" + type + "</select></td>"
					+ "<td style='vertical-align: middle;'><input type='text' class='param_input' name='param_hint_" + rowCount + "' id='param_hint_" + rowCount + "'><p style='color: red' id='hint_validate_" + rowCount + "' hidden><i class='fa fa-exclamation-triangle'></i> Field cannot be null !</p></td>"                
					+ "<td style='text-align: center;'><button type='button' class='custom_btn btn btn btn-danger btn-block btn-default btn-xs fa fa-trash' name='row_" + rowCount + "' onclick='deleteRow(this)'></button></td>"
					+ '</tr>');
				}
				else {
				  //get last row id
				  var row_id = $('table#paramTable tr:last').attr('id');
				  var count = parseInt(row_id.substr(4, 1));

				  //add new row
				  $('#paramTable > tbody:last-child')
				  .append("<tr id='row_" + (count + 1) + "'>"
					+ "<td><select class='form-control select2 param_input' style='width: 100%;' id='col_name_" + (count + 1) + "'>" + str + "</select></td>"
					//+ "<td><input type='text' class='param_input' name='param_name_" + (count + 1) + "' id='param_name_" + (count + 1) + "'><p style='color: red' id='name_validate_" + (count + 1) + "' hidden><i class='fa fa-exclamation-triangle'></i> Field cannot be null !</p></td>"
					+ "<td><select class='form-control select2 param_input' style='width: 100%;' id='data_type_" + (count + 1) + "'>" + type + "</select></td>"
					+ "<td style='vertical-align: middle;'><input type='text' class='param_input' name='param_hint_" + (count + 1) + "' id='param_hint_" + (count + 1) + "'><p style='color: red' id='hint_validate_" + (count + 1) + "' hidden><i class='fa fa-exclamation-triangle'></i> Field cannot be null !</p></td>"
					+ "<td style='text-align: center;'><button type='button' class='custom_btn btn btn btn-danger btn-block btn-default btn-xs fa fa-trash' name='row_" + (count + 1) + "' onclick='deleteRow(this)'></button></td>"
					+ '</tr>');
				}
				
			  }
			  else{
				//get last row id
				var row_id = $('table#paramTable tr:last').attr('id');
				var count = parseInt(row_id.substr(4, 1));

				//add new row
				$('#paramTable > tbody:last-child')
				  .append("<tr id='row_" + (count + 1) + "'>"
					+ "<td><select class='form-control select2 param_input' style='width: 100%;' id='col_name_" + (count + 1) + "'>" + str + "</select></td>"
					//+ "<td><input type='text' class='param_input' name='param_name_" + (count + 1) + "' id='param_name_" + (count + 1) + "'><p style='color: red' id='name_validate_" + (count + 1) + "' hidden><i class='fa fa-exclamation-triangle'></i> Field cannot be null !</p></td>"
					+ "<td><select class='form-control select2 param_input' style='width: 100%;' id='data_type_" + (count + 1) + "'>" + type + "</select></td>"
					+ "<td style='vertical-align: middle;'><input type='text' class='param_input' name='param_hint_" + (count + 1) + "' id='param_hint_" + (count + 1) + "'><p style='color: red' id='hint_validate_" + (count + 1) + "' hidden><i class='fa fa-exclamation-triangle'></i> Field cannot be null !</p></td>"
					+ "<td style='text-align: center;'><button type='button' class='custom_btn btn btn btn-danger btn-block btn-default btn-xs fa fa-trash' name='row_" + (count + 1) + "' onclick='deleteRow(this)'></button></td>"
					+ '</tr>');
			  }
			},
			error: function (exception) {
			  alert('Oops! Something went wrong.');
			  console.log('ERROR', exception);
			}
		});            
    });
