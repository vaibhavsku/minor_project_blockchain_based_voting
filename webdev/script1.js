function f1(){

var from = "0x8CC0b991cA1698242f74bbaf260Dd8BDA6AF4A6A"
var to = "0x8214D7Fd311F42A5Fc11743A9f90c9CB5FeA6926"
var t_hash = "0xcd509352d9ee9d9fc472451209d2b6b68480d8f7fb9cf7aecd99d5704e18e8ae"
var gas = 48188
var gas_t = gas.toString(10, gas)

document.getElementById("heading").innerText = "Transaction Stats"
document.getElementById("page_image").src = "https://img.icons8.com/color/48/000000/ok--v1.png"
document.getElementById("formContent").style.maxWidth = "850px";

document.getElementById("t1").id = "t_hash"
document.getElementById("t2").id = "from"
document.getElementById("b_selected").id = "to"
document.getElementById("c_selected").id = "gas"

document.getElementById("ballotList").remove()
document.getElementById("candidateList").remove()
document.getElementById("ethPrivKey").remove()

document.getElementById("t_hash").innerText = "Transaction Hash : " + t_hash
document.getElementById("from").innerText = "Source Address : " + from
document.getElementById("to").innerText = "Destination Address : " + to
document.getElementById("gas").innerText = "Total gas used : " + gas_t

document.getElementById("vote").id = "result"
document.getElementById("result").value = "View Results"
document.getElementById("result").setAttribute('onclick', 'f2()')
}

function f2(){
    
    var res = document.getElementById("loadresult")
    while(res.firstChild){
        res.firstChild.remove()
    }
    var lst = generateList("b_name", [[0, "BNM"], [1, "BMC"]])
    lst.setAttribute('onchange', 'f3()')
    res.appendChild(lst)
   
}

function f3(){
    res = document.getElementById("loadresult");
    var f = document.getElementById("b_name")
    var val = f.options[f.selectedIndex].value
    if(document.getElementById("b_table") != null){
        document.getElementById("b_table").remove()
    }
    
    if(val == 0){
        var tbl = generateTable("b_table", ["S_No","Candidate", "Votes"], [["1","avvvv", 78687687], ["2","asasa", 868786868]])
        res.appendChild(tbl)
    }
    if(val == 1){
        var tbl = generateTable("b_table", ["S_No","Candidate", "Votes"], [["1","dscsd", 987988798], ["2","aasda", 987987979]])
        res.appendChild(tbl)
    }

}

function generateList(name="", data=[]){
    var b_list = document.createElement("select")
    b_list.id = name
    var op1 = document.createElement("option")
    op1.selected = true
    op1.hidden = true
    op1.disabled = true
    op1.text= "Select a ballot"
    op1.value = ""
    b_list.appendChild(op1)

    for(var i =0; i<data.length; i++){

        var temp = data[i]
        var op = document.createElement("option")
        op.text = temp[1]
        op.value = temp[0]
        b_list.appendChild(op)
   
    }

    return b_list;

}

function generateTable(name="",colnames=[],data=[]){

    var res_table = document.createElement("table")
    res_table.id = name
    var res_head = document.createElement("thead")
    var res_row_heading = document.createElement("tr")

    for(var i=0; i<colnames.length; i++){
        var res_heading_row = document.createElement("th")
        res_heading_row.innerText = colnames[i]
        res_row_heading.appendChild(res_heading_row)
    }
  
    res_head.appendChild(res_row_heading)
    

    var res_table_body = document.createElement("thead");

    for(var i =0; i<data.length; i++){

        var res_row = document.createElement("tr")
        var temp = data[i]
        for(var j =0; j<colnames.length; j++){
            var res_col = document.createElement("td")
            res_col.innerText = temp[j]
            res_row.appendChild(res_col)
        }

        res_table_body.appendChild(res_row)
    }

    res_table.appendChild(res_head)
    res_table.appendChild(res_table_body)
    return res_table
}





