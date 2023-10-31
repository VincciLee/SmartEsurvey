// var question_count = 1;
var question_count = document.getElementsByClassName('question-card').length
// const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
// const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
// const exampleEl = document.getElementById('example')
// const tooltip = new bootstrap.Tooltip(exampleEl, options)

function deleteNote(noteId) {
    fetch('/delete-note', {
        method: 'POST',
        body: JSON.stringify({ noteId: noteId }),
    }).then((_res => {
        window.location.href = "/";
    }))
}

function delete_survey(id, status) {
    fetch('/delete_survey', {
        method: 'POST',
        body: JSON.stringify({ survey_id: id }),
    }).then((_res => {
        window.location.href = "/created_survey/"+status;
    }))
}

function delete_response(response_id, status) {
    fetch('/delete_response', {
        method: 'POST',
        body: JSON.stringify({ response_id: response_id }),
    }).then((_res => {
        window.location.href = "/participated_survey/"+status;
    }))
}

function switch_survey(current, next) {
    // alert(current, next)
    // window.print();
    console.log(current, next);

    var x = (current);
    var y = (next);
    // document.getElementById("current").innerHTML = current;
    // document.getElementById("next").innerHTML = next;

    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
      
    if (y.style.display === "none") {
        y.style.display = "block";
    } else {
        y.style.display = "none";
    }
}

function print(x, y) {
    alert(x, y)
    window.print();
}

function add_question(curr_id) {
    // alert(curr_card_id);
    // alert(curr_id)
    var curr_card_id = "card_" + curr_id
    // var next_id = curr_id + 1
    // var next_card_id = "card_" + next_id
    var curr_card = document.getElementById(curr_card_id);

    question_count = question_count + 1
    var next_card_id = "card_" + question_count
    // <div class="card mx-auto mt-3" style="width: 80%;">
    //         <div class="card-body" style="padding-left: 5%; padding-right: 5%">
    //             <div class="form-group" >
    //                 <label for="questions">Question 1</label>
    //                 <input type="text" class="form-control" id="questions" name="questions[]" placeholder="Enter question">
    //             </div>
    // let displayButton = document.querySelector("form button");

    let card = document.createElement("div");
    card.setAttribute("class", "card mx-auto mt-3 question-card");
    card.setAttribute("id", next_card_id);
    card.setAttribute("style", "width: 80%;");

    let card_body = document.createElement("div");
    card_body.setAttribute("class", "card-body");
    card_body.setAttribute("style", "padding-left: 5%; padding-right: 5%");

    let form = document.createElement("div");
    form.setAttribute("class", "form-group");

    let field = document.createElement("input");
    field.setAttribute("type", "text");
    field.setAttribute("class", "form-control");
    field.setAttribute("id", "questions");
    field.setAttribute("name", "questions[]");
    field.setAttribute("placeholder", "Enter question");

    let form2 = document.createElement("div");
    form2.setAttribute("class", "form-group");

    let field2 = document.createElement("textarea");
    field2.setAttribute("class", "form-control");
    field2.setAttribute("id", "tips");
    field2.setAttribute("name", "tips[]");
    field2.setAttribute("placeholder", "Enter more information to this question (Additional explanation / terms definition etc)");

    let btn_div = document.createElement("div");
    btn_div.setAttribute("class", "d-flex justify-content-end");

    let btn_add = document.createElement("button");
    btn_add.setAttribute("type", "button");
    btn_add.setAttribute("class", "add btn btn-primary ms-3");
    btn_add.setAttribute("onclick", "add_question("+question_count+")");

    let i_add = document.createElement("i");
    i_add.setAttribute("class", "fa fa-plus");

    let btn_delete = document.createElement("button");
    btn_delete.setAttribute("type", "button");
    btn_delete.setAttribute("class", "remove btn btn-primary");
    btn_delete.setAttribute("onclick", "remove_question("+question_count+")");

    let i_delete = document.createElement("i");
    i_delete.setAttribute("class", "fa fa-minus");

    btn_add.append(i_add)
    btn_add.append(" Add ")
    btn_delete.append(i_delete)
    btn_delete.append(" Remove ")
    btn_div.append(btn_delete)
    btn_div.append(btn_add)

    form2.append(field2)
    form.append(field)
    card_body.append(form)
    card_body.append(form2)
    card_body.append(btn_div)
    card.append(card_body)

    // var html_code = '<div class="card mx-auto mt-3 question-card" id="'+next_card_id+'" style="width: 80%;">' +
    // '<div class="card-body" style="padding-left: 5%; padding-right: 5%">' +
    // '<div class="form-group" >' + 
    // '<input type="text" class="form-control" id="questions" name="questions[]" placeholder="Enter question">' + '</div>' + '<div>' + '<button type="button" class="add btn btn-primary ms-3" onclick="add_question('+question_count+')"><i class="fa fa-plus"></i> Add </button><button type="button" class="remove btn btn-primary ms-3" onclick="remove_question('+question_count+')"><i class="fa fa-minus"></i> Remove </button>' + '</div>' + '</div>' + '</div>'

    // form.insertBefore(card, displayButton)   
    curr_card.after(card);
    // var html = $.parseHTML(html_code);
    // curr_card.after(html);

    // alert(curr_card_id);
    // alert(card.outerHTML);
    // alert(html);
    // console.log(card.outerHTML)
    // const para = document.createElement("p");
    // const node = document.createTextNode(card);
    // para.appendChild(node);
    // const element = document.getElementById("div1");
    // element.appendChild(para);


    // alert(card);
}

function remove_question(curr_id) {
    question_num = document.getElementsByClassName("question-card").length

    if (question_num > 1) {
        var curr_card_id = "card_" + curr_id
        var curr_card = document.getElementById(curr_card_id);
        curr_card.remove();
    }
}

function show_hide_code(id){
    modal_id = "modal"+id;

    var modal = document.getElementById(modal_id);
    
    if (modal.style.display == "none"){
        modal.style.display = "block";
    }else{
        modal.style.display = "none";
    }
}

// function add_question(curr_ques) {
//     var new_num = curr_ques.split("_")[1] + 1
//     var new_ques = "question_" + new_num
//     new_question_list.push(new_ques)
//     document.getElementById(question_1).innerHTML = myVar;
// }

/*{ <div class="card mx-auto mt-3 question-card" id="card_3" style="width: 80%;">
    <div class="card-body" style="padding-left: 5%; padding-right: 5%">
        <div class="form-group">
            <input type="text" class="form-control" id="questions" name="questions[]" placeholder="Enter question">

        </div>
<div>
    <span class="add btn btn-primary" onclick="add_question(3)">
        <i class="fa fa-plus"></i>Add
    </span>
    <span class="remove btn btn-primary" onclick="remove_question(3)">
        <i class="fa fa-minus"></i>Remove</span>
</div> }*/