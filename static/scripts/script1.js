var PreviousErrorOcurred = false;
async function ballotOption(){
    document.getElementById("candidateList").disabled = true;
    var val = document.getElementById("ballotList");
    var b_name= val.options[val.selectedIndex].text;
    if(b_name != "--SELECT--"){
        var b_id = val.options[val.selectedIndex].value;
        var data = {ballot_id : b_id};
        var rsp = await postData('/candidates', data);
        var c_list = rsp['candidate_list'];
        document.getElementById("c_selected").innerText = "Candidate selected : ";
        deleteList("candidateList");
        createList("candidateList", c_list);
        document.getElementById("candidateList").disabled = false;
        document.getElementById("b_selected").innerText = "Ballot selected : " + b_name;
    }
   
};

async function vote(){
    document.getElementById("vote_button").disabled = true;
    var ballot_id = document.getElementById("ballotList").options[document.getElementById("ballotList").selectedIndex].value;
    var candidateIndex = document.getElementById("candidateList").selectedIndex;
    var user_priv_key = document.getElementById("ethPrivKey").value;
    var data = {b_id : ballot_id, c_index : candidateIndex, priv_key : user_priv_key};
    var rsp = await postData('/castvote', data);
    if(rsp['response'] == "okay"){
        success(rsp['receipt']);
    }else{
        document.getElementById("vote_button").disabled = false;
        if(PreviousErrorOcurred == true){
            document.getElementById("er_message").firstChild.remove();
         }
         var message = document.createElement("p");
         message.innerText = "Your voting process failed. Please try again";
         document.getElementById("er_message").appendChild(message);
         PreviousErrorOcurred= true;
    }
   
};

function success(stats= {}){
   

        var from = stats['source']
        var to = stats['destination']
        var t_hash = stats['t_hash']
        var gas = stats['totalGas']
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
        if(document.getElementById("er_message").firstChild != null){
            document.getElementById("er_message").firstChild.remove()
        }
        
        document.getElementById("t_hash").innerText = "Transaction Hash : " + t_hash
        document.getElementById("from").innerText = "Source Address : " + from
        document.getElementById("to").innerText = "Destination Address : " + to
        document.getElementById("gas").innerText = "Total gas used : " + gas_t
        
        document.getElementById("vote_button").id = "result"
        document.getElementById("result").value = "View Results"
        document.getElementById("result").setAttribute('onclick', 'f2()')
        document.getElementById("result").disabled = false
        
};

async function f2(){
    
    var res = document.getElementById("loadresult")
    while(res.firstChild){
        res.firstChild.remove()
    }
    var resp = await postData('/getBallots')
    var blts = resp['userballots']
    generateList("b_name", blts)
    var lst = document.getElementById("b_name")
    lst.setAttribute('onchange', 'f3()')
    
   
}

async function f3(){
    var res = document.getElementById("loadresult");
    var f = document.getElementById("b_name")
    var val = f.options[f.selectedIndex].value
    if(document.getElementById("b_table") != null){
        document.getElementById("b_table").remove()
    }
    
    var data = {ballot_id: val}
    var res = await postData('/results', data)
    var result = res['result']
    generateTable("b_table", ["S_No","Candidate", "Votes"], result)
   
    

}

function generateList(name="", data=[]){
    var res = document.getElementById("loadresult")
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

    res.appendChild(b_list)

}




function generateTable(name="",colnames=[],data=[]){
    var res = document.getElementById("loadresult")
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
    res.appendChild(res_table)
}







function votingOption(){
    var val = document.getElementById("candidateList");
    var c_name= val.options[val.selectedIndex].text;
    document.getElementById("c_selected").innerText = "Candidate selected : " + c_name;
};

function createList(listID="", options=[]){
    var list = document.getElementById(listID);
    for(var i = 0; i<options.length; i++){
        var opt = document.createElement("option")
        opt.value = i;
        opt.text = options[i];
        list.appendChild(opt)
    }
};

function deleteList(listID=""){
    var list = document.getElementById(listID);
    while (list.firstChild) {
        list.firstChild.remove();
    }
};

async function postData(url='',data={}){
    var options = {
        method : 'POST',
        headers : {
            'Content-Type'  : 'application/json'
        },
        body : JSON.stringify(data)
    };

    const response =  await fetch(url, options);
    return response.json()
};




